"""R1 boundary regression with real current-template verification, synthetic pixels.
Not a frozen-corpus case or game-acceptance result. Geometry is isolated so only
same-source legacy-current enrichment is exercised.
"""
import copy,hashlib,io,sys,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'ml/map_pipeline.py').is_file())
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
import map_vision
from map_current import inspect_current_node
from frame_intermediates import FrameIntermediates
from map_pipeline import observe_geometry
V1=Path('F:/CRK helper')

class LegacyCurrentPhaseTests(unittest.TestCase):
 def fixture(self,erase=False):
  with Image.open(V1/'data/map/node-live-current.png') as f:ref=f.convert('RGB')
  image=Image.new('RGB',(960,720),(20,30,40));x,y=400,300;w,h=ref.size
  image.paste(ref,(x,y));progress={'score':.99,'lastEnteredFloor':1,'displayedZone':6,'conflictingEvidence':False,'displayedAreaComplete':False}
  evidence=[{'text':'進行中','score':.92,'box':[[x+3,y+h+2],[x+w-3,y+h+2],[x+w-3,y+h+12],[x+3,y+h+12]]}]
  node={'id':'baseline-current','type':'battle','score':.99,'floor':1,'column':2,'box':[x,y,w,h],'center':[x+w/2,y+h/2],'completed':False}
  base={'absoluteFloorKnown':True,'floorAnchorSource':'visible_top_gate','columns':[200,400,600,800],'nodes':[node],'edges':[],'header':progress}
  measured=inspect_current_node(image,evidence,base,V1/'data/map',progress);self.assertTrue(measured['verified'])
  base['currentPosition']=measured
  if erase:image.paste((20,30,40),(x,y,x+w,y+h))
  raw=io.BytesIO();image.save(raw,format='PNG');pngsha=hashlib.sha256(raw.getvalue()).hexdigest();pixel=hashlib.sha256(image.tobytes()).hexdigest();base['frameId']=pixel[:20]
  binding={'frameId':'a'*32,'imageSha256':pngsha,'pixelSha256':pixel,'width':960,'height':720}
  packet={'binding':binding,'mapReview':base,'progress':progress,'evidence':evidence,'v2MapActions':{'current':None}}
  expanded=copy.deepcopy(base);expanded.pop('currentPosition');expanded['nodes'][0]['id']='expanded-current'
  return image,packet,expanded
 def run_phase(self,erase=False,enabled=True):
  image,packet,expanded=self.fixture(erase)
  with patch.object(map_vision,'inspect_map',return_value=copy.deepcopy(expanded)),patch('map_pipeline.recover_map_geometry',side_effect=lambda image,p:p['mapReview']),patch('map_pipeline.recover_map_aspect',side_effect=lambda image,p:p['mapReview']):
   with FrameIntermediates(packet['binding']['frameId'],packet['binding']['imageSha256'],list(image.size),enabled=enabled) as context:
    observe_geometry(image,packet,V1,context=context,coverage=True)
  return packet
 def test_valid_legacy_current_is_remeasured_for_new_geometry_not_copied(self):
  packets=[]
  for enabled in [True,False]:
   with self.subTest(reuse=enabled):
    packet=self.run_phase(enabled=enabled);current=packet['mapReview'].get('currentPosition',{})
    self.assertTrue(current.get('verified'),'Coverage dropped the verified current-position path')
    self.assertEqual(current['nodeId'],'expanded-current')
    self.assertEqual(packet['v2OriginalMapReview']['currentPosition']['nodeId'],'baseline-current')
    self.assertIsNone(packet['v2MapActions']['current']);self.assertLess(current['labelScore'],.95)
    packets.append(packet)
  if len(packets)==2:self.assertEqual(packets[0],packets[1])
 def test_old_verified_metadata_cannot_survive_failed_current_pixels(self):
  packet=self.run_phase(erase=True)
  self.assertTrue(packet['v2OriginalMapReview']['currentPosition']['verified'])
  self.assertIn('currentPosition',packet['mapReview'])
  self.assertFalse(packet['mapReview']['currentPosition']['verified'])
if __name__=='__main__':unittest.main()
