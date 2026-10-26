import hashlib,sys,tempfile,types,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
from frame_intermediates import FrameIntermediates

class FrameIntermediatesTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/'artifacts');self.folder=Path(self.temp.name);(self.folder/'node-test.png').write_bytes(b'template');self.calls=0
        def detect(image,folder,**kw):self.calls+=1;return [{'box':[1,2,3,4],'score':.7,'template':'node-test.png'}]
        self.original=detect;self.owner=types.SimpleNamespace(node_candidates=detect);self.image=Image.new('RGB',(16,12),'red')
    def tearDown(self):self.temp.cleanup()
    def scope(self,source='a'*32):return FrameIntermediates(source,'b'*64,[16,12],owner=self.owner)
    def test_same_frame_exact_input_reuses_unmodified_raw_measurement(self):
        with self.scope() as f:
            first=self.owner.node_candidates(self.image,self.folder);first[0]['box'][0]=999;first[0]['type']='heal'
            second=self.owner.node_candidates(self.image.copy(),self.folder)
            self.assertEqual(second,[{'box':[1,2,3,4],'score':.7,'template':'node-test.png'}]);self.assertEqual(self.calls,1)
            self.assertEqual(f.summary()['hits'],1);self.assertEqual(f.summary()['misses'],1)
        self.assertIs(self.owner.node_candidates,self.original)
    def test_changed_pixels_size_and_parameters_do_not_share(self):
        with self.scope():
            self.owner.node_candidates(self.image,self.folder)
            self.owner.node_candidates(Image.new('RGB',(16,12),'blue'),self.folder)
            self.owner.node_candidates(self.image.resize((17,12)),self.folder)
            self.owner.node_candidates(self.image,self.folder,workers=1)
        self.assertEqual(self.calls,4)
    def test_next_frame_recomputes_even_identical_pixels(self):
        for key in ['a'*32,'c'*32]:
            with self.scope(key):self.owner.node_candidates(self.image,self.folder)
        self.assertEqual(self.calls,2)
    def test_template_change_inside_frame_refuses_stale_measurement(self):
        with self.scope():
            self.owner.node_candidates(self.image,self.folder);(self.folder/'node-test.png').write_bytes(b'changed!')
            with self.assertRaisesRegex(ValueError,'FRAME_ASSETS_CHANGED'):self.owner.node_candidates(self.image,self.folder)
        self.assertEqual(self.calls,1)
    def test_exception_restores_backend_and_empty_result_is_not_truthy_authority(self):
        with self.assertRaisesRegex(RuntimeError,'stop'):
            with self.scope():self.owner.node_candidates(self.image,self.folder);raise RuntimeError('stop')
        self.assertIs(self.owner.node_candidates,self.original)
        self.owner.node_candidates=lambda *a,**k:[]
        with self.scope():self.assertEqual(self.owner.node_candidates(self.image,self.folder),[]);self.assertEqual(self.owner.node_candidates(self.image,self.folder),[])
    def test_changed_template_configuration_requires_restart_across_frames(self):
        with self.scope():self.owner.node_candidates(self.image,self.folder)
        (self.folder/'node-test.png').write_bytes(b'changed!')
        with self.scope('c'*32):
            with self.assertRaisesRegex(ValueError,'FRAME_ASSETS_CHANGED'):self.owner.node_candidates(self.image,self.folder)
        self.assertEqual(self.calls,1)

    def test_opencv_configuration_change_does_not_reuse_previous_result(self):
        import cv2
        original=cv2.useOptimized()
        try:
            with self.scope():
                self.owner.node_candidates(self.image,self.folder);cv2.setUseOptimized(not original)
                self.owner.node_candidates(self.image,self.folder)
            self.assertEqual(self.calls,2)
        finally:cv2.setUseOptimized(original)

    def test_nested_frames_cannot_inherit_outer_measurements(self):
        with self.scope():
            with self.assertRaisesRegex(RuntimeError,'FRAME_CONTEXT_NESTED'):
                with self.scope('c'*32):pass

if __name__=='__main__':unittest.main()
