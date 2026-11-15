import hashlib,json,sys,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from map_aspect import _gate_pixel_geometry,estimate_pixel_aspect


class GateReferenceFamilyTests(unittest.TestCase):
    def sample(self,number):
        base=ROOT/'artifacts/concentrated-repair-20261103-01'
        a=json.loads((base/'geometry-diagnosis.json').read_text(encoding='utf-8'))
        row=next(r for r in a if r['number']==number)
        probe=json.loads((base/'gate-reference-probe.json').read_text())
        gates=next(r for r in probe if r['number']==number)['gateCandidates']
        candidate=next(r for r in gates if any(t.get('name')=='node-b-exit.png' and t.get('score',0)>.8 for t in r['references']))
        im=Image.open(row['image']).convert('RGB')
        return im,candidate['searchBox']
    def test_existing_secondary_gate_family_supplies_unchanged_point_nine_proof(self):
        im,box=self.sample(58);result=_gate_pixel_geometry(im,box,Path('F:/CRK helper'),hashlib.sha256(im.tobytes()).hexdigest())
        self.assertIsNotNone(result)
        _,p=result;self.assertGreaterEqual(p['innerScore'],.9)
        self.assertEqual(p['templateImageSha256'],hashlib.sha256(Path('F:/CRK helper/data/map/node-b-exit.png').read_bytes()).hexdigest())
    def test_actual_secondary_family_restores_three_independent_aspect_peers(self):
        im,_=self.sample(58);p=estimate_pixel_aspect(im)
        self.assertIsNotNone(p);self.assertGreaterEqual(len(p['consensus']),3)
        kinds=[p['candidates'][i].get('circleKind') for i in p['consensus']]
        self.assertGreaterEqual(kinds.count('orange_battle'),2);self.assertEqual(kinds.count('cyan_gate'),1)
    def test_subthreshold_secondary_reference_still_rejects(self):
        im,box=self.sample(59)
        self.assertIsNone(_gate_pixel_geometry(im,box,Path('F:/CRK helper'),hashlib.sha256(im.tobytes()).hexdigest()))


if __name__=='__main__':unittest.main()
