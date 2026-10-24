import copy,sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
import text_reader,flow_vision
from bounded_ocr import BoundedOCRRuntime
from progress_evidence import ProgressRuntime

class MapTitleRereadTests(unittest.TestCase):
    def image(self):return Image.open(ROOT/'artifacts/p4c-earlier-gate-native-01/L0ktY5qUppI-1197.5/0036163.png').convert('RGB')
    def test_actual_truncated_title_is_recovered_from_original_pixels(self):
        with ProgressRuntime(),BoundedOCRRuntime(960) as runtime:
            rows=text_reader.read_text(self.image())
            self.assertEqual(flow_vision.semantic_state(rows)['state'],'MAP')
            raw=[r for r in rows if r.get('text')=='冥界']
            self.assertEqual(len(raw),1)
            fresh=[r for r in rows if r.get('source')=='map_title_original_crop']
            self.assertEqual(len(fresh),1);self.assertIn(fresh[0]['text'],['冥界試','冥界試煉'])
            self.assertGreaterEqual(fresh[0]['score'],.9)
            self.assertIn('cropBox',fresh[0]);self.assertIn('analysisSize',fresh[0])
            self.assertTrue(runtime.take_metadata()['recognitionCrops'])
    def test_missing_or_ambiguous_timer_cannot_authorize_title_reread(self):
        import json
        packet=json.loads((ROOT/'artifacts/p4c-earlier-gate-dev-analysis-01/dev-earlier-L0-zone5-floor1-col1/0036163.packet.json').read_text(encoding='utf-8'))
        rows=packet['evidence'];timer=next(r for r in rows if '剩餘時間' in r['text'])
        variants=[[r for r in rows if r is not timer],[*rows,copy.deepcopy(timer)]]
        with ProgressRuntime(),BoundedOCRRuntime(960) as runtime:
            for bad in variants:
                before=copy.deepcopy(bad)
                self.assertEqual(runtime._reread_map_title(self.image(),bad),before)
                self.assertFalse(runtime.take_metadata()['recognitionCrops'])

    def test_erased_title_cannot_be_guessed_from_timer_and_zone(self):
        image=self.image();ImageDraw.Draw(image).rectangle((14,12,126,51),fill=(45,40,65))
        with ProgressRuntime(),BoundedOCRRuntime(960):rows=text_reader.read_text(image)
        state=flow_vision.semantic_state(rows)
        self.assertFalse(state['state']=='MAP' and state['confidence']>=.9)
        self.assertFalse(any(r.get('source')=='map_title_original_crop' for r in rows))

if __name__=='__main__':unittest.main()
