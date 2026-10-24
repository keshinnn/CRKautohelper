import hashlib,os,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
try:
    from freeze_video_cases import extract_case
except ImportError:
    def extract_case(*args):return []

class OriginalVideoSourceTests(unittest.TestCase):
    def test_original_pixels_and_every_post_barrier_frame_are_preserved(self):
        video=Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper'))/'data/video-validation/buAwy1zf2LI/buAwy1zf2LI.mp4'
        with tempfile.TemporaryDirectory(prefix='crk-source-',dir=Path(__file__).resolve().parents[1]/'artifacts') as directory:
            frames=extract_case(video,{'preFrames':[2514,2520],'lastFrame':2522},Path(directory)/'case')
            self.assertEqual([f['frameIndex'] for f in frames],[2514,2520,2521,2522])
            for f in frames:
                with Image.open(f['image']) as im:self.assertEqual(im.size,(1440,1080))
                self.assertEqual(f['sha256'],hashlib.sha256(Path(f['image']).read_bytes()).hexdigest())
                self.assertAlmostEqual(f['sourcePtsMs'],f['frameIndex']/30*1000,places=4)

if __name__=='__main__':unittest.main()
