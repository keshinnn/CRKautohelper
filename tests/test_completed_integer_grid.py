import copy,hashlib,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
import cv2,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from map_action_evidence import _neutral_overlay_check,inspect_map_actions


class CompletedIntegerGridTests(unittest.TestCase):
    def sample(self):
        a=json.loads((ROOT/'artifacts/exploration-20261102-01/audit-summary.json').read_text(encoding='utf-8'))
        r=next(r for r in a['rows'] if r['number']==60)
        p=json.loads(Path(r['criticalPacket']).read_text(encoding='utf-8'))
        im=Image.open(r['criticalImage']).convert('RGB')
        return im,p
    def patch_pixels(self):
        im,p=self.sample();n=next(n for n in p['mapReview']['nodes'] if n['completed'])
        x,y,w,h=n['box'];return np.asarray(im.crop((x,y,x+w,y+h)).resize((58,58)))[12:46,12:46]
    def test_actual_odd_integer_alignment_clears_two_original_point_eight_gates(self):
        q=self.patch_pixels()
        with patch.object(cv2,'warpAffine',wraps=cv2.warpAffine) as calls:
            proof=_neutral_overlay_check(q,complete_grid=True)
        self.assertIsNotNone(proof)
        self.assertEqual(proof['minimumTemplateIoU'],.8)
        self.assertEqual(len(set(proof['saturationLevels'])),2)
        self.assertGreaterEqual(min(proof['maskIoUs']),.8)
        self.assertTrue(any(abs(v)==1 for v in proof['alignmentPx']))
        for call in calls.call_args_list:
            matrix=call.args[1];self.assertLessEqual(abs(matrix[0,2]),2);self.assertLessEqual(abs(matrix[1,2]),2)
    def test_actual_current_path_is_remeasured_without_intent_or_previous_frame(self):
        im,p=self.sample();before=copy.deepcopy(p)
        result=inspect_map_actions(im,p)
        self.assertIsNotNone(result['current'])
        self.assertEqual(result['current']['completedPath'],['exit-0','visible-1-2'])
        self.assertEqual(p,before)
    def test_blank_patch_never_supplies_a_completed_check(self):
        self.assertIsNone(_neutral_overlay_check(np.full((34,34,3),55,dtype=np.uint8),complete_grid=True))
    def test_geometry_phase_keeps_the_original_grid_decision(self):
        self.assertIsNone(_neutral_overlay_check(self.patch_pixels()))


if __name__=='__main__':unittest.main()
