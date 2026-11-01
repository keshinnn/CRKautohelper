"""Fresh same-image M1 routing evidence and explicit coverage observation."""
import copy, hashlib, json, sys, unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'ml'), 'F:/CRK helper/ml']
import fast_map_candidates as fm
import map_vision
from frame_intermediates import FrameIntermediates

V1 = Path('F:/CRK helper')


def iou(a, b):
    area = max(0, min(a[0]+a[2], b[0]+b[2])-max(a[0], b[0])) * max(0, min(a[1]+a[3], b[1]+b[3])-max(a[1], b[1]))
    return area / (a[2]*a[3]+b[2]*b[3]-area)


class PhaseMapPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        prefix = json.loads((ROOT/'artifacts/coverage-20261028-01/prefix41-current-01/manifest.json').read_text(encoding='utf-8'))
        cls.case31 = next(c for c in prefix['cases'] if c['id'] == 'dev-L0-zone6-floor1-col2-select-1773-random-fixed')
        cls.case42 = json.loads((ROOT/'artifacts/coverage-20261028-01/case42-fresh-02/manifest.json').read_text(encoding='utf-8'))['cases'][0]

    def observe(self, frame, *, enabled=True):
        from map_pipeline import observe_geometry
        raw = Path(frame['image']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), frame['sha256'])
        with Image.open(frame['image']) as source:
            image = source.convert('RGB')
        recorded = json.loads(Path(frame['packet']).read_text(encoding='utf-8'))
        packet = {k: copy.deepcopy(recorded[k]) for k in ['binding', 'flow', 'evidence', 'progress', 'sourceBinding']}
        self.assertEqual(packet['binding']['pixelSha256'], hashlib.sha256(image.tobytes()).hexdigest())
        with patch.object(map_vision, 'node_candidates', fm.node_candidates):
            with FrameIntermediates(packet['binding']['frameId'], frame['sha256'], list(image.size), enabled=enabled) as context:
                # Fresh M1 observation, not coordinates or a map from an earlier frame.
                base = map_vision.inspect_map(image, V1/'data/map', read_header=False)
                packet['mapReview'] = copy.deepcopy(base)
                observe_geometry(image, packet, V1, context=context, coverage=True)
                self.assertIs(context.original, fm.node_candidates)
        return packet, base

    def test_near_native_route_keeps_fresh_m1_prior_and_recovers_outer_extent(self):
        for frame in self.case31['frames'][:2]:
            with self.subTest(frame=frame['frameIndex']):
                packet, base = self.observe(frame)
                self.assertFalse(base['absoluteFloorKnown'])
                self.assertEqual(packet['v2OriginalMapReview'], base)
                m = packet['mapReview']
                self.assertEqual(m['aspectRectification']['rectificationPurpose'], 'unanchored_near_native_recovery')
                target = next(n for n in m['nodes'] if n.get('floor') == 1 and n.get('column') == 2)
                self.assertGreaterEqual(iou(target['box'], self.case31['expectedBox']), .90)

    def test_source_route_also_recovers_missing_target_without_changing_prior(self):
        for frame in self.case42['frames'][:2]:
            with self.subTest(frame=frame['frameIndex']):
                packet, base = self.observe(frame)
                self.assertTrue(base['absoluteFloorKnown'])
                self.assertEqual(packet['v2OriginalMapReview'], base)
                self.assertFalse(any(n.get('floor') == 1 and n.get('column') == 1 for n in base['nodes']))
                targets = [n for n in packet['mapReview']['nodes'] if n.get('floor') == 1 and n.get('column') == 1]
                self.assertEqual(len(targets), 1)
                self.assertEqual(targets[0]['type'], 'battle')
                self.assertGreaterEqual(iou(targets[0]['box'], self.case42['expectedBox']), .90)

    def test_wrong_frame_prior_is_rejected_before_candidate_augmentation(self):
        from map_pipeline import observe_geometry
        frame = self.case31['frames'][0]
        with Image.open(frame['image']) as source:
            image = source.convert('RGB')
        recorded = json.loads(Path(frame['packet']).read_text(encoding='utf-8'))
        packet = {'binding': recorded['binding']}
        with patch.object(map_vision, 'node_candidates', fm.node_candidates):
            with FrameIntermediates(packet['binding']['frameId'], frame['sha256'], list(image.size)) as context:
                prior = map_vision.inspect_map(image, V1/'data/map', read_header=False)
                prior['frameId'] = '0' * 20
                packet['mapReview'] = prior
                with patch.object(fm, 'coverage_node_candidates', side_effect=AssertionError('must not run')):
                    with self.assertRaisesRegex(ValueError, 'FRAME_MAP_PRIOR_SOURCE_MISMATCH'):
                        observe_geometry(image, packet, V1, context=context, coverage=True)
                self.assertEqual(packet['mapReview'], prior)

    def test_absent_map_keeps_same_timing_partition_without_fabricating_nodes(self):
        from map_pipeline import observe_geometry
        from stage_timing import StageTiming
        timing=StageTiming()
        packet={'mapReview':None}
        with FrameIntermediates('a'*32,'b'*64,[16,12]) as context:
            observe_geometry(Image.new('RGB',(16,12)),packet,V1,context=context,coverage=True,timing=timing)
        self.assertIsNone(packet['mapReview'])
        self.assertEqual(set(timing.module_ms),{'source_coverage','sparse_geometry','aspect_geometry'})

    def test_shared_and_disabled_controls_have_identical_semantic_evidence(self):
        for case in [self.case31, self.case42]:
            with self.subTest(case=case['id']):
                shared, base = self.observe(case['frames'][0])
                control, control_base = self.observe(case['frames'][0], enabled=False)
                self.assertEqual(base, control_base)
                self.assertEqual(shared, control)


if __name__ == '__main__':
    unittest.main()
