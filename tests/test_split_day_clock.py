import json,sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from bounded_ocr import BoundedOCRRuntime
from progress_evidence import ProgressRuntime
from english_scene import EnglishSceneRuntime,semantic_state
class SplitDayClockTests(unittest.TestCase):
 def fixture(self):
  b=ROOT/'artifacts/p4c-random-development-60-run-24/dev-L0-zone6-floor1-col2-resume-1781-random-post-change';m=json.loads((b/'analysis/manifest.json').read_text(encoding='utf-8'));f=m['cases'][0]['frames'][20];p=json.loads(Path(f['packet']).read_text(encoding='utf-8'));return Image.open(f['image']).convert('RGB'),p['evidence']
 def test_actual_days_stay_with_label_while_clock_is_separate_requires_full_reread(self):
  im,rows=self.fixture()
  with ProgressRuntime(),BoundedOCRRuntime(960) as runtime,EnglishSceneRuntime():
   result=runtime._reread_map_context(im,rows);state=semantic_state(result)
  self.assertEqual(state['state'],'MAP');self.assertGreaterEqual(state['confidence'],.9)
  timer=next(r for r in result if r.get('contextKind')=='timer');self.assertGreaterEqual(timer['score'],.9);self.assertIn('12天',timer['remainingLabelLocator']['text']);self.assertEqual(timer['adjacentClockLocator']['text'],'13:09:18');self.assertIn('13:09:18',timer['text'])
 def test_erased_days_or_clock_cannot_be_restored_from_split_tokens(self):
  for box in [(50,56,190,84),(190,56,284,84)]:
   im,rows=self.fixture();ImageDraw.Draw(im).rectangle(box,fill=(30,30,60))
   with ProgressRuntime(),BoundedOCRRuntime(960) as runtime,EnglishSceneRuntime():
    result=runtime._reread_map_context(im,rows);self.assertFalse(any(r.get('contextKind')=='timer' for r in result));self.assertFalse(semantic_state(result)['state']=='MAP' and semantic_state(result)['confidence']>=.9)
if __name__=='__main__':unittest.main()
