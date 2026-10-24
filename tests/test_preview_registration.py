import copy,json,sys,unittest
from pathlib import Path
from PIL import Image
import io
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
try:
    from preview_registration import recover_preview_anchor
except ImportError:
    def recover_preview_anchor(*args):return {'verified':False}
try:
    from preview_registration import PreviewAnchorTracker
except ImportError:
    class PreviewAnchorTracker:
        def observe(self,*args):return {'verified':False}

class PreviewRegistrationTests(unittest.TestCase):
    def frame(self,index):
        root=Path(__file__).resolve().parents[1]
        packet=json.loads((root/f'artifacts/p4c-registration-dev-analysis-01/dev-zone4-scroll/{index:07}.packet.json').read_text(encoding='utf-8'))
        return {'png':(root/f'artifacts/p4c-registration-dev-source/{index:07}.png').read_bytes(),'packet':packet,'atMs':round(index/30*1000,6),'sourcePtsMs':round(index/30*1000,6),'windowKey':'offline:dev','geometryVersion':'original'}

    def test_actual_auto_scroll_restores_absolute_floors_from_unique_original_pixels_only(self):
        a,b=self.frame(23730),self.frame(23745);original=copy.deepcopy(b['packet'])
        self.assertTrue(a['packet']['mapReview']['absoluteFloorKnown']);self.assertFalse(b['packet']['mapReview']['absoluteFloorKnown'])
        result=recover_preview_anchor(a,b)
        self.assertTrue(result['verified'])
        self.assertTrue(result['previewOnly']);self.assertFalse(result['actionsExecuted'])
        self.assertEqual(result['sourceImageSha256'],a['packet']['binding']['imageSha256'])
        self.assertEqual(result['mapReview']['floorAnchorSource'],'verified_preview_pixel_registration')
        self.assertGreaterEqual(len(result['registration']['pairs']),5)
        for n in result['mapReview']['nodes']:
            if n.get('column') is not None:self.assertEqual(n['floor'],n['visibleRow'])
        self.assertEqual(b['packet'],original)

    def test_wrong_zone_clock_window_geometry_or_pixel_binding_never_transfer_anchor(self):
        self.assertTrue(recover_preview_anchor(self.frame(23730),self.frame(23745))['verified'])
        for mutate in [lambda b:b.update(atMs=800000),lambda b:b.update(atMs=790000),lambda b:b.update(windowKey='other'),lambda b:b.update(geometryVersion='changed'),lambda b:b['packet']['progress'].update(displayedZone=5),lambda b:b['packet']['progress'].update(score=.8),lambda b:b['packet']['binding'].update(imageSha256='a'*64),lambda b:b['packet']['binding'].update(pixelSha256='a'*64)]:
            a,b=self.frame(23730),self.frame(23745);mutate(b)
            self.assertFalse(recover_preview_anchor(a,b)['verified'])

    def test_current_graph_with_no_unique_node_correspondence_rejects(self):
        a,b=self.frame(23730),self.frame(23745)
        b['packet']['mapReview']['columns']=None
        self.assertFalse(recover_preview_anchor(a,b)['verified'])

    def test_recovered_anchor_still_requires_current_selected_ring_and_enabled_preview(self):
        from preview_identity import inspect_preview_identity
        a,b=self.frame(23730),self.frame(23745);packet=copy.deepcopy(b['packet'])
        packet['v2TrackedMap']=recover_preview_anchor(a,b)
        image=Image.open(io.BytesIO(b['png'])).convert('RGB')
        self.assertFalse(inspect_preview_identity(image,b['packet'])['verified'])
        result=inspect_preview_identity(image,packet)
        self.assertTrue(result['verified'])
        self.assertEqual(result['selectedNode']['zone'],3)
        self.assertEqual(result['selectedNode']['floor'],3)
        self.assertEqual(result['selectedNode']['column'],1)
        packet['v2TrackedMap']['pixelSha256']='a'*64
        self.assertFalse(inspect_preview_identity(image,packet)['verified'])

    def test_stream_uses_oldest_fresh_gate_frame_and_never_crosses_windows(self):
        tracker=PreviewAnchorTracker();a,b,c=self.frame(23724),self.frame(23730),self.frame(23745)
        self.assertFalse(tracker.observe(a)['verified']);self.assertFalse(tracker.observe(b)['verified'])
        result=tracker.observe(c);self.assertTrue(result['verified'])
        self.assertEqual(result['sourceImageSha256'],a['packet']['binding']['imageSha256'])
        c['windowKey']='different';self.assertFalse(tracker.observe(c)['verified'])

if __name__=='__main__':unittest.main()
