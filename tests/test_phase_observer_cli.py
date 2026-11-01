"""Explicit coverage must preserve source evidence with reuse on or off."""
import copy, json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PhaseObserverCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        before = json.loads((ROOT/'artifacts/coverage-20261028-01/prefix41-current-01/manifest.json').read_text(encoding='utf-8'))
        c31 = copy.deepcopy(next(c for c in before['cases'] if c['id'] == 'dev-L0-zone6-floor1-col2-select-1773-random-fixed'))
        c42 = copy.deepcopy(json.loads((ROOT/'artifacts/coverage-20261028-01/case42-fresh-02/manifest.json').read_text(encoding='utf-8'))['cases'][0])
        c31['frames'] = c31['frames'][:2]
        c42['frames'] = c42['frames'][:2]
        cls.temp = tempfile.TemporaryDirectory(dir=ROOT/'artifacts')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.folder = Path(cls.temp.name)
        cls.source = cls.folder/'source.json'
        cls.source.write_text(json.dumps({**before, 'cases': [c31, c42]}), encoding='utf-8')

    def test_current_coverage_reuse_and_fresh_control_are_semantically_identical(self):
        runs = []
        for label, extra in [('shared', []), ('control', ['--disable-frame-reuse'])]:
            out = self.folder/label
            result = subprocess.run([sys.executable, '-B', 'ml/analyze_cases.py', str(self.source), str(out),
                '--fast-map', '--map-coverage', '--bounded-ocr', '960', *extra],
                cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=180)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((out/'manifest.json').read_text(encoding='utf-8'))
            self.assertEqual(manifest['analysis']['mapBackend'], 'exact_grouped_masks_parallel4_phase_coverage')
            runs.append([json.loads(Path(f['packet']).read_text(encoding='utf-8')) for c in manifest['cases'] for f in c['frames']])
        reused = 0
        for shared, control in zip(*runs):
            for packet in [shared, control]:
                self.assertTrue(packet['analysisTiming']['freshFullPipeline'])
                self.assertFalse(packet['frameIntermediates']['crossFrameReuse'])
                self.assertFalse(packet['frameIntermediates']['authorityCached'])
            reused += sum(c.get('rawScanReused', False) for c in shared['frameIntermediates']['calls'])
            self.assertFalse(control['frameIntermediates']['enabled'])
            for key in ['binding', 'sourceBinding', 'flow', 'evidence', 'mapReview', 'v2OriginalMapReview',
                        'progress', 'v2TrackedMap', 'v2PreviewContext', 'v2Preview', 'v2MapActions']:
                self.assertEqual(shared.get(key), control.get(key), key)
        self.assertEqual(len(runs[0]), 4)
        self.assertGreater(reused, 0)

    def test_coverage_without_fast_backend_is_rejected_before_observation(self):
        out = self.folder/'invalid-mode'
        result = subprocess.run([sys.executable, '-B', 'ml/analyze_cases.py', str(self.source), str(out),
            '--map-coverage'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('--map-coverage requires --fast-map', result.stderr)
        self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
