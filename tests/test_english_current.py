import copy,json,sys,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from map_action_evidence import inspect_map_actions

class EnglishCurrentTests(unittest.TestCase):
    def source(self):
        p=json.loads((ROOT/'artifacts/p4c-LX46-dev-analysis-02/dev-LX46-zone1-floor1-col1-resume/0002194.packet.json').read_text(encoding='utf-8'))
        image=Image.open(ROOT/'artifacts/p4c-LX46-native-qualification-01/candidate-00-38.0/0002194.png').convert('RGB')
        return image,p
    def test_actual_english_label_keeps_same_yellow_ring_triangle_pixel_requirements(self):
        image,p=self.source();result=inspect_map_actions(image,p)
        self.assertIsNotNone(result['current'])
        self.assertEqual(result['current']['nodeId'],'visible-1-1')
        self.assertTrue(result['current']['verified']);self.assertEqual(result['current']['zone'],1)
    def test_watermark_partial_and_duplicate_labels_never_prove_current(self):
        for bad in ['@chateaw In Progress','In Progr','missing','duplicate']:
            image,p=self.source();row=next(r for r in p['evidence'] if r['text']=='In progress')
            if bad=='missing':p['evidence'].remove(row)
            elif bad=='duplicate':p['evidence'].append(copy.deepcopy(row))
            else:row['text']=bad
            self.assertIsNone(inspect_map_actions(image,p)['current'])

if __name__=='__main__':unittest.main()
