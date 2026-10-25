import hashlib,json,sys,tempfile,unittest
from pathlib import Path
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'ml'))
try:
    from freeze_replay_prefixes import freeze_prefixes
except ImportError:
    def freeze_prefixes(*a,**k):return None

class PrefixFreezerTests(unittest.TestCase):
    def fixture(self,folder):
        video=Path(folder)/'synthetic-protocol-only.avi'
        writer=cv2.VideoWriter(str(video),cv2.VideoWriter_fourcc(*'MJPG'),30,(80,60))
        self.assertTrue(writer.isOpened())
        try:
            for i in range(12):writer.write(np.full((60,80,3),i*15,dtype=np.uint8))
        finally:writer.release()
        return {'id':'synthetic-prefix-fixture','reviewed':True,'video':str(video),'videoSha256':hashlib.sha256(video.read_bytes()).hexdigest(),'sourceFps':30,'sourceSize':[80,60],'preFrames':[3,9]}
    def test_exact_preceding_native_frame_is_frozen_but_never_auto_reviewed(self):
        with tempfile.TemporaryDirectory(prefix='crk-prefix-',dir=ROOT/'artifacts') as folder:
            c=self.fixture(folder);out=Path(folder)/'prefix';result=freeze_prefixes([c],out,'c'*64)
            self.assertIsNotNone(result);self.assertTrue(result['prefixBytesVerified']);self.assertFalse(result['g4Complete'])
            p=result['cases'][0];self.assertEqual(p['frameIndex'],2);self.assertEqual(p['sourcePtsMs'],66.666667)
            self.assertEqual(p['videoSha256'],c['videoSha256']);self.assertEqual(p['size'],[80,60]);self.assertFalse(p['reviewed'])
            self.assertEqual(p['sha256'],hashlib.sha256(Path(p['image']).read_bytes()).hexdigest())
            self.assertEqual(result['nativeActions'],0);self.assertFalse(result['modelInferenceRun'])
            before=(out/'manifest.json').read_bytes()
            with self.assertRaises(FileExistsError):freeze_prefixes([c],out,'c'*64)
            self.assertEqual(before,(out/'manifest.json').read_bytes())
    def test_changed_video_or_native_spec_cannot_claim_verified_prefix(self):
        with tempfile.TemporaryDirectory(prefix='crk-prefix-invalid-',dir=ROOT/'artifacts') as folder:
            c=self.fixture(folder)
            for kind in ['hash','fps','size','review','annotation','unsafe-id']:
                with self.subTest(kind=kind):
                    bad=dict(c);sha='c'*64
                    if kind=='hash':bad['videoSha256']='d'*64
                    elif kind=='fps':bad['sourceFps']=60
                    elif kind=='size':bad['sourceSize']=[81,60]
                    elif kind=='review':bad['reviewed']=False
                    elif kind=='annotation':sha='unknown'
                    elif kind=='unsafe-id':bad['id']='../escape'
                    with self.assertRaises(ValueError):freeze_prefixes([bad],Path(folder)/kind,sha)

if __name__=='__main__':unittest.main()
