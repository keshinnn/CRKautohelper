"""Real source-bound local coverage without changing the legacy M1 policy."""
import hashlib,json,math,sys,unittest
from pathlib import Path
from unittest.mock import patch
import cv2
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
import fast_map_candidates as fm
from map_vision import classify_node,map_templates
FOLDER=Path('F:/CRK helper/data/map')
def iou(a,b):
 area=max(0,min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0]))*max(0,min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1]))
 return area/(a[2]*a[3]+b[2]*b[3]-area)
class BoundedCoverageTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  m=json.loads((ROOT/'artifacts/m1-20261027-01/case42-fresh-01/manifest.json').read_text(encoding='utf-8'));cls.case=m['cases'][0];cls.fixtures=[]
  for f in cls.case['frames'][:2]:
   if hashlib.sha256(Path(f['image']).read_bytes()).hexdigest()!=f['sha256']:raise ValueError('SOURCE_CHANGED')
   with Image.open(f['image']) as source:im=source.convert('RGB')
   cls.fixtures.append((im.resize((960,round(im.height*960/im.width)),Image.Resampling.LANCZOS),f))
 def test_source_bound_local_omissions_recovered_with_original_prefix(self):
  for im,f in self.fixtures:
   with self.subTest(frame=f['frameIndex']):
    base=fm.node_candidates(im,FOLDER);self.assertEqual(len(base),11)
    got=fm.coverage_node_candidates(im,FOLDER);self.assertEqual(got[:len(base)],base)
    projected=[[n['box'][0]*f['size'][0]/im.width,n['box'][1]*f['size'][1]/im.height,n['box'][2]*f['size'][0]/im.width,n['box'][3]*f['size'][1]/im.height] for n in got]
    best=max(range(len(got)),key=lambda i:iou(projected[i],self.case['expectedBox']))
    self.assertGreaterEqual(iou(projected[best],self.case['expectedBox']),.90)
    self.assertEqual(classify_node(im,got[best],FOLDER)['type'],'battle')
    self.assertTrue(all(.48<=n['score']<=1 for n in got))
 def test_single_canny_unique_bounded_incremental_kernels(self):
  im,_=self.fixtures[0];seen=[];original=fm._match_group
  def collect(edges,g):
   seen.extend((name,tuple(t.shape[::-1])) for _,name,t,_ in g[1]);return original(edges,g)
  with patch.object(fm,'_match_group',side_effect=collect),patch.object(cv2,'Canny',wraps=cv2.Canny) as canny:
   fm.coverage_node_candidates(im,FOLDER)
  base=[(n,tuple(t.shape[::-1])) for _,ks in fm._groups(str(FOLDER.resolve()),im.height,im.width) for _,n,t,_ in ks]
  self.assertEqual(len(base),204);self.assertEqual(canny.call_count,1)
  self.assertEqual(len(seen),len(set(seen)));self.assertTrue(set(base).issubset(seen));self.assertGreater(len(seen),204)
  self.assertLessEqual(len(seen),204+16*len(map_templates(FOLDER)))
  meta=json.loads((FOLDER/'template-metadata.json').read_text(encoding='utf-8'));templates={n+'.png':t for n,t,_,_,_ in map_templates(FOLDER)}
  for n,(w,h) in set(seen)-set(base):
   t=templates[n];ref=meta.get(n,{}).get('frame_height',720 if n.startswith('node-b-') else 540);scale=round(im.height/ref,4)
   self.assertTrue(math.floor(t.shape[1]*scale)-1<=w<=math.ceil(t.shape[1]*scale)+1)
   self.assertTrue(math.floor(t.shape[0]*scale)-1<=h<=math.ceil(t.shape[0]*scale)+1)
 def test_blank_pixels_do_not_gain_coverage_candidates(self):
  self.assertEqual(fm.coverage_node_candidates(Image.new('RGB',(960,712)),FOLDER),[])
if __name__=='__main__':unittest.main()
