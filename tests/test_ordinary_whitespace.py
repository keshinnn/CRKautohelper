import json,sys,unittest,re
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from bounded_ocr import BoundedOCRRuntime
from preview_identity import inspect_preview_identity
class OrdinaryWhitespaceTests(unittest.TestCase):
 def test_actual_equivalent_high_confidence_original_readings_do_not_conflict(self):
  b=ROOT/'artifacts/p4c-sparse-peer-case36-analysis-02';m=json.loads((b/'manifest.json').read_text(encoding='utf-8'));f=next(f for f in m['cases'][0]['frames'] if f['frameIndex']==53434);p=json.loads(Path(f['packet']).read_text(encoding='utf-8'));im=Image.open(f['image']).convert('RGB')
  with BoundedOCRRuntime(960) as runtime:
   result=inspect_preview_identity(im,p);metadata=runtime.take_metadata()
  readings=[v for crop in metadata['recognitionCrops'] for v in crop['variants'] if re.sub(r'\s+','',v['text'])=='普通' and v['score']>=.95]
  self.assertGreaterEqual(len({r['text'] for r in readings}),2);self.assertTrue(result['verified']);e=result['ordinaryEvidence'];self.assertEqual(e['refinedScore'],max(r['score'] for r in readings));self.assertEqual(e['refinedReading']['text'].strip(),'普通');self.assertEqual(e['refinedReading']['score'],e['refinedScore'])
if __name__=='__main__':unittest.main()
