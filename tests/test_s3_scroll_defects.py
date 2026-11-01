import hashlib,json,math,subprocess,sys,tempfile,unittest
from PIL import Image
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def iou(a,b):
 area=max(0,min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0]))*max(0,min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1]))
 return area/(a[2]*a[3]+b[2]*b[3]-area)
def checked_coverage(label,packet,video_sha):
 raw=(ROOT/label['image']).read_bytes();digest=hashlib.sha256(raw).hexdigest()
 if digest!=label['sha256']:raise ValueError('SOURCE_IMAGE_CHANGED')
 with Image.open(ROOT/label['image']) as image:
  if image.format!='PNG' or list(image.size)!=label['size']:raise ValueError('SOURCE_IMAGE_CHANGED')
  pixel=hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()
 binding=packet.get('binding',{});source=packet.get('sourceBinding',{})
 expected_id=hashlib.sha256((video_sha+str(label['frameIndex'])+digest).encode()).hexdigest()[:32]
 if (binding.get('imageSha256')!=digest or binding.get('pixelSha256')!=pixel or binding.get('frameId')!=expected_id
     or [binding.get('width'),binding.get('height')]!=label['size']
     or source.get('videoSha256')!=video_sha or source.get('frameIndex')!=label['frameIndex'] or source.get('imageSha256')!=digest):raise ValueError('PACKET_SOURCE_MISMATCH')
 box=label.get('expectedBox');review=packet.get('mapReview')
 if (not label.get('reviewed') or not isinstance(box,list) or len(box)!=4 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in box)
     or min(box[:2])<0 or min(box[2:])<=0 or box[0]+box[2]>label['size'][0] or box[1]+box[3]>label['size'][1]
     or not .90<=label.get('minimumIoU',0)<=1 or not isinstance(review,dict) or review.get('frameId')!=pixel[:20]
     or not isinstance(review.get('nodes'),list) or not review['nodes']):raise ValueError('PACKET_SCHEMA_INVALID')
 for node in review['nodes']:
  b=node.get('box')
  if not isinstance(node.get('type'),str) or not isinstance(b,list) or len(b)!=4 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in b) or min(b[2:])<=0:raise ValueError('PACKET_SCHEMA_INVALID')
 return any(n['type']==label['expectedType'] and iou(n['box'],box)>=label['minimumIoU'] for n in review['nodes'])

class S3ScrollCoverageDefects(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads((ROOT/'data/p4c/s3-scroll-known-defects-v1.json').read_text(encoding='utf-8'));cls.labels=cls.data['cases']
  cls.temp=tempfile.TemporaryDirectory(dir=ROOT/'artifacts');cls.addClassCleanup(cls.temp.cleanup)
  m=json.loads((ROOT/'artifacts/performance-20261027/profile-source.json').read_text(encoding='utf-8'));c=next(c for c in m['cases'] if c['id']=='dev-earlier-0Q-zone4-floor1-col4')
  source=Path(cls.temp.name)/'source.json';out=Path(cls.temp.name)/'analysis';source.write_text(json.dumps({**m,'cases':[c]}),encoding='utf-8')
  r=subprocess.run([sys.executable,'-B','ml/analyze_cases.py',str(source),str(out),'--fast-map','--map-coverage','--bounded-ocr','960'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=120)
  if r.returncode:raise RuntimeError(r.stderr)
  result=json.loads((out/'manifest.json').read_text(encoding='utf-8'));cls.packets={f['frameIndex']:json.loads(Path(f['packet']).read_text(encoding='utf-8')) for f in result['cases'][0]['frames']}
  cls.covered={label['frameIndex']:checked_coverage(label,cls.packets[label['frameIndex']],cls.data['parentVideoSha256']) for label in cls.labels}
 def test_battle_46047_detects_reviewed_physical_icon(self):self.assertTrue(self.covered[46047],'Known OPEN battle omission46047')
 def test_heal_46057_detects_reviewed_physical_icon(self):self.assertTrue(self.covered[46057],'Known OPEN heal omission46057')
 def test_unanchored_scroll_frames_do_not_claim_absolute_floor(self):
  for p in self.packets.values():self.assertIs(p['mapReview']['absoluteFloorKnown'],False)
class GroundTruthFixtureContractTests(unittest.TestCase):
 def setUp(self):
  self.data=json.loads((ROOT/'data/p4c/s3-scroll-known-defects-v1.json').read_text(encoding='utf-8'));self.label=self.data['cases'][0]
  self.packet=json.loads((ROOT/'artifacts/performance-20261027/profile-after-01/analysis/dev-earlier-0Q-zone4-floor1-col4/0046047.packet.json').read_text(encoding='utf-8'))
  self.packet['mapReview']['nodes']=[{'type':self.label['expectedType'],'box':self.label['expectedBox']}]
 def test_wrong_source_sha_is_an_ordinary_fixture_error(self):
  with self.assertRaisesRegex(ValueError,'SOURCE_IMAGE_CHANGED'):checked_coverage({**self.label,'sha256':'f'*64},self.packet,self.data['parentVideoSha256'])
 def test_wrong_packet_identity_is_an_ordinary_fixture_error(self):
  self.packet['binding']['imageSha256']='f'*64
  with self.assertRaisesRegex(ValueError,'PACKET_SOURCE_MISMATCH'):checked_coverage(self.label,self.packet,self.data['parentVideoSha256'])
 def test_broken_node_schema_is_not_a_known_omission(self):
  self.packet['mapReview']['nodes']=[{'type':'battle','box':None}]
  with self.assertRaisesRegex(ValueError,'PACKET_SCHEMA_INVALID'):checked_coverage(self.label,self.packet,self.data['parentVideoSha256'])
if __name__=='__main__':unittest.main()
