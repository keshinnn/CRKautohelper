import copy,json,sys,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']

def actual_frame():
    path=ROOT/'artifacts/p4c-random-development-60-run-25/dev-L0-zone6-floor3-col3-select-1932-random-post-change/analysis/manifest.json'
    m=json.loads(path.read_text(encoding='utf-8'))
    f=next(f for f in m['cases'][0]['frames'] if f['frameIndex']==57947)
    return Image.open(f['image']).convert('RGB'),json.loads(Path(f['packet']).read_text(encoding='utf-8'))

class PreviewContextTests(unittest.TestCase):
    def test_batch_classification_uses_independent_controls_without_inventing_identity(self):
        from analyze_cases import effective_observation_state
        from preview_context import inspect_preview_context
        from bounded_ocr import BoundedOCRRuntime
        image,p=actual_frame();p['flow']['state']='UNKNOWN'
        with BoundedOCRRuntime(960):p['v2PreviewContext']=inspect_preview_context(image,p)
        self.assertFalse(p['v2Preview']['verified'])
        self.assertEqual(effective_observation_state(p),'PREVIEW_PENDING')
        p['v2PreviewContext']={'verified':False}
        self.assertEqual(effective_observation_state(p),'UNKNOWN')

    def test_actual_transition_controls_are_known_even_with_no_map_nodes(self):
        from preview_context import inspect_preview_context
        from bounded_ocr import BoundedOCRRuntime
        image,p=actual_frame();self.assertEqual(len(p['mapReview']['nodes']),0)
        with BoundedOCRRuntime(960): result=inspect_preview_context(image,p)
        self.assertTrue(result['verified']);self.assertTrue(result['waitOnly'])
        self.assertEqual(result['zone'],6);self.assertNotIn('selectedNode',result)
        self.assertEqual(result['timerEvidence']['text'],'03:00')

    def test_context_cannot_be_produced_from_wrong_pixels_or_conflicting_zone(self):
        from preview_context import inspect_preview_context
        image,p=actual_frame()
        for mutate in [lambda q:q['binding'].update(pixelSha256='f'*64),lambda q:q['progress'].update(conflictingEvidence=True),lambda q:q.update(evidence=[])]:
            q=copy.deepcopy(p);mutate(q);self.assertFalse(inspect_preview_context(image,q)['verified'])

if __name__=='__main__':unittest.main()
