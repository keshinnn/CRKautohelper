import copy,hashlib,io,json,sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
try:
    from map_aspect import estimate_pixel_aspect,recover_map_aspect
except ImportError:
    def estimate_pixel_aspect(*a):return None
    def recover_map_aspect(image,packet):return packet['mapReview']

class MapAspectTests(unittest.TestCase):
    def test_actual_hud_overlap_does_not_create_a_second_nonclosed_consensus(self):
        m=json.loads((ROOT/'artifacts/p4c-random-development-60-run-08/zone-9-first-battle-random-post-change/analysis/manifest.json').read_text(encoding='utf-8'))
        for f in m['cases'][0]['frames'][:2]:
            with Image.open(f['image']) as image:calibration=estimate_pixel_aspect(image)
            self.assertIsNotNone(calibration)
            self.assertEqual(len(calibration['consensus']),6)
            chosen=[i for i,q in enumerate(calibration['candidates']) if abs(q['ratio']/calibration['ratio']-1)<.04]
            self.assertEqual(calibration['consensus'],chosen)
            self.assertTrue(all(calibration['candidates'][i]['center'][1]>600 for i in chosen))

    def test_actual_unanchored_five_percent_aspect_recovers_gate_without_changing_native_maps(self):
        m=json.loads((ROOT/'artifacts/p4c-time-locator-zone9-pre-analysis-01/manifest.json').read_text(encoding='utf-8'))
        for f in m['cases'][0]['frames'][1:3]:
            p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
            self.assertFalse(p['mapReview']['absoluteFloorKnown'])
            with Image.open(f['image']) as image:result=recover_map_aspect(image,p)
            self.assertTrue(result['absoluteFloorKnown'])
            self.assertEqual(result['aspectRectification']['rectificationPurpose'],'unanchored_near_native_recovery')
            self.assertEqual(len([n for n in result['nodes'] if n.get('floor')==1 and n.get('column')==4]),1)

    def test_actual_small_source_node_measures_outer_box_from_verified_icon_core(self):
        m=json.loads((ROOT/'artifacts/p4c-random-development-60-run-06/zone-9-first-battle-random-fixed/analysis/manifest.json').read_text(encoding='utf-8'))
        c=m['cases'][0]
        for f in c['frames'][:2]:
            p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
            with Image.open(f['image']) as image:result=recover_map_aspect(image,p)
            n=next(n for n in result['nodes'] if n.get('floor')==1 and n.get('column')==4)
            a,b=n['box'],c['expectedBox']
            intersection=max(0,min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0]))*max(0,min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1]))
            self.assertGreaterEqual(intersection/(a[2]*a[3]+b[2]*b[3]-intersection),.9)
            self.assertEqual(n['score'],next(n for n in p['mapReview']['nodes'] if n.get('floor')==1 and n.get('column')==4)['score'])
            self.assertGreaterEqual(n['orangeRefinement']['iconCoreEvidence']['score'],.9)

    def test_actual_early_preview_uses_original_icon_core_without_relaxing_score(self):
        from bounded_ocr import BoundedOCRRuntime
        from preview_identity import inspect_preview_identity
        manifest=json.loads((ROOT/'artifacts/p4c-proposal-zone8-analysis-01/manifest.json').read_text(encoding='utf-8'))
        f=next(f for f in manifest['cases'][0]['frames'] if f['frameIndex']==64890)
        p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
        with Image.open(f['image']) as image:
            p['mapReview']=recover_map_aspect(image,p)
            with BoundedOCRRuntime(960):result=inspect_preview_identity(image,p)
        self.assertTrue(result['verified'])
        self.assertEqual([result['selectedNode'][k] for k in ['zone','floor','column']],[8,1,4])
        node=next(n for n in p['mapReview']['nodes'] if n.get('floor')==1 and n.get('column')==4)
        core=node['pixelProposal']['geometryEvidence']['iconCoreEvidence']
        self.assertGreaterEqual(core['score'],.9)
        self.assertGreaterEqual(core['score']-core['runnerUpScore'],.08)

    def cases(self):return json.loads((ROOT/'artifacts/p4c-random-pilot-pixels-01/manifest.json').read_text(encoding='utf-8'))['cases']
    def image(self,c):
        f=next(f for f in c['frames'] if f['frameIndex']==2514)
        return Image.open(f['image']).convert('RGB'),f
    def packet(self,image,image_sha=None):
        pixel=hashlib.sha256(image.tobytes()).hexdigest();raw=io.BytesIO();image.save(raw,format='PNG')
        return {'binding':{'pixelSha256':pixel,'imageSha256':image_sha or hashlib.sha256(raw.getvalue()).hexdigest(),'width':image.width,'height':image.height},'mapReview':{'frameId':pixel[:20],'nodes':[],'edges':[],'columns':None,'absoluteFloorKnown':False,'header':None}}
    def test_actual_pixels_estimate_three_different_aspects_without_layout_input(self):
        for c in self.cases():
            image,f=self.image(c);estimate=estimate_pixel_aspect(image)
            self.assertIsNotNone(estimate);truth=f['transform']['sx']/f['transform']['sy']
            self.assertLess(abs(estimate['ratio']/truth-1),.03)
            self.assertGreaterEqual(len(estimate['consensus']),3)
    def test_actual_zero_candidate_map_recovers_source_pixel_boxes_and_unique_gate(self):
        c=self.cases()[0];image,f=self.image(c);p=self.packet(image,f['sha256']);before=copy.deepcopy(p)
        result=recover_map_aspect(image,p);self.assertIsNot(result,p['mapReview']);self.assertEqual(p,before)
        self.assertTrue(result['absoluteFloorKnown']);self.assertEqual(result['floorAnchorSource'],'visible_top_gate')
        self.assertEqual(result['frameId'],p['binding']['pixelSha256'][:20])
        n=next(n for n in result['nodes'] if n.get('floor')==1 and n.get('column')==2);a=n['box'];b=c['expectedBox']
        area=max(0,min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0]))*max(0,min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1]))
        self.assertGreaterEqual(area/(a[2]*a[3]+b[2]*b[3]-area),.9)
        proof=result['aspectRectification'];self.assertEqual(proof['sourceSize'],list(image.size));self.assertEqual(proof['pixelSha256'],p['binding']['pixelSha256']);self.assertIn('inverseMatrix',proof)
    def test_native_chinese_and_english_frames_keep_original_geometry(self):
        for case,index in [('zone-1-first-battle',2514),('dev-LX46-zone1-floor1-col1-resume',2194)]:
            image=Image.open(ROOT/f'artifacts/p4c-frozen-native-30-v3/{case}/{index:07}.png').convert('RGB')
            packet=json.loads((ROOT/f'artifacts/p4c-development-20-v3-analysis-01/{case}/{index:07}.packet.json').read_text(encoding='utf-8'))
            self.assertIs(recover_map_aspect(image,packet),packet['mapReview'])
    def test_wrong_pixels_missing_gate_and_ellipse_noise_never_grant_absolute_map(self):
        c=self.cases()[0];image,f=self.image(c);p=self.packet(image,f['sha256']);p['binding']['pixelSha256']='0'*64
        self.assertIs(recover_map_aspect(image,p),p['mapReview'])
        erased=image.copy();ImageDraw.Draw(erased).rectangle((1100,390,1330,580),fill=(240,30,20))
        self.assertFalse(recover_map_aspect(erased,self.packet(erased))['absoluteFloorKnown'])
        noise=Image.new('RGB',(960,720),(20,20,20));d=ImageDraw.Draw(noise)
        for x,y in [(100,100),(300,300),(600,500)]:d.ellipse((x,y,x+100,y+60),fill=(255,160,0))
        self.assertFalse(recover_map_aspect(noise,self.packet(noise))['absoluteFloorKnown'])
    def test_two_distinct_pixel_aspect_consensuses_are_ambiguous(self):
        image=Image.new('RGB',(960,720),(20,20,20));d=ImageDraw.Draw(image)
        for x,y in [(100,100),(300,250),(500,400)]:d.ellipse((x,y,x+84,y+60),fill=(255,160,0))
        for x,y in [(100,550),(700,100),(700,500)]:d.ellipse((x,y,x+114,y+60),fill=(255,160,0))
        self.assertIsNone(estimate_pixel_aspect(image))

    def test_actual_preview_panel_icon_above_visible_gate_cannot_break_sparse_map_lattice(self):
        manifest=json.loads((ROOT/'artifacts/p4c-random-pilot-analysis-03/manifest.json').read_text(encoding='utf-8'))
        f=next(f for f in manifest['cases'][1]['frames'] if f['frameIndex']==2541)
        p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
        image=Image.open(f['image']).convert('RGB');result=recover_map_aspect(image,p)
        self.assertTrue(result['absoluteFloorKnown'])
        self.assertEqual(len(result['columns']),4)
        self.assertTrue(result['aspectRectification']['candidateScope']['excluded'])
        self.assertTrue(all(n.get('floor',1)>=1 for n in result['nodes'] if n['type']!='exit'))

    def test_actual_unchanged_orange_circle_keeps_two_frame_selection_geometry_stable(self):
        manifest=json.loads((ROOT/'artifacts/p4c-random-pilot-analysis-04/manifest.json').read_text(encoding='utf-8'))
        boxes=[]
        for f in manifest['cases'][2]['frames'][:2]:
            image=Image.open(f['image']).convert('RGB');p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
            result=recover_map_aspect(image,p)
            node=next(n for n in result['nodes'] if n.get('floor')==1 and n.get('column')==2)
            boxes.append(node['box'])
        a,b=boxes
        area=max(0,min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0]))*max(0,min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1]))
        self.assertGreaterEqual(area/(a[2]*a[3]+b[2]*b[3]-area),.95)
        self.assertLessEqual(__import__('math').hypot(a[0]+a[2]/2-b[0]-b[2]/2,a[1]+a[3]/2-b[1]-b[3]/2),min(b[2:])*.02)

    def test_actual_static_gate_keeps_geometry_when_outer_template_variant_changes(self):
        manifest=json.loads((ROOT/'artifacts/p4c-random-development-60-run-01/zone-2-first-battle-random-fixed/analysis/manifest.json').read_text(encoding='utf-8'))
        gates=[]
        for f in manifest['cases'][0]['frames'][:2]:
            image=Image.open(f['image']).convert('RGB');p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
            result=recover_map_aspect(image,p);gate=next(n for n in result['nodes'] if n['type']=='exit');gates.append(gate['box'])
        a,b=gates;area=max(0,min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0]))*max(0,min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1]))
        self.assertGreaterEqual(area/(a[2]*a[3]+b[2]*b[3]-area),.95)

    def test_gate_geometry_cannot_use_a_cyan_blob_without_actual_arrow_pixels(self):
        import numpy as np
        from map_aspect import _gate_pixel_geometry
        manifest=json.loads((ROOT/'artifacts/p4c-random-development-60-run-01/zone-2-first-battle-random-fixed/analysis/manifest.json').read_text(encoding='utf-8'))
        f=manifest['cases'][0]['frames'][0];image=Image.open(f['image']).convert('RGB')
        p=json.loads(Path(f['packet']).read_text(encoding='utf-8'));gate=next(n for n in p['mapReview']['nodes'] if n['type']=='exit')
        self.assertIsNotNone(_gate_pixel_geometry(image,gate['box'],Path('F:/CRK helper'),hashlib.sha256(image.tobytes()).hexdigest()))
        a=np.array(image);x,y,w,h=gate['box'];region=a[int(y):int(y+h+1),int(x):int(x+w+1)]
        white=(region.min(2)>140)&(region.max(2).astype(float)-region.min(2)<80)
        region[white]=[30,130,170];image=Image.fromarray(a)
        self.assertIsNone(_gate_pixel_geometry(image,gate['box'],Path('F:/CRK helper'),hashlib.sha256(a.tobytes()).hexdigest()))

    def test_partial_bottom_node_is_not_refined_outside_actual_image(self):
        manifest=json.loads((ROOT/'artifacts/p4c-aspect-zone2-fixed-analysis-01/manifest.json').read_text(encoding='utf-8'))
        f=manifest['cases'][0]['frames'][9];image=Image.open(f['image']).convert('RGB')
        p=json.loads(Path(f['packet']).read_text(encoding='utf-8'));result=recover_map_aspect(image,p)
        w,h=result['aspectRectification']['rectifiedInputSize']
        for n in result['nodes']:
            x,y,nw,nh=n['analysisBox'];self.assertGreaterEqual(min(x,y),0)
            self.assertLessEqual(x+nw,w);self.assertLessEqual(y+nh,h)

    def test_actual_new_client_size_measures_outer_node_from_original_inner_ellipse(self):
        manifest=json.loads((ROOT/'artifacts/p4c-random-development-60-run-03/zone-2-first-battle-random-pre-change/analysis/manifest.json').read_text(encoding='utf-8'))
        c=manifest['cases'][0]
        for f in c['frames'][1:3]:
            image=Image.open(f['image']).convert('RGB');p=json.loads(Path(f['packet']).read_text(encoding='utf-8'));before=copy.deepcopy(p)
            result=recover_map_aspect(image,p);self.assertEqual(p,before)
            a=next(n['box'] for n in result['nodes'] if n.get('floor')==1 and n.get('column')==2);b=c['expectedBox']
            area=max(0,min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0]))*max(0,min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1]))
            self.assertGreaterEqual(area/(a[2]*a[3]+b[2]*b[3]-area),.9)

    def test_plain_orange_ellipse_without_battle_icon_cannot_supply_outer_geometry(self):
        import numpy as np
        from map_aspect import _orange_node_pixel_geometry
        m=json.loads((ROOT/'artifacts/p4c-random-development-60-run-03/zone-2-first-battle-random-pre-change/analysis/manifest.json').read_text(encoding='utf-8'))
        f=m['cases'][0]['frames'][1];image=Image.open(f['image']).convert('RGB');p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
        node=next(n for n in p['mapReview']['nodes'] if n.get('floor')==1 and n.get('column')==2)
        self.assertIsNotNone(_orange_node_pixel_geometry(image,node['box'],Path('F:/CRK helper'),hashlib.sha256(image.tobytes()).hexdigest()))
        a=np.array(image);x,y,w,h=node['box'];region=a[int(y):int(y+h+1),int(x):int(x+w+1)]
        white=(region.min(2)>140)&(region.max(2).astype(float)-region.min(2)<80);region[white]=[255,160,0]
        self.assertIsNone(_orange_node_pixel_geometry(Image.fromarray(a),node['box'],Path('F:/CRK helper'),hashlib.sha256(a.tobytes()).hexdigest()))
        self.assertIsNone(_orange_node_pixel_geometry(Image.fromarray(a),node['box'],Path('F:/CRK helper'),hashlib.sha256(a.tobytes()).hexdigest(),allow_icon_core=True))

    def test_actual_glowing_outer_edge_can_use_independent_inner_icon_candidate(self):
        import map_vision
        m=json.loads((ROOT/'artifacts/p4c-random-development-60-run-05/zone-8-first-battle-random-fixed/analysis/manifest.json').read_text(encoding='utf-8'))
        before=map_vision.node_candidates
        for f in m['cases'][0]['frames'][:2]:
            p=json.loads(Path(f['packet']).read_text(encoding='utf-8'));image=Image.open(f['image']).convert('RGB')
            result=recover_map_aspect(image,p)
            self.assertTrue(result['absoluteFloorKnown'])
            target=next(n for n in result['nodes'] if n.get('floor')==1 and n.get('column')==4)
            self.assertGreaterEqual(target['pixelProposal']['geometryEvidence']['innerScore'],.9)
            self.assertEqual(target['type'],'battle');self.assertFalse(target['completed'])
        self.assertIs(map_vision.node_candidates,before)

if __name__=='__main__':unittest.main()
