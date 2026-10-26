import json,sys,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']

class MapObserverGeometryTests(unittest.TestCase):
    def test_actual_model_boxes_project_before_legacy_decimal_rounding(self):
        from map_observer import inspect_map
        m=json.loads((ROOT/'artifacts/convergence-20261026/random39-final-01/manifest.json').read_text(encoding='utf-8'))
        c=next(c for c in m['cases'] if c['id']=='dev-primary-zone4-floor2-col3-random-pre-change')
        f=c['frames'][5];im=Image.open(f['image']).convert('RGB').resize((1364,1018),Image.Resampling.LANCZOS)
        result=inspect_map(im,Path('F:/CRK helper/data/map'),read_header=False)
        n=next(n for n in result['nodes'] if n['id']=='visible-1-2')
        self.assertEqual(n['detectorGeometry']['box'],[414,323,74,74])
        self.assertAlmostEqual(n['box'][0],588.225,places=10)
        self.assertAlmostEqual(n['center'][0],640.7958333333333,places=10)
        for n in result['nodes']:
            for i in [0,1]:self.assertAlmostEqual(n['center'][i],n['box'][i]+n['box'][i+2]/2,places=9)

if __name__=='__main__':unittest.main()
