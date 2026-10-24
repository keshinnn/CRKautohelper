import copy,hashlib,sys,unittest
import json
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,'F:/CRK helper/ml');sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
import text_reader
try:
    from bounded_ocr import BoundedOCRRuntime,normalize_evidence
except ImportError:
    def normalize_evidence(rows):return rows
    class BoundedOCRRuntime:
        def __init__(self,*args):self.reader=None
        def __enter__(self):return self
        def __exit__(self,*args):pass

class BoundedOCRTests(unittest.TestCase):
    def test_actual_seventyfive_percent_failure_confirms_only_after_independent_line_read(self):
        from preview_identity import inspect_preview_identity
        root=Path(__file__).resolve().parents[1]
        packet=json.loads((root/'artifacts/p4c-bounded960-analysis-01/zone-3-first-battle-scale-0.75/0020225.packet.json').read_text(encoding='utf-8'))
        image=Image.open(root/'artifacts/p4b-fixed-source/zone-3-first-battle-scale-0.75/0020225.png').convert('RGB')
        self.assertFalse(packet['v2Preview']['verified'])
        original=next(r for r in packet['evidence'] if '普通' in r['text'])['score']
        with BoundedOCRRuntime(960) as runtime:
            result=inspect_preview_identity(image,packet)
            self.assertTrue(result['verified'])
            self.assertEqual(result['ordinaryEvidence']['originalScore'],original)
            self.assertGreaterEqual(result['ordinaryEvidence']['refinedScore'],.95)
            self.assertGreater(len(runtime.take_metadata()['recognitionCrops']),0)

    def test_actual_floor2_star_prefix_is_removed_only_by_fresh_pixel_read(self):
        from preview_identity import inspect_preview_identity
        root=Path(__file__).resolve().parents[1]
        manifest=json.loads((root/'artifacts/p4c-bounded-high-floor-analysis-02/case-0.json').read_text(encoding='utf-8'))
        source=manifest['cases'][0]['frames'][-1]
        packet=json.loads(Path(source['packet']).read_text(encoding='utf-8'))
        image=Image.open(source['image']).convert('RGB')
        self.assertFalse(packet['v2Preview']['verified'])
        with BoundedOCRRuntime(960) as runtime:
            result=inspect_preview_identity(image,packet)
            self.assertTrue(result['verified'])
            self.assertEqual(result['selectedNode']['floor'],2)
            self.assertGreaterEqual(result['ordinaryEvidence']['refinedScore'],.95)
            crops=runtime.take_metadata()['recognitionCrops']
            self.assertGreater(len(crops),1)
            self.assertTrue(any(v['text']=='普通' and v['score']>=.95 for c in crops for v in c['variants']))

    def test_actual_native_missing_zone_requires_new_text_pixels_not_history(self):
        from PIL import ImageDraw
        root=Path(__file__).resolve().parents[1]
        packet=json.loads((root/'artifacts/p4c-L0-native-dev-analysis-01/dev-L0-zone6-floor1-col2-resume-1781/0053427.packet.json').read_text(encoding='utf-8'))
        self.assertIsNone(packet['progress']['displayedZone'])
        source=root/'artifacts/p4c-native-timing-01/L0ktY5qUppI-1781/0053427.png'
        image=Image.open(source).convert('RGB')
        with BoundedOCRRuntime(960):
            evidence=text_reader.read_text(image)
            progress=text_reader.map_header_from_evidence(evidence)
            self.assertEqual(progress['displayedZone'],6)
            self.assertGreaterEqual(progress['score'],.9)
            row=next(r for r in evidence if r.get('source')=='remaining_time_adjacent_progress_original_crop')
            self.assertGreaterEqual(row['score'],.9)
            self.assertGreater(min(p[1] for p in row['box']),118)
            erased=image.copy();ImageDraw.Draw(erased).rectangle((0,118,246,180),fill='black')
            self.assertIsNone(text_reader.map_header_from_evidence(text_reader.read_text(erased))['displayedZone'])

    def test_transitional_frame_without_four_column_geometry_is_still_unproven(self):
        from preview_identity import inspect_preview_identity
        root=Path(__file__).resolve().parents[1]
        packet=json.loads((root/'artifacts/p4c-bounded960-analysis-01/zone-3-first-battle-scale-0.75/0020223.packet.json').read_text(encoding='utf-8'))
        image=Image.open(root/'artifacts/p4b-fixed-source/zone-3-first-battle-scale-0.75/0020223.png').convert('RGB')
        self.assertIsNone(packet['mapReview']['columns'])
        with BoundedOCRRuntime(960):self.assertFalse(inspect_preview_identity(image,packet)['verified'])

    def test_orthographic_phrase_retains_exact_raw_score_box_and_other_text(self):
        rows=[{'text':'剩余時間13天','score':.9438,'box':[[1,2],[3,2],[3,4],[1,4]]},{'text':'余','score':.99,'box':[]},{'text':'剩問時間','score':.99,'box':[]}]
        before=copy.deepcopy(rows);actual=normalize_evidence(rows)
        self.assertEqual(actual[0]['text'],'剩餘時間13天');self.assertEqual(actual[0]['recognizerText'],before[0]['text'])
        self.assertEqual(actual[0]['score'],before[0]['score']);self.assertEqual(actual[0]['box'],before[0]['box'])
        self.assertEqual(actual[1:],before[1:]);self.assertEqual(rows,before)

    def test_actual_tensor_cap_and_independent_axes_are_recorded_and_context_restores(self):
        old_reader,old_read=text_reader._reader,text_reader.read_text
        with BoundedOCRRuntime(960) as runtime:
            self.assertIsNotNone(runtime.reader)
            tensor=runtime.reader.text_det.get_preprocess(1920)(np.zeros((1440,1920,3),dtype='uint8'))
            self.assertEqual(list(tensor.shape[-2:]),[704,960])
            record=runtime.take_metadata()['detectorCalls'][0]
            self.assertEqual(record['inputSize'],[1920,1440]);self.assertEqual(record['tensorSize'],[960,704])
            self.assertEqual(record['sx'],.5);self.assertAlmostEqual(record['sy'],704/1440);self.assertNotEqual(record['sx'],record['sy'])
        self.assertIs(text_reader._reader,old_reader);self.assertIs(text_reader.read_text,old_read)

    def test_actual_low_resolution_ocr_preserves_map_and_zone_authority_without_score_override(self):
        from flow_vision import semantic_state
        source=Path(__file__).resolve().parents[1]/'artifacts/p4c-dev-floor2/0014530.png';before=source.read_bytes()
        with BoundedOCRRuntime(960) as runtime:
            self.assertIsNotNone(runtime.reader)
            image=Image.open(source).convert('RGB');e=text_reader.refine_map_progress(image,text_reader.refine_map_title(image,text_reader.read_text(image)))
            state=semantic_state(e);zone=text_reader.map_header_from_evidence(e)
            self.assertEqual(state['state'],'MAP');self.assertGreaterEqual(state['confidence'],.85)
            self.assertEqual(zone['displayedZone'],2);self.assertGreaterEqual(zone['score'],.9)
            self.assertTrue(any(r.get('recognizerText','').startswith('剩余時間') for r in e))
            for call in runtime.take_metadata()['detectorCalls']:self.assertLessEqual(max(call['tensorSize']),960)
        self.assertEqual(hashlib.sha256(source.read_bytes()).digest(),hashlib.sha256(before).digest())

if __name__=='__main__':unittest.main()
