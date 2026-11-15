import copy,hashlib,json,sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from bounded_ocr import BoundedOCRRuntime
from preview_context import inspect_preview_context


class PreviewLineEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        a=json.loads((ROOT/'artifacts/exploration-20261102-01/audit-summary.json').read_text(encoding='utf-8'))
        cls.cases={r['number']:r for r in a['rows']}
        cls.runtime=BoundedOCRRuntime(960);cls.runtime.__enter__()
    @classmethod
    def tearDownClass(cls):cls.runtime.close()
    def sample(self,n):
        r=self.cases[n]
        return Image.open(r['criticalImage']).convert('RGB'),json.loads(Path(r['criticalPacket']).read_text(encoding='utf-8'))
    def test_actual_normal_suffix_and_timer_need_complete_original_line(self):
        for n in [52,53,55,56,57]:
            with self.subTest(n=n):
                im,p=self.sample(n);before=copy.deepcopy(p)
                self.assertTrue(inspect_preview_context(im,p)['verified'])
                self.assertEqual(p,before)
    def test_erased_normal_or_timer_cannot_be_restored_from_old_rows(self):
        for n in [52,53,55,57]:
            for label in ['Difficulty','Time Limit','Enter']:
                with self.subTest(n=n,label=label):
                    im,p=self.sample(n);r=next(e for e in p['evidence'] if e['text']==label)
                    x=min(q[0] for q in r['box']);y=min(q[1] for q in r['box']);bottom=max(q[1] for q in r['box']);h=bottom-y
                    ImageDraw.Draw(im).rectangle((x,y-h*.5,im.width,bottom+h*.5),fill=(55,59,92))
                    p['binding']['pixelSha256']=hashlib.sha256(im.tobytes()).hexdigest()
                    self.assertFalse(inspect_preview_context(im,p)['verified'])
    def test_no_label_or_duplicate_label_cannot_grant_wait(self):
        im,p=self.sample(53)
        for label in ['Difficulty','Time Limit']:
            for duplicate in [False,True]:
                q=copy.deepcopy(p);r=next(e for e in q['evidence'] if e['text']==label)
                if duplicate:q['evidence'].append(copy.deepcopy(r))
                else:q['evidence'].remove(r)
                self.assertFalse(inspect_preview_context(im,q)['verified'])


if __name__=='__main__':unittest.main()
