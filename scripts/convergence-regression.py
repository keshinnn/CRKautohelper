"""Version-bound offline regression. Explicit input only; never advances a corpus.

Each shard runs the current observer, then the current virtual transaction.
Optional cache is raw V1 evidence only; analyze_cases validates its OCR runtime.
No native capture/input module is invoked. Fresh and cached frames are counted.
"""
import argparse,concurrent.futures,hashlib,json,subprocess,sys,time,os
from pathlib import Path


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def code_snapshot(root):
    return {p.relative_to(root).as_posix():sha(p) for folder in ['ml','lib','scripts','tests','data']
            if (root/folder).exists() for p in sorted((root/folder).rglob('*'))
            if p.is_file() and p.suffix in ['.py','.cjs','.js','.json','.png','.onnx','.yaml','.yml']}


def dependency_snapshot(v1,runtime):
    paths=[]
    for folder in ['ml','data/map','data/flow']:
        base=v1/folder
        if not base.is_dir():raise ValueError('V1_DEPENDENCY_DIRECTORY_MISSING')
        paths.extend(p for p in base.rglob('*') if p.is_file() and p.suffix in ['.py','.json','.png','.onnx','.yaml','.yml'])
    paths.extend(Path(runtime['packageRoot'])/a['path'] for a in runtime['ocrAssets'])
    return {str(p.resolve()):sha(p) for p in sorted(set(paths))}


def check_snapshot(root,expected):
    if code_snapshot(root)!=expected:raise ValueError('CODE_OR_DATA_CHANGED_DURING_REGRESSION')


def merge_cases(source,shards):
    by_id={}
    for shard in shards:
        for c in shard['cases']:
            if c['id'] in by_id:raise ValueError('DUPLICATE_CASE')
            by_id[c['id']]=c
    if set(by_id)!={c['id'] for c in source['cases']}:raise ValueError('CASE_SET_CHANGED')
    merged=[]
    for before in source['cases']:
        after=by_id[before['id']]
        if {k:v for k,v in before.items() if k!='frames'}!={k:v for k,v in after.items() if k!='frames'}:raise ValueError('CASE_CHANGED')
        if len(before['frames'])!=len(after['frames']):raise ValueError('FRAME_COUNT_CHANGED')
        for a,b in zip(before['frames'],after['frames']):
            if {k:v for k,v in a.items() if k!='packet'}!={k:v for k,v in b.items() if k!='packet'}:raise ValueError('FRAME_CHANGED')
        merged.append(after)
    return merged


def replay_command(manifest,out,source):
    if source.get('stage') in ['P4-A','P4-B']:
        expected='none' if source['stage']=='P4-A' else 'fixed_scale'
        if source.get('transform')!=expected:raise ValueError('MILESTONE_TRANSFORM_INVALID')
        return ['node','scripts/accept-replay.cjs',str(manifest),'data/p4a/cases.json',str(out)]
    return ['node','scripts/replay-development.cjs',str(manifest),str(out)]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',required=True);parser.add_argument('--output',required=True)
    parser.add_argument('--workers',type=int,choices=[1,2,3],default=1);parser.add_argument('--cache');parser.add_argument('--disable-frame-reuse',action='store_true')
    args=parser.parse_args();root=Path(__file__).resolve().parents[1];out=Path(args.output).resolve();out.mkdir()
    source=Path(args.source).resolve();raw=source.read_bytes();original=json.loads(raw)
    if not original.get('cases'):raise ValueError('NO_CASES')
    (out/'source.snapshot.json').write_bytes(raw);code=code_snapshot(root)
    sys.path.insert(0,str(root/'ml'))
    from runtime_evidence import capture_runtime_evidence
    runtime=capture_runtime_evidence();v1=Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper')).resolve()
    dependencies=dependency_snapshot(v1,runtime)
    report={'stage':'architecture-convergence-regression','complete':False,'passed':False,
            'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip(),
            'workingTreeStatus':subprocess.check_output(['git','status','--porcelain'],cwd=root).decode(),
            'code':code,'externalDependencies':dependencies,'runtimeFingerprint':runtime['fingerprint'],
            'runnerSha256':sha(__file__),'sourceManifestSha256':sha(source),
            'cacheManifestSha256':sha(args.cache) if args.cache else None,
            'expectedCases':len(original['cases']),'workers':args.workers,'frameReuseEnabled':not args.disable_frame_reuse,'performanceEvidence':False,
            'nativeActions':0,'g4Complete':False,'mapBackendPolicy':'exact_grouped_masks_parallel4_phase_coverage','shards':[]}
    def save():(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    def run_shard(index):
        folder=out/f'shard-{index}';folder.mkdir();group={**original,'cases':original['cases'][index::args.workers]}
        src=folder/'source.json';src.write_text(json.dumps(group,indent=2),encoding='utf-8')
        command=[sys.executable,'-B','ml/analyze_cases.py',str(src),str(folder/'analysis'),'--fast-map','--map-coverage','--bounded-ocr','960']
        if args.disable_frame_reuse:command+=['--disable-frame-reuse']
        if args.cache:command+=['--cache',str(Path(args.cache).resolve())]
        with (folder/'analysis.log').open('wb') as log:r=subprocess.run(command,cwd=root,stdout=log,stderr=subprocess.STDOUT)
        return index,folder,r.returncode
    save()
    try:
        # Each subprocess owns its reader and monkeypatches; no shared Python runtime.
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            pending=[pool.submit(run_shard,i) for i in range(min(args.workers,len(original['cases'])))]
            while pending:
                done,rest=concurrent.futures.wait(pending,timeout=1,return_when=concurrent.futures.FIRST_COMPLETED)
                check_snapshot(root,code)
                if dependency_snapshot(v1,runtime)!=dependencies:raise ValueError('EXTERNAL_DEPENDENCIES_CHANGED')
                for result in done:
                    i,folder,status=result.result();report['shards'].append({'index':i,'path':str(folder),'status':status});save()
                    print(json.dumps({'shard':i,'status':status}),flush=True)
                pending=list(rest)
        if any(s['status']!=0 for s in report['shards']):raise ValueError('ANALYSIS_FAILED_SEE_SHARD_LOG')
        manifests=[json.loads((Path(s['path'])/'analysis/manifest.json').read_text(encoding='utf-8')) for s in sorted(report['shards'],key=lambda s:s['index'])]
        if not all(m['analysis']['allFramesAnalyzed'] is True for m in manifests):raise ValueError('INCOMPLETE_ANALYSIS')
        if not all(m['analysis'].get('mapBackend')==report['mapBackendPolicy'] for m in manifests):raise ValueError('WRONG_MAP_BACKEND_POLICY')
        if not all(m['analysis']['runtimeEvidence']['fingerprint']==runtime['fingerprint'] for m in manifests):raise ValueError('SHARD_RUNTIME_MISMATCH')
        cases=merge_cases(original,manifests);merged={**original,'cases':cases,'analysis':{**manifests[0]['analysis'],'sourceManifestSha256':sha(source),'shardProvenance':report['shards']}}
        manifest=out/'manifest.json';manifest.write_text(json.dumps(merged,indent=2),encoding='utf-8')
        report['frames']=sum(len(c['frames']) for c in cases);report['freshFrames']=report['cachedRawV1Frames']=0
        for c in cases:
            for f in c['frames']:
                if sha(f['image'])!=f['sha256']:raise ValueError('SOURCE_PNG_CHANGED')
                p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
                report['freshFrames' if p['analysisTiming']['freshFullPipeline'] else 'cachedRawV1Frames']+=1
        check_snapshot(root,code)
        if dependency_snapshot(v1,runtime)!=dependencies:raise ValueError('EXTERNAL_DEPENDENCIES_CHANGED')
        with (out/'replay.log').open('wb') as log:r=subprocess.run(replay_command(manifest,out/'replay',original),cwd=root,stdout=log,stderr=subprocess.STDOUT)
        check_snapshot(root,code)
        if dependency_snapshot(v1,runtime)!=dependencies:raise ValueError('EXTERNAL_DEPENDENCIES_CHANGED')
        replay=out/'replay/report.json'
        if replay.exists():report.update(replayReportSha256=sha(replay),results=json.loads(replay.read_text(encoding='utf-8'))['results'])
        if r.returncode:raise ValueError('REPLAY_FAILED_SEE_REPLAY_LOG')
        if len(report.get('results',[]))!=len(cases) or not all(r['passed'] for r in report['results']):raise ValueError('REPLAY_COUNT_OR_GRADE_INVALID')
        report.update(passed=True,complete=True);save();print(json.dumps({'passed':True,'cases':len(cases),'frames':report['frames'],'freshFrames':report['freshFrames'],'cachedRawV1Frames':report['cachedRawV1Frames'],'nativeActions':0}),flush=True)
    except BaseException as error:
        report['error']=str(error);save();raise


if __name__=='__main__':main()
