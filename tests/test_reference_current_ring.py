import copy,hashlib,json,sys,unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from map_action_evidence import inspect_map_actions
class ReferenceCurrentRingTests(unittest.TestCase):
 def source(self):
  b=ROOT/'artifacts/p4c-random-development-60-run-23/dev-L0-zone6-floor1-col2-resume-1781-random-fixed';m=json.loads((b/'analysis/manifest.json').read_text(encoding='utf-8'));f=m['cases'][0]['frames'][0];return Image.open(f['image']).convert('RGB'),json.loads(Path(f['packet']).read_text(encoding='utf-8'))
 def test_actual_thin_ring_keeps_original_threshold_at_template_reference_size(self):
  im,p=self.source();c=inspect_map_actions(im,p)['current'];self.assertIsNotNone(c);self.assertTrue(c['verified']);self.assertEqual(c['nodeId'],'visible-1-2');self.assertGreaterEqual(c['ringCoverage'],.08);self.assertTrue(all(x>=.04 for x in c['quadrants']))
  e=c['referenceRing'];self.assertLess(e['originalCoverage'],.08);self.assertEqual(e['referenceNodeBox'][2:],[58,58]);self.assertEqual(e['pixelSha256'],p['binding']['pixelSha256']);self.assertEqual(e['sourceNodeBox'],c['box'])
 def test_erased_source_ring_or_triangle_cannot_use_resampling_to_gain_authority(self):
  for part in ['ring','triangle']:
   im,p=self.source();a=np.array(im);n=next(n for n in p['mapReview']['nodes'] if n.get('floor')==1 and n.get('column')==2);x,y,w,h=n['box'];yy,xx=np.mgrid[:im.height,:im.width];radius=np.maximum(abs((xx-x-w/2)/(w/2)),abs((yy-y-h/2)/(h/2)))
   mask=(radius>.76)&(radius<1.2) if part=='ring' else (xx>x)&(xx<x+w)&(yy>y-h*.4)&(yy<y)
   a[mask]=0;im=Image.fromarray(a);p['binding']['pixelSha256']=hashlib.sha256(a.tobytes()).hexdigest();p['mapReview']['frameId']=p['binding']['pixelSha256'][:20];self.assertIsNone(inspect_map_actions(im,p)['current'])
if __name__=='__main__':unittest.main()
