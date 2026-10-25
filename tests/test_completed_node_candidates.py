"""Original check pixels must supply a missing completed predecessor."""
import hashlib,io,json,sys,unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from map_aspect import recover_map_aspect
from map_action_evidence import inspect_map_actions

class CompletedNodeCandidateTests(unittest.TestCase):
    def fixtures(self):
        m=json.loads((ROOT/'artifacts/p4c-random-development-60-run-09/dev-primary-zone2-floor2-col3-higher-random-fixed/analysis/manifest.json').read_text(encoding='utf-8'))
        return m['cases'][0]['frames'][:2]

    def test_actual_missing_completed_node_requires_original_icon_and_check_shape(self):
        for f in self.fixtures():
            p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
            with Image.open(f['image']) as image:
                p['mapReview']=recover_map_aspect(image,p);result=inspect_map_actions(image,p)
            self.assertIsNotNone(result['current'])
            self.assertEqual(result['current']['completedPath'],['exit-0','visible-1-3'])
            node=next(n for n in p['mapReview']['nodes'] if n['id']=='visible-1-3')
            self.assertGreaterEqual(node['checkProposal']['iconScore'],.9)
            self.assertGreaterEqual(result['nodes'][node['id']]['checkMaskIoU'],.8)

    def test_erased_original_check_cannot_be_replaced_by_reward_panel_check(self):
        f=self.fixtures()[0];p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
        with Image.open(f['image']) as image:a=np.array(image.convert('RGB'))
        a[278:298,760:804]=[55,55,55];image=Image.fromarray(a);raw=io.BytesIO();image.save(raw,format='PNG');pixel=hashlib.sha256(a.tobytes()).hexdigest()
        p['binding'].update(pixelSha256=pixel,imageSha256=hashlib.sha256(raw.getvalue()).hexdigest(),frameId=hashlib.sha256(raw.getvalue()+b'negative').hexdigest()[:32]);p['flow']['frameId']=pixel[:20];p['mapReview']['frameId']=pixel[:20]
        p['mapReview']=recover_map_aspect(image,p);result=inspect_map_actions(image,p)
        self.assertIsNone(result['current'])

if __name__=='__main__':unittest.main()
