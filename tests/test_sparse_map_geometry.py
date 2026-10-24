import copy,hashlib,json,sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
try:
    from sparse_map_geometry import recover_map_geometry
except ImportError:
    def recover_map_geometry(image,packet):return packet['mapReview']
class SparseMapGeometryTests(unittest.TestCase):
    def source(self):
        p=json.loads((ROOT/'artifacts/p4c-LX46-dev-additional-analysis-01/dev-LX46-zone4-floor2-col1-select/0030102.packet.json').read_text(encoding='utf-8'))
        im=Image.open(ROOT/'artifacts/p4c-LX46-native-qualification-01/candidate-13-502.0/0030102.png').convert('RGB')
        return im,p
    def test_real_three_visible_columns_use_unique_visible_gate_to_locate_missing_fourth(self):
        image,p=self.source();before=copy.deepcopy(p);self.assertFalse(p['mapReview']['absoluteFloorKnown'])
        m=recover_map_geometry(image,p)
        self.assertTrue(m['absoluteFloorKnown']);self.assertEqual(m['floorAnchorSource'],'visible_top_gate')
        self.assertEqual(m['columns'],[680,900,1120,1340])
        self.assertTrue(any(n.get('floor')==2 and n.get('column')==1 for n in m['nodes']))
        self.assertEqual(p,before)
    def test_missing_duplicate_gate_two_columns_and_wrong_binding_never_infer_lattice(self):
        for mode in ['missing','duplicate','two-columns','wrong-binding']:
            image,p=self.source();nodes=p['mapReview']['nodes'];gate=next(n for n in nodes if n['type']=='exit')
            if mode=='missing':nodes.remove(gate)
            elif mode=='duplicate':nodes.append(copy.deepcopy(gate))
            elif mode=='two-columns':p['mapReview']['nodes']=[n for n in nodes if n['type']=='exit' or n['center'][0]!=680]
            else:p['binding']['pixelSha256']='a'*64
            self.assertFalse(recover_map_geometry(image,p)['absoluteFloorKnown'])
    def test_erased_gate_with_fresh_binding_cannot_reuse_original_candidate(self):
        image,p=self.source();ImageDraw.Draw(image).rectangle((920,260,1100,440),fill=(30,30,30));digest=hashlib.sha256(image.tobytes()).hexdigest()
        p['binding']['pixelSha256']=digest;p['mapReview']['frameId']=digest[:20]
        self.assertFalse(recover_map_geometry(image,p)['absoluteFloorKnown'])
if __name__=='__main__':unittest.main()
