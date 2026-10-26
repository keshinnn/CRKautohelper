"""Single-worker warmed baseline, including current functional replay; no tuning."""
import argparse,hashlib,json,math,platform,subprocess,sys
from pathlib import Path


def percentiles(values):
    if not values:raise ValueError('NO_MEASURED_SAMPLES')
    a=sorted(values)
    return {'count':len(a),'p50':a[math.ceil(len(a)*.5)-1],'p95':a[math.ceil(len(a)*.95)-1],'max':a[-1]}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);parser.add_argument('--output',required=True);parser.add_argument('--warmup',type=int,default=10);args=parser.parse_args()
    if args.warmup<1:raise ValueError('EXPLICIT_WARMUP_REQUIRED')
    root=Path(__file__).resolve().parents[1];out=Path(args.output).resolve()
    subprocess.run([sys.executable,'-B','scripts/convergence-regression.py','--source',args.source,'--output',str(out),'--workers','1'],cwd=root,check=True)
    run=json.loads((out/'report.json').read_text(encoding='utf-8'));m=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
    records=[json.loads(Path(f['packet']).read_text(encoding='utf-8'))['analysisTiming'] for c in m['cases'] for f in c['frames']]
    if not all(r['freshFullPipeline'] for r in records):raise ValueError('CACHE_FORBIDDEN_IN_BASELINE')
    measured=records[args.warmup:]
    if len(measured)<20:raise ValueError('INSUFFICIENT_WARM_SAMPLES')
    modules=sorted(measured[0]['moduleMs'])
    if not all(sorted(r['moduleMs'])==modules and all(v>=0 for v in r['moduleMs'].values()) and sum(r['moduleMs'].values())<=r['elapsedMs']+.01 for r in measured):raise ValueError('TIMING_PARTITION_INVALID')
    result={'schema':1,'workers':1,'cache':False,'warmupFrames':args.warmup,'warmedAnalysisMs':percentiles([r['elapsedMs'] for r in measured]),
      'modulesMs':{name:percentiles([r['moduleMs'][name] for r in measured]) for name in modules},
      'commit':run['commit'],'code':run['code'],'externalDependencies':run['externalDependencies'],
      'sourceManifestSha256':run['sourceManifestSha256'],'runnerSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'runtimeFingerprint':run['runtimeFingerprint'],'platform':platform.platform(),'nativeActions':0,'g4Complete':False,
      'method':'nearest-rank percentiles; one project inference worker, no other project tests/inference scheduled concurrently; Python decode through observation assembly, JSON/artifact I/O excluded; Node adapter timings in associated replay',
      'formalG4PerformanceAcceptance':False}
    result['baselineAnalysisP95Within1500']=result['warmedAnalysisMs']['p95']<=1500
    (out/'performance.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result['warmedAnalysisMs']),flush=True)


if __name__=='__main__':main()
