import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def iou(a,b):
 area=max(0,min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0]))*max(0,min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1]))
 return area/(a[2]*a[3]+b[2]*b[3]-area)
class S3ScrollCoverageDefects(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.labels=json.loads((ROOT/'data/p4c/s3-scroll-known-defects-v1.json').read_text(encoding='utf-8'))['cases']
  cls.temp=tempfile.TemporaryDirectory(dir=ROOT/'artifacts');cls.addClassCleanup(cls.temp.cleanup)
  m=json.loads((ROOT/'artifacts/performance-20261027/profile-source.json').read_text(encoding='utf-8'));c=next(c for c in m['cases'] if c['id']=='dev-earlier-0Q-zone4-floor1-col4')
  source=Path(cls.temp.name)/'source.json';out=Path(cls.temp.name)/'analysis';source.write_text(json.dumps({**m,'cases':[c]}),encoding='utf-8')
  r=subprocess.run([sys.executable,'-B','ml/analyze_cases.py',str(source),str(out),'--fast-map','--bounded-ocr','960'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=120)
  if r.returncode:raise RuntimeError(r.stderr)
  result=json.loads((out/'manifest.json').read_text(encoding='utf-8'));cls.packets={f['frameIndex']:json.loads(Path(f['packet']).read_text(encoding='utf-8')) for f in result['cases'][0]['frames']}
 def coverage(self,index):
  label=next(c for c in self.labels if c['frameIndex']==index);self.assertEqual(hashlib.sha256((ROOT/label['image']).read_bytes()).hexdigest(),label['sha256'])
  matches=[n for n in self.packets[index]['mapReview']['nodes'] if n['type']==label['expectedType'] and iou(n['box'],label['expectedBox'])>=label['minimumIoU']]
  self.assertTrue(matches,f"Known OPEN source-bound omission {index}, {label['expectedType']}, source box {label['expectedBox']}")
 @unittest.expectedFailure
 def test_battle_46047_detects_reviewed_physical_icon(self):self.coverage(46047)
 @unittest.expectedFailure
 def test_heal_46057_detects_reviewed_physical_icon(self):self.coverage(46057)
 def test_unanchored_scroll_frames_do_not_claim_absolute_floor(self):
  for p in self.packets.values():self.assertIs(p['mapReview']['absoluteFloorKnown'],False)
if __name__=='__main__':unittest.main()
