import copy,hashlib,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
import flow_vision,text_reader
from bounded_ocr import BoundedOCRRuntime
from progress_evidence import ProgressRuntime
from english_scene import EnglishSceneRuntime

class ContextLineRemeasurementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run=ROOT/'artifacts/development-20261027-medium-01/case-40/run-01'
        m=json.loads((run/'manifest.json').read_text(encoding='utf-8'))
        cls.frames={f['frameIndex']:f for f in m['cases'][0]['frames']}
        f=cls.frames[35970]
        if hashlib.sha256(Path(f['image']).read_bytes()).hexdigest()!=f['sha256']:raise ValueError('SOURCE_CHANGED')
        cls.path=Path(f['image']);p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
        if p['binding']['imageSha256']!=f['sha256'] or p['sourceBinding']['frameIndex']!=35970:raise ValueError('PACKET_CHANGED')
        cls.rows=p['evidence']
    def image(self):return Image.open(self.path).convert('RGB')
    def recover(self,image,rows):
        with ProgressRuntime(),BoundedOCRRuntime(960) as rt,EnglishSceneRuntime():
            result=rt._reread_map_context(image,rows)
            state=flow_vision.semantic_state(result)
        return result,state
    def test_actual_loose_boxes_recover_two_fresh_original_lines(self):
        rows,state=self.recover(self.image(),copy.deepcopy(self.rows))
        self.assertEqual(state['state'],'MAP');self.assertGreaterEqual(state['confidence'],.9)
        fresh=[r for r in rows if r.get('source')=='map_context_original_crop']
        self.assertEqual({r['contextKind'] for r in fresh},{'season','timer'})
        self.assertEqual(len(fresh),2);self.assertTrue(all(r['score']>=.9 for r in fresh))
        self.assertEqual(rows[:len(self.rows)],self.rows)
        for row in fresh:
            self.assertIn('originalPixelRefinement',row)
            self.assertIn('cropBox',row)
    def test_erased_season_cannot_reuse_its_old_high_confidence(self):
        image=self.image();ImageDraw.Draw(image).rectangle((5,45,265,80),fill=(25,30,40))
        _,state=self.recover(image,copy.deepcopy(self.rows))
        self.assertFalse(state['state']=='MAP' and state['confidence']>=.9)
    def test_erased_timer_cannot_reuse_its_old_clock(self):
        image=self.image();ImageDraw.Draw(image).rectangle((65,80,450,125),fill=(25,30,40))
        _,state=self.recover(image,copy.deepcopy(self.rows))
        self.assertFalse(state['state']=='MAP' and state['confidence']>=.9)
    def test_duplicate_season_locator_cannot_grant_context(self):
        rows=copy.deepcopy(self.rows);rows.append(copy.deepcopy(next(r for r in rows if r['text'].endswith('\u5b634') and r['score']>=.9)))
        result,state=self.recover(self.image(),rows)
        self.assertEqual(result,rows);self.assertFalse(state['state']=='MAP' and state['confidence']>=.9)
    def test_conflicting_zone_cannot_grant_context(self):
        rows=[*copy.deepcopy(self.rows),{'text':'\u5340\u57df4\u9032\u884c\u4e2d','score':.99,'box':[]}]
        _,state=self.recover(self.image(),rows)
        self.assertFalse(state['state']=='MAP' and state['confidence']>=.9)
    def test_duplicate_local_detector_lines_are_not_independent_evidence(self):
        original_read=text_reader.read_text
        with ProgressRuntime(),BoundedOCRRuntime(960) as rt,EnglishSceneRuntime():
            actual=rt.previous_read
            with patch.object(rt,'previous_read',side_effect=lambda image: [*actual(image),*actual(image)]):
                rows=rt._reread_map_context(self.image(),copy.deepcopy(self.rows))
                state=flow_vision.semantic_state(rows)
        self.assertFalse(state['state']=='MAP' and state['confidence']>=.9)
        self.assertIs(text_reader.read_text,original_read)
    def test_already_valid_season_is_retained_when_only_timer_needs_remeasurement(self):
        f=self.frames[36169]
        self.assertEqual(hashlib.sha256(Path(f['image']).read_bytes()).hexdigest(),f['sha256'])
        packet=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
        self.assertEqual(packet['binding']['imageSha256'],f['sha256'])
        image=Image.open(f['image']).convert('RGB')
        rows,state=self.recover(image,copy.deepcopy(packet['evidence']))
        self.assertEqual(state['state'],'MAP');self.assertGreaterEqual(state['confidence'],.9)
        fresh=[r for r in rows if r.get('source')=='map_context_original_crop']
        self.assertEqual(len(fresh),2)
        self.assertTrue(all(r['score']>=.9 for r in fresh))
    def test_fresh_clock_cannot_silently_change_a_complete_locator_clock(self):
        rows=copy.deepcopy(self.rows)
        timer=next(r for r in rows if '\u5269\u9918\u6642\u9593' in r['text'])
        timer['text']=timer['text'].replace('13:19:00','13:19:01')
        _,state=self.recover(self.image(),rows)
        self.assertFalse(state['state']=='MAP' and state['confidence']>=.9)
    def test_fresh_season_cannot_silently_change_its_locator_number(self):
        rows=copy.deepcopy(self.rows)
        season=next(r for r in rows if r['text'].endswith('\u5b634') and r['score']>=.9)
        season['text']=season['text'][:-1]+'5'
        _,state=self.recover(self.image(),rows)
        self.assertFalse(state['state']=='MAP' and state['confidence']>=.9)
    def test_retained_season_cannot_disagree_when_a_timer_retry_succeeds(self):
        f=self.frames[36169];p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
        image=Image.open(f['image']).convert('RGB')
        with ProgressRuntime(),BoundedOCRRuntime(960) as rt,EnglishSceneRuntime():
            actual=rt.read_line_variants
            def readings(crop,count):
                if count==5:return [{'text':'\u51a5\u754c\u8a66\u5b635','score':.99,'analysisSize':[190,40]}]
                return actual(crop,count)
            with patch.object(rt,'read_line_variants',side_effect=readings):
                rows=rt._reread_map_context(image,copy.deepcopy(p['evidence']))
                state=flow_vision.semantic_state(rows)
        self.assertFalse(state['state']=='MAP' and state['confidence']>=.9)
    def test_missing_glyph_locator_cannot_change_its_complete_clock(self):
        rows=copy.deepcopy(self.rows);timer=next(r for r in rows if '\u5269\u9918\u6642\u9593' in r['text'])
        timer['text']='\u5269\u6642\u959312\u592913:19:01'
        _,state=self.recover(self.image(),rows)
        self.assertFalse(state['state']=='MAP' and state['confidence']>=.9)
    def test_legacy_success_path_also_refuses_a_contradictory_season(self):
        f=self.frames[36169];p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
        image=Image.open(f['image']).convert('RGB')
        with ProgressRuntime(),BoundedOCRRuntime(960) as rt,EnglishSceneRuntime():
            def readings(crop,count):
                return [{'text':'\u51a5\u754c\u8a66\u5b635' if count==5 else '\u5269\u9918\u6642\u959312\u592913:18:54','score':.99,'analysisSize':[190,40]}]
            with patch.object(rt,'read_line_variants',side_effect=readings):
                rows=rt._reread_map_context(image,copy.deepcopy(p['evidence']))
                state=flow_vision.semantic_state(rows)
        self.assertFalse(state['state']=='MAP' and state['confidence']>=.9)
    def test_conflicting_confident_reads_cannot_be_overridden_by_another_crop(self):
        f=self.frames[36169];p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
        image=Image.open(f['image']).convert('RGB')
        with ProgressRuntime(),BoundedOCRRuntime(960) as rt,EnglishSceneRuntime():
            reads=[{'text':'\u51a5\u754c\u8a66\u5b63'+s,'score':.99,'analysisSize':[190,40]} for s in ['4','5']]
            with patch.object(rt,'read_line_variants',return_value=reads),patch.object(rt,'_remeasure_map_context',side_effect=AssertionError('conflicting reads must be refused')):
                rows=rt._reread_map_context(image,copy.deepcopy(p['evidence']))
                state=flow_vision.semantic_state(rows)
        self.assertFalse(state['state']=='MAP' and state['confidence']>=.9)
    def test_accepted_season_spellings_with_one_number_are_one_claim(self):
        f=self.frames[35988]
        self.assertEqual(hashlib.sha256(Path(f['image']).read_bytes()).hexdigest(),f['sha256'])
        p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
        rows,state=self.recover(Image.open(f['image']).convert('RGB'),copy.deepcopy(p['evidence']))
        self.assertEqual(state['state'],'MAP');self.assertGreaterEqual(state['confidence'],.9)
        fresh=[r for r in rows if r.get('source')=='map_context_original_crop']
        self.assertEqual(len(fresh),2)

if __name__=='__main__':unittest.main()
