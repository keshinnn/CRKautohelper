"""Incomplete OCR locates a crop; only fresh complete pixels grant context."""
import copy,json,sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from bounded_ocr import BoundedOCRRuntime
from progress_evidence import ProgressRuntime
from english_scene import EnglishSceneRuntime,semantic_state

class RemainingTimeLocatorTests(unittest.TestCase):
    def fixture(self):
        base=ROOT/'artifacts/p4c-random-development-60-run-07/zone-9-first-battle-random-pre-change/analysis'
        m=json.loads((base/'manifest.json').read_text(encoding='utf-8'))
        f=next(f for f in m['cases'][0]['frames'] if f['frameIndex']==78306)
        return Image.open(f['image']).convert('RGB'),json.loads(Path(f['packet']).read_text(encoding='utf-8'))['evidence']

    def test_actual_missing_global_glyph_is_read_from_original_crop(self):
        image,rows=self.fixture()
        with ProgressRuntime(),BoundedOCRRuntime(960) as runtime,EnglishSceneRuntime():
            result=runtime._reread_map_context(image,rows);state=semantic_state(result)
        self.assertEqual(state['state'],'MAP');self.assertGreaterEqual(state['confidence'],.9)
        timer=next(r for r in result if r.get('contextKind')=='timer')
        self.assertIn('剩時間',timer['originalText']);self.assertIn('剩餘時間',timer['text'])
        self.assertGreaterEqual(timer['score'],.9);self.assertIn('cropBox',timer)

    def test_erased_timer_cannot_be_filled_from_original_ocr_locator(self):
        image,rows=self.fixture();ImageDraw.Draw(image).rectangle((50,110,325,163),fill=(30,30,60))
        with ProgressRuntime(),BoundedOCRRuntime(960) as runtime,EnglishSceneRuntime():
            result=runtime._reread_map_context(image,rows);state=semantic_state(result)
        self.assertFalse(state['state']=='MAP' and state['confidence']>=.9)
        self.assertFalse(any(r.get('contextKind')=='timer' for r in result))

    def test_missing_or_duplicate_partial_locator_cannot_start_reread(self):
        image,rows=self.fixture();timer=next(r for r in rows if '剩時間' in r.get('text',''))
        with ProgressRuntime(),BoundedOCRRuntime(960) as runtime,EnglishSceneRuntime():
            for bad in [[r for r in rows if r is not timer],[*rows,copy.deepcopy(timer)]]:
                self.assertEqual(runtime._reread_map_context(image,bad),bad)
                self.assertFalse(runtime.take_metadata()['recognitionCrops'])

if __name__=='__main__':unittest.main()
