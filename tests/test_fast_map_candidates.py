import os,sys,unittest
from pathlib import Path
from PIL import Image
root=Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper'));sys.path.insert(0,str(root/'ml'));sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
from map_vision import node_candidates as baseline
try:
    from fast_map_candidates import node_candidates
except ImportError:
    def node_candidates(*args,**kwargs):return []

class ExactCandidateSearchTests(unittest.TestCase):
    def test_parallel_mask_groups_preserve_actual_candidates_scores_and_tie_order(self):
        project=Path(__file__).resolve().parents[1]
        for source in [project/'artifacts/p4a-native/0002520.png',project/'artifacts/p4a-native/0002550.png',root/'data/reviewed-frames/20261024/gpg-native-map.png']:
            with Image.open(source) as im:image=im.convert('RGB').resize((960,round(im.height*960/im.width)),Image.Resampling.LANCZOS)
            expected=baseline(image,root/'data/map');self.assertGreater(len(expected),5)
            for workers in [1,4]:
                actual=node_candidates(image,root/'data/map',workers=workers)
                self.assertEqual(len(actual),len(expected))
                for a,b in zip(actual,expected):
                    self.assertEqual(a['box'],b['box']);self.assertEqual(a['center'],b['center']);self.assertEqual(a['template'],b['template']);self.assertAlmostEqual(a['score'],b['score'],places=6)

if __name__=='__main__':unittest.main()
