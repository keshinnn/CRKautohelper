import hashlib,json,sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from sparse_map_geometry import recover_map_geometry
from map_action_evidence import inspect_map_actions
class WatermarkedCheckTests(unittest.TestCase):
    def source(self):
        p=json.loads((ROOT/'artifacts/p4c-LX46-dev-additional-analysis-01/dev-LX46-zone4-floor2-col1-select/0030102.packet.json').read_text(encoding='utf-8'))
        im=Image.open(ROOT/'artifacts/p4c-LX46-native-qualification-01/candidate-13-502.0/0030102.png').convert('RGB');p['mapReview']=recover_map_geometry(im,p)
        return im,p
    def test_real_neutral_watermark_preserves_completed_check_shape_and_unique_path(self):
        image,p=self.source();a=inspect_map_actions(image,p)
        self.assertTrue(a['nodes']['visible-1-2']['completed'])
        self.assertGreaterEqual(a['nodes']['visible-1-2']['checkMaskIoU'],.8)
        self.assertEqual(a['current']['completedPath'],['exit-0','visible-1-2'])
    def test_gray_or_filled_green_or_missing_check_pixels_do_not_inherit_completion(self):
        for mode in ['gray','filled-green','missing']:
            image,p=self.source()
            if mode=='gray':image=ImageOps.grayscale(image).convert('RGB')
            else:ImageDraw.Draw(image).rectangle((850,520,950,620),fill=(45,180,45) if mode=='filled-green' else (40,40,40))
            digest=hashlib.sha256(image.tobytes()).hexdigest();p['binding']['pixelSha256']=digest;p['mapReview']['frameId']=digest[:20]
            a=inspect_map_actions(image,p)
            self.assertFalse(a['nodes']['visible-1-2']['completed']);self.assertIsNone(a['current'])
if __name__=='__main__':unittest.main()
