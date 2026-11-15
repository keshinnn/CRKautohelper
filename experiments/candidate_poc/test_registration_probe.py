"""Research probe: provenance/time failures never become action authority."""
import unittest
import hashlib
import tempfile
from pathlib import Path
from PIL import Image
import registration_probe as p


class RegistrationProbeTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(p, 'registration probe missing')
        self.a = dict(sourceKey='video', geometryVersion='g', atMs=1000,
                      imageSha256='a'*64, sourceSize=[100, 80])
        self.b = dict(self.a, atMs=1200, imageSha256='b'*64)

    def test_ttl_is_not_extended_for_research(self):
        self.b['atMs'] = 3501
        self.assertIn('PAIR_AGE_EXCEEDED', p.pair_blockers(self.a, self.b))

    def test_source_and_geometry_are_not_interchangeable(self):
        self.b.update(sourceKey='other', geometryVersion='other')
        self.assertEqual(set(p.pair_blockers(self.a, self.b)),
                         {'SOURCE_CHANGED', 'GEOMETRY_CHANGED'})

    def test_duplicate_and_future_reference_rejected(self):
        self.b.update(atMs=900, imageSha256=self.a['imageSha256'])
        self.assertEqual(set(p.pair_blockers(self.a, self.b)),
                         {'NONCAUSAL_PAIR', 'DUPLICATE_IMAGE'})

    def test_box_error_is_measurement_not_correction(self):
        r = p.box_error([1, 2, 9, 8], [0, 0, 10, 10])
        self.assertAlmostEqual(r['widthRatio'], .9)
        self.assertEqual(r['centerDelta'], [.5, 1.0])
        self.assertFalse(r['correctionApplied'])

    def test_even_good_pixel_fit_is_not_authority(self):
        r = p.non_authority_result(dict(pixelFitWithinLegacyBounds=True))
        self.assertFalse(r['registrationVerified'])
        self.assertFalse(r['identityVerified'])
        self.assertEqual(r['capabilities'], dict(select=False, confirm=False, dispatch=False))

    def test_different_png_encoding_does_not_make_independent_pixels(self):
        self.a['pixelSha256'] = 'c'*64
        self.b['pixelSha256'] = 'c'*64
        self.assertIn('DUPLICATE_PIXELS', p.pair_blockers(self.a, self.b))

    def images(self):
        tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(tmp.cleanup)
        paths = [Path(tmp.name)/name for name in ['a.png', 'b.png']]
        im = Image.new('RGB', (100, 80), (10, 20, 30))
        for level, path in zip([0, 9], paths):
            im.save(path, compress_level=level)
        sources = [dict(self.a if i == 0 else self.b, image=str(path),
                        imageSha256=hashlib.sha256(path.read_bytes()).hexdigest())
                   for i, path in enumerate(paths)]
        predictions = [dict(imageSha256=s['imageSha256'], boxes=[]) for s in sources]
        return sources, predictions

    def test_real_decoder_rejects_reencoded_duplicate_without_supplied_digest(self):
        sources, predictions = self.images()
        self.assertNotEqual(sources[0]['imageSha256'], sources[1]['imageSha256'])
        r = p.pixel_probe(*sources, *predictions)
        self.assertIn('DUPLICATE_PIXELS', r['pairBlockers'])
        self.assertFalse(r['registrationVerified'])

    def test_real_decoder_rejects_wrong_source_hash(self):
        sources, predictions = self.images()
        sources[0]['imageSha256'] = 'f'*64
        with self.assertRaisesRegex(ValueError, 'SOURCE_CHANGED'):
            p.pixel_probe(*sources, *predictions)

    def test_real_decoder_rejects_wrong_source_size_and_pixel_digest(self):
        sources, predictions = self.images()
        sources[0]['sourceSize'] = [1, 1]
        with self.assertRaisesRegex(ValueError, 'SIZE_CHANGED'):
            p.pixel_probe(*sources, *predictions)
        sources[0]['sourceSize'] = [100, 80]
        sources[0]['pixelSha256'] = 'f'*64
        with self.assertRaisesRegex(ValueError, 'SOURCE_PIXELS_CHANGED'):
            p.pixel_probe(*sources, *predictions)


if __name__ == '__main__':
    unittest.main()
