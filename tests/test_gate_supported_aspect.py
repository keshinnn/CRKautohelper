"""A real gate can supplement two independently verified battle circles."""
import json,sys,unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from map_aspect import estimate_pixel_aspect,recover_map_aspect
from bounded_ocr import BoundedOCRRuntime
from progress_evidence import ProgressRuntime
from english_scene import EnglishSceneRuntime,semantic_state

class GateSupportedAspectTests(unittest.TestCase):
    def test_actual_resized_map_recovers_verified_gate_then_completed_predecessor(self):
        from map_action_evidence import inspect_map_actions
        m=json.loads((ROOT/'artifacts/p4c-random-development-60-run-10/dev-primary-zone2-floor2-col3-higher-random-pre-change/analysis/manifest.json').read_text(encoding='utf-8'))
        for f in m['cases'][0]['frames'][1:3]:
            p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
            with Image.open(f['image']) as image:
                p['mapReview']=recover_map_aspect(image,p);actions=inspect_map_actions(image,p)
            self.assertTrue(p['mapReview']['absoluteFloorKnown'])
            gate=next(n for n in p['mapReview']['nodes'] if n['type']=='exit')
            self.assertGreaterEqual(gate['gateProposal']['geometryEvidence']['innerScore'],.9)
            self.assertEqual(actions['current']['completedPath'],['exit-0','visible-1-3'])

    def test_near_native_map_recovers_actual_missing_completed_node_without_rectification(self):
        from map_action_evidence import inspect_map_actions
        m=json.loads((ROOT/'artifacts/p4c-random-negative-fresh-run-30-01/neg-native-completed-node-random-2/analysis/manifest.json').read_text(encoding='utf-8'))
        for f in m['cases'][0]['frames']:
            p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
            with Image.open(f['image']) as image:
                p['mapReview']=recover_map_aspect(image,p);actions=inspect_map_actions(image,p)
            self.assertNotIn('aspectRectification',p['mapReview'])
            node=next((n for n in p['mapReview']['nodes'] if n.get('floor')==1 and n.get('column')==3),None)
            self.assertIsNotNone(node)
            self.assertTrue(node['completed'])
            self.assertGreaterEqual(node['checkProposal']['checkMaskIoU'],.8)
            self.assertEqual(actions['current']['completedPath'],['exit-0','visible-1-3'])

    def test_orange_consensus_still_recovers_a_missing_verified_gate_candidate(self):
        m=json.loads((ROOT/'artifacts/p4c-random-negative-fresh-run-30-02/neg-native-heal-not-battle-random-1/analysis/manifest.json').read_text(encoding='utf-8'))
        for f in m['cases'][0]['frames']:
            p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
            with Image.open(f['image']) as image:p['mapReview']=recover_map_aspect(image,p)
            self.assertTrue(p['mapReview']['absoluteFloorKnown'])
            self.assertEqual(next(n for n in p['mapReview']['nodes'] if n.get('floor')==1 and n.get('column')==2)['type'],'heal')

    def test_actual_large_node_connection_uses_reference_geometry_without_lowering_support(self):
        m=json.loads((ROOT/'artifacts/p4c-random-development-60-run-12/dev-primary-zone2-floor2-col3-higher-random-post-change/analysis/manifest.json').read_text(encoding='utf-8'))
        for f in m['cases'][0]['frames'][:2]:
            p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
            with Image.open(f['image']) as image:r=recover_map_aspect(image,p)
            links=[e for e in r['edges'] if e['from']=='visible-1-3' and e['to']=='visible-2-3']
            self.assertEqual(len(links),1)
            self.assertGreaterEqual(links[0]['pixel_support'],.85)
            if 'lineReference' in links[0]:self.assertEqual(links[0]['lineReference']['referenceNodeSize'],58)

    def fixtures(self):
        return json.loads((ROOT/'artifacts/p4c-random-development-60-run-09/dev-primary-zone2-floor2-col3-higher-random-fixed/analysis/manifest.json').read_text(encoding='utf-8'))['cases'][0]['frames'][:2]

    def test_actual_two_battle_circles_and_gate_supply_three_pixel_anchors(self):
        for f in self.fixtures():
            p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
            with Image.open(f['image']) as image:
                calibration=estimate_pixel_aspect(image)
                self.assertIsNotNone(calibration)
                self.assertEqual(calibration['method'],'original_pixel_orange_and_gate_unique_aspect_consensus')
                kinds=[calibration['candidates'][i]['circleKind'] for i in calibration['consensus']]
                self.assertEqual(kinds.count('orange_battle'),2);self.assertEqual(kinds.count('cyan_gate'),1)
                result=recover_map_aspect(image,p)
            self.assertTrue(result['absoluteFloorKnown'])
            self.assertEqual(len([n for n in result['nodes'] if n.get('floor')==2 and n.get('column')==3]),1)

    def test_plain_cyan_without_arrow_does_not_replace_a_gate(self):
        f=self.fixtures()[0]
        with Image.open(f['image']) as image:a=np.array(image.convert('RGB'))
        region=a[171:230,648:758]
        white=(region.min(2)>=170)&((region.max(2).astype(float)-region.min(2))<=80)
        self.assertGreater(int(white.sum()),100);region[white]=[35,160,190]
        self.assertIsNone(estimate_pixel_aspect(Image.fromarray(a)))

    def test_actual_stretched_header_uses_pixel_aspect_for_horizontal_indent(self):
        for f in self.fixtures():
            p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
            with Image.open(f['image']) as image,ProgressRuntime(),BoundedOCRRuntime(960) as runtime,EnglishSceneRuntime():
                rows=runtime._reread_map_context(image,p['evidence']);state=semantic_state(rows)
            self.assertEqual(state['state'],'MAP');self.assertGreaterEqual(state['confidence'],.9)
            fresh=[r for r in rows if r.get('source')=='map_context_original_crop']
            self.assertEqual({r['contextKind'] for r in fresh},{'season','timer'})
            self.assertTrue(all(r['positionEvidence']['pixelAspect']>1.8 for r in fresh))

    def test_stretched_header_does_not_guess_an_erased_timer(self):
        from PIL import ImageDraw
        f=self.fixtures()[0];p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
        with Image.open(f['image']) as original:image=original.convert('RGB')
        ImageDraw.Draw(image).rectangle((50,58,308,83),fill=(30,30,60))
        with ProgressRuntime(),BoundedOCRRuntime(960) as runtime,EnglishSceneRuntime():
            rows=runtime._reread_map_context(image,p['evidence']);state=semantic_state(rows)
        self.assertFalse(state['state']=='MAP' and state['confidence']>=.9)

if __name__=='__main__':unittest.main()
