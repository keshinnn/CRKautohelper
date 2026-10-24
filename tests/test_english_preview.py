import copy,hashlib,json,sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from preview_identity import inspect_preview_identity
from bounded_ocr import BoundedOCRRuntime
class EnglishPreviewTests(unittest.TestCase):
    def source(self):
        p=json.loads((ROOT/'artifacts/p4c-LX46-dev-analysis-02/dev-LX46-zone1-floor1-col1-resume/0002286.packet.json').read_text(encoding='utf-8'))
        image=Image.open(ROOT/'artifacts/p4c-LX46-native-qualification-01/candidate-00-38.0/0002286.png').convert('RGB')
        return image,p
    def test_real_english_preview_requires_independent_normal_pixels(self):
        image,p=self.source();before=copy.deepcopy(p)
        with BoundedOCRRuntime(960):result=inspect_preview_identity(image,p)
        self.assertTrue(result['verified']);self.assertEqual(result['selectedNode']['zone'],1)
        self.assertEqual(result['selectedNode']['floor'],1);self.assertEqual(result['selectedNode']['column'],1)
        self.assertEqual(p,before)
    def test_erased_normal_pixels_with_fresh_binding_cannot_be_inferred_from_context(self):
        image,p=self.source();ImageDraw.Draw(image).rectangle((1640,315,1890,390),fill=(55,59,92))
        digest=hashlib.sha256(image.tobytes()).hexdigest();p['binding']['pixelSha256']=digest;p['mapReview']['frameId']=digest[:20]
        with BoundedOCRRuntime(960):self.assertFalse(inspect_preview_identity(image,p)['verified'])

    def test_missing_difficulty_or_watermark_text_cannot_substitute_ordinary_label(self):
        image,p=self.source();p['evidence']=[r for r in p['evidence'] if r['text']!='Difficulty']
        p['evidence'].append({'text':'@chateaw Normal','score':.999,'box':[[1730,330],[1900,330],[1900,370],[1730,370]]})
        with BoundedOCRRuntime(960):self.assertFalse(inspect_preview_identity(image,p)['verified'])
if __name__=='__main__':unittest.main()
