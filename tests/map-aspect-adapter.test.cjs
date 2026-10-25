const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {adaptMap,adaptPreview}=require('../lib/observer-adapter.cjs'),{loadReplayFrames}=require('../lib/replay-case.cjs'),{selectNode}=require('../lib/node-selector.cjs');
function fixture(){const m=JSON.parse(fs.readFileSync(path.join(__dirname,'../artifacts/p4c-aspect-map-bridge-02/manifest.json')));const c=m.cases[0];return {c,frames:loadReplayFrames(c)};}
function observe(s,p=s.packet){return adaptMap({...s.frame,png:s.png},p);}
test('two battle circles and original cyan arrow support a freshly confirmed higher-floor selection',()=>{
 const {execFileSync}=require('node:child_process'),source='artifacts/p4c-random-development-60-run-09/dev-primary-zone2-floor2-col3-higher-random-fixed/analysis/manifest.json';
 const raw=execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',`
import json,sys,pathlib
sys.path[:0]=['ml','F:/CRK helper/ml']
from PIL import Image
from map_aspect import recover_map_aspect
from map_action_evidence import inspect_map_actions
from bounded_ocr import BoundedOCRRuntime
from progress_evidence import ProgressRuntime
from english_scene import EnglishSceneRuntime,semantic_state
m=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'));packets=[]
for f in m['cases'][0]['frames'][:2]:
 p=json.loads(pathlib.Path(f['packet']).read_text(encoding='utf-8'));original=p['mapReview']
 with Image.open(f['image']) as im,ProgressRuntime(),BoundedOCRRuntime(960) as runtime,EnglishSceneRuntime():
  p['evidence']=runtime._reread_map_context(im,p['evidence']);p['flow'].update(semantic_state(p['evidence']))
  p['mapReview']=recover_map_aspect(im,p);p['v2MapActions']=inspect_map_actions(im,p)
 p['v2OriginalMapReview']=original;packets.append(p)
print(json.dumps(packets))
`,source],{cwd:path.join(__dirname,'..'),maxBuffer:10*1024*1024});
 const m=JSON.parse(fs.readFileSync(path.join(__dirname,'..',source))),c=m.cases[0],frames=loadReplayFrames(c),packets=JSON.parse(raw);
 const a=observe(frames[0],packets[0]),b=observe(frames[1],packets[1]);
 assert.equal(a.anchorVerified,true);assert.equal(b.anchorVerified,true);
 assert.equal(selectNode(a,b,c.intent,{nowMs:b.frame.atMs}).nodeId,'visible-2-3');
 for(const kind of ['pixels','score','inner-box','kind','missing-proof']){
  const p=structuredClone(packets[1]),q=p.mapReview.aspectRectification.calibration.candidates.find(q=>q.circleKind==='cyan_gate');
  if(kind==='pixels')q.iconEvidence.pixelSha256='0'.repeat(64);
  if(kind==='score')q.iconEvidence.innerScore=.1;
  if(kind==='inner-box')q.iconEvidence.sourceInnerBox[0]+=10;
  if(kind==='kind')q.circleKind='orange_battle';
  if(kind==='missing-proof')delete q.iconEvidence;
  assert.equal(observe(frames[1],p).anchorVerified,false,kind);
 }
 for(const kind of ['check-pixels','check-box','check-score','check-kind','missing-check-proof']){
  const p=structuredClone(packets[1]),n=p.mapReview.nodes.find(n=>n.checkProposal),e=n.checkProposal;
  if(kind==='check-pixels')e.pixelSha256='0'.repeat(64);
  if(kind==='check-box')e.sourceCheckBox[0]+=10;
  if(kind==='check-score')e.checkMaskIoU=.7;
  if(kind==='check-kind')e.matchedTemplate='node-orange';
  if(kind==='missing-check-proof')delete n.checkProposal;
  assert.equal(observe(frames[1],p).anchorVerified,false,kind);
 }
});
test('a missing gate candidate binds original arrow pixels and completed predecessor before selection',()=>{
 const {execFileSync}=require('node:child_process'),source='artifacts/p4c-random-development-60-run-10/dev-primary-zone2-floor2-col3-higher-random-pre-change/analysis/manifest.json';
 const raw=execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',`
import json,sys,pathlib
sys.path[:0]=['ml','F:/CRK helper/ml']
from PIL import Image
from map_aspect import recover_map_aspect
from map_action_evidence import inspect_map_actions
from bounded_ocr import BoundedOCRRuntime
from progress_evidence import ProgressRuntime
from english_scene import EnglishSceneRuntime,semantic_state
m=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'));packets=[]
for f in m['cases'][0]['frames'][1:3]:
 p=json.loads(pathlib.Path(f['packet']).read_text(encoding='utf-8'));original=p['mapReview']
 with Image.open(f['image']) as im,ProgressRuntime(),BoundedOCRRuntime(960) as runtime,EnglishSceneRuntime():
  p['evidence']=runtime._reread_map_context(im,p['evidence']);p['flow'].update(semantic_state(p['evidence']))
  p['mapReview']=recover_map_aspect(im,p);p['v2MapActions']=inspect_map_actions(im,p)
 p['v2OriginalMapReview']=original;packets.append(p)
print(json.dumps(packets))
`,source],{cwd:path.join(__dirname,'..'),maxBuffer:10*1024*1024});
 const m=JSON.parse(fs.readFileSync(path.join(__dirname,'..',source))),c=m.cases[0],frames=loadReplayFrames(c).slice(1,3),packets=JSON.parse(raw);
 const a=observe(frames[0],packets[0]),b=observe(frames[1],packets[1]);
 assert.equal(a.anchorVerified,true);assert.equal(b.anchorVerified,true);
 assert.equal(selectNode(a,b,c.intent,{nowMs:b.frame.atMs}).nodeId,'visible-2-3');
 for(const kind of ['pixels','score','inner-box','index','missing-proof','capture','injected-box']){
  const p=structuredClone(packets[1]),n=p.mapReview.nodes.find(n=>n.gateProposal),e=n.gateProposal;
  if(kind==='pixels')e.pixelSha256='0'.repeat(64);
  if(kind==='score')e.geometryEvidence.innerScore=.1;
  if(kind==='inner-box')e.geometryEvidence.sourceInnerBox[0]+=10;
  if(kind==='index')e.geometryEvidence.candidateIndex=999;
  if(kind==='missing-proof')delete n.gateProposal;
  if(kind==='capture')e.sourceCaptureFrameId='0'.repeat(32);
  if(kind==='injected-box')e.injectedAnalysisBox[0]+=10;
  assert.equal(observe(frames[1],p).anchorVerified,false,kind);
 }
 for(const kind of ['check-pixels','check-box','check-score','check-kind','missing-check-proof']){
  const p=structuredClone(packets[1]),n=p.mapReview.nodes.find(n=>n.checkProposal),e=n.checkProposal;
  if(kind==='check-pixels')e.pixelSha256='0'.repeat(64);
  if(kind==='check-box')e.sourceCheckBox[0]+=10;
  if(kind==='check-score')e.checkMaskIoU=.7;
  if(kind==='check-kind')e.matchedTemplate='node-orange';
  if(kind==='missing-check-proof')delete n.checkProposal;
  assert.equal(observe(frames[1],p).anchorVerified,false,kind);
 }
});
test('near-native completed node requires source-bound proof without aspect rectification',()=>{
 const {execFileSync}=require('node:child_process'),source='artifacts/p4c-random-negative-fresh-run-30-01/neg-native-completed-node-random-2/analysis/manifest.json';
 const raw=execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',`
import json,sys,pathlib
sys.path[:0]=['ml','F:/CRK helper/ml']
from PIL import Image
from map_aspect import recover_map_aspect
from map_action_evidence import inspect_map_actions
from bounded_ocr import BoundedOCRRuntime
from progress_evidence import ProgressRuntime
from english_scene import EnglishSceneRuntime,semantic_state
m=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'));packets=[]
for f in m['cases'][0]['frames'][:2]:
 p=json.loads(pathlib.Path(f['packet']).read_text(encoding='utf-8'));original=p['mapReview']
 with Image.open(f['image']) as im,ProgressRuntime(),BoundedOCRRuntime(960) as runtime,EnglishSceneRuntime():
  p['evidence']=runtime._reread_map_context(im,p['evidence']);p['flow'].update(semantic_state(p['evidence']))
  p['mapReview']=recover_map_aspect(im,p);p['v2MapActions']=inspect_map_actions(im,p)
 p['v2OriginalMapReview']=original;packets.append(p)
print(json.dumps(packets))
`,source],{cwd:path.join(__dirname,'..'),maxBuffer:10*1024*1024});
 const m=JSON.parse(fs.readFileSync(path.join(__dirname,'..',source))),c=m.cases[0],frames=loadReplayFrames(c),packets=JSON.parse(raw);
 const a=observe(frames[0],packets[0]),b=observe(frames[1],packets[1]);
 assert.equal(a.anchorVerified,true);assert.equal(b.anchorVerified,true);
 assert.throws(()=>selectNode(a,b,c.intent,{nowMs:b.frame.atMs}),e=>e.code==='COORDINATE_INVALID');
 assert.equal(packets[1].mapReview.aspectRectification,undefined);
 for(const kind of ['check-pixels','check-box','check-score','check-kind','missing-check-proof']){
  const p=structuredClone(packets[1]),n=p.mapReview.nodes.find(n=>n.checkProposal),e=n.checkProposal;
  if(kind==='check-pixels')e.pixelSha256='0'.repeat(64);
  if(kind==='check-box')e.sourceCheckBox[0]+=10;
  if(kind==='check-score')e.checkMaskIoU=.7;
  if(kind==='check-kind')e.matchedTemplate='node-orange';
  if(kind==='missing-check-proof')delete n.checkProposal;
  assert.equal(observe(frames[1],p).anchorVerified,false,kind);
 }
});
test('orange-only aspect consensus independently binds a supplementary gate candidate',()=>{
 const {execFileSync}=require('node:child_process'),source='artifacts/p4c-random-negative-fresh-run-30-02/neg-native-heal-not-battle-random-1/analysis/manifest.json';
 const raw=execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',`
import json,sys,pathlib
sys.path[:0]=['ml','F:/CRK helper/ml']
from PIL import Image
from map_aspect import recover_map_aspect
from map_action_evidence import inspect_map_actions
from bounded_ocr import BoundedOCRRuntime
from progress_evidence import ProgressRuntime
from english_scene import EnglishSceneRuntime,semantic_state
m=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'));packets=[]
for f in m['cases'][0]['frames'][:2]:
 p=json.loads(pathlib.Path(f['packet']).read_text(encoding='utf-8'));original=p['mapReview']
 with Image.open(f['image']) as im,ProgressRuntime(),BoundedOCRRuntime(960) as runtime,EnglishSceneRuntime():
  p['evidence']=runtime._reread_map_context(im,p['evidence']);p['flow'].update(semantic_state(p['evidence']))
  p['mapReview']=recover_map_aspect(im,p);p['v2MapActions']=inspect_map_actions(im,p)
 p['v2OriginalMapReview']=original;packets.append(p)
print(json.dumps(packets))
`,source],{cwd:path.join(__dirname,'..'),maxBuffer:10*1024*1024});
 const m=JSON.parse(fs.readFileSync(path.join(__dirname,'..',source))),c=m.cases[0],frames=loadReplayFrames(c),packets=JSON.parse(raw);
 const a=observe(frames[0],packets[0]),b=observe(frames[1],packets[1]);
 assert.equal(a.anchorVerified,true);assert.equal(b.anchorVerified,true);
 assert.throws(()=>selectNode(a,b,c.intent,{nowMs:b.frame.atMs}),e=>e.code==='COORDINATE_INVALID');
 for(const kind of ['pixels','index','missing-membership','ratio','box','score','missing-proof']){
  const p=structuredClone(packets[0]),n=p.mapReview.nodes.find(n=>n.gateProposal),e=n.gateProposal,c=p.mapReview.aspectRectification.calibration;
  if(kind==='pixels')e.pixelSha256='0'.repeat(64);
  if(kind==='index')e.geometryEvidence.candidateIndex=999;
  if(kind==='missing-membership')delete c.supplementalGateCandidateIndex;
  if(kind==='ratio')c.candidates[e.geometryEvidence.candidateIndex].ratio*=1.1;
  if(kind==='box')e.geometryEvidence.sourceInnerBox[0]+=10;
  if(kind==='score')e.geometryEvidence.innerScore=.1;
  if(kind==='missing-proof')delete n.gateProposal;
  assert.equal(observe(frames[0],p).anchorVerified,false,kind);
 }
});

test('reference-size line proof binds pixels geometry and unchanged support threshold',()=>{
 const {execFileSync}=require('node:child_process'),source='artifacts/p4c-random-development-60-run-12/dev-primary-zone2-floor2-col3-higher-random-post-change/analysis/manifest.json';
 const raw=execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',`
import json,sys,pathlib
sys.path[:0]=['ml','F:/CRK helper/ml']
from PIL import Image
from map_aspect import recover_map_aspect
from map_action_evidence import inspect_map_actions
from bounded_ocr import BoundedOCRRuntime
from progress_evidence import ProgressRuntime
from english_scene import EnglishSceneRuntime,semantic_state
m=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'));packets=[]
for f in m['cases'][0]['frames'][:2]:
 p=json.loads(pathlib.Path(f['packet']).read_text(encoding='utf-8'));original=p['mapReview']
 with Image.open(f['image']) as im,ProgressRuntime(),BoundedOCRRuntime(960) as runtime,EnglishSceneRuntime():
  p['evidence']=runtime._reread_map_context(im,p['evidence']);p['flow'].update(semantic_state(p['evidence']))
  p['mapReview']=recover_map_aspect(im,p);p['v2MapActions']=inspect_map_actions(im,p)
 p['v2OriginalMapReview']=original;packets.append(p)
print(json.dumps(packets))
`,source],{cwd:path.join(__dirname,'..'),maxBuffer:10*1024*1024});
 const m=JSON.parse(fs.readFileSync(path.join(__dirname,'..',source))),c=m.cases[0],frames=loadReplayFrames(c),packets=JSON.parse(raw);
 const a=observe(frames[0],packets[0]),b=observe(frames[1],packets[1]);
 assert.equal(a.anchorVerified,true);assert.equal(b.anchorVerified,true);
 assert.equal(selectNode(a,b,c.intent,{nowMs:b.frame.atMs}).nodeId,'visible-2-3');
 for(const kind of ['pixels','reference-size','score','node-box','capture','missing-proof']){
  const p=structuredClone(packets[1]),edge=p.mapReview.edges.find(e=>e.from==='visible-1-3'&&e.to==='visible-2-3'),e=edge.lineReference;
  assert.ok(e);
  if(kind==='pixels')e.pixelSha256='0'.repeat(64);
  if(kind==='reference-size')e.referenceNodeSize=59;
  if(kind==='score')e.pixelSupport=.8;
  if(kind==='node-box')e.sourceNodeBoxes[0][0]+=10;
  if(kind==='capture')e.sourceCaptureFrameId='0'.repeat(32);
  if(kind==='missing-proof')delete edge.lineReference;
  assert.equal(observe(frames[1],p).anchorVerified,false,kind);
 }
});

test('completed peer binds the same physical node when adding a missing first row changes IDs',()=>{
 const {execFileSync}=require('node:child_process'),source='artifacts/p4c-reference-line-higher-post-analysis-01/manifest.json';
 const raw=execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',`
import json,sys,pathlib
sys.path[:0]=['ml','F:/CRK helper/ml']
from PIL import Image
from map_aspect import recover_map_aspect
m=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'));f=m['cases'][0]['frames'][2];p=json.loads(pathlib.Path(f['packet']).read_text(encoding='utf-8'))
with Image.open(f['image']) as im:p['mapReview']=recover_map_aspect(im,p)
print(json.dumps(p))
`,source],{cwd:path.join(__dirname,'..'),maxBuffer:10*1024*1024});
 const m=JSON.parse(fs.readFileSync(path.join(__dirname,'..',source))),s=loadReplayFrames(m.cases[0])[2],p=JSON.parse(raw),n=p.mapReview.nodes.find(n=>n.checkProposal);
 assert.ok(n);assert.equal(n.checkProposal.peerNodeId,'visible-3-1');
 assert.equal(adaptMap({...s.frame,png:s.png},p).verified,true);
 const altered=structuredClone(p);altered.mapReview.nodes.find(n=>n.checkProposal).checkProposal.peerNodeId='visible-2-1';
 assert.equal(adaptMap({...s.frame,png:s.png},altered).verified,false);
});

test('anchored near-native preview still requires measured aspect and matching original anchor status',()=>{
 const {execFileSync}=require('node:child_process'),source='artifacts/p4c-near-native-zone9-pre-analysis-01/manifest.json';
 const raw=execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',`
import json,sys,pathlib
sys.path[:0]=['ml','F:/CRK helper/ml']
from PIL import Image
from map_aspect import recover_map_aspect
from preview_identity import inspect_preview_identity
from bounded_ocr import BoundedOCRRuntime
m=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'));f=next(f for f in m['cases'][0]['frames'] if f['frameIndex']==78308)
p=json.loads(pathlib.Path(f['packet']).read_text(encoding='utf-8'));original=p['mapReview']
with Image.open(f['image']) as im,BoundedOCRRuntime(960):
 p['mapReview']=recover_map_aspect(im,p);p['v2Preview']=inspect_preview_identity(im,p)
p['v2OriginalMapReview']=original
print(json.dumps(p))
`,source],{cwd:path.join(__dirname,'..'),maxBuffer:10*1024*1024});
 const m=JSON.parse(fs.readFileSync(path.join(__dirname,'..',source))),c=m.cases[0],s=loadReplayFrames(c)[c.frames.findIndex(f=>f.frameIndex===78308)],packet=JSON.parse(raw);
 assert.equal(adaptPreview({...s.frame,png:s.png},packet).state,'PREVIEW');
 for(const kind of ['purpose','prior-anchor']){
  const p=structuredClone(packet);
  if(kind==='purpose')p.mapReview.aspectRectification.rectificationPurpose='unanchored_near_native_recovery';
  else p.v2OriginalMapReview.absoluteFloorKnown=false;
  assert.equal(adaptPreview({...s.frame,png:s.png},p).state,'UNKNOWN');
 }
});
test('unanchored near-native source uses bound purpose without changing anchored maps',()=>{
 const {execFileSync}=require('node:child_process'),source='artifacts/p4c-time-locator-zone9-pre-analysis-01/manifest.json';
 const raw=execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',`
import json,sys,pathlib
sys.path[:0]=['ml','F:/CRK helper/ml']
from PIL import Image
from map_aspect import recover_map_aspect
from map_action_evidence import inspect_map_actions
m=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'));packets=[]
for f in m['cases'][0]['frames'][1:3]:
 p=json.loads(pathlib.Path(f['packet']).read_text(encoding='utf-8'));original=p['mapReview']
 with Image.open(f['image']) as im:p['mapReview']=recover_map_aspect(im,p);p['v2MapActions']=inspect_map_actions(im,p)
 p['v2OriginalMapReview']=original;packets.append(p)
print(json.dumps(packets))
`,source],{cwd:path.join(__dirname,'..'),maxBuffer:10*1024*1024});
 const m=JSON.parse(fs.readFileSync(path.join(__dirname,'..',source))),c=m.cases[0],frames=loadReplayFrames(c).slice(1,3),packets=JSON.parse(raw);
 const a=observe(frames[0],packets[0]),b=observe(frames[1],packets[1]);
 assert.equal(selectNode(a,b,c.intent,{nowMs:b.frame.atMs}).nodeId,'visible-1-4');
 for(const kind of ['purpose','prior-anchor','prior-frame','missing-prior']){
  const altered=structuredClone(packets[1]);
  if(kind==='purpose')altered.mapReview.aspectRectification.rectificationPurpose='pixel_aspect_recovery';
  if(kind==='prior-anchor')altered.v2OriginalMapReview.absoluteFloorKnown=true;
  if(kind==='prior-frame')altered.v2OriginalMapReview.frameId='0'.repeat(20);
  if(kind==='missing-prior')delete altered.v2OriginalMapReview;
  assert.equal(observe(frames[1],altered).verified,false,kind);
 }
});
test('small original node core refines physical extent while retaining detector score',()=>{
 const {execFileSync}=require('node:child_process'),source='artifacts/p4c-random-development-60-run-06/zone-9-first-battle-random-fixed/analysis/manifest.json';
 const raw=execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',`
import json,sys,pathlib
sys.path[:0]=['ml','F:/CRK helper/ml']
from PIL import Image
from map_aspect import recover_map_aspect
from map_action_evidence import inspect_map_actions
m=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'));packets=[]
for f in m['cases'][0]['frames'][:2]:
 p=json.loads(pathlib.Path(f['packet']).read_text(encoding='utf-8'))
 with Image.open(f['image']) as im:p['mapReview']=recover_map_aspect(im,p);p['v2MapActions']=inspect_map_actions(im,p)
 packets.append(p)
print(json.dumps(packets))
`,source],{cwd:path.join(__dirname,'..'),maxBuffer:10*1024*1024});
 const m=JSON.parse(fs.readFileSync(path.join(__dirname,'..',source))),c=m.cases[0],frames=loadReplayFrames(c),packets=JSON.parse(raw);
 const a=observe(frames[0],packets[0]),b=observe(frames[1],packets[1]);
 assert.equal(selectNode(a,b,c.intent,{nowMs:b.frame.atMs}).nodeId,'visible-1-4');
 const altered=structuredClone(packets[1]);altered.mapReview.nodes.find(n=>n.id==='visible-1-4').orangeRefinement.iconCoreEvidence.runnerUpScore=.99;
 assert.equal(observe(frames[1],altered).verified,false);
});
test('original candidate precision survives rounded legacy analysis geometry',()=>{
 const {execFileSync}=require('node:child_process');
 const source='artifacts/p4c-proposal-controls-nine-analysis-02/manifest.json';
 const raw=execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',`
import json,sys,pathlib
sys.path[:0]=['ml','F:/CRK helper/ml']
from PIL import Image
from map_aspect import recover_map_aspect
from preview_identity import inspect_preview_identity
from bounded_ocr import BoundedOCRRuntime
m=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
f=next(f for f in m['cases'][7]['frames'] if f['frameIndex']==20224)
p=json.loads(pathlib.Path(f['packet']).read_text(encoding='utf-8'))
with Image.open(f['image']) as im,BoundedOCRRuntime(960):
 p['mapReview']=recover_map_aspect(im,p);p['v2Preview']=inspect_preview_identity(im,p)
print(json.dumps(p))
`,source],{cwd:path.join(__dirname,'..'),maxBuffer:10*1024*1024});
 const m=JSON.parse(fs.readFileSync(path.join(__dirname,'..',source))),c=m.cases[7],frames=loadReplayFrames(c),s=frames[c.frames.findIndex(f=>f.frameIndex===20224)];
 assert.equal(adaptPreview({...s.frame,png:s.png},JSON.parse(raw)).state,'PREVIEW');
});
test('original inner-icon candidate supports glowing node and rejects corrupted producer proof',()=>{
 const {execFileSync}=require('node:child_process');
 const source='artifacts/p4c-random-development-60-run-05/zone-8-first-battle-random-fixed/analysis/manifest.json';
 const raw=execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',`
import json,sys,pathlib
sys.path[:0]=['ml','F:/CRK helper/ml']
from PIL import Image
from map_aspect import recover_map_aspect
from map_action_evidence import inspect_map_actions
m=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'));packets=[]
for f in m['cases'][0]['frames'][:2]+[next(f for f in m['cases'][0]['frames'] if f['frameIndex']==64890)]:
 p=json.loads(pathlib.Path(f['packet']).read_text(encoding='utf-8'))
 with Image.open(f['image']) as im:
  p['mapReview']=recover_map_aspect(im,p);p['v2MapActions']=inspect_map_actions(im,p)
 packets.append(p)
print(json.dumps(packets))
`,source],{cwd:path.join(__dirname,'..'),maxBuffer:10*1024*1024});
 const m=JSON.parse(fs.readFileSync(path.join(__dirname,'..',source))),c=m.cases[0],frames=loadReplayFrames(c),packets=JSON.parse(raw);
 const a=observe(frames[0],packets[0]),b=observe(frames[1],packets[1]);
 const proof=selectNode(a,b,c.intent,{nowMs:b.frame.atMs});assert.equal(proof.nodeId,'visible-1-4');
 for(const kind of ['pixels','frame','candidate','score','injected-box','rectified-pixels','missing-proposal']){
  const altered=structuredClone(packets[1]),n=altered.mapReview.nodes.find(n=>n.id===proof.nodeId),e=n.pixelProposal;
  assert(e);
  if(kind==='pixels')e.pixelSha256='0'.repeat(64);
  if(kind==='frame')e.sourceCaptureFrameId='0'.repeat(32);
  if(kind==='candidate')e.geometryEvidence.candidateIndex=999;
  if(kind==='score')n.score=.99;
  if(kind==='injected-box')e.injectedAnalysisBox[0]+=20;
  if(kind==='rectified-pixels')e.rectifiedPixelSha256='0'.repeat(64);
  if(kind==='missing-proposal')delete n.pixelProposal;
  assert.equal(observe(frames[1],altered).verified,false,kind);
 }
 const early=packets[2],earlyFrame=frames[m.cases[0].frames.findIndex(f=>f.frameIndex===64890)];
 // This bridge checks map authority; Python separately checks preview identity.
 assert.equal(observe(earlyFrame,early).verified,true);
 for(const kind of ['core-margin','core-crop','core-alignment','core-template','missing-core']){
  const altered=structuredClone(early),n=altered.mapReview.nodes.find(n=>n.pixelProposal?.geometryEvidence.iconCoreEvidence),e=n.pixelProposal.geometryEvidence.iconCoreEvidence;
  if(kind==='core-margin')e.runnerUpScore=e.score;
  if(kind==='core-crop')e.sourceCropBox[0]+=10;
  if(kind==='core-alignment')e.alignmentPx[0]=100;
  if(kind==='core-template')e.template='node-gray';
  if(kind==='missing-core')delete n.pixelProposal.geometryEvidence.iconCoreEvidence;
  assert.equal(observe(earlyFrame,altered).verified,false,kind);
 }
});
test('actual pixel-derived rectification supports one source-coordinate selection proof',()=>{
 const {c,frames}=fixture(),a=observe(frames[0]),b=observe(frames[1]);
 const proof=selectNode(a,b,c.intent,{nowMs:b.frame.atMs});const [x,y,w,h]=c.clientBox;
 assert(proof.point[0]>x&&proof.point[0]<x+w&&proof.point[1]>y&&proof.point[1]<y+h);assert.equal(proof.nodeId,'visible-1-2');
});

test('actual distorted selected preview confirms with independently derived vertical lattice',()=>{
 const {execFileSync}=require('node:child_process');
 const raw=execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',`
import json,sys,pathlib
sys.path[:0]=['ml','F:/CRK helper/ml']
from PIL import Image
from bounded_ocr import BoundedOCRRuntime
from preview_identity import inspect_preview_identity
m=json.loads(pathlib.Path('artifacts/p4c-random-pilot-analysis-02/manifest.json').read_text(encoding='utf-8'))
packets=[]
for index in [0,2]:
 c=m['cases'][index];f=c['frames'][-1];p=json.loads(pathlib.Path(f['packet']).read_text(encoding='utf-8'))
 with Image.open(f['image']) as im,BoundedOCRRuntime(960):p['v2Preview']=inspect_preview_identity(im,p)
 packets.append(p)
print(json.dumps(packets))
`],{cwd:path.join(__dirname,'..'),maxBuffer:10*1024*1024});
 const m=JSON.parse(fs.readFileSync(path.join(__dirname,'../artifacts/p4c-random-pilot-analysis-02/manifest.json'))),packets=JSON.parse(raw);
 for(const [j,index] of [0,2].entries()){
  const s=loadReplayFrames(m.cases[index]).at(-1),p=packets[j];
  assert.equal(p.v2Preview.verified,true);
  const observed=adaptPreview({...s.frame,png:s.png},p);
  assert.equal(observed.state,'PREVIEW');assert.equal(observed.verified,true);
  const altered=structuredClone(p);altered.v2Preview.selectedNode.floor=2;altered.v2Preview.recoveredNodes[0].floor=2;
  assert.notEqual(adaptPreview({...s.frame,png:s.png},altered).state,'PREVIEW');
  if(index===2){
   const wrongSize=structuredClone(p);wrongSize.v2Preview.recoveredNodes[0].iconSizeEvidence.candidateIndex=999;
   assert.notEqual(adaptPreview({...s.frame,png:s.png},wrongSize).state,'PREVIEW');
  }
 }
});
test('source swapped or inconsistent rectification evidence cannot acquire click authority',()=>{
 const {c,frames}=fixture(),a=observe(frames[0]);
 for(const kind of ['image','pixels','frame','matrix','analysis-box','consensus','missing']){
  const p=structuredClone(frames[1].packet),e=p.mapReview.aspectRectification;
  if(kind==='image')e.sourceImageSha256='0'.repeat(64);
  else if(kind==='pixels')e.pixelSha256='0'.repeat(64);
  else if(kind==='frame')e.sourceCaptureFrameId='0'.repeat(32);
  else if(kind==='matrix')e.inverseMatrix[0][0]*=1.1;
  else if(kind==='analysis-box')p.mapReview.nodes[0].analysisBox[0]+=10;
  else if(kind==='consensus')e.calibration.consensus=[0,0,0];
  else if(kind==='missing')delete p.mapReview.aspectRectification;
  const b=observe(frames[1],p);assert.equal(b.verified,false,kind);assert.equal(b.anchorVerified,false,kind);
  assert.throws(()=>selectNode(a,b,c.intent,{nowMs:b.frame.atMs}),/ANCHOR_MISSING/,kind);
 }
});

test('actual circle-centered selection stays stable and rejects unbound center measurements',()=>{
 const {execFileSync}=require('node:child_process');
 const raw=execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',`
import json,sys,pathlib
sys.path[:0]=['ml','F:/CRK helper/ml']
from PIL import Image
from map_aspect import recover_map_aspect
from map_action_evidence import inspect_map_actions
m=json.loads(pathlib.Path('artifacts/p4c-random-pilot-analysis-04/manifest.json').read_text(encoding='utf-8'))
packets=[]
for f in m['cases'][2]['frames'][:2]:
 p=json.loads(pathlib.Path(f['packet']).read_text(encoding='utf-8'))
 with Image.open(f['image']) as im:
  p['mapReview']=recover_map_aspect(im,p);p['v2MapActions']=inspect_map_actions(im,p)
 packets.append(p)
print(json.dumps(packets))
`],{cwd:path.join(__dirname,'..'),maxBuffer:10*1024*1024});
 const m=JSON.parse(fs.readFileSync(path.join(__dirname,'../artifacts/p4c-random-pilot-analysis-04/manifest.json'))),c=m.cases[2],frames=loadReplayFrames(c),packets=JSON.parse(raw);
 const a=observe(frames[0],packets[0]),b=observe(frames[1],packets[1]);
 const proof=selectNode(a,b,c.intent,{nowMs:b.frame.atMs});assert.equal(proof.nodeId,'visible-1-2');
 const altered=structuredClone(packets[1]);
 const selected=altered.mapReview.nodes.find(n=>n.id===proof.nodeId);
 (selected.orangeRefinement||selected.centerRefinement).candidateIndex=999;
 assert.equal(observe(frames[1],altered).verified,false);
});

test('static gate arrow pixels support actual second-source selection and require bound proof',()=>{
 const {execFileSync}=require('node:child_process');
 const source='artifacts/p4c-random-development-60-run-01/zone-2-first-battle-random-fixed/analysis/manifest.json';
 const raw=execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',`
import json,sys,pathlib
sys.path[:0]=['ml','F:/CRK helper/ml']
from PIL import Image
from map_aspect import recover_map_aspect
from map_action_evidence import inspect_map_actions
m=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'));packets=[]
for f in m['cases'][0]['frames'][:2]:
 p=json.loads(pathlib.Path(f['packet']).read_text(encoding='utf-8'))
 with Image.open(f['image']) as im:
  p['mapReview']=recover_map_aspect(im,p);p['v2MapActions']=inspect_map_actions(im,p)
 packets.append(p)
print(json.dumps(packets))
`,source],{cwd:path.join(__dirname,'..'),maxBuffer:10*1024*1024});
 const m=JSON.parse(fs.readFileSync(path.join(__dirname,'..',source))),c=m.cases[0],frames=loadReplayFrames(c),packets=JSON.parse(raw);
 const a=observe(frames[0],packets[0]),b=observe(frames[1],packets[1]);
 assert.equal(selectNode(a,b,c.intent,{nowMs:b.frame.atMs}).nodeId,'visible-1-2');
 const altered=structuredClone(packets[1]);altered.mapReview.nodes.find(n=>n.type==='exit').gateRefinement.pixelSha256='0'.repeat(64);
 assert.equal(observe(frames[1],altered).verified,false);
});
