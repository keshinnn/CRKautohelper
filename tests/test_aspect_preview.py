"""Real distorted preview pixels, independent of pending click intent."""
import copy, hashlib, io, json, sys, unittest
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from bounded_ocr import BoundedOCRRuntime
from preview_identity import inspect_preview_identity
from map_aspect import recover_map_aspect

class AspectPreviewTests(unittest.TestCase):
    def fixture(self,case_index=0):
        m=json.loads((ROOT/'artifacts/p4c-random-pilot-analysis-02/manifest.json').read_text(encoding='utf-8'))
        f=m['cases'][case_index]['frames'][-1]
        return Image.open(f['image']).convert('RGB'),json.loads(Path(f['packet']).read_text(encoding='utf-8'))

    def test_actual_anisotropic_preview_recovers_selected_node_using_vertical_spacing(self):
        image,p=self.fixture();before=copy.deepcopy(p)
        with BoundedOCRRuntime(960):result=inspect_preview_identity(image,p)
        self.assertTrue(result['verified'])
        self.assertEqual([result['selectedNode'][k] for k in ['zone','floor','column']],[1,1,2])
        self.assertGreaterEqual(result['recoveredNodes'][0]['iconScore'],.9)
        self.assertEqual(p,before)

    def test_actual_post_resize_preview_sizes_icon_from_same_frame_orange_circle(self):
        image,p=self.fixture(2)
        with BoundedOCRRuntime(960):result=inspect_preview_identity(image,p)
        self.assertTrue(result['verified'])
        self.assertEqual([result['selectedNode'][k] for k in ['zone','floor','column']],[1,1,2])
        self.assertGreaterEqual(result['recoveredNodes'][0]['iconScore'],.9)
        self.assertEqual(result['recoveredNodes'][0]['iconSizeEvidence']['method'],'same_frame_orange_circle_and_original_template_extent')

    def test_erased_selected_green_pixels_with_fresh_geometry_cannot_confirm(self):
        image,p=self.fixture();a=np.array(image);hsv=cv2.cvtColor(a,cv2.COLOR_RGB2HSV)
        # Erase all selected-outline green, including unrelated green controls;
        # refresh every image binding and derive geometry again from new pixels.
        a[(hsv[:,:,0]>30)&(hsv[:,:,0]<85)&(hsv[:,:,1]>100)&(hsv[:,:,2]>150)]=[60,60,60]
        image=Image.fromarray(a);pixel=hashlib.sha256(a.tobytes()).hexdigest()
        raw=io.BytesIO();image.save(raw,format='PNG')
        p['binding']['imageSha256']=hashlib.sha256(raw.getvalue()).hexdigest()
        p['binding']['pixelSha256']=pixel;p['flow']['frameId']=pixel[:20]
        p['mapReview']=copy.deepcopy(p['v2OriginalMapReview']);p['mapReview']['frameId']=pixel[:20]
        p['mapReview']=recover_map_aspect(image,p);p.pop('v2TrackedMap',None)
        with BoundedOCRRuntime(960):result=inspect_preview_identity(image,p)
        self.assertFalse(result['verified'])

if __name__=='__main__':unittest.main()
