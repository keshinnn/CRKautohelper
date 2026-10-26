"""Re-run the frozen 30 negative variants and positive/negative grader controls."""
import argparse,hashlib,importlib.util,json,os,subprocess,sys
from pathlib import Path


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--positive-analysis',required=True);args=parser.parse_args()
    root=Path(__file__).resolve().parents[1];out=Path(args.output).resolve();out.mkdir()
    spec=importlib.util.spec_from_file_location('regression',root/'scripts/convergence-regression.py');reg=importlib.util.module_from_spec(spec);spec.loader.exec_module(reg)
    sys.path.insert(0,str(root/'ml'));from runtime_evidence import capture_runtime_evidence
    runtime=capture_runtime_evidence();v1=Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper')).resolve();deps=reg.dependency_snapshot(v1,runtime);code=reg.code_snapshot(root)
    qualification=root/'data/p4c/negative-random-source-v1.json';q=json.loads(qualification.read_text(encoding='utf-8'));source=root/q['sourceManifest']
    if reg.sha(source)!=q['sourceManifestSha256'] or q['cases']!=30 or q['renderedFrames']!=60:raise ValueError('NEGATIVE_CORPUS_CHANGED')
    m=json.loads(source.read_text(encoding='utf-8'));report={'passed':False,'results':[],'expectedCases':30,'sourceQualificationSha256':reg.sha(qualification),'sourceManifestSha256':reg.sha(source),'code':code,'externalDependencies':deps,'runtimeFingerprint':runtime['fingerprint'],'runnerSha256':reg.sha(__file__),'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip(),'nativeActions':0,'virtualClicks':0,'formalNegativeGateComplete':False,'g4Complete':False,'holdoutTouched':False}
    def unchanged():
        reg.check_snapshot(root,code)
        if reg.dependency_snapshot(v1,runtime)!=deps:raise ValueError('EXTERNAL_DEPENDENCIES_CHANGED')
    def save():(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    def check(manifest,folder):
        with (folder/'check.log').open('wb') as log:r=subprocess.run(['node','scripts/negative-selection-check.cjs',str(manifest),str(folder/'check')],cwd=root,stdout=log,stderr=subprocess.STDOUT)
        unchanged();return r.returncode,json.loads((folder/'check/report.json').read_text(encoding='utf-8'))
    try:
        for c in m['cases']:
            unchanged();folder=out/c['id'];folder.mkdir();p=folder/'source.json';p.write_text(json.dumps({**m,'cases':[c]},indent=2),encoding='utf-8')
            with (folder/'analysis.log').open('wb') as log:r=subprocess.run([sys.executable,'-B','ml/analyze_cases.py',str(p),str(folder/'analysis'),'--fast-map','--bounded-ocr','960'],cwd=root,stdout=log,stderr=subprocess.STDOUT)
            unchanged()
            if r.returncode and 'UNKNOWN; failure packet preserved:' not in (folder/'analysis.log').read_text(encoding='utf-8'):raise ValueError('UNEXPECTED_NEGATIVE_ANALYSIS_FAILURE')
            status,result=check(folder/'analysis/manifest.json',folder);report['results'].append({k:v for k,v in result.items() if k!='version'});save()
            print(json.dumps({'completed':len(report['results']),'id':c['id'],'passed':result['passed']}),flush=True)
            if status or not result['passed']:raise ValueError('NEGATIVE_REJECTION_FAILED')
        positive_file=Path(args.positive_analysis).resolve();positive=json.loads(positive_file.read_text(encoding='utf-8'))
        original=next(c for c in positive['cases'] if c['id']=='zone-2-first-battle-random-fixed')
        controls=[]
        for label,invalid in [('gray-request',True),('eligible-request',False)]:
            folder=out/label;folder.mkdir();c=json.loads(json.dumps(original));c.update(id=label,frames=c['frames'][:2],expectedRecognizedMapContext=True,expectedRejectionReasons=['NODE_UNAVAILABLE','COORDINATE_INVALID'])
            if invalid:c['intent']={'zone':2,'floor':1,'column':1,'event':'battle','mode':'select'}
            p=folder/'source.json';p.write_text(json.dumps({**positive,'cases':[c]},indent=2),encoding='utf-8')
            status,result=check(p,folder)
            if not result['recognizedMapContext'] or result['passed'] is not invalid or result['unexpectedSelectionProof'] is invalid or status!=int(not invalid):raise ValueError('GRADER_CONTROL_FAILED')
            controls.append({'label':label,'correctlyGraded':True,'analysisSourceSha256':reg.sha(positive_file)})
        report.update(passed=len(report['results'])==30 and all(r['passed'] for r in report['results']),controls=controls);save()
    except BaseException as error:report['error']=str(error);save();raise


if __name__=='__main__':main()
