from pathlib import Path
import hashlib
import tempfile
import unittest
from PIL import Image
from duplicate_audit import audit_duplicates


class DuplicateAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def image(self, name, split, color='red', compression=6):
        p = self.root / name
        Image.new('RGB', (64, 48), color).save(p, compress_level=compression)
        return dict(image=str(p), imageSha256=hashlib.sha256(p.read_bytes()).hexdigest(), split=split)

    def test_reencoded_same_pixels_across_splits_are_detected(self):
        a = self.image('a.png', 'train', compression=0)
        b = self.image('b.png', 'test', compression=9)
        self.assertNotEqual(a['imageSha256'], b['imageSha256'])
        result = audit_duplicates([a, b], [])
        self.assertEqual(len(result['crossSplitExactRgb']), 1)
        self.assertFalse(result['trainingAdmitted'])

    def test_protected_pixels_are_not_mistaken_for_new_source(self):
        a = self.image('a.png', 'train')
        b = self.image('b.png', 'protected')
        self.assertEqual(len(audit_duplicates([a], [b])['protectedExactRgb']), 1)

    def test_equal_rgb_buffer_with_different_dimensions_is_not_exact_image(self):
        a = self.image('a.png', 'train')
        path = self.root / 'other-shape.png'
        Image.new('RGB', (48, 64), 'red').save(path)
        b = dict(image=str(path), imageSha256=hashlib.sha256(path.read_bytes()).hexdigest(), split='test')
        self.assertEqual(audit_duplicates([a, b], [])['crossSplitExactRgb'], [])

    def test_within_split_redundancy_is_reported_separately(self):
        a = self.image('a.png', 'train'); b = self.image('b.png', 'train')
        result = audit_duplicates([a, b], [])
        self.assertEqual(len(result['withinSplitExactRgb']), 1)
        self.assertEqual(result['crossSplitExactRgb'], [])

    def test_changed_asset_is_rejected_not_treated_as_unique(self):
        a = self.image('a.png', 'train')
        Image.new('RGB', (64, 48), 'blue').save(a['image'])
        with self.assertRaisesRegex(ValueError, 'DATA_IMAGE_CHANGED'):
            audit_duplicates([a], [])

    def test_low_information_never_claims_perceptual_independence(self):
        result = audit_duplicates([self.image('a.png', 'train')], [])
        self.assertEqual(len(result['lowInformationImages']), 1)
        self.assertFalse(result['perceptualIndependenceProven'])


if __name__ == '__main__':
    unittest.main()
