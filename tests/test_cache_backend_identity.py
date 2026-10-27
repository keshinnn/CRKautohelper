"""Exercise actual analyzer subprocess cache admission, not a copied predicate."""
import copy,hashlib,json,pathlib,subprocess,sys,tempfile,unittest
ROOT=next(p for p in pathlib.Path(__file__).resolve().parents if (p/'ml/analyze_cases.py').is_file())
class CacheBackendIdentityTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='crk-backend-contract-',dir=ROOT/'artifacts');self.folder=pathlib.Path(self.temp.name)
  image=ROOT/'artifacts/p4a-native/0002550.png';self.source=self.folder/'source.json';self.source.write_text(json.dumps({'videoSha256':'a'*64,'cases':[{'id':'cache-backend','frames':[{'image':str(image),'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'frameIndex':2550,'size':[1440,1080]}]}]}),encoding='utf-8');self.counter=0
 def tearDown(self):self.temp.cleanup()
 def run_analyzer(self,cache=None,fast=True):
  self.counter+=1;out=self.folder/('out-'+str(self.counter));args=[sys.executable,'-B',str(ROOT/'ml/analyze_cases.py'),str(self.source),str(out)]
  if fast:args+=['--fast-map']
  if cache is not None:
   file=self.folder/('cache-'+str(self.counter)+'.json');file.write_text(json.dumps(cache),encoding='utf-8');args+=['--cache',str(file)]
  p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=120);self.assertEqual(p.returncode,0,p.stderr)
  m=json.loads((out/'manifest.json').read_text(encoding='utf-8'));packet=json.loads(pathlib.Path(m['cases'][0]['frames'][0]['packet']).read_text(encoding='utf-8'));return m,packet
 def test_backend_changed_or_unbound_forces_fresh_core_observation(self):
  baseline,_=self.run_analyzer()
  for key,value in [('mapBackendSha256','0'*64),('mapBackend','different-backend'),('mapBackendSha256',None),('mapBackend',None)]:
   with self.subTest(key=key,value=value):
    cache=copy.deepcopy(baseline)
    if value is None:cache['analysis'].pop(key)
    else:cache['analysis'][key]=value
    actual,packet=self.run_analyzer(cache)
    self.assertEqual(actual['analysis']['cacheIgnoredReason'],'MAP_BACKEND_CHANGED_OR_UNBOUND')
    self.assertTrue(packet['analysisTiming']['freshFullPipeline'])
 def test_matching_backend_retains_valid_raw_cache_reuse(self):
  for fast in [True,False]:
   with self.subTest(fast=fast):
    baseline,_=self.run_analyzer(fast=fast);actual,packet=self.run_analyzer(baseline,fast=fast)
    self.assertIsNone(actual['analysis']['cacheIgnoredReason']);self.assertFalse(packet['analysisTiming']['freshFullPipeline'])
 def test_backend_mode_transition_to_original_forces_fresh(self):
  for before,after in [(True,False),(False,True)]:
   with self.subTest(before=before,after=after):
    baseline,_=self.run_analyzer(fast=before);actual,packet=self.run_analyzer(baseline,fast=after)
    self.assertEqual(actual['analysis']['cacheIgnoredReason'],'MAP_BACKEND_CHANGED_OR_UNBOUND');self.assertTrue(packet['analysisTiming']['freshFullPipeline'])
if __name__=='__main__':unittest.main()
