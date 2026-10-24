'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {runReplay}=require('../lib/replay-runner.cjs');
const {adaptMap,adaptPreview}=require('../lib/observer-adapter.cjs');
function load(file='../artifacts/p4c-dev-floor2-closed-analysis-01/manifest-rounded-gate.json',windowKey='offline:floor2'){
 const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,file),'utf8'));
 const c=manifest.cases[0];
 return {c,frames:c.frames.map(e=>{
  const png=fs.readFileSync(e.image),packet=JSON.parse(fs.readFileSync(e.packet,'utf8'));
  assert.equal(crypto.createHash('sha256').update(png).digest('hex'),e.sha256);
  return {png,packet,frame:{id:packet.binding.frameId,sha256:e.sha256,atMs:e.atMs,sourcePtsMs:e.sourcePtsMs,width:e.size[0],height:e.size[1],geometryVersion:e.geometryVersion,windowKey,origin:[0,0]}};
 })};
}
async function replay({c,frames}){
 return runReplay({frames,intent:c.intent,gate:{windowMs:c.gateWindowMs,clientBox:c.clientBox,previewFromPtsMs:c.frames[2].sourcePtsMs},observe:async s=>{
  const f={...s.frame,png:s.png};return s.packet.flow.state==='MAP'&&!s.packet.v2Preview?.verified?adaptMap(f,s.packet):adaptPreview(f,s.packet);
 }});
}
test('actual second-floor video closes through independent completed path and preview pixels',async()=>{
 const result=await replay(load());assert.equal(result.state,'PREVIEW_CONFIRMED');assert.equal(result.actions.length,1);assert.equal(result.nativeActions,0);assert.equal(result.g4Complete,false);
 assert.equal(result.transaction.proof.predecessors[0].id,'visible-1-3');
 assert.equal(result.observations.at(-1).selectedNode.floor,2);assert.equal(result.observations.at(-1).selectedNode.column,3);
});
test('same real sequence without completed pixels cannot follow the successful human branch',async()=>{
 const data=load();for(const s of data.frames)s.packet.v2MapActions.current=null;
 const result=await replay(data);assert.equal(result.state,'CURRENT_POSITION_UNPROVEN');assert.equal(result.actions.length,0);assert.equal(result.passed,false);
});
test('actual third-floor auto-scroll closes with the selection source anchor and all transition frames',async()=>{
 const data=load('../artifacts/p4c-registration-closed-analysis-01/manifest.json','offline:original-video');
 assert.equal(data.frames.length,29);
 for(let i=2;i<data.c.frames.length;i++)assert.equal(data.c.frames[i].frameIndex,data.c.frames[i-1].frameIndex+1);
 const result=await replay(data);assert.equal(result.state,'PREVIEW_CONFIRMED');assert.equal(result.actions.length,1);assert.equal(result.nativeActions,0);
 assert.equal(result.observations.at(-1).selectedNode.floor,3);
 assert.equal(result.observations.at(-1).registrationSource.imageSha256,data.frames[0].frame.sha256);
});
test('registered preview from a different source cannot confirm this actual third-floor transaction',async()=>{
 const data=load('../artifacts/p4c-registration-closed-analysis-01/manifest.json','offline:original-video');
 for(const s of data.frames){
  const p=s.packet;if(!p.v2TrackedMap?.verified)continue;
  p.v2TrackedMap.sourceImageSha256='b'.repeat(64);
  p.v2TrackedMap.mapReview.registrationEvidence.sourceImageSha256='b'.repeat(64);
  if(p.v2Preview?.recoveredMapReview?.registrationEvidence)p.v2Preview.recoveredMapReview.registrationEvidence.sourceImageSha256='b'.repeat(64);
 }
 const result=await replay(data);assert.equal(result.state,'PREVIEW_REGISTRATION_SOURCE_MISMATCH');assert.equal(result.passed,false);assert.equal(result.actions.length,1);
});
