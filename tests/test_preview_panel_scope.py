"""The preview illustration is not a fifth map column."""
import copy,json,sys,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from map_aspect import recover_map_aspect
from preview_registration import recover_preview_anchor
from preview_identity import inspect_preview_identity

class PreviewPanelScopeTests(unittest.TestCase):
 def frames(self,after_index=11):
  m=json.loads((ROOT/'artifacts/p4c-random-development-60-run-16/dev-primary-zone3-floor3-col1-higher-random-post-change/analysis/manifest.json').read_text(encoding='utf-8'))
  result=[]
  for index in [2,after_index]:
   f=m['cases'][0]['frames'][index];p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
   result.append({'png':Path(f['image']).read_bytes(),'packet':p,'atMs':f['atMs'],'sourcePtsMs':f['sourcePtsMs'],'windowKey':'offline:original-video','geometryVersion':'random:3d3657a506d574801337a79d906bc7951b2e9bff72e94b209c4d67746945139a'})
  return result
 def test_actual_offscreen_gate_preview_retains_a_relative_map_then_independent_registration(self):
  import io
  a,b=self.frames();image=Image.open(io.BytesIO(b['png'])).convert('RGB')
  repaired=recover_map_aspect(image,b['packet']);self.assertEqual(len(repaired.get('columns') or []),4)
  self.assertGreaterEqual(len(repaired['nodes']),5);self.assertFalse(repaired['absoluteFloorKnown'])
  scope=repaired['aspectRectification']['candidateScope'];self.assertEqual(scope['method'],'same_frame_ordinary_preview_control_panel_scope')
  self.assertEqual(scope['pixelSha256'],b['packet']['binding']['pixelSha256']);self.assertTrue(scope['excluded'])
  b['packet']['mapReview']=repaired;b['packet']['v2TrackedMap']=recover_preview_anchor(a,b)
  self.assertTrue(b['packet']['v2TrackedMap']['verified'])
  preview=inspect_preview_identity(image,b['packet']);self.assertTrue(preview['verified'])
  self.assertEqual([preview['selectedNode'][k] for k in ['zone','floor','column']],[3,3,1])
 def test_incomplete_or_weak_ordinary_preview_controls_do_not_scope_a_map(self):
  import io
  for mode in ['enter','timer','ordinary']:
   _,b=self.frames();p=b['packet'];image=Image.open(io.BytesIO(b['png'])).convert('RGB')
   def selected(r):
    t=''.join(r.get('text','').split())
    return t in ('進入','enter') if mode=='enter' else t=='03:00' if mode=='timer' else '普通' in t
   p['evidence']=[r for r in p['evidence'] if not selected(r)]
   repaired=recover_map_aspect(image,p)
   self.assertIsNone(repaired.get('aspectRectification',{}).get('candidateScope'))
 def test_actual_later_preview_also_calibrates_without_a_visible_gate(self):
  import io
  _,b=self.frames(12);image=Image.open(io.BytesIO(b['png'])).convert('RGB')
  repaired=recover_map_aspect(image,b['packet']);self.assertEqual(len(repaired.get('columns') or []),4)
 def test_erased_enabled_button_or_wrong_source_binding_cannot_grant_panel_scope(self):
  import hashlib,io
  import numpy as np
  from preview_panel_scope import ordinary_preview_panel_scope
  _,b=self.frames();image=Image.open(io.BytesIO(b['png'])).convert('RGB');p=b['packet']
  scope=ordinary_preview_panel_scope(image,p);self.assertIsNotNone(scope)
  p['binding']['pixelSha256']='a'*64;self.assertIsNone(ordinary_preview_panel_scope(image,p))
  _,b=self.frames();p=b['packet'];array=np.asarray(image).copy();x,y,w,h=scope['greenButtonBox'];array[y:y+h,x:x+w]=[40,40,40]
  changed=Image.fromarray(array);raw=io.BytesIO();changed.save(raw,format='PNG');digest=hashlib.sha256(changed.tobytes()).hexdigest()
  p['binding'].update(pixelSha256=digest,imageSha256=hashlib.sha256(raw.getvalue()).hexdigest(),frameId=hashlib.sha256(raw.getvalue()).hexdigest()[:32]);p['mapReview']['frameId']=digest[:20];p['flow']['frameId']=digest[:20]
  self.assertIsNone(ordinary_preview_panel_scope(changed,p))
  repaired=recover_map_aspect(changed,p);self.assertIsNone(repaired.get('aspectRectification',{}).get('candidateScope'))
 def test_erased_original_heal_green_cannot_create_a_source_heal_proposal(self):
  import hashlib,io
  import numpy as np
  _,b=self.frames(12);p=b['packet'];image=Image.open(io.BytesIO(b['png'])).convert('RGB')
  repaired=recover_map_aspect(image,p);heal=next(n for n in repaired['nodes'] if n.get('healProposal'))
  self.assertEqual(heal['type'],'heal');self.assertFalse(heal['completed']);h=heal['healProposal'];self.assertGreaterEqual(h['iconScore'],.9);self.assertGreaterEqual(h['iconScore']-h['otherFamilyScore'],.08)
  x,y,w,hh=h['greenBox'];array=np.asarray(image).copy();array[y:y+hh,x:x+w]=[40,40,40];changed=Image.fromarray(array);raw=io.BytesIO();changed.save(raw,format='PNG');digest=hashlib.sha256(changed.tobytes()).hexdigest()
  p['binding'].update(pixelSha256=digest,imageSha256=hashlib.sha256(raw.getvalue()).hexdigest(),frameId=hashlib.sha256(raw.getvalue()).hexdigest()[:32]);p['mapReview']['frameId']=digest[:20];p['flow']['frameId']=digest[:20]
  after=recover_map_aspect(changed,p)
  self.assertFalse(any(n.get('healProposal') and abs(n['center'][0]-heal['center'][0])<w for n in after.get('nodes',[])))
if __name__=='__main__':unittest.main()
