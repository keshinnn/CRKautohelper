"""Legacy pixel decisions plus required work bounds, with real OpenCV."""
import hashlib, json, sys, unittest
from pathlib import Path
from unittest.mock import patch
import cv2, numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from map_vision import map_templates
try:
    import icon_ranking
except ModuleNotFoundError:
    icon_ranking=None

class IconRankingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder=ROOT/'tests/fixtures/icon-ranking'
        cls.rows=json.loads((cls.folder/'manifest.json').read_text(encoding='utf-8'))['rows']
        cls.templates=map_templates(Path('F:/CRK helper/data/map'))

    def rank(self,row):
        self.assertIsNotNone(icon_ranking, 'Exact required-family ranking is not implemented')
        file=self.folder/row['file']
        self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(),row['sha256'])
        q=np.asarray(Image.open(file).convert('RGB'))
        self.assertEqual(q.shape,(34,34,3))
        return icon_ranking.rank_required_icon(q,cv2.cvtColor(q,cv2.COLOR_RGB2GRAY),self.templates,row['required'],row['incumbent'])

    def test_old_real_pixel_decisions_and_accepted_scores_are_exact(self):
        for row in self.rows:
            with self.subTest(row=row['file']):
                result=self.rank(row)
                if row['expectedAccept']:
                    self.assertEqual(result,(tuple(row['done']),tuple(row['other'])))
                else:
                    self.assertIsNone(result)

    def test_rejected_required_scores_do_not_scan_unrelated_templates(self):
        for row in self.rows:
            if row['category'] not in ('low-done','incumbent-reject'): continue
            with self.subTest(row=row['file']),patch.object(cv2,'matchTemplate',wraps=cv2.matchTemplate) as measured:
                self.assertIsNone(self.rank(row))
                self.assertEqual(measured.call_count,len(row['required']))

    def test_accepted_pixels_still_compare_every_reference_template(self):
        for row in self.rows:
            if not row['expectedAccept']:continue
            with self.subTest(row=row['file']),patch.object(cv2,'matchTemplate',wraps=cv2.matchTemplate) as measured:
                self.assertIsNotNone(self.rank(row))
                self.assertEqual(measured.call_count,len(self.templates))

    def test_invalid_required_family_cannot_produce_a_match(self):
        self.assertIsNotNone(icon_ranking, 'Exact required-family ranking is not implemented')
        q=np.zeros((34,34,3),dtype=np.uint8)
        with self.assertRaises(ValueError):
            icon_ranking.rank_required_icon(q,cv2.cvtColor(q,cv2.COLOR_RGB2GRAY),self.templates,['missing-template'])

if __name__=='__main__':unittest.main()
