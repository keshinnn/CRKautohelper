"""Actual original-video pixels; annotations are assertions only."""
import copy, json, os, sys, unittest
from pathlib import Path
import cv2
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
try:
    from preview_identity import inspect_preview_identity
except ImportError:
    def inspect_preview_identity(*args): return {'verified':False}

class PreviewIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper'))
        cap=cv2.VideoCapture(str(root/'data/video-validation/buAwy1zf2LI/buAwy1zf2LI.mp4'))
        cap.set(cv2.CAP_PROP_POS_FRAMES,2550);ok,raw=cap.read();cap.release()
        if not ok:raise RuntimeError('original video fixture unavailable')
        cls.image=Image.fromarray(cv2.cvtColor(raw,cv2.COLOR_BGR2RGB))
        packet=Path(__file__).resolve().parents[1]/'artifacts/p4a-first-preview/observation.json'
        cls.packet=json.loads(packet.read_text(encoding='utf-8'))['rawPacket']
    def test_original_video_preview_independently_identifies_selected_node(self):
        result=inspect_preview_identity(self.image,self.packet)
        self.assertTrue(result['verified'])
        self.assertEqual(result['selectedNode']['floor'],1)
        self.assertEqual(result['selectedNode']['column'],2)
        self.assertEqual(result['selectedNode']['zone'],1)
    def test_removing_selected_outline_rejects(self):
        import numpy as np
        a=np.array(self.image);hsv=cv2.cvtColor(a,cv2.COLOR_RGB2HSV)
        yy,xx=np.mgrid[:a.shape[0],:a.shape[1]]
        mask=(hsv[:,:,0]>30)&(hsv[:,:,0]<85)&(hsv[:,:,1]>100)&(hsv[:,:,2]>150)&(xx>450)&(xx<630)&(yy>350)&(yy<550)
        a[mask]=[60,60,60]
        import hashlib
        p=copy.deepcopy(self.packet);digest=hashlib.sha256(a.tobytes()).hexdigest()
        p['binding']['pixelSha256']=digest;p['flow']['frameId']=digest[:20];p['mapReview']['frameId']=digest[:20]
        self.assertFalse(inspect_preview_identity(Image.fromarray(a),p)['verified'])
    def test_missing_enter_timer_anchor_or_conflicting_zone_rejects(self):
        for mode in ['enter','timer','anchor','zone']:
            p=copy.deepcopy(self.packet)
            if mode=='enter':p['evidence']=[e for e in p['evidence'] if e['text']!='進入']
            if mode=='timer':p['evidence']=[e for e in p['evidence'] if e['text']!='03:00']
            if mode=='anchor':p['mapReview']['absoluteFloorKnown']=False
            if mode=='zone':p['progress']['conflictingEvidence']=True
            self.assertFalse(inspect_preview_identity(self.image,p)['verified'],mode)
    def test_second_actual_zone_preview_with_correct_but_lower_confidence_ordinary_text(self):
        root=Path(__file__).resolve().parents[1]/'artifacts/p4a-original-source/zone-3'
        p=json.loads((root/'0020229.packet.json').read_text(encoding='utf-8'))
        with Image.open(root/'0020229.png') as image:
            result=inspect_preview_identity(image,p)
        self.assertTrue(result['verified'])
        self.assertEqual(result['selectedNode']['zone'],3)
    def test_selected_outline_recovers_node_missed_by_outer_hex_candidate(self):
        root=Path(__file__).resolve().parents[1]/'artifacts/p4a-original-source/zone-8'
        p=json.loads((root/'0064890.packet.json').read_text(encoding='utf-8'))
        with Image.open(root/'0064890.png') as image:
            result=inspect_preview_identity(image,p)
        self.assertTrue(result['verified'])
        self.assertEqual(result['selectedNode']['floor'],1)
        self.assertEqual(result['selectedNode']['column'],4)
    def test_bounded_original_pixel_ocr_resolves_low_confidence_ordinary_caption(self):
        root=Path(__file__).resolve().parents[1]/'artifacts/p4a-analysis-01/zone-3-first-battle'
        p=json.loads((root/'0020230.packet.json').read_text(encoding='utf-8'))
        image=Path(__file__).resolve().parents[1]/'artifacts/p4a-frozen-original/zone-3-first-battle/0020230.png'
        with Image.open(image) as im:result=inspect_preview_identity(im,p)
        self.assertTrue(result['verified'])
        self.assertGreaterEqual(result['ordinaryEvidence']['refinedScore'],.95)
    def test_subpixel_crop_alignment_does_not_lower_icon_match_requirement(self):
        packet=Path(__file__).resolve().parents[1]/'artifacts/p4a-analysis-01/zone-3-first-battle/0020225.packet.json'
        image=Path(__file__).resolve().parents[1]/'artifacts/p4a-frozen-original/zone-3-first-battle/0020225.png'
        p=json.loads(packet.read_text(encoding='utf-8'))
        with Image.open(image) as im:result=inspect_preview_identity(im,p)
        self.assertTrue(result['verified'])
        self.assertGreaterEqual(result['recoveredNodes'][0]['iconScore'],.9)
    def test_actual_125_percent_unknown_preview_requires_new_pixel_evidence(self):
        root=Path(__file__).resolve().parents[1]
        p=json.loads((root/'artifacts/p4b-analysis-01/zone-3-first-battle-scale-1.25/0020226.packet.json').read_text(encoding='utf-8'))
        self.assertEqual(p['flow']['state'],'UNKNOWN');self.assertIsNone(p['mapReview'])
        with Image.open(root/'artifacts/p4b-fixed-source/zone-3-first-battle-scale-1.25/0020226.png') as im:
            result=inspect_preview_identity(im,p)
        self.assertTrue(result['verified']);self.assertEqual(result['selectedNode']['column'],2)
        self.assertEqual(result['recoveredMapReview']['frameId'],p['binding']['pixelSha256'][:20])
        for missing in ['03:00','進入']:
            altered=copy.deepcopy(p);altered['evidence']=[r for r in altered['evidence'] if r['text']!=missing]
            with Image.open(root/'artifacts/p4b-fixed-source/zone-3-first-battle-scale-1.25/0020226.png') as im:
                self.assertFalse(inspect_preview_identity(im,altered)['verified'])

if __name__=='__main__':unittest.main()
