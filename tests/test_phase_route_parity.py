"""A richer candidate bank must not silently change the accepted source raster."""
import copy, hashlib, json, sys, unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'ml'), 'F:/CRK helper/ml']
import fast_map_candidates as fm
import map_vision
from frame_intermediates import FrameIntermediates
from map_pipeline import observe_geometry

V1 = Path('F:/CRK helper')


class PhaseRouteParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = json.loads((ROOT / 'artifacts/phase-routing-20261028-01/native20-current-01/manifest.json').read_text(encoding='utf-8'))
        case = next(c for c in manifest['cases'] if c['id'] == 'dev-earlier-0Q-zone4-floor1-col4')
        cls.frame = next(f for f in case['frames'] if f['frameIndex'] == 46045)

    def observe(self, enabled=True, nested_coverage=False):
        frame = self.frame
        recorded = json.loads(Path(frame['packet']).read_text(encoding='utf-8'))
        self.assertEqual(hashlib.sha256(Path(frame['image']).read_bytes()).hexdigest(), frame['sha256'])
        with Image.open(frame['image']) as source:
            image = source.convert('RGB')
        self.assertEqual(hashlib.sha256(image.tobytes()).hexdigest(), recorded['binding']['pixelSha256'])
        packet = {k: copy.deepcopy(recorded[k]) for k in ['binding', 'flow', 'evidence', 'progress', 'sourceBinding']}
        with patch.object(map_vision, 'node_candidates', fm.node_candidates):
            with FrameIntermediates(packet['binding']['frameId'], frame['sha256'], list(image.size), enabled=enabled) as context:
                raw = map_vision.inspect_map(image, V1 / 'data/map', read_header=False)
                raw['header'] = copy.deepcopy(recorded['v2OriginalMapReview']['header'])
                packet['mapReview'] = copy.deepcopy(raw)
                baseline = copy.deepcopy(packet)
                observe_geometry(image, baseline, V1, context=context, coverage=False)
                active = fm.coverage_node_candidates if nested_coverage else fm.node_candidates
                with context.backend(active):
                    observe_geometry(image, packet, V1, context=context, coverage=True)
        return baseline['mapReview'], packet

    def test_unaccepted_rectification_cannot_replace_existing_source_candidates(self):
        baseline, packet = self.observe()
        self.assertEqual(len(baseline['nodes']), 4)
        self.assertIsNone(baseline.get('aspectRectification'))
        final = packet['mapReview']
        # Exact same-raster measurement identity; no new matching tolerance.
        original = {(tuple(n['box']), tuple(n['center']), n['type']) for n in baseline['nodes']}
        current = {(tuple(n['box']), tuple(n['center']), n['type']) for n in final['nodes']}
        self.assertTrue(original <= current, 'A visible source-native battle vanished after resampling')
        self.assertIsNone(final.get('aspectRectification'))
        self.assertFalse(final['absoluteFloorKnown'])

    def test_source_routing_is_identical_with_shared_intermediates_disabled(self):
        baseline, shared = self.observe(True)
        control_baseline, control = self.observe(False)
        self.assertEqual(baseline, control_baseline)
        self.assertEqual(shared, control)
        original = {(tuple(n['box']), n['type']) for n in baseline['nodes']}
        self.assertTrue(original <= {(tuple(n['box']), n['type']) for n in shared['mapReview']['nodes']})

    def test_m1_geometry_route_is_explicit_even_inside_coverage_scope(self):
        baseline, packet = self.observe(nested_coverage=True)
        self.assertIsNone(baseline.get('aspectRectification'))
        self.assertIsNone(packet['mapReview'].get('aspectRectification'))
        original = {(tuple(n['box']), n['type']) for n in baseline['nodes']}
        self.assertTrue(original <= {(tuple(n['box']), n['type']) for n in packet['mapReview']['nodes']})


if __name__ == '__main__':
    unittest.main()
