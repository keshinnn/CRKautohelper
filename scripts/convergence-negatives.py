"""Re-run the frozen 30 negative variants and positive/negative grader controls."""
import argparse,hashlib,importlib.util,json,os,subprocess,sys
from pathlib import Path


def require_phase_backend(manifest,code):
    analysis=manifest.get('analysis') or {}
    expected={'mapBackend':'exact_grouped_masks_parallel4_phase_coverage',
              'mapBackendSha256':code['ml/fast_map_candidates.py'],
              'mapPipelineSha256':code['ml/map_pipeline.py']}
    if any(analysis.get(key)!=value for key,value in expected.items()):
        raise ValueError('CURRENT_COVERAGE_BACKEND_REQUIRED')


def control_case(manifest,case_id):
    cases=[c for c in manifest['cases'] if c['id']==case_id]
    if len(cases)!=1 or len(cases[0]['frames'])<2:raise ValueError('CONTROL_CASE_REQUIRED')
    for f in cases[0]['frames'][:2]:
        packet=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
        if packet.get('analysisTiming',{}).get('freshFullPipeline') is not True:raise ValueError('FRESH_CONTROL_REQUIRED')
    return cases[0]


def control_request(source,label):
    if label not in ['gray-request','eligible-request']:raise ValueError('CONTROL_LABEL_INVALID')
    if label=='gray-request' and (source.get('baseNegativeId')!='neg-native-gray-node' or source.get('expectedRecognizedMapContext') is not True):raise ValueError('REVIEWED_GRAY_CONTROL_REQUIRED')
    c=json.loads(json.dumps(source));c.update(id=label,frames=c['frames'][:2],expectedRecognizedMapContext=True)
    if label=='eligible-request':c['expectedRejectionReasons']=['NODE_UNAVAILABLE','COORDINATE_INVALID']
    return c


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--positive-analysis',required=True);parser.add_argument('--control-case',default='zone-2-first-battle-random-fixed');args=parser.parse_args()
    root=Path(__file__).resolve().parents[1];out=Path(args.output).resolve();out.mkdir()
    spec=importlib.util.spec_from_file_location('regression',root/'scripts/convergence-regression.py');reg=importlib.util.module_from_spec(spec);spec.loader.exec_module(reg)
    sys.path.insert(0,str(root/'ml'));from runtime_evidence import capture_runtime_evidence
    runtime=capture_runtime_evidence();v1=Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper')).resolve();deps=reg.dependency_snapshot(v1,runtime);code=reg.code_snapshot(root)
    qualification=root/'data/p4c/negative-random-source-v1.json';q=json.loads(qualification.read_text(encoding='utf-8'));source=root/q['sourceManifest']
    if reg.sha(source)!=q['sourceManifestSha256'] or q['cases']!=30 or q['renderedFrames']!=60:raise ValueError('NEGATIVE_CORPUS_CHANGED')
    m=json.loads(source.read_text(encoding='utf-8'));report={'passed':False,'results':[],'expectedCases':30,'sourceQualificationSha256':reg.sha(qualification),'sourceManifestSha256':reg.sha(source),'code':code,'externalDependencies':deps,'runtimeFingerprint':runtime['fingerprint'],'runnerSha256':reg.sha(__file__),'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip(),'nativeActions':0,'virtualClicks':0,'formalNegativeGateComplete':False,'g4Complete':False,'holdoutTouched':False,'mapBackendPolicy':'exact_grouped_masks_parallel4_phase_coverage'}
    def unchanged():
        reg.check_snapshot(root,code)
        if reg.dependency_snapshot(v1,runtime)!=deps:raise ValueError('EXTERNAL_DEPENDENCIES_CHANGED')
    def save():(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    def check(manifest,folder):
        with (folder/'check.log').open('wb') as log:r=subprocess.run(['node','scripts/negative-selection-check.cjs',str(manifest),str(folder/'check')],cwd=root,stdout=log,stderr=subprocess.STDOUT)
        unchanged();return r.returncode,json.loads((folder/'check/report.json').read_text(encoding='utf-8'))
    try:
        positive_file=Path(args.positive_analysis).resolve();positive=json.loads(positive_file.read_text(encoding='utf-8'))
        require_phase_backend(positive,code)
        original=control_case(positive,args.control_case)
        for c in m['cases']:
            unchanged();folder=out/c['id'];folder.mkdir();p=folder/'source.json';p.write_text(json.dumps({**m,'cases':[c]},indent=2),encoding='utf-8')
            with (folder/'analysis.log').open('wb') as log:r=subprocess.run([sys.executable,'-B','ml/analyze_cases.py',str(p),str(folder/'analysis'),'--fast-map','--map-coverage','--bounded-ocr','960'],cwd=root,stdout=log,stderr=subprocess.STDOUT)
            unchanged()
            if r.returncode and 'UNKNOWN; failure packet preserved:' not in (folder/'analysis.log').read_text(encoding='utf-8'):raise ValueError('UNEXPECTED_NEGATIVE_ANALYSIS_FAILURE')
            analyzed=folder/'analysis/manifest.json'
            require_phase_backend(json.loads(analyzed.read_text(encoding='utf-8')),code)
            status,result=check(analyzed,folder)
            report['results'].append({**{k:v for k,v in result.items() if k!='version'},'analysisManifestSha256':reg.sha(analyzed),'mapBackendPolicy':report['mapBackendPolicy']});save()
            print(json.dumps({'completed':len(report['results']),'id':c['id'],'passed':result['passed']}),flush=True)
            if status or not result['passed']:raise ValueError('NEGATIVE_REJECTION_FAILED')
        gray_case=next(c for c in m['cases'] if c.get('baseNegativeId')=='neg-native-gray-node')
        gray_file=out/gray_case['id']/'analysis/manifest.json';gray_manifest=json.loads(gray_file.read_text(encoding='utf-8'))
        gray=control_case(gray_manifest,gray_case['id'])
        controls=[]
        for label,invalid in [('gray-request',True),('eligible-request',False)]:
            folder=out/label;folder.mkdir();c=control_request(gray if invalid else original,label)
            p=folder/'source.json';p.write_text(json.dumps({**(gray_manifest if invalid else positive),'cases':[c]},indent=2),encoding='utf-8')
            status,result=check(p,folder)
            if not result['recognizedMapContext'] or result['passed'] is not invalid or result['unexpectedSelectionProof'] is invalid or status!=int(not invalid):raise ValueError('GRADER_CONTROL_FAILED')
            controls.append({'label':label,'correctlyGraded':True,'analysisSourceSha256':reg.sha(gray_file if invalid else positive_file)})
        report.update(passed=len(report['results'])==30 and all(r['passed'] for r in report['results']),controls=controls);save()
    except BaseException as error:report['error']=str(error);save();raise


if __name__=='__main__':main()
