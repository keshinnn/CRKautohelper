import json,sys,unittest
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from map_vision import line_evidence
try:
 from reference_line_geometry import reference_line
except ImportError:
 def reference_line(image,a,b,original):return original(image,a,b),None
class ReferenceLineTests(unittest.TestCase):
 def fixture(self):
  m=json.loads((ROOT/'artifacts/p4c-random-development-60-run-12/dev-primary-zone2-floor2-col3-higher-random-post-change/analysis/manifest.json').read_text(encoding='utf-8'));f=m['cases'][0]['frames'][1];p=json.loads(Path(f['packet']).read_text(encoding='utf-8'));r=p['mapReview'];e=r['aspectRectification'];nw,nh=e['rectifiedInputSize'];aw,ah=e['modelAnalysisSize'];nodes=[]
  for ident in ['visible-1-3','visible-2-3']:
   n=next(n for n in r['nodes'] if n['id']==ident);b=n['analysisBox'];nodes.append({'id':ident,'box':[v*(aw/nw if i%2==0 else ah/nh) for i,v in enumerate(b)],'center':[n['analysisCenter'][0]*aw/nw,n['analysisCenter'][1]*ah/nh]})
  with Image.open(f['image']) as im:image=im.convert('RGB').resize((nw,nh),Image.Resampling.LANCZOS).resize((aw,ah),Image.Resampling.LANCZOS)
  return image,nodes
 def test_actual_large_nodes_keep_original_kernel_and_support_threshold(self):
  image,nodes=self.fixture();raw=line_evidence(image,*nodes);self.assertLess(raw,.85)
  score,proof=reference_line(image,*nodes,line_evidence);self.assertGreaterEqual(score,.85);self.assertEqual(proof['referenceNodeSize'],58);self.assertEqual(proof['originalSupport'],raw)
 def test_erased_stem_cannot_be_replaced_by_arrow_pixels(self):
  image,nodes=self.fixture();ImageDraw.Draw(image).rectangle((548,412,576,422),fill=(236,47,45))
  score,_=reference_line(image,*nodes,line_evidence);self.assertLess(score,.85)
if __name__=='__main__':unittest.main()
