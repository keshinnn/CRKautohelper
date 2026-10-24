import copy,json,sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from progress_evidence import parse_progress,ProgressRuntime
from bounded_ocr import BoundedOCRRuntime
import text_reader

class EnglishProgressTests(unittest.TestCase):
    def test_full_english_claim_preserves_score_and_rejects_conflicts_and_watermark(self):
        row={'text':'Zone 1 in Progress','score':.96,'box':[]}
        before=copy.deepcopy(row);p=parse_progress([row])
        self.assertEqual(p['displayedZone'],1);self.assertEqual(p['score'],.96)
        self.assertEqual(row,before)
        for text in ['@chateaw Zone 1 in Progress','Zone 11 in Progress','Zone 100 in Progress','Zone 1ClearReward','Zone 1 in Progr']:
            self.assertIsNone(parse_progress([dict(row,text=text)])['displayedZone'])
        p=parse_progress([row,dict(row,text='Zone 2 in Progress')])
        self.assertTrue(p['conflictingEvidence']);self.assertIsNone(p['displayedZone'])
        p=parse_progress([row,dict(row,text='區域2進行中')])
        self.assertTrue(p['conflictingEvidence']);self.assertIsNone(p['displayedZone'])

    def test_real_watermarked_fragmented_zone_requires_fresh_original_crop(self):
        packet=json.loads((ROOT/'artifacts/p4c-LX46-dev-analysis-01/dev-LX46-zone1-floor1-col1-resume/0002194.packet.json').read_text(encoding='utf-8'))
        self.assertIsNone(packet['progress']['displayedZone'])
        image=Image.open(ROOT/'artifacts/p4c-LX46-native-qualification-01/candidate-00-38.0/0002194.png').convert('RGB')
        with ProgressRuntime(),BoundedOCRRuntime(960):
            rows=text_reader.read_text(image)
            p=parse_progress(rows)
            self.assertEqual(p['displayedZone'],1);self.assertGreaterEqual(p['score'],.9)
            actual=[r for r in rows if r.get('source')=='remaining_time_adjacent_progress_original_crop']
            self.assertEqual(len(actual),1);self.assertIn('Zone',actual[0]['text'])
            self.assertGreaterEqual(actual[0]['score'],.9)
            erased=image.copy();ImageDraw.Draw(erased).rectangle((90,245,430,310),fill=(24,24,24))
            self.assertIsNone(parse_progress(text_reader.read_text(erased))['displayedZone'])

if __name__=='__main__':unittest.main()
