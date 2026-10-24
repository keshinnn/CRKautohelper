import copy,hashlib,json,sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw
sys.path[:0]=['F:/CRK helper/ml',str(Path(__file__).resolve().parents[1]/'ml')]
from map_action_evidence import inspect_map_actions

class CurrentPositionEvidenceTests(unittest.TestCase):
    def source(self):
        root=Path(__file__).resolve().parents[1]
        packet=json.loads((root/'artifacts/p4c-L0-native-dev-analysis-02/dev-L0-zone6-floor1-col2-resume-1781/0053406.packet.json').read_text(encoding='utf-8'))
        image=Image.open(root/'artifacts/p4c-native-timing-01/L0ktY5qUppI-1781/0053406.png').convert('RGB')
        return image,packet

    def test_actual_unique_progress_label_ring_and_triangle_prove_current_without_header_floor(self):
        image,p=self.source();self.assertIsNone(p['progress']['lastEnteredFloor'])
        result=inspect_map_actions(image,p)
        self.assertTrue(result['current']['verified']);self.assertTrue(result['current']['inProgress'])
        self.assertEqual(result['current']['nodeId'],'visible-1-2')
        self.assertEqual(result['current']['floor'],1)
        self.assertIsNone(p['progress']['lastEnteredFloor'])

    def test_missing_or_duplicated_progress_label_rejects_current(self):
        for mode in ['missing','duplicate']:
            image,p=self.source();row=next(r for r in p['evidence'] if r['text']=='進行中')
            if mode=='missing':p['evidence'].remove(row)
            else:p['evidence'].append(copy.deepcopy(row))
            self.assertIsNone(inspect_map_actions(image,p)['current'])

    def test_erased_triangle_with_fresh_pixel_binding_cannot_prove_current(self):
        image,p=self.source();ImageDraw.Draw(image).rectangle((430,169,470,194),fill='black')
        digest=hashlib.sha256(image.tobytes()).hexdigest();p['binding']['pixelSha256']=digest;p['mapReview']['frameId']=digest[:20]
        self.assertIsNone(inspect_map_actions(image,p)['current'])

    def test_erased_outer_ring_with_triangle_label_and_orange_fill_still_rejects(self):
        import numpy as np
        image,p=self.source();rgb=np.array(image);yy,xx=np.mgrid[:image.height,:image.width]
        radius=np.maximum(abs((xx-450)/37),abs((yy-232)/37))
        rgb[(radius>.8)&(radius<1.15)]=0
        image=Image.fromarray(rgb);digest=hashlib.sha256(image.tobytes()).hexdigest()
        p['binding']['pixelSha256']=digest;p['mapReview']['frameId']=digest[:20]
        result=inspect_map_actions(image,p)
        self.assertTrue(result['nodes']['visible-1-2']['available'])
        self.assertIsNone(result['current'])

    def test_missing_absolute_anchor_or_wrong_pixel_binding_rejects_current(self):
        for mode in ['anchor','pixels']:
            image,p=self.source()
            if mode=='anchor':p['mapReview']['absoluteFloorKnown']=False
            else:p['binding']['pixelSha256']='a'*64
            self.assertIsNone(inspect_map_actions(image,p)['current'])

if __name__=='__main__':unittest.main()
