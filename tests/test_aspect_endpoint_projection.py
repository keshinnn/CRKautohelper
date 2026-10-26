import json,sys,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from map_aspect import estimate_pixel_aspect
class AspectEndpointProjectionTests(unittest.TestCase):
 def test_actual_boundary_components_project_their_interval_endpoints_without_overshoot(self):
  m=json.loads((ROOT/'artifacts/p4c-random-development-60-run-19/dev-primary-zone6-floor1-col2-random-fixed/analysis/manifest.json').read_text(encoding='utf-8'));f=m['cases'][0]['frames'][5];image=Image.open(f['image']).convert('RGB');c=estimate_pixel_aspect(image);self.assertIsNotNone(c)
  boundary=0
  for q in c['candidates']:
   x,y,w,h=q['analysisBox'];left,top,bw,bh=q['box'];self.assertGreaterEqual(left,0);self.assertGreaterEqual(top,0);self.assertLessEqual(left+bw,image.width);self.assertLessEqual(top+bh,image.height)
   self.assertAlmostEqual(left,x*image.width/960,places=10);self.assertAlmostEqual(top,y*image.height/c['analysisSize'][1],places=10)
   if y+h==c['analysisSize'][1]:boundary+=1;self.assertEqual(top+bh,image.height)
  self.assertGreaterEqual(boundary,2)
if __name__=='__main__':unittest.main()
