import hashlib,json,sys,unittest
from pathlib import Path
import cv2,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
import map_vision
from fast_map_candidates import node_candidates
from map_aspect import recover_map_aspect
class SparsePeerBootstrapTests(unittest.TestCase):
 def source(self):
  b=ROOT/'artifacts/p4c-random-development-60-run-24/dev-L0-zone6-floor1-col2-resume-1781-random-post-change';m=json.loads((b/'analysis/manifest.json').read_text(encoding='utf-8'));f=m['cases'][0]['frames'][4];return Image.open(f['image']).convert('RGB'),json.loads(Path(f['packet']).read_text(encoding='utf-8'))
 def test_actual_three_measured_peers_bootstrap_a_fourth_original_icon_before_lattice(self):
  im,p=self.source();old=map_vision.node_candidates;map_vision.node_candidates=node_candidates
  try:r=recover_map_aspect(im,p)
  finally:map_vision.node_candidates=old
  self.assertTrue(r['absoluteFloorKnown']);self.assertEqual(len(r['columns']),4);e=r['aspectRectification']['sparsePeerBootstrap'];self.assertEqual(len(e['peers']),3);self.assertEqual(e['pixelSha256'],p['binding']['pixelSha256']);self.assertGreaterEqual(e['geometryEvidence']['innerScore'],.9);self.assertGreaterEqual(len(r['nodes']),6)
 def test_erased_source_orange_icons_cannot_bootstrap_from_old_detector_fields(self):
  im,p=self.source();a=np.array(im);hsv=cv2.cvtColor(a,cv2.COLOR_RGB2HSV);a[(hsv[:,:,0]>=5)&(hsv[:,:,0]<=35)&(hsv[:,:,1]>100)&(hsv[:,:,2]>100)]=[30,30,60];im=Image.fromarray(a);p['binding']['pixelSha256']=hashlib.sha256(a.tobytes()).hexdigest();p['mapReview']['frameId']=p['binding']['pixelSha256'][:20]
  old=map_vision.node_candidates;map_vision.node_candidates=node_candidates
  try:r=recover_map_aspect(im,p)
  finally:map_vision.node_candidates=old
  self.assertFalse(r['absoluteFloorKnown']);self.assertNotIn('aspectRectification',r)
if __name__=='__main__':unittest.main()
