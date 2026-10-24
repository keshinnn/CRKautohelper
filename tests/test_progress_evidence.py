import json,sys,unittest
from pathlib import Path
sys.path[:0]=['F:/CRK helper/ml',str(Path(__file__).resolve().parents[1]/'ml')]
import text_reader
try:
    from progress_evidence import ProgressRuntime,parse_progress
except ImportError:
    parse_progress=text_reader.map_header_from_evidence
    class ProgressRuntime:
        def __enter__(self):return self
        def __exit__(self,*a):pass

class ProgressEvidenceTests(unittest.TestCase):
    def test_actual_zone10_native_text_is_not_discarded_by_zone9_limit(self):
        p=json.loads((Path(__file__).resolve().parents[1]/'artifacts/p4c-zone10-before.packet.json').read_text(encoding='utf-8'))
        self.assertIsNone(p['progress']['displayedZone'])
        actual=parse_progress(p['evidence'])
        self.assertEqual(actual['displayedZone'],10);self.assertGreaterEqual(actual['score'],.9)
        self.assertFalse(actual['conflictingEvidence'])

    def test_exact_zone10_phrases_keep_floor_scores_and_conflict_with_other_claims(self):
        for text,floor in [('區域10進行中',None),('10區域第3層進行中',3)]:
            row={'text':text,'score':.96,'box':[]};actual=parse_progress([row])
            self.assertEqual(actual['displayedZone'],10);self.assertEqual(actual['lastEnteredFloor'],floor);self.assertEqual(actual['score'],.96)
            actual=parse_progress([row,{'text':'區域9進行中','score':.99,'box':[]}])
            self.assertTrue(actual['conflictingEvidence']);self.assertIsNone(actual['displayedZone'])
        self.assertEqual(parse_progress([{'text':'10區域完成','score':.97,'box':[]}])['displayedAreaComplete'],True)
        for text in ['區域11進行中','區域100進行中','110區域完成','10區域第32層進行中']:
            self.assertIsNone(parse_progress([{'text':text,'score':.99,'box':[]}])['displayedZone'])
        self.assertIsNone(parse_progress([{'text':'區域10進行中','score':.77,'box':[]}])['displayedZone'])

    def test_zone_extension_is_scoped_and_existing_claims_are_unchanged(self):
        original=text_reader.map_header_from_evidence;rows=[{'text':'區域6進行中','score':.94,'box':[]}]
        self.assertEqual(parse_progress(rows),original(rows))
        with ProgressRuntime():self.assertEqual(text_reader.map_header_from_evidence([{'text':'區域10進行中','score':.97,'box':[]}])['displayedZone'],10)
        self.assertIs(text_reader.map_header_from_evidence,original)

if __name__=='__main__':unittest.main()
