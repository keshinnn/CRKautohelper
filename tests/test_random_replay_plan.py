import copy,hashlib,json,sys,tempfile,unittest
from PIL import Image,ImageDraw
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'ml'))
try:
    from random_replay_plan import plan_sequences
except ImportError:
    def plan_sequences(*a,**k):return None

try:
    from random_replay_plan import render_sequences
except ImportError:
    def render_sequences(*a,**k):return None

class RandomReplayPlanTests(unittest.TestCase):
    def fixture(self):
        def frame(i):return {'frameIndex':i,'sourcePtsMs':round(i/30*1000,6),'atMs':round(i/30*1000,6),'image':f'fixture-{i}.png','sha256':'a'*64,'size':[1440,1080],'packet':'must-not-leak'}
        case={'id':'fixture-only','reviewed':True,'videoSha256':'b'*64,'sourceFps':30,'sourceSize':[1440,1080],'preFrames':[100,106],'gateWindowMs':[3533.333333,3533.333333],'expectedBox':[600,500,100,100],'clientBox':[620,520,60,60],'frames':[frame(i) for i in [100,106,107,108]],'intent':{'zone':1,'floor':1,'column':2,'event':'battle','mode':'select'}}
        anchors={'reviewed':True,'caseId':'fixture-only','videoSha256':'b'*64,'annotationSha256':'c'*64,'sourceSize':[1440,1080],'boxes':[[10,10,1420,1060]]}
        prefix={**frame(99),'reviewed':True,'videoSha256':'b'*64}
        return case,anchors,prefix
    def test_three_sequences_keep_real_time_and_reacquire_a_new_prechange_pair(self):
        c,a,p=self.fixture();before=copy.deepcopy(c);plans=plan_sequences(c,a,p,'c'*64)
        self.assertIsNotNone(plans);self.assertEqual(plans,plan_sequences(c,a,p,'c'*64));self.assertEqual(c,before)
        by={s['transformMode']:s for s in plans}
        self.assertEqual(set(by),{'fixed','pre-change','post-change'})
        self.assertEqual([f['frameIndex'] for f in by['pre-change']['frames']],[99,100,106,107,108])
        self.assertEqual(by['pre-change']['previewFromPtsMs'],3566.666667)
        for s in plans:
            self.assertEqual(s['gateWindowMs'],c['gateWindowMs'])
            for f in s['frames']:
                self.assertEqual(f['sourcePtsMs'],round(f['frameIndex']/30*1000,6));self.assertNotIn('packet',f)
                self.assertGreater(sum(f['renderLayout']['cropMargins']),0)
        pre=by['pre-change']['frames'];self.assertNotEqual(pre[0]['geometryVersion'],pre[1]['geometryVersion']);self.assertEqual(pre[1]['geometryVersion'],pre[2]['geometryVersion'])
        post=by['post-change']['frames'];self.assertEqual(post[0]['geometryVersion'],post[1]['geometryVersion']);self.assertNotEqual(post[1]['geometryVersion'],post[2]['geometryVersion'])
        for i in [100,106,107,108]:
            sizes={tuple(next(f['size'] for f in s['frames'] if f['frameIndex']==i)) for s in plans}
            self.assertEqual(len(sizes),3)
    def pixel_fixture(self,folder):
        c,a,p=self.fixture()
        for f in [p,*c['frames']]:
            image=Image.new('RGB',(1440,1080),(255,0,0));ImageDraw.Draw(image).rectangle((0,540,1439,1079),fill=(0,0,255))
            target=Path(folder)/f"source-{f['frameIndex']}.png";image.save(target)
            f['image']=str(target);f['sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
        return c,a,p
    def test_rendered_sequences_freeze_actual_pngs_dimensions_and_original_byte_bindings(self):
        with tempfile.TemporaryDirectory(prefix='crk-random-render-',dir=ROOT/'artifacts') as folder:
            c,a,p=self.pixel_fixture(folder);plans=plan_sequences(c,a,p,'c'*64);out=Path(folder)/'rendered'
            result=render_sequences(plans,out);self.assertIsNotNone(result)
            self.assertTrue(result['pixelsRendered']);self.assertFalse(result['g4Complete']);self.assertEqual(len(result['cases']),3)
            self.assertNotIn('must-not-leak',json.dumps(result))
            for case in result['cases']:
                x,y,w,h=case['expectedBox']
                for f in case['frames']:
                    self.assertFalse(f['renderPending']);self.assertNotIn('packet',f)
                    self.assertEqual(f['sha256'],hashlib.sha256(Path(f['image']).read_bytes()).hexdigest())
                    self.assertEqual(f['transform']['inputSha256'],f['sourceImageSha256'])
                    with Image.open(f['image']) as image:
                        self.assertEqual(image.format,'PNG');self.assertEqual(list(image.size),f['size'])
                    if f['frameIndex']==106:
                        with Image.open(f['image']) as image:self.assertEqual(image.getpixel((round(x+w/2),round(y+h/2))),(0,0,255))
            snapshot=(out/'manifest.json').read_bytes()
            with self.assertRaises(FileExistsError):render_sequences(plans,out)
            self.assertEqual((out/'manifest.json').read_bytes(),snapshot)
    def test_changed_source_stops_renderer_and_keeps_failure_unaccepted(self):
        with tempfile.TemporaryDirectory(prefix='crk-random-failure-',dir=ROOT/'artifacts') as folder:
            c,a,p=self.pixel_fixture(folder);plans=plan_sequences(c,a,p,'c'*64);out=Path(folder)/'rendered'
            Image.new('RGB',(1440,1080),(0,255,0)).save(c['frames'][0]['image'])
            with self.assertRaisesRegex(ValueError,'source PNG changed'):render_sequences(plans,out)
            self.assertFalse(json.loads((out/'manifest.json').read_text())['pixelsRendered'])
            self.assertFalse(json.loads((out/'failure.json').read_text())['g4Complete'])

    def test_plan_truth_is_not_a_mutable_alias_of_the_frozen_input(self):
        c,a,p=self.fixture();before=copy.deepcopy(c);plans=plan_sequences(c,a,p,'c'*64)
        plans[0]['originalExpectedBox'][0]=0;plans[0]['originalClientBox'][0]=0
        self.assertEqual(c,before)

    def test_unreviewed_wrong_source_or_time_cannot_generate_random_positive(self):
        for kind in ['case','anchors','prefix','source','index','time','gate','box','hash','anchor-case','anchor-source','anchor-annotation']:
            with self.subTest(kind=kind):
                c,a,p=self.fixture();sha='c'*64
                if kind=='case':c['reviewed']=False
                elif kind=='anchors':a['reviewed']=False
                elif kind=='prefix':p['reviewed']=False
                elif kind=='source':p['videoSha256']='d'*64
                elif kind=='index':p['frameIndex']=98
                elif kind=='time':c['frames'][2]['sourcePtsMs']+=10
                elif kind=='gate':c['gateWindowMs'][0]+=1
                elif kind=='box':a['boxes']=[[0,0,2000,2000]]
                elif kind=='hash':sha='unknown'
                elif kind=='anchor-case':a['caseId']='different-case'
                elif kind=='anchor-source':a['videoSha256']='d'*64
                elif kind=='anchor-annotation':a['annotationSha256']='d'*64
                with self.assertRaises(ValueError):plan_sequences(c,a,p,sha)

if __name__=='__main__':unittest.main()
