import copy, hashlib, json, sys, unittest
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from bounded_ocr import BoundedOCRRuntime
from progress_evidence import parse_progress, ProgressRuntime
from english_scene import semantic_state
try:
    from english_context_evidence import reread_english_context
except ImportError:
    def reread_english_context(runtime,image,rows): return rows


class EnglishContextEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        a=json.loads((ROOT/'artifacts/exploration-20261102-01/audit-summary.json').read_text(encoding='utf-8'))
        cls.cases={r['number']:r for r in a['rows']}
        cls.progress=ProgressRuntime();cls.progress.__enter__()
        cls.runtime=BoundedOCRRuntime(960);cls.runtime.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.runtime.close();cls.progress.close()

    def sample(self,n):
        r=self.cases[n];p=json.loads(Path(r['criticalPacket']).read_text(encoding='utf-8'))
        return Image.open(r['criticalImage']).convert('RGB'),copy.deepcopy(p['evidence'])

    def assert_recovery(self,n):
        image,rows=self.sample(n);before=copy.deepcopy(rows)
        self.assertEqual(semantic_state(rows)['state'],'UNKNOWN')
        result=reread_english_context(self.runtime,image,rows)
        self.assertEqual(semantic_state(result)['state'],'MAP')
        self.assertEqual(parse_progress(result)['displayedZone'],1)
        self.assertEqual(rows,before)
        fresh=[r for r in result if r.get('source')=='english_header_original_crop']
        self.assertTrue(fresh)
        for r in fresh:
            self.assertGreaterEqual(r['score'],.9)
            self.assertEqual(r['sourcePixelSha256'],hashlib.sha256(image.tobytes()).hexdigest())
            self.assertEqual(r['sourceSize'],list(image.size))
            self.assertTrue(r['originalLocators']);self.assertTrue(r['recognitionReadings'])

    def test_actual_period_zone_49_requires_fresh_whole_label(self):self.assert_recovery(49)
    def test_actual_split_zone_50_requires_fresh_whole_label(self):self.assert_recovery(50)
    def test_actual_bracket_timer_51_requires_fresh_whole_label(self):self.assert_recovery(51)

    def test_missing_detector_suffix_is_remeasured_from_full_header_line(self):
        for n,index in [(50,2206),(51,2236)]:
            with self.subTest(n=n):
                base=ROOT/'artifacts/concentrated-repair-20261103-01'
                p=json.loads(next((base/f'english-case{n}-fresh-01').rglob(f'{index:07d}.packet.json')).read_text(encoding='utf-8'))
                case=json.loads((base/f'english-case{n}-source.json').read_text())['cases'][0]
                f=next(f for f in case['frames'] if f['frameIndex']==index)
                image=Image.open(f['image']).convert('RGB')
                self.assertEqual(semantic_state(reread_english_context(self.runtime,image,p['evidence']))['state'],'MAP')

    def test_old_locators_cannot_restore_erased_source_pixels(self):
        for n in [49,50,51]:
            with self.subTest(n=n):
                image,rows=self.sample(n)
                ImageDraw.Draw(image).rectangle((0,0,image.width*.55,image.height*.35),fill=(24,24,24))
                self.assertEqual(semantic_state(reread_english_context(self.runtime,image,rows))['state'],'UNKNOWN')

    def test_conflicting_zone_locator_cannot_be_overridden_by_pixel_reread(self):
        image,rows=self.sample(49)
        next(r for r in rows if r['text'].startswith('Zone 1in'))['text']='Zone 2in Progress.'
        self.assertEqual(semantic_state(reread_english_context(self.runtime,image,rows))['state'],'UNKNOWN')

    def test_off_header_locators_do_not_supply_context(self):
        image,rows=self.sample(49)
        for r in rows:
            if r['text'].startswith('Zone 1in'):r['box']=[[x,y+image.height*.5] for x,y in r['box']]
        self.assertEqual(semantic_state(reread_english_context(self.runtime,image,rows))['state'],'UNKNOWN')

    def test_duplicate_conflicting_label_is_not_silently_discarded(self):
        image,rows=self.sample(49)
        rows.append({'text':'Zone 1 in Progress','score':.99,'box':rows[2]['box']})
        rows.append({'text':'Zone 2 in Progress','score':.99,'box':rows[2]['box']})
        self.assertEqual(semantic_state(reread_english_context(self.runtime,image,rows))['state'],'UNKNOWN')


if __name__=='__main__':unittest.main()
