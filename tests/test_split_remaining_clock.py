import copy,json,sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from bounded_ocr import BoundedOCRRuntime
from progress_evidence import ProgressRuntime
from english_scene import EnglishSceneRuntime,semantic_state
class SplitRemainingClockTests(unittest.TestCase):
 def fixture(self):
  base=ROOT/'artifacts/p4c-random-development-60-run-22/dev-L0-zone6-floor1-col2-select-1773-random-post-change'
  m=json.loads((base/'source.json').read_text(encoding='utf-8'));f=next(f for f in m['cases'][0]['frames'] if f['frameIndex']==53172)
  p=json.loads((base/'analysis'/m['cases'][0]['id']/'0053172.packet.json').read_text(encoding='utf-8'))
  return Image.open(f['image']).convert('RGB'),p['evidence']
 def test_actual_split_weak_label_and_clock_require_fresh_full_pixel_reading(self):
  im,rows=self.fixture()
  with ProgressRuntime(),BoundedOCRRuntime(960) as runtime,EnglishSceneRuntime():
   result=runtime._reread_map_context(im,rows);state=semantic_state(result)
  self.assertEqual(state['state'],'MAP');self.assertGreaterEqual(state['confidence'],.9)
  timer=next(r for r in result if r.get('contextKind')=='timer');self.assertGreaterEqual(timer['score'],.9)
  self.assertLess(timer['originalScore'],.85);self.assertIn('remainingLabelLocator',timer);self.assertIn('adjacentClockLocator',timer)
  self.assertIn('12',timer['text']);self.assertIn('13:09:27',timer['text'])
 def test_missing_duplicate_or_misaligned_clock_cannot_supply_context(self):
  im,rows=self.fixture();clock=next(r for r in rows if r['text']=='12天13:09:27');label=next(r for r in rows if '剩餘時間' in r['text'])
  badclock=copy.deepcopy(clock);badclock['box']=[[x,y+80] for x,y in badclock['box']]
  badsets=[[r for r in rows if r is not clock],[*rows,copy.deepcopy(clock)],[r for r in rows if r is not label],[badclock if r is clock else r for r in rows]]
  with ProgressRuntime(),BoundedOCRRuntime(960) as runtime,EnglishSceneRuntime():
   for bad in badsets:
    result=runtime._reread_map_context(im,bad);self.assertFalse(any(r.get('contextKind')=='timer' for r in result));self.assertNotEqual(semantic_state(result)['state'],'MAP')
 def test_erased_label_or_clock_pixels_cannot_be_filled_from_old_tokens(self):
  for box in [(43,59,137,87),(137,59,278,87)]:
   im,rows=self.fixture();ImageDraw.Draw(im).rectangle(box,fill=(30,30,60))
   with ProgressRuntime(),BoundedOCRRuntime(960) as runtime,EnglishSceneRuntime():
    result=runtime._reread_map_context(im,rows);self.assertFalse(any(r.get('contextKind')=='timer' for r in result));self.assertNotEqual(semantic_state(result)['state'],'MAP')
if __name__=='__main__':unittest.main()
