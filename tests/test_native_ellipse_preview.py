import hashlib,io,json,sys,unittest
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from preview_identity import inspect_preview_identity
from bounded_ocr import BoundedOCRRuntime
class NativeEllipsePreviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.runtime=BoundedOCRRuntime(960);cls.runtime.__enter__()
 @classmethod
 def tearDownClass(cls):cls.runtime.__exit__(None,None,None)
 def source(self):
  d=json.loads((ROOT/'artifacts/p4c-development30-failure-source-01.json').read_text(encoding='utf-8'));return Image.open(d['frame']['image']).convert('RGB'),d['packet']
 def test_actual_native_preview_recovers_original_ellipse_extent_without_normalization(self):
  im,p=self.source();self.assertNotIn('aspectRectification',p['mapReview']);r=inspect_preview_identity(im,p);self.assertTrue(r['verified']);self.assertEqual([r['selectedNode'][k] for k in ['zone','floor','column']],[10,1,2]);n=next(n for n in r['recoveredNodes'] if n['id']==r['selectedNode']['nodeId']);self.assertIn('iconEllipseSizeEvidence',n);self.assertGreaterEqual(n['iconScore'],.9)
 def test_erased_actual_orange_pixels_cannot_recover_a_native_ellipse_preview(self):
  im,p=self.source();a=np.asarray(im).copy();a[481:569,596:687]=[40,40,40];im=Image.fromarray(a);digest=hashlib.sha256(im.tobytes()).hexdigest();raw=io.BytesIO();im.save(raw,format='PNG');p['binding'].update(pixelSha256=digest,imageSha256=hashlib.sha256(raw.getvalue()).hexdigest(),frameId=hashlib.sha256(raw.getvalue()).hexdigest()[:32]);p['mapReview']['frameId']=digest[:20];p['flow']['frameId']=digest[:20];self.assertFalse(inspect_preview_identity(im,p)['verified'])
if __name__=='__main__':unittest.main()
