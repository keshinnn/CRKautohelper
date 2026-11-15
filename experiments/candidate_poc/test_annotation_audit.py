import copy
import hashlib
from pathlib import Path
import tempfile
import unittest
from PIL import Image
from annotation_audit import audit_full_frame


class AnnotationAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.image = Path(self.tmp.name) / 'source.png'
        Image.new('RGB', (96, 64), 'red').save(self.image)
        self.source = dict(image=str(self.image), imageSha256=hashlib.sha256(self.image.read_bytes()).hexdigest(), sourceSize=[96, 64])
        annotation = dict(className='map_node', box=[10, 10, 20, 20], visibility='complete')
        self.a = dict(imageSha256=self.source['imageSha256'], reviewerId='first',
                      exhaustive=True, annotations=[annotation])
        self.b = copy.deepcopy(self.a); self.b['reviewerId'] = 'independent'

    def test_agreement_is_annotation_only_not_training_or_action_authority(self):
        result = audit_full_frame(self.source, self.a, self.b)
        self.assertTrue(result['consistent'])
        self.assertEqual(result['matchedBoxes'], 1)
        self.assertFalse(result['trainingAdmitted'])

    def test_two_boxes_cannot_match_one_reference(self):
        self.a['annotations'] *= 2
        self.assertFalse(audit_full_frame(self.source, self.a, self.b)['consistent'])

    def test_same_counts_with_duplicate_boxes_do_not_hide_missing_object(self):
        self.a['annotations'] *= 2
        other = copy.deepcopy(self.b['annotations'][0]); other['box'] = [60, 30, 20, 20]
        self.b['annotations'].append(other)
        self.assertFalse(audit_full_frame(self.source, self.a, self.b)['consistent'])

    def test_partial_cannot_be_promoted_to_complete_by_overlap(self):
        self.b['annotations'][0]['visibility'] = 'partial'
        self.assertFalse(audit_full_frame(self.source, self.a, self.b)['consistent'])

    def test_wrong_source_hash_rejects_identical_boxes(self):
        self.b['imageSha256'] = '0' * 64
        self.assertFalse(audit_full_frame(self.source, self.a, self.b)['consistent'])

    def test_changed_png_is_rejected(self):
        Image.new('RGB', (96, 64), 'blue').save(self.image)
        self.assertFalse(audit_full_frame(self.source, self.a, self.b)['consistent'])

    def test_truncated_png_cannot_pass_with_self_consistent_header_hash(self):
        self.image.write_bytes(self.image.read_bytes()[:41])
        digest = hashlib.sha256(self.image.read_bytes()).hexdigest()
        for item in [self.source, self.a, self.b]:
            item['imageSha256'] = digest
        self.assertFalse(audit_full_frame(self.source, self.a, self.b)['consistent'])

    def test_non_rgb_pixels_are_not_silently_converted(self):
        Image.new('L', (96, 64), 100).save(self.image)
        digest = hashlib.sha256(self.image.read_bytes()).hexdigest()
        for item in [self.source, self.a, self.b]:
            item['imageSha256'] = digest
        self.assertFalse(audit_full_frame(self.source, self.a, self.b)['consistent'])

    def test_missing_exhaustiveness_attestation_is_not_silently_accepted(self):
        self.a.pop('exhaustive')
        self.assertFalse(audit_full_frame(self.source, self.a, self.b)['consistent'])

    def test_same_reviewer_is_not_an_independent_pass(self):
        self.b['reviewerId'] = self.a['reviewerId']
        self.assertFalse(audit_full_frame(self.source, self.a, self.b)['consistent'])

    def test_out_of_bounds_or_nan_box_rejects_no_clamping(self):
        for box in [[-1, 0, 20, 20], [80, 0, 20, 20], [float('nan'), 0, 20, 20]]:
            with self.subTest(box=box):
                self.a['annotations'][0]['box'] = box
                self.assertFalse(audit_full_frame(self.source, self.a, self.b)['consistent'])

    def test_low_iou_is_reported_instead_of_averaging(self):
        self.b['annotations'][0]['box'] = [13, 10, 20, 20]
        self.assertFalse(audit_full_frame(self.source, self.a, self.b)['consistent'])


if __name__ == '__main__':
    unittest.main()
