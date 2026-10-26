import copy,json,sys,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from map_aspect import recover_map_aspect
class SmallAspectSparseTests(unittest.TestCase):
 def source(self,index=0):
  m=json.loads((ROOT/'artifacts/p4c-random-development-60-run-21/dev-L0-zone6-floor1-col2-select-1773-random-fixed/analysis/manifest.json').read_text(encoding='utf-8'));f=m['cases'][0]['frames'][index];return Image.open(f['image']).convert('RGB'),json.loads(Path(f['packet']).read_text(encoding='utf-8'))
 def test_actual_small_warp_recovers_only_a_source_verified_missing_lattice(self):
  im,p=self.source();self.assertFalse(p['mapReview']['absoluteFloorKnown']);r=recover_map_aspect(im,p);self.assertTrue(r['absoluteFloorKnown']);self.assertEqual(len(r['columns']),4);e=r['aspectRectification'];self.assertLessEqual(abs(e['calibration']['ratio']-1),.03);self.assertEqual(e['rectificationPurpose'],'unanchored_near_native_recovery');self.assertIn('smallAspectSparseRecovery',e);self.assertNotEqual(e['rectifiedInputSize'][0],im.width)
 def test_adjacent_raw_sparse_frames_keep_the_same_source_geometry_convention(self):
  results=[]
  for index in [0,1]:
   im,p=self.source(index);g=recover_map_aspect(im,p);self.assertIn('aspectRectification',g);self.assertIn('smallAspectSparseRecovery',g['aspectRectification']);self.assertEqual(g['aspectRectification']['rectificationPurpose'],'unanchored_near_native_recovery');results.append(g)
  def overlap(a,b):
   inter=max(0,min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0]))*max(0,min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1]));return inter/(a[2]*a[3]+b[2]*b[3]-inter)
  targets=[next(n['box'] for n in g['nodes'] if n.get('floor')==1 and n.get('column')==2) for g in results]
  gates=[next(n['box'] for n in g['nodes'] if n['type']=='exit') for g in results]
  self.assertGreaterEqual(overlap(*targets),.95);self.assertGreaterEqual(overlap(*gates),.95)
 def test_missing_duplicate_gate_or_insufficient_raw_lattice_cannot_enable_small_rectification(self):
  for mode in ['missing','duplicate','known-columns','few-nodes','two-columns','boundary-gate']:
   im,p=self.source();m=p['mapReview'];gate=next(n for n in m['nodes'] if n['type']=='exit')
   if mode=='missing':m['nodes'].remove(gate)
   if mode=='duplicate':m['nodes'].append(copy.deepcopy(gate))
   if mode=='known-columns':m['columns']=[1,2,3,4]
   if mode=='few-nodes':m['nodes']=[gate]+[n for n in m['nodes'] if n['type']!='exit'][:4]
   if mode=='boundary-gate':gate['box'][1]=0;gate['center'][1]=gate['box'][3]/2
   if mode=='two-columns':
    for n in m['nodes']:
     if n['type']!='exit':n['center'][0]=100;n['box'][0]=100-n['box'][2]/2
   r=recover_map_aspect(im,p);self.assertFalse(r['absoluteFloorKnown'],mode);self.assertNotIn('aspectRectification',r,mode)
if __name__=='__main__':unittest.main()
