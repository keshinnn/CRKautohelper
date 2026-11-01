"""Backend phases share exact raw work, never routing or selection authority."""
import sys, types, unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import cv2
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'ml'), 'F:/CRK helper/ml']
import fast_map_candidates as fm
import map_vision
from frame_intermediates import FrameIntermediates

FOLDER = Path('F:/CRK helper/data/map')


class CandidatePhaseTests(unittest.TestCase):
    def test_real_phases_preserve_m1_and_scan_each_increment_only_once(self):
        files = [
            ROOT / 'artifacts/m1-20261027-01/case42-trace-35929/model.png',
            ROOT / 'artifacts/case41-stability-analysis-20261027-01/S2-35935-actual/model.png',
        ]
        for file in files:
            with self.subTest(model=file.parent.name):
                with Image.open(file) as source:
                    image = source.convert('RGB')
                expected_base = fm.node_candidates(image, FOLDER)
                expected_expanded = fm.coverage_node_candidates(image, FOLDER)
                seen = []
                original = fm._match_group

                def collect(edges, group):
                    seen.extend((name, tuple(t.shape[::-1])) for _, name, t, _ in group[1])
                    return original(edges, group)

                with patch.object(map_vision, 'node_candidates', fm.node_candidates):
                    with patch.object(cv2, 'Canny', wraps=cv2.Canny) as canny:
                        with patch.object(fm, '_match_group', side_effect=collect):
                            with FrameIntermediates('a' * 32, 'b' * 64, list(image.size)) as context:
                                base = map_vision.node_candidates(image, FOLDER)
                                with context.backend(fm.coverage_node_candidates):
                                    expanded = map_vision.node_candidates(image, FOLDER)
                                    expanded[0]['box'][0] = -999
                                    self.assertEqual(map_vision.node_candidates(image, FOLDER), expected_expanded)
                                self.assertEqual(map_vision.node_candidates(image, FOLDER), expected_base)
                                self.assertEqual(base, expected_base)
                                self.assertEqual(context.summary()['hits'], 2)
                    self.assertEqual(canny.call_count, 1)
                original_bank = [
                    (name, tuple(t.shape[::-1]))
                    for _, kernels in fm._groups(str(FOLDER.resolve()), image.height, image.width)
                    for _, name, t, _ in kernels
                ]
                original_set = set(original_bank)
                self.assertEqual(Counter(k for k in seen if k in original_set), Counter(original_bank))
                extras = [k for k in seen if k not in original_set]
                self.assertEqual(len(extras), len(set(extras)))

    def test_changed_supplement_implementation_cannot_reuse_old_scan_or_result(self):
        file = ROOT / 'artifacts/m1-20261027-01/case42-trace-35929/model.png'
        with Image.open(file) as source:
            image = source.convert('RGB')
        base = fm.node_candidates(image, FOLDER)
        expanded = fm.coverage_node_candidates(image, FOLDER)
        self.assertGreater(len(expanded), len(base))
        with patch.object(map_vision, 'node_candidates', fm.coverage_node_candidates):
            with FrameIntermediates('a' * 32, 'b' * 64, list(image.size)):
                self.assertEqual(map_vision.node_candidates(image, FOLDER), expanded)
                with patch.object(fm, '_coverage_groups', return_value=()):
                    self.assertEqual(map_vision.node_candidates(image, FOLDER), base)
                self.assertEqual(map_vision.node_candidates(image, FOLDER), expanded)

    def test_backend_results_are_separate_and_exception_restores_default(self):
        base = lambda *a: [{'box': [1, 2, 3, 4]}]
        expanded = lambda *a: [{'box': [5, 6, 7, 8]}]
        owner = types.SimpleNamespace(node_candidates=base)
        image = Image.new('RGB', (16, 12))
        with FrameIntermediates('a' * 32, 'b' * 64, [16, 12], owner=owner) as context:
            self.assertEqual(owner.node_candidates(image, FOLDER)[0]['box'], [1, 2, 3, 4])
            with self.assertRaisesRegex(RuntimeError, 'stop'):
                with context.backend(expanded):
                    self.assertEqual(owner.node_candidates(image, FOLDER)[0]['box'], [5, 6, 7, 8])
                    raise RuntimeError('stop')
            self.assertEqual(owner.node_candidates(image, FOLDER)[0]['box'], [1, 2, 3, 4])
            self.assertEqual(context.summary()['hits'], 1)
        self.assertIs(owner.node_candidates, base)

    def test_disabled_control_switches_backend_without_sharing_results(self):
        calls = []
        def base(*args):
            calls.append('base')
            return []
        def expanded(*args):
            calls.append('expanded')
            return []
        owner = types.SimpleNamespace(node_candidates=base)
        image = Image.new('RGB', (16, 12))
        with FrameIntermediates('a' * 32, 'b' * 64, [16, 12], owner=owner, enabled=False) as context:
            owner.node_candidates(image, FOLDER)
            with context.backend(expanded):
                owner.node_candidates(image, FOLDER)
                owner.node_candidates(image, FOLDER)
            owner.node_candidates(image, FOLDER)
            self.assertFalse(context.summary()['enabled'])
        self.assertEqual(calls, ['base', 'expanded', 'expanded', 'base'])
        self.assertIs(owner.node_candidates, base)

    def test_inactive_or_invalid_phase_cannot_mutate_backend(self):
        owner = types.SimpleNamespace(node_candidates=lambda *a: [])
        context = FrameIntermediates('a' * 32, 'b' * 64, [16, 12], owner=owner)
        with self.assertRaisesRegex(RuntimeError, 'FRAME_CONTEXT_NOT_ACTIVE'):
            with context.backend(lambda *a: []):
                pass
        with context:
            with self.assertRaisesRegex(ValueError, 'FRAME_BACKEND_INVALID'):
                with context.backend(None):
                    pass


if __name__ == '__main__':
    unittest.main()
