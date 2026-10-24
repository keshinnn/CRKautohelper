import copy,json,sys,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
try:
    from map_action_evidence import inspect_map_actions
except ImportError:
    def inspect_map_actions(*args):return {'nodes':{},'current':None}

class PixelMapActionTests(unittest.TestCase):
    def setUp(self):
        self.root=Path(__file__).resolve().parents[1]
        self.image=Image.open(self.root/'artifacts/p4c-dev-floor2/0014530.png').convert('RGB')
        self.packet=json.loads((self.root/'artifacts/p4c-dev-floor2/analysis-01/dev-floor2/0014530.packet.json').read_text(encoding='utf-8'))

    def test_actual_orange_target_and_gray_inactive_are_distinguished(self):
        result=inspect_map_actions(self.image,self.packet)
        self.assertTrue(result['nodes'].get('visible-2-3',{}).get('available'))
        self.assertFalse(result['nodes'].get('visible-1-4',{}).get('available',True))
        self.assertTrue(result['nodes']['visible-2-3']['verified'])

    def test_completed_pixels_and_unique_path_establish_current_without_v1_current(self):
        result=inspect_map_actions(self.image,self.packet)
        self.assertIsNotNone(result['current'])
        self.assertEqual(result['current']['nodeId'],'visible-1-3')
        self.assertTrue(result['nodes']['visible-1-3']['completed'])
        self.assertGreaterEqual(result['nodes']['visible-1-3']['checkMaskIoU'],.8)

    def test_forged_v1_completed_candidate_does_not_create_completed_pixel_proof(self):
        packet=copy.deepcopy(self.packet)
        for node in packet['mapReview']['nodes']:
            if node['id']=='visible-1-4':node['completed']=True;node['completion_shape_score']=1
        result=inspect_map_actions(self.image,packet)
        self.assertFalse(result['nodes'].get('visible-1-4',{}).get('completed',True))
        self.assertEqual(result['current']['nodeId'],'visible-1-3')

    def test_missing_edge_or_changed_pixels_reject_current_proof(self):
        packet=copy.deepcopy(self.packet);packet['mapReview']['edges']=[]
        self.assertIsNone(inspect_map_actions(self.image,packet)['current'])
        image=self.image.copy();image.paste((0,0,0),(784,508,896,621))
        self.assertIsNone(inspect_map_actions(image,self.packet)['current'])

    def test_actual_transitional_map_without_node_ids_returns_unproven_instead_of_crashing(self):
        folder=self.root/'artifacts/p4c-fast-shadow-analysis-01/zone-1-first-battle-scale-0.75'
        packet=json.loads((folder/'0002541.packet.json').read_text(encoding='utf-8'))
        image=Image.open(self.root/'artifacts/p4b-fixed-source/zone-1-first-battle-scale-0.75/0002541.png').convert('RGB')
        self.assertTrue(any('id' not in n for n in packet['mapReview']['nodes']))
        result=inspect_map_actions(image,packet)
        self.assertFalse(result['verified']);self.assertIsNone(result['current'])

if __name__=='__main__':unittest.main()
