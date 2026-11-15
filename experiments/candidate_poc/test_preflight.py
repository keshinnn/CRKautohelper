import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from preflight import lock_baseline, negative_suite, negative_cases


class BaselineLockTests(unittest.TestCase):
    def test_actual_negative_suite_locks_all_original_cases(self):
        root = Path(__file__).resolve().parents[2] / 'artifacts/concentrated-repair-20261103-02/current-negative30'
        cases = negative_cases(root)
        self.assertEqual(len(cases), 30)
        # Original negative manifests plan 60 images. The previous runner stopped
        # after one frame for three missing-zone cases (57 actually analyzed).
        self.assertEqual(sum(len(c['frames']) for c in cases), 60)
        self.assertTrue(all(Path(c['frames'][0]['image']).is_file() for c in cases))

    def test_negative_suite_uses_actual_summary_schema(self):
        actual = {'suites': [{'label': 'current-native20', 'results': [{}] * 20},
                            {'label': 'current-negative30', 'resultsCount': 30, 'report': 'negative.json'}]}
        self.assertEqual(negative_suite(actual)['report'], 'negative.json')

    def test_verified_bytes_are_archived_and_roundtrip_checked(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp); (root / 'source.py').write_bytes(b'approved baseline\n')
            h = hashlib.sha256((root / 'source.py').read_bytes()).hexdigest()
            v = {'code': {'source.py': h}, 'externalDependencies': {}}
            result = lock_baseline(root, v, root / 'snapshot.zip')
            self.assertEqual(result['verifiedFiles'], 1)
            self.assertTrue(result['roundtripVerified'])
            with zipfile.ZipFile(root / 'snapshot.zip') as archive:
                self.assertEqual(archive.read('source/source.py'), b'approved baseline\n')

    def test_mismatch_prevents_snapshot(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp); (root / 'source.py').write_bytes(b'changed')
            v = {'code': {'source.py': '0' * 64}, 'externalDependencies': {}}
            with self.assertRaisesRegex(ValueError, 'BASELINE_CHANGED'):
                lock_baseline(root, v, root / 'snapshot.zip')
            self.assertFalse((root / 'snapshot.zip').exists())

    def test_archive_is_never_silently_overwritten(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp); archive = root / 'snapshot.zip'; archive.write_bytes(b'keep')
            with self.assertRaises(FileExistsError):
                lock_baseline(root, {'code': {}, 'externalDependencies': {}}, archive)
            self.assertEqual(archive.read_bytes(), b'keep')


if __name__ == '__main__':
    unittest.main()
