import json, subprocess, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'ml'))

class GeometryContractTests(unittest.TestCase):
    def test_real_aspect_producer_declares_coordinate_spaces_and_preserves_measurement_precision(self):
        from PIL import Image
        sys.path.insert(1,'F:/CRK helper/ml')
        from map_aspect import recover_map_aspect
        root=Path(__file__).resolve().parents[1]
        m=json.loads((root/'artifacts/p4c-random-development-60-run-19/dev-primary-zone6-floor1-col2-random-fixed/analysis/manifest.json').read_text(encoding='utf-8'))
        f=m['cases'][0]['frames'][5];p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
        p['mapReview']=p['v2OriginalMapReview']
        actual=recover_map_aspect(Image.open(f['image']).convert('RGB'),p)
        self.assertIn('coordinateContract',actual.get('aspectRectification',{}))
        from geometry_contract import resize_box
        target=f['size'];source=actual['aspectRectification']['rectifiedInputSize']
        for n in actual['nodes']:
            self.assertEqual(n['box'],resize_box(n['analysisBox'],source,target))

    def test_rectified_to_source_uses_independent_endpoint_scales_without_rounding(self):
        from geometry_contract import resize_box, resize_point
        self.assertEqual(resize_box([0, 7, 960, 533], [960, 540], [1921, 1081]), [0, 1081*7/540, 1921, 1081-1081*7/540])
        self.assertEqual(resize_point([480, 270], [960, 540], [1921, 1081]), [960.5, 540.5])

    def test_real_raster_endpoint_stays_on_bottom_and_outside_is_not_clamped(self):
        from geometry_contract import resize_box
        self.assertEqual(sum(resize_box([0, 352, 20, 1], [960, 353], [1961, 721])[1::2]), 721)
        with self.assertRaises(ValueError): resize_box([0, 352, 20, 1.000001], [960,353], [1961,721])

    def test_half_up_raster_rounding_agrees_with_javascript_at_ties(self):
        from geometry_contract import raster_round
        self.assertEqual([raster_round(v) for v in [2.5,3.5,540.5]], [3,4,541])

    def test_geometry_certificate_records_actual_spaces_and_binds_capture(self):
        from geometry_contract import geometry_certificate
        binding={'frameId':'a'*32,'imageSha256':'b'*64,'pixelSha256':'c'*64,'width':1961,'height':721}
        g=geometry_certificate(binding,[1500,721],[960,461])
        self.assertEqual(g['spaces'], {'source':[1961,721],'client':[1961,721],'rectified':[1500,721],'analysis':[960,461]})
        self.assertEqual(g['sourceCaptureFrameId'],binding['frameId'])
        self.assertEqual(g['rounding'],'endpoints_float64_raster_half_up')

if __name__=='__main__': unittest.main()
