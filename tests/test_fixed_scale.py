import hashlib,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
try:
    from scale_cases import scale_png
except ImportError:
    def scale_png(*args):return {'size':None}

class FixedScaleTests(unittest.TestCase):
    def test_scale_one_preserves_actual_png_bytes_and_fixed_sizes_use_real_output(self):
        root=Path(__file__).resolve().parents[1];source=root/'artifacts/p4a-native/0002550.png'
        with tempfile.TemporaryDirectory(prefix='crk-scale-',dir=root/'artifacts') as folder:
            for scale,size in [(1,[1440,1080]),(.75,[1080,810]),(1.25,[1800,1350])]:
                out=Path(folder)/f'{scale}.png';result=scale_png(source,scale,out)
                self.assertEqual(result['size'],size)
                with Image.open(out) as image:self.assertEqual(list(image.size),size)
                self.assertEqual(result['sha256'],hashlib.sha256(out.read_bytes()).hexdigest())
                if scale==1:self.assertEqual(source.read_bytes(),out.read_bytes())
                else:self.assertNotEqual(source.read_bytes(),out.read_bytes())

if __name__=='__main__':unittest.main()
