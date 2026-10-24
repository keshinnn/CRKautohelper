import copy,json,sys,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
import flow_vision,text_reader
from progress_evidence import ProgressRuntime
from bounded_ocr import BoundedOCRRuntime
try:
    from english_scene import semantic_state,EnglishSceneRuntime
except ImportError:
    semantic_state=flow_vision.semantic_state
    class EnglishSceneRuntime:
        def __enter__(self):return self
        def __exit__(self,*a):pass

class EnglishSceneTests(unittest.TestCase):
    def test_actual_original_crop_evidence_classifies_map_despite_watermark(self):
        image=Image.open(ROOT/'artifacts/p4c-LX46-native-qualification-01/candidate-00-38.0/0002194.png').convert('RGB')
        with ProgressRuntime(),BoundedOCRRuntime(960):rows=text_reader.read_text(image)
        before=copy.deepcopy(rows);result=semantic_state(rows)
        self.assertEqual(result['state'],'MAP');self.assertGreaterEqual(result['confidence'],.9)
        self.assertEqual(rows,before)
        for predicate in [lambda t:t.strip()=='Trials of the Nether Realm',lambda t:t.strip().startswith('Ends in:'),lambda t:'Zone' in t]:
            self.assertEqual(semantic_state([r for r in rows if not predicate(r['text'])])['state'],'UNKNOWN')
        self.assertEqual(semantic_state([r for r in rows if '@' in r['text']])['state'],'UNKNOWN')
        self.assertEqual(semantic_state(rows+[{'text':'Zone 2 in Progress','score':.99,'box':[]}])['state'],'UNKNOWN')

    def test_runtime_scoped_and_existing_chinese_semantics_preserved(self):
        original=flow_vision.semantic_state
        rows=[{'text':s,'score':.97,'box':[]} for s in ['冥界試煉','剩餘時間','區域6進行中']]
        self.assertEqual(semantic_state(rows),original(rows))
        en=[{'text':s,'score':.96,'box':[]} for s in ['Trials of the Nether Realm','Ends in: 9D 17:06:48','Zone 1 in Progress']]
        with EnglishSceneRuntime():self.assertEqual(flow_vision.semantic_state(en)['state'],'MAP')
        self.assertIs(flow_vision.semantic_state,original)

if __name__=='__main__':unittest.main()
