"""Approved M1: real pixels, retained base candidates, incremental work only."""
import hashlib,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
import cv2
import fast_map_candidates as fm
from map_vision import node_candidates as legacy,classify_node
from map_aspect import estimate_pixel_aspect
from geometry_contract import raster_round,analysis_raster,resize_box
FOLDER=Path('F:/CRK helper/data/map')
def iou(a,b):
    inter=max(0,min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0]))*max(0,min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1]))
    return inter/(a[2]*a[3]+b[2]*b[3]-inter)
class NominalQuantizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        m=json.loads((ROOT/'artifacts/development-20261027-medium-01/case-41/run-01/manifest.json').read_text(encoding='utf-8'))
        cls.case=m['cases'][0];cls.images={};cls.sources={}
        for index in [35929,35935]:
            f=next(f for f in cls.case['frames'] if f['frameIndex']==index)
            if hashlib.sha256(Path(f['image']).read_bytes()).hexdigest()!=f['sha256']:raise ValueError('SOURCE_CHANGED')
            with Image.open(f['image']) as image:rgb=image.convert('RGB')
            cal=estimate_pixel_aspect(rgb);rect=[raster_round(rgb.width/cal['ratio']),rgb.height];size=analysis_raster(rect)
            cls.images[index]=rgb.resize(tuple(rect),Image.Resampling.LANCZOS).resize(tuple(size),Image.Resampling.LANCZOS)
            cls.sources[index]=f
    def test_actual_dispatch_pixels_gain_battle_without_displacing_base(self):
        im=self.images[35935];before=legacy(im,FOLDER);self.assertEqual(len(before),2)
        after=fm.node_candidates(im,FOLDER)
        self.assertGreaterEqual(len(after),4,'dispatch raster needs genuine supplementary candidates')
        self.assertEqual(after[:len(before)],before)
        projected=[resize_box(n['box'],list(im.size),self.sources[35935]['size']) for n in after]
        index=max(range(len(after)),key=lambda i:iou(projected[i],self.case['expectedBox']))
        self.assertGreaterEqual(iou(projected[index],self.case['expectedBox']),.90)
        self.assertEqual(classify_node(im,after[index],FOLDER)['type'],'battle')
        self.assertTrue(all(n['score']>=.48 for n in after))
    def test_high_count_real_pixels_keep_exact_original_results(self):
        im=self.images[35929];before=legacy(im,FOLDER);self.assertEqual(len(before),8)
        self.assertEqual(fm.node_candidates(im,FOLDER),before)
    def test_low_count_scans_only_new_kernels_and_runs_canny_once(self):
        im=self.images[35935];scans=[];original=fm._match_group
        def collect(edges,group):
            scans.extend((order,name,tuple(temp.shape)) for order,name,temp,norm in group[1])
            return original(edges,group)
        with patch.object(fm,'_match_group',side_effect=collect),patch.object(cv2,'Canny',wraps=cv2.Canny) as canny:
            fm.node_candidates(im,FOLDER)
        base=[(order,name,tuple(temp.shape)) for _,kernels in fm._groups(str(FOLDER.resolve()),im.height,im.width) for order,name,temp,norm in kernels]
        self.assertEqual(len(base),204);self.assertEqual(canny.call_count,1)
        self.assertGreater(len(scans),len(base),'M1 must actually scan additional kernels')
        self.assertLessEqual(len(scans),255,'must not rerun the full augmented matcher')
        old={(name,shape) for _,name,shape in base};extra=[(name,shape) for order,name,shape in scans if order>=204]
        self.assertTrue(extra);self.assertTrue(all(k not in old for k in extra));self.assertEqual(len(extra),len(set(extra)))
    def test_four_base_candidates_do_not_activate_supplement(self):
        fake=[(i,0,dict(box=[x,50,30,30],center=[x+15,65],score=.6,template='node-orange.png')) for i,x in enumerate([50,150,250,350])]
        with patch.object(fm,'_match_group',return_value=fake),patch.object(fm,'_nominal_groups',create=True) as extra:
            result=fm.node_candidates(self.images[35935],FOLDER)
        self.assertEqual(len(result),4);extra.assert_not_called()
    def test_blank_pixels_do_not_become_candidates(self):
        self.assertEqual(fm.node_candidates(Image.new('RGB',(960,721)),FOLDER),[])
if __name__=='__main__':unittest.main()
