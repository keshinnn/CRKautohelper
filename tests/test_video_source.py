import hashlib,os,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
try:
    from freeze_video_cases import extract_case
except ImportError:
    def extract_case(*args):return []

class OriginalVideoSourceTests(unittest.TestCase):
    def test_additional_native_sources_keep_their_own_fps_dimensions_and_frames(self):
        root=Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper'))/'data/map-video'
        for name,fps,size in [('L0ktY5qUppI',30,[960,720]),('0QxozULx_SQ',60,[1280,720])]:
            with tempfile.TemporaryDirectory(prefix='crk-native-',dir=Path(__file__).resolve().parents[1]/'artifacts') as directory:
                start=fps*100;barrier=start+round(fps*.2)
                frames=extract_case(root/(name+'.mp4'),{'preFrames':[start,barrier],'lastFrame':barrier+2},Path(directory)/'case',source_spec={'fps':fps,'size':size})
                self.assertEqual([f['frameIndex'] for f in frames],[start,barrier,barrier+1,barrier+2])
                for f in frames:
                    self.assertEqual(f['size'],size)
                    with Image.open(f['image']) as im:self.assertEqual(list(im.size),size)
                    self.assertAlmostEqual(f['sourcePtsMs'],f['frameIndex']/fps*1000,places=4)

    def test_sixty_fps_stability_requires_twelve_frames_not_six(self):
        video=Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper'))/'data/map-video/0QxozULx_SQ.mp4'
        with tempfile.TemporaryDirectory(prefix='crk-short-',dir=Path(__file__).resolve().parents[1]/'artifacts') as directory:
            with self.assertRaisesRegex(ValueError,'invalid source interval'):
                extract_case(video,{'preFrames':[6000,6006],'lastFrame':6008},Path(directory)/'case',source_spec={'fps':60,'size':[1280,720]})

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
