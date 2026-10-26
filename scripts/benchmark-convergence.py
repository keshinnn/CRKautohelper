"""Single-worker warmed baseline, including current functional replay; no tuning."""
import argparse,hashlib,json,math,platform,subprocess,sys
from pathlib import Path


def percentiles(values):
    if not values:raise ValueError('NO_MEASURED_SAMPLES')
    a=sorted(values)
    return {'count':len(a),'p50':a[math.ceil(len(a)*.5)-1],'p95':a[math.ceil(len(a)*.95)-1],'max':a[-1]}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);parser.add_argument('--output',required=True);parser.add_argument('--warmup',type=int,default=10);parser.add_argument('--disable-frame-reuse',action='store_true');args=parser.parse_args()
    if args.warmup<1:raise ValueError('EXPLICIT_WARMUP_REQUIRED')
    root=Path(__file__).resolve().parents[1];out=Path(args.output).resolve()
    subprocess.run([sys.executable,'-B','scripts/convergence-regression.py','--source',args.source,'--output',str(out),'--workers','1']+(['--disable-frame-reuse'] if args.disable_frame_reuse else []),cwd=root,check=True)
    run=json.loads((out/'report.json').read_text(encoding='utf-8'));m=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
    packets=[json.loads(Path(f['packet']).read_text(encoding='utf-8')) for c in m['cases'] for f in c['frames']]
    records=[p['analysisTiming'] for p in packets]
    if not all(r['freshFullPipeline'] for r in records):raise ValueError('CACHE_FORBIDDEN_IN_BASELINE')
    measured=records[args.warmup:]
    if len(measured)<20:raise ValueError('INSUFFICIENT_WARM_SAMPLES')
    modules=sorted(measured[0]['moduleMs'])
    if not all(sorted(r['moduleMs'])==modules and all(v>=0 for v in r['moduleMs'].values()) and sum(r['moduleMs'].values())<=r['elapsedMs']+.01 for r in measured):raise ValueError('TIMING_PARTITION_INVALID')
    node_file=out/'node-timing.json'
    subprocess.run(['node','scripts/benchmark-replay.cjs',str(out/'manifest.json'),str(node_file)],cwd=root,check=True)
    node=json.loads(node_file.read_text(encoding='utf-8'));warm={p['binding']['frameId'] for p in packets[:args.warmup]}
    causal=[r for r in node['rows'] if r['frameId'] not in warm]
    within=[x for p in packets[args.warmup:] for x in p.get('frameIntermediates',{}).get('calls',[])]
    hit=[x['elapsedMs'] for x in within if x['hit']];miss=[x['elapsedMs'] for x in within if not x['hit']]
    slow=max(packets[args.warmup:],key=lambda p:p['analysisTiming']['elapsedMs'])
    slow_module=max(slow['analysisTiming']['moduleMs'],key=slow['analysisTiming']['moduleMs'].get)
    result={'schema':1,'workers':1,'cache':False,'warmupFrames':args.warmup,'sameFrameReuse':{'enabled':not args.disable_frame_reuse,'crossFrame':False,'hits':len(hit),'misses':len(miss),'hitMs':percentiles(hit) if hit else None,'missMs':percentiles(miss) if miss else None},
      'slowestWarmedFrame':{'frameId':slow['binding']['frameId'],'sourceBinding':slow.get('sourceBinding'),'elapsedMs':slow['analysisTiming']['elapsedMs'],'dominantModule':slow_module,'dominantModuleMs':slow['analysisTiming']['moduleMs'][slow_module]},'warmedAnalysisMs':percentiles([r['elapsedMs'] for r in measured]),
      'warmedNodeMs':percentiles([r['nodeMs'] for r in causal]),'warmedOverallCpuMs':percentiles([r['overallMs'] for r in causal]),
      'modulesMs':{name:percentiles([r['moduleMs'][name] for r in measured]) for name in modules},
      'commit':run['commit'],'code':run['code'],'externalDependencies':run['externalDependencies'],
      'sourceManifestSha256':run['sourceManifestSha256'],'runnerSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'runtimeFingerprint':run['runtimeFingerprint'],'platform':platform.platform(),'nativeActions':0,'g4Complete':False,
      'method':'nearest-rank percentiles; one project inference worker, no other project tests/inference scheduled concurrently; module/producer stats use all analyzed frames after warmup; combined stats use consumed causal replay frames. Combined CPU baseline sums measured producer+Node adapter/selection/transaction/verification, not continuous live latency; capture/IPC and report I/O excluded.',
      'formalG4PerformanceAcceptance':False}
    result['baselineAnalysisP95Within1500']=result['warmedAnalysisMs']['p95']<=1500
    result['baselineOverallP95Within1500']=result['warmedOverallCpuMs']['p95']<=1500
    (out/'performance.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result['warmedAnalysisMs']),flush=True)


if __name__=='__main__':main()
