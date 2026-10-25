"""Actual clock-icon/timer merge; no token stripping or score promotion."""
import copy,json,sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from bounded_ocr import BoundedOCRRuntime
from preview_identity import inspect_preview_identity,_box

class PreviewTimerTests(unittest.TestCase):
    def fixture(self,index=20228):
        m=json.loads((ROOT/'artifacts/p4c-random-development-60-run-04/zone-3-first-battle-random-pre-change/analysis/manifest.json').read_text(encoding='utf-8'))
        f=next(f for f in m['cases'][0]['frames'] if f['frameIndex']==index)
        return Image.open(f['image']).convert('RGB'),json.loads(Path(f['packet']).read_text(encoding='utf-8'))

    def test_actual_clock_prefix_is_re_read_from_original_digits_without_accepting_raw_token(self):
        with BoundedOCRRuntime(960):
            for index in [20226,20228,20229,20230,20231]:
                with self.subTest(index=index):
                    image,p=self.fixture(index);before=copy.deepcopy(p)
                    weak=next(r for r in p['evidence'] if r['text']=='@03:00')
                    self.assertLess(weak['score'],.95)
                    result=inspect_preview_identity(image,p);self.assertTrue(result['verified'])
                    self.assertEqual(result['timerEvidence']['text'],'03:00')
                    self.assertGreaterEqual(result['timerEvidence']['score'],.95)
                    self.assertEqual(result['timerEvidence']['originalText'],'@03:00')
                    self.assertEqual(p,before)

    def test_missing_digit_pixels_or_duplicate_clock_rows_cannot_gain_timer_authority(self):
        from preview_identity import _timer_original_crop
        image,p=self.fixture();rows=p['evidence'];weak=next(r for r in rows if r['text']=='@03:00')
        with BoundedOCRRuntime(960):
            self.assertEqual(_timer_original_crop(image,[*rows,copy.deepcopy(weak)]),[])
            self.assertEqual(_timer_original_crop(image,[*rows,{**weak,'text':'02:59'}]),[])
            erased=image.copy();x,y,w,h=_box(weak)
            ImageDraw.Draw(erased).rectangle((int(x),int(y),int(x+w+1),int(y+h+1)),fill=(45,50,80))
            self.assertEqual(_timer_original_crop(erased,rows),[])

    def test_clock_text_without_adjacent_time_limit_label_is_not_game_timer_evidence(self):
        from preview_identity import _timer_original_crop
        image,p=self.fixture();rows=[r for r in p['evidence'] if '限制時' not in r.get('text','')]
        with BoundedOCRRuntime(960):self.assertEqual(_timer_original_crop(image,rows),[])

if __name__=='__main__':unittest.main()
