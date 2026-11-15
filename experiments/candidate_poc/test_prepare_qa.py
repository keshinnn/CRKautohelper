import hashlib
import io
from pathlib import Path
import tempfile
import unittest
import cv2
import numpy as np
from PIL import Image
from prepare_qa import validate_reservations, extract_frame


class SourcePreparationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.video = self.root / 'frames.avi'
        writer = cv2.VideoWriter(str(self.video), cv2.VideoWriter_fourcc(*'MJPG'), 10, (64, 48))
        self.assertTrue(writer.isOpened())
        for i in range(4):
            frame = np.zeros((48, 64, 3), dtype=np.uint8)
            frame[:] = [20 + i * 25, 40, 100]
            writer.write(frame)
        writer.release()

    def test_protected_original_id_cannot_be_evaded_by_reencoding(self):
        rows = [dict(id='protected-id', split='train', sha256='a' * 64)]
        self.assertIn('PROTECTED_SOURCE_ID', validate_reservations(rows, ['protected-id']))

    def test_same_id_cannot_cross_splits(self):
        rows = [dict(id='same-id', split='train'), dict(id='same-id', split='test')]
        self.assertIn('SOURCE_CROSS_SPLIT', validate_reservations(rows, []))

    def test_same_bytes_cannot_cross_source_ids(self):
        rows = [dict(id='first', split='train', sha256='a' * 64),
                dict(id='second', split='test', sha256='a' * 64)]
        self.assertIn('BYTE_DUPLICATE_SOURCE', validate_reservations(rows, []))

    def test_raw_png_equals_decoded_frame_without_resizing(self):
        target = self.root / 'raw.png'
        result = extract_frame(self.video, 2, target)
        cap = cv2.VideoCapture(str(self.video)); cap.set(cv2.CAP_PROP_POS_FRAMES, 2)
        ok, bgr = cap.read(); cap.release(); self.assertTrue(ok)
        with Image.open(target) as im:
            self.assertEqual(im.size, (64, 48))
            self.assertEqual(im.tobytes(), cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).tobytes())
        self.assertEqual(result['frameIndex'], 2)
        self.assertFalse(result['reviewed'])
        self.assertEqual(result['independentReviews'], 0)

    def test_existing_raw_image_is_not_overwritten(self):
        target = self.root / 'raw.png'; target.write_bytes(b'keep')
        with self.assertRaises(FileExistsError):
            extract_frame(self.video, 1, target)
        self.assertEqual(target.read_bytes(), b'keep')

    def test_invalid_frame_index_is_rejected(self):
        for index in [-1, 4, 1.5]:
            with self.subTest(index=index):
                with self.assertRaisesRegex(ValueError, 'FRAME_INDEX_INVALID'):
                    extract_frame(self.video, index, self.root / 'absent.png')
        self.assertFalse((self.root / 'absent.png').exists())


if __name__ == '__main__':
    unittest.main()
