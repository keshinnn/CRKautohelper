const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const {adaptPreview}=require('../lib/observer-adapter.cjs'),{loadReplayFrames}=require('../lib/replay-case.cjs');
const currentPackets={};
function fixture(index=11){const m=JSON.parse(fs.readFileSync('artifacts/p4c-random-development-60-run-16/dev-primary-zone3-floor3-col1-higher-random-post-change/analysis/manifest.json'));const source=loadReplayFrames(m.cases[0])[index];return {frame:{...source.frame,png:source.png},p:JSON.parse(currentPackets[index]??=require('node:child_process').execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',"import sys,json,io;sys.path[:0]=['ml','tests','F:/CRK helper/ml'];from test_preview_panel_scope import PreviewPanelScopeTests;from PIL import Image;from map_aspect import recover_map_aspect;from preview_registration import recover_preview_anchor;from preview_identity import inspect_preview_identity;a,b=PreviewPanelScopeTests().frames("+index+");im=Image.open(io.BytesIO(b['png'])).convert('RGB');b['packet']['mapReview']=recover_map_aspect(im,b['packet']);b['packet']['v2TrackedMap']=recover_preview_anchor(a,b);b['packet']['v2Preview']=inspect_preview_identity(im,b['packet']);print(json.dumps(b['packet'],ensure_ascii=True))"],{encoding:'utf8',maxBuffer:10000000}))};}
function change(p,mutate){mutate(p.mapReview.aspectRectification);mutate(p.v2TrackedMap.mapReview.aspectRectification);mutate(p.v2Preview.recoveredMapReview.aspectRectification);}
test('actual scoped relative map still needs independent registered preview pixels',()=>{const {frame,p}=fixture();assert.equal(adaptPreview(frame,p).verified,true);assert.equal(p.mapReview.absoluteFloorKnown,false);assert.equal(p.v2Preview.selectedNode.floor,3);});
test('missing or altered scope controls pixels exclusion boundary or source geometry rejects',()=>{
 for(const mutate of [e=>delete e.candidateScope,e=>e.candidateScope.cutX++,e=>e.candidateScope.pixelSha256='a'.repeat(64),e=>e.candidateScope.enterEvidence.score=.8,e=>e.candidateScope.greenArea=0,e=>e.candidateScope.excluded[0].center[0]=0,e=>e.candidateScope.sourceSize[0]++,e=>e.candidateScope.greenButtonBox[0]++]){
  const {frame,p}=fixture();change(p,mutate);const o=adaptPreview(frame,p);assert.equal(o.verified,false);assert.equal(o.reason,'ASPECT_RECTIFICATION_UNBOUND');
 }
});


test('source-only recovered heal keeps the later preview valid and rejects missing or altered heal proof',()=>{
 const {frame,p}=fixture(12);assert.equal(adaptPreview(frame,p).verified,true);
 const maps=q=>[q.mapReview,q.v2TrackedMap.mapReview,q.v2Preview.recoveredMapReview];assert.ok(maps(p)[0].nodes.some(n=>n.healProposal));
 for(const mutate of [n=>delete n.healProposal,n=>n.healProposal.iconScore=.89,n=>n.healProposal.greenArea=0,n=>n.healProposal.sourceBox[0]++,n=>n.healProposal.pixelSha256='f'.repeat(64),n=>n.healProposal.peerSourceBoxes=[]]){
  const q=structuredClone(p);for(const m of maps(q)){const n=m.nodes.find(n=>n.healProposal);assert.ok(n);mutate(n);}
  assert.equal(adaptPreview(frame,q).verified,false);
 }
});
