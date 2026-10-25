const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {adaptMap,adaptPreview}=require('../lib/observer-adapter.cjs'),{loadReplayFrames}=require('../lib/replay-case.cjs'),{selectNode}=require('../lib/node-selector.cjs');
function fixture(){const m=JSON.parse(fs.readFileSync(path.join(__dirname,'../artifacts/p4c-aspect-map-bridge-02/manifest.json')));const c=m.cases[0];return {c,frames:loadReplayFrames(c)};}
function observe(s,p=s.packet){return adaptMap({...s.frame,png:s.png},p);}
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
 altered.mapReview.nodes.find(n=>n.id===proof.nodeId).centerRefinement.candidateIndex=999;
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
