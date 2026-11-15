import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile
import unittest
from PIL import Image
from research_evidence import make_witness


HERE = Path(__file__).parent


class IndependentResearchEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=HERE)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.image = self.root / 'source.png'
        im = Image.new('RGB', (96, 64))
        im.putdata([(x % 256, (x * 3) % 256, (x * 7) % 256) for x in range(96 * 64)])
        im.save(self.image)
        self.context = dict(frameToken='opaque-current', geometryEpoch='g1', sourceKey='offline-source',
                            atMs=1000, nowMs=1200, imageSha256=hashlib.sha256(self.image.read_bytes()).hexdigest())

    def verify(self, witness, context=None, source=None):
        evidence = self.root / 'witness.json'; evidence.write_text(json.dumps(witness), encoding='utf-8')
        trusted = self.root / 'context.json'; trusted.write_text(json.dumps(context or self.context), encoding='utf-8')
        result = subprocess.run(['node', str(HERE / 'verify_research.cjs'), str(source or self.image),
                                 str(evidence), str(trusted)], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    def test_node_independently_decodes_source_and_reproduces_measurements(self):
        result = self.verify(make_witness(self.image, [10.25, 12.5, 31.5, 24.25], self.context))
        self.assertTrue(result['geometryChecked'])
        self.assertTrue(result['boundaryMeasurementsReproduced'])
        self.assertFalse(result['outerBoundaryVerified'])
        self.assertEqual(result['capabilities'], dict(select=False, confirm=False, dispatch=False))

    def test_changed_source_is_rejected(self):
        witness = make_witness(self.image, [10, 12, 30, 24], self.context)
        Image.new('RGB', (96, 64), 'red').save(self.image)
        self.assertEqual(self.verify(witness)['status'], 'REJECTED')

    def test_tampered_pixel_digest_is_rejected(self):
        witness = make_witness(self.image, [10, 12, 30, 24], self.context)
        witness['sourceRgbSha256'] = '0' * 64
        self.assertEqual(self.verify(witness)['status'], 'REJECTED')

    def test_tampered_sample_is_rejected(self):
        witness = make_witness(self.image, [10, 12, 30, 24], self.context)
        witness['edgeSamples'][0]['gradient'] += 1
        self.assertEqual(self.verify(witness)['status'], 'REJECTED')

    def test_tampered_transform_is_rejected(self):
        witness = make_witness(self.image, [10, 12, 30, 24], self.context)
        witness['sourceToTensor'][0][0] += .01
        self.assertEqual(self.verify(witness)['status'], 'REJECTED')

    def test_changed_geometry_or_source_or_frame_is_rejected(self):
        witness = make_witness(self.image, [10, 12, 30, 24], self.context)
        for key in ('geometryEpoch', 'sourceKey', 'frameToken'):
            ctx = {**self.context, key: 'different'}
            with self.subTest(key=key):
                self.assertEqual(self.verify(witness, ctx)['status'], 'REJECTED')

    def test_expired_context_cannot_be_revived_by_confidence(self):
        witness = make_witness(self.image, [10, 12, 30, 24], self.context)
        witness['confidence'] = 1
        self.assertEqual(self.verify(witness, {**self.context, 'nowMs': 3501})['status'], 'REJECTED')

    def test_model_and_forged_verified_fields_never_grant_authority(self):
        witness = make_witness(self.image, [10, 12, 30, 24], self.context)
        witness.update(confidence=1, verified=True, identityVerified=True)
        result = self.verify(witness)
        self.assertEqual(result['capabilities'], dict(select=False, confirm=False, dispatch=False))
        self.assertFalse(result['identityVerified'])

    def test_out_of_bounds_box_is_rejected_without_clamping(self):
        with self.assertRaisesRegex(ValueError, 'BOX_INVALID'):
            make_witness(self.image, [-1, 0, 30, 24], self.context)

    def test_singular_letterbox_transform_is_not_geometry_evidence(self):
        Image.new('RGB', (3, 5000), 'red').save(self.image)
        self.context['imageSha256'] = hashlib.sha256(self.image.read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValueError, 'GEOMETRY_INVALID'):
            make_witness(self.image, [1, 10, .5, 20], self.context)

    def test_node_rejects_singular_transform_even_with_consistent_samples(self):
        witness = make_witness(self.image, [10, 12, 30, 24], self.context)
        im = Image.new('RGB', (3, 5000), 'red'); im.save(self.image)
        self.context['imageSha256'] = hashlib.sha256(self.image.read_bytes()).hexdigest()
        samples = []
        for side in range(4):
            for i in range(16):
                y = 10 if side == 0 else 30 if side == 1 else math.floor(10 + 20 * (i + .5) / 16)
                samples.append(dict(x=1, y=y, axis='y' if side < 2 else 'x', gradient=0))
        witness.update(sourceImageSha256=self.context['imageSha256'], sourceRgbSha256=hashlib.sha256(im.tobytes()).hexdigest(),
                       sourceSize=[3, 5000], sourceBox=[1, 10, .5, 20], tensorBox=[320, 1.28, 0, 2.56],
                       sourceToTensor=[[0, 0, 320], [0, .128, 0], [0, 0, 1]], edgeSamples=samples)
        self.assertEqual(self.verify(witness)['status'], 'REJECTED')


if __name__ == '__main__':
    unittest.main()
