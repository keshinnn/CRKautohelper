import sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
import flow_vision,text_reader
from bounded_ocr import BoundedOCRRuntime
from progress_evidence import ProgressRuntime
from english_scene import EnglishSceneRuntime

class WatermarkedMapContextTests(unittest.TestCase):
    def image(self):return Image.open(ROOT/'artifacts/p4c-earlier-gate-native-01/0QxozULx_SQ-766/0046021.png').convert('RGB')
    def test_actual_watermarked_title_uses_separate_original_season_timer_and_zone(self):
        with ProgressRuntime(),BoundedOCRRuntime(960),EnglishSceneRuntime():
            rows=text_reader.read_text(self.image());state=flow_vision.semantic_state(rows)
        self.assertEqual(state['state'],'MAP');self.assertGreaterEqual(state['confidence'],.9)
        fresh=[r for r in rows if r.get('source')=='map_context_original_crop']
        self.assertEqual({r['contextKind'] for r in fresh},{'season','timer'})
        for row in fresh:
            self.assertGreaterEqual(row['score'],.9);self.assertIn('cropBox',row);self.assertIn('analysisSize',row)
        self.assertTrue(any('PonPon' in r['text'] for r in rows))
    def test_real_duplicate_and_missing_global_zone_frames_keep_independent_context(self):
        with ProgressRuntime(),BoundedOCRRuntime(960),EnglishSceneRuntime():
            for index in [46045,46046,46058,46072]:
                with self.subTest(index=index):
                    image=Image.open(ROOT/f'artifacts/p4c-earlier-gate-native-01/0QxozULx_SQ-766/{index:07}.png').convert('RGB')
                    rows=text_reader.read_text(image);state=flow_vision.semantic_state(rows)
                    self.assertEqual(state['state'],'MAP');self.assertGreaterEqual(state['confidence'],.9)

    def test_conflicting_zone_or_duplicate_fresh_context_does_not_gain_authority(self):
        import copy
        from english_scene import semantic_state
        with ProgressRuntime(),BoundedOCRRuntime(960),EnglishSceneRuntime():rows=text_reader.read_text(self.image())
        season=next(r for r in rows if r.get('contextKind')=='season')
        variants=[[*rows,copy.deepcopy(season)],[*rows,{'text':'區域3進行中','score':.99,'box':[]}],[r for r in rows if r.get('contextKind')!='season']]
        for bad in variants:
            state=semantic_state(bad)
            self.assertFalse(state['state']=='MAP' and state['confidence']>=.9)

    def test_erasing_required_original_context_cannot_gain_map_authority(self):
        for box in [(173,47,291,79),(170,77,390,112),(208,123,320,157)]:
            image=self.image();ImageDraw.Draw(image).rectangle(box,fill=(40,50,80))
            with ProgressRuntime(),BoundedOCRRuntime(960),EnglishSceneRuntime():
                rows=text_reader.read_text(image);state=flow_vision.semantic_state(rows)
            self.assertFalse(state['state']=='MAP' and state['confidence']>=.9)

if __name__=='__main__':unittest.main()
