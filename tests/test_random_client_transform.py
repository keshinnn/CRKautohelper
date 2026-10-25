import hashlib,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
try:
    from random_client_transform import sample_layout,transform_png,transform_box,inverse_point
except ImportError:
    def sample_layout(*args,**kwargs):return None

class RandomClientTransformTests(unittest.TestCase):
    def test_random_virtual_clients_stay_in_the_design_test_range(self):
        for size in [[960,720],[1440,1080],[1280,720]]:
            for seed in range(30):
                layout=sample_layout(size,[[10,10,size[0]-20,size[1]-20]],seed)
                w,h=layout['outputSize']
                self.assertGreaterEqual(w,960);self.assertLessEqual(w,2560)
                self.assertGreaterEqual(h,540);self.assertLessEqual(h,1440)
                self.assertGreaterEqual(w/h,1.25);self.assertLessEqual(w/h,2.5)

    def test_reproducible_nonfixed_sizes_aspects_and_crops_preserve_required_boxes(self):
        required=[[18,20,300,200],[610,500,120,120],[1000,250,420,680]]
        layouts=[sample_layout([1440,1080],required,seed) for seed in [119,120,121]]
        self.assertTrue(all(layouts),'seeded random layouts must exist')
        self.assertEqual(layouts[0],sample_layout([1440,1080],required,119))
        self.assertEqual(len({tuple(x['outputSize']) for x in layouts}),3)
        for layout in layouts:
            self.assertNotEqual(layout['sx'],layout['sy'])
            self.assertGreater(sum(layout['cropMargins']),0)
            for box in required:
                b=transform_box(box,layout);w,h=layout['outputSize']
                self.assertGreaterEqual(min(b[:2]),0);self.assertLessEqual(b[0]+b[2],w);self.assertLessEqual(b[1]+b[3],h)
                point=[box[0]+box[2]/2,box[1]+box[3]/2]
                mapped=transform_box([*point,1,1],layout)
                actual=inverse_point(mapped[:2],layout)
                for a,b in zip(actual,point):self.assertAlmostEqual(a,b,places=8)

    def test_actual_new_png_binds_bytes_dimensions_and_does_not_expose_old_packet(self):
        root=Path(__file__).resolve().parents[1];source=root/'artifacts/p4a-native/0002550.png'
        layout=sample_layout([1440,1080],[[18,20,1400,900]],881)
        self.assertIsNotNone(layout)
        with tempfile.TemporaryDirectory(prefix='crk-random-',dir=root/'artifacts') as folder:
            one=transform_png(source,layout,Path(folder)/'one.png');two=transform_png(source,layout,Path(folder)/'two.png')
            self.assertEqual(one['sha256'],two['sha256'])
            self.assertNotEqual(one['sha256'],hashlib.sha256(source.read_bytes()).hexdigest())
            with Image.open(one['image']) as image:self.assertEqual(list(image.size),layout['outputSize'])
            self.assertNotIn('packet',one)
            with self.assertRaises(FileExistsError):transform_png(source,layout,Path(folder)/'one.png')

    def test_rendered_pixels_bind_the_same_input_bytes_that_were_hashed(self):
        import io
        from unittest.mock import patch
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix='crk-random-binding-',dir=root/'artifacts') as folder:
            source=Path(folder)/'source.png';output=Path(folder)/'output.png'
            Image.new('RGB',(80,60),(255,0,0)).save(source)
            original=source.read_bytes();replacement=io.BytesIO();Image.new('RGB',(80,60),(0,0,255)).save(replacement,format='PNG')
            read=Path.read_bytes
            def changed_after_read(path):
                raw=read(path)
                if path==source:source.write_bytes(replacement.getvalue())
                return raw
            layout=sample_layout([80,60],[[4,4,72,52]],71)
            with patch.object(Path,'read_bytes',changed_after_read):result=transform_png(source,layout,output)
            self.assertEqual(result['transform']['inputSha256'],hashlib.sha256(original).hexdigest())
            with Image.open(output) as image:self.assertEqual(image.getpixel((image.width//2,image.height//2)),(255,0,0))

    def test_outside_or_empty_anchor_annotations_are_rejected(self):
        for required in [[],[[1400,1000,100,100]],[[20,20,-5,10]],[[0,0,1440,1080]]]:
            with self.assertRaises(ValueError):sample_layout([1440,1080],required,3)

if __name__=='__main__':unittest.main()
