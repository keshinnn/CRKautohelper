"""Same-call exact ranking reuse; geometry and source proofs still run."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
import completed_node_candidates as cn
from map_aspect import recover_map_aspect
from map_action_evidence import inspect_map_actions


class CompletedRankingReuseTests(unittest.TestCase):
    def fixture(self):
        path=ROOT/'artifacts/p4c-random-development-60-run-09/dev-primary-zone2-floor2-col3-higher-random-fixed/analysis/manifest.json'
        return json.loads(path.read_text(encoding='utf-8'))['cases'][0]['frames'][0]

    def observe(self,packet,image):
        records=[];active=[]
        original=cn.completed_node_candidates;ranking=cn.rank_required_icon
        def search(*args,**kwargs):
            row={'keys':set(),'calls':0,'duplicates':0};active.append(row)
            try:return original(*args,**kwargs)
            finally:active.pop();records.append(row)
        def measured(q,gray,templates,required,incumbent=None):
            row=active[-1];key=(q.shape,q.dtype.str,q.tobytes(),gray.tobytes(),tuple(required),incumbent)
            row['calls']+=1;row['duplicates']+=int(key in row['keys']);row['keys'].add(key)
            return ranking(q,gray,templates,required,incumbent)
        with patch.object(cn,'completed_node_candidates',search),patch.object(cn,'rank_required_icon',measured):
            packet['mapReview']=recover_map_aspect(image,packet)
        return records

    def test_real_completed_predecessor_keeps_proof_without_duplicate_ranking(self):
        f=self.fixture();packet=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
        with Image.open(f['image']) as image:
            rows=self.observe(packet,image);actions=inspect_map_actions(image,packet)
        self.assertGreater(sum(r['calls'] for r in rows),0)
        self.assertEqual(sum(r['duplicates'] for r in rows),0)
        self.assertEqual(actions['current']['completedPath'],['exit-0','visible-1-3'])
        node=next(n for n in packet['mapReview']['nodes'] if n['id']=='visible-1-3')
        self.assertGreaterEqual(node['checkProposal']['iconScore'],.9)
        self.assertGreaterEqual(actions['nodes'][node['id']]['checkMaskIoU'],.8)

    def test_identical_next_search_recomputes_instead_of_reusing_prior_call(self):
        f=self.fixture();original=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
        with Image.open(f['image']) as image:
            first=self.observe(copy.deepcopy(original),image)
            second=self.observe(copy.deepcopy(original),image)
        self.assertGreater(sum(r['calls'] for r in first),0)
        self.assertEqual([r['calls'] for r in first],[r['calls'] for r in second])

if __name__=='__main__':unittest.main()
