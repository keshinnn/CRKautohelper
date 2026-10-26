import copy,io,json,sys,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from preview_identity import inspect_preview_identity
class NativePreviewSizeTests(unittest.TestCase):
 def source(self):
  m=json.loads((ROOT/'artifacts/p4c-random-development-60-run-18/dev-primary-zone4-floor2-col3-random-post-change/analysis/manifest.json').read_text(encoding='utf-8'));f=m['cases'][0]['frames'][-1]
  return Image.open(f['image']).convert('RGB'),json.loads(Path(f['packet']).read_text(encoding='utf-8'))
 def test_actual_native_aspect_preview_uses_a_measured_same_frame_peer_extent(self):
  image,p=self.source();self.assertNotIn('aspectRectification',p['mapReview']);r=inspect_preview_identity(image,p);self.assertTrue(r['verified']);self.assertEqual([r['selectedNode'][k] for k in ['zone','floor','column']],[4,2,3])
  node=next(n for n in r['recoveredNodes'] if n['id']==r['selectedNode']['nodeId']);self.assertGreaterEqual(node['iconScore'],.9);self.assertIn('iconPeerSizeEvidence',node)
 def test_unavailable_peer_extents_or_missing_controls_do_not_promote_native_preview(self):
  image,p=self.source();p['evidence']=[r for r in p['evidence'] if r.get('text')!='03:00'];self.assertFalse(inspect_preview_identity(image,p)['verified'])
  image,p=self.source()
  for n in p['mapReview']['nodes']:
   if n['type']!='exit':n['box'][2:]=[110.11,110.06]
  self.assertFalse(inspect_preview_identity(image,p)['verified'])
if __name__=='__main__':unittest.main()
