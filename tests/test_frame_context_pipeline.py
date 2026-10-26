import json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class SameFramePipelineTests(unittest.TestCase):
    def test_actual_supplement_reuses_only_raw_candidates_and_preserves_all_semantic_evidence(self):
        before=json.loads((ROOT/'artifacts/performance-20261027/unprofiled-before-01/manifest.json').read_text(encoding='utf-8'))
        case=next(c for c in before['cases'] if c['id']=='dev-primary-zone6-floor1-col2-random-fixed')
        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts') as tmp:
            source=Path(tmp)/'source.json';out=Path(tmp)/'analysis';source.write_text(json.dumps({**before,'cases':[case]}),encoding='utf-8')
            r=subprocess.run([sys.executable,'-B','ml/analyze_cases.py',str(source),str(out),'--fast-map','--bounded-ocr','960'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=120)
            self.assertEqual(r.returncode,0,r.stderr)
            after=json.loads((out/'manifest.json').read_text(encoding='utf-8'));hits=0
            for old,new in zip(case['frames'],after['cases'][0]['frames']):
                p=json.loads(Path(old['packet']).read_text(encoding='utf-8'));q=json.loads(Path(new['packet']).read_text(encoding='utf-8'))
                self.assertTrue('frameIntermediates' in q,'missing same-frame stats');self.assertFalse(q['frameIntermediates']['crossFrameReuse']);self.assertTrue(q['analysisTiming']['freshFullPipeline']);hits+=q['frameIntermediates']['hits']
                for k in ['binding','flow','evidence','mapReview','v2OriginalMapReview','progress','v2TrackedMap','v2PreviewContext','v2Preview','v2MapActions']:self.assertEqual(p.get(k),q.get(k),k)
            self.assertGreater(hits,0)
if __name__=='__main__':unittest.main()
