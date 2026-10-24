import hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path

class OfflineAnalyzerTests(unittest.TestCase):
    def test_saved_png_binding_and_independent_identity_survive_batch_entry(self):
        root=Path(__file__).resolve().parents[1];image=root/'artifacts/p4a-native/0002550.png';before=image.read_bytes()
        with tempfile.TemporaryDirectory(prefix='crk-analyzer-',dir=root/'artifacts') as folder:
            manifest=Path(folder)/'source.json';manifest.write_text(json.dumps({'videoSha256':'a'*64,'cases':[{'id':'test','frames':[{'image':str(image),'sha256':hashlib.sha256(before).hexdigest(),'frameIndex':2550,'size':[1440,1080]}]}]}),encoding='utf-8')
            output=Path(folder)/'result'
            result=subprocess.run([sys.executable,'-B',str(root/'ml/analyze_cases.py'),str(manifest),str(output)],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stderr)
            generated=json.loads((output/'manifest.json').read_text(encoding='utf-8'));packet=json.loads(Path(generated['cases'][0]['frames'][0]['packet']).read_text(encoding='utf-8'))
            self.assertEqual(packet['binding']['imageSha256'],hashlib.sha256(before).hexdigest())
            self.assertTrue(packet['v2Preview']['verified'])
            self.assertFalse(packet['actionsExecuted'])
            self.assertEqual(image.read_bytes(),before)
    def test_incomplete_failure_cache_does_not_discard_unprocessed_frames(self):
        root=Path(__file__).resolve().parents[1];image=root/'artifacts/p4a-native/0002550.png'
        with tempfile.TemporaryDirectory(prefix='crk-partial-',dir=root/'artifacts') as folder:
            data={'videoSha256':'a'*64,'cases':[{'id':'test','frames':[{'image':str(image),'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'frameIndex':2550,'size':[1440,1080]}]}]}
            source=Path(folder)/'source.json';source.write_text(json.dumps(data),encoding='utf-8');output=Path(folder)/'result'
            r=subprocess.run([sys.executable,'-B',str(root/'ml/analyze_cases.py'),str(source),str(output),'--cache',str(source)],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(r.returncode,0,r.stderr)
            m=json.loads((output/'manifest.json').read_text(encoding='utf-8'));packet=json.loads(Path(m['cases'][0]['frames'][0]['packet']).read_text(encoding='utf-8'))
            self.assertTrue(packet['analysisTiming']['freshFullPipeline'])

if __name__=='__main__':unittest.main()
