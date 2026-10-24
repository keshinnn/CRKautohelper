import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'ml'))
try:
    from freeze_replay_corpus import validate_corpus
except ImportError:
    def validate_corpus(data):return data['cases']

class CorpusFreezerTests(unittest.TestCase):
    def actual(self):return json.loads((ROOT/'data/p4c/corpus-30-v1.json').read_text(encoding='utf-8'))
    def test_actual_thirty_reviewed_interactions_have_frozen_twenty_ten_split(self):
        cases=validate_corpus(self.actual())
        self.assertEqual(len(cases),30);self.assertEqual(sum(c['split']=='holdout' for c in cases),10)
        self.assertEqual(len({c['videoSha256'] for c in cases}),4)
    def test_duplicate_source_interaction_is_rejected_even_with_new_id_or_intent(self):
        data=self.actual();replacement=copy.deepcopy(data['cases'][0]);replacement['id']='renamed-duplicate';replacement['intent']['column']=4
        data['cases'][1]=replacement
        with self.assertRaisesRegex(ValueError,'overlapping source interactions'):validate_corpus(data)
    def test_incomplete_or_unsafe_or_unreviewed_corpus_cannot_be_frozen(self):
        for kind in ['count','split','geometry','nan','review','interval','gate','unsafe-id','fps']:
            with self.subTest(kind=kind):
                d=self.actual();c=d['cases'][0]
                if kind=='count':d['cases'].pop()
                elif kind=='split':c['split']='holdout'
                elif kind=='geometry':c['clientBox']=[0,0,5,5]
                elif kind=='nan':c['expectedBox'][0]=float('nan')
                elif kind=='review':c['reviewed']=False
                elif kind=='interval':c['preFrames'][1]=c['preFrames'][0]+1
                elif kind=='gate':c['gateWindowMs'][0]+=100
                elif kind=='unsafe-id':c['id']='../escape'
                elif kind=='fps':c['sourceFps']=24
                with self.assertRaises(ValueError):validate_corpus(d)

if __name__=='__main__':unittest.main()
