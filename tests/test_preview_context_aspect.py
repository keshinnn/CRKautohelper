import copy,hashlib,io,json,math,sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from bounded_ocr import BoundedOCRRuntime
from preview_context import inspect_preview_context
from geometry_contract import geometry_certificate,analysis_raster

class PreviewContextAspectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m=json.loads((ROOT/'artifacts/development-20261027-medium-01/case-40/run-03/manifest.json').read_text(encoding='utf-8'))
        cls.frames={f['frameIndex']:f for f in m['cases'][0]['frames']}
    def source(self,index=36198):
        f=self.frames[index];raw=Path(f['image']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=f['sha256']:raise ValueError('SOURCE_CHANGED')
        p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
        if p['binding']['imageSha256']!=f['sha256'] or p['sourceBinding']['frameIndex']!=index:raise ValueError('PACKET_CHANGED')
        return Image.open(f['image']).convert('RGB'),p
    def test_actual_stretched_low_score_ordinary_is_read_from_full_glyph_crop(self):
        for index in [36196,36198]:
            with self.subTest(index=index):
                image,p=self.source(index)
                with BoundedOCRRuntime(960):result=inspect_preview_context(image,p)
                self.assertTrue(result['verified']);self.assertTrue(result['waitOnly'])
                self.assertNotIn('selectedNode',result)
                e=result['ordinaryEvidence']
                self.assertEqual(e['refinedReading']['text'],'普通');self.assertGreaterEqual(e['refinedReading']['score'],.95)
                self.assertEqual(e['positionEvidence']['horizontalScale'],image.width/p['mapReview']['aspectRectification']['rectifiedInputSize'][0])
    def test_erased_word_cannot_be_restored_from_old_ocr_with_rebound_metadata(self):
        image,p=self.source();row=next(r for r in p['evidence'] if '普通' in r['text'])
        xs=[v[0] for v in row['box']];ys=[v[1] for v in row['box']]
        ImageDraw.Draw(image).rectangle((math.floor(min(xs)),math.floor(min(ys)),math.ceil(max(xs)),math.ceil(max(ys))),fill=(40,40,60))
        out=io.BytesIO();image.save(out,format='PNG');sha=hashlib.sha256(out.getvalue()).hexdigest();pixel=hashlib.sha256(image.tobytes()).hexdigest()
        p['binding'].update(frameId='e'*32,imageSha256=sha,pixelSha256=pixel)
        e=p['mapReview']['aspectRectification'];e.update(sourceCaptureFrameId='e'*32,sourceImageSha256=sha,pixelSha256=pixel)
        e['calibration']['pixelSha256']=pixel
        e['coordinateContract']=geometry_certificate(p['binding'],e['rectifiedInputSize'],analysis_raster(e['rectifiedInputSize']))
        with BoundedOCRRuntime(960) as rt:
            result=inspect_preview_context(image,p);meta=rt.take_metadata()
        self.assertFalse(result['verified']);self.assertTrue(meta['recognitionCrops'])
    def test_wrong_aspect_binding_or_matrix_is_rejected_before_reread(self):
        image,p=self.source()
        variants=[lambda e:e.update(pixelSha256='f'*64),lambda e:e.update(sourceCaptureFrameId='f'*32),lambda e:e['inverseMatrix'][0].__setitem__(0,1.2),lambda e:e['coordinateContract']['spaces']['rectified'].__setitem__(0,1000),lambda e:e.pop('coordinateContract')]
        for mutate in variants:
            q=copy.deepcopy(p);mutate(q['mapReview']['aspectRectification'])
            with BoundedOCRRuntime(960) as rt:
                result=inspect_preview_context(image,q);meta=rt.take_metadata()
            self.assertFalse(result['verified']);self.assertFalse(meta['recognitionCrops'])
    def test_absent_geometry_does_not_guess_horizontal_scale_from_window_shape(self):
        image,p=self.source();p['mapReview'].pop('aspectRectification')
        with BoundedOCRRuntime(960):result=inspect_preview_context(image,p)
        self.assertFalse(result['verified'])
    def test_legacy_unversioned_controls_use_scale_one_without_old_geometry(self):
        root=ROOT/'artifacts/p4c-sparse-peer-case36-analysis-02'
        m=json.loads((root/'manifest.json').read_text(encoding='utf-8'));f=next(f for f in m['cases'][0]['frames'] if f['frameIndex']==53434)
        self.assertEqual(hashlib.sha256(Path(f['image']).read_bytes()).hexdigest(),f['sha256'])
        p=json.loads(Path(f['packet']).read_text(encoding='utf-8'));self.assertNotIn('observerContractVersion',p)
        with BoundedOCRRuntime(960):result=inspect_preview_context(Image.open(f['image']).convert('RGB'),p)
        self.assertTrue(result['verified']);self.assertTrue(result['waitOnly'])
        self.assertNotIn('positionEvidence',result['ordinaryEvidence'])
        self.assertGreaterEqual(result['ordinaryEvidence']['refinedScore'],.95)

if __name__=='__main__':unittest.main()
