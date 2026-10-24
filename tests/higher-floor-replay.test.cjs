'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {runReplay}=require('../lib/replay-runner.cjs');
const {adaptMap,adaptPreview}=require('../lib/observer-adapter.cjs');
function load(){
 const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'../artifacts/p4c-dev-floor2-closed-analysis-01/manifest-rounded-gate.json'),'utf8'));
 const c=manifest.cases[0];
 return {c,frames:c.frames.map(e=>{
  const png=fs.readFileSync(e.image),packet=JSON.parse(fs.readFileSync(e.packet,'utf8'));
  assert.equal(crypto.createHash('sha256').update(png).digest('hex'),e.sha256);
  return {png,packet,frame:{id:packet.binding.frameId,sha256:e.sha256,atMs:e.atMs,sourcePtsMs:e.sourcePtsMs,width:e.size[0],height:e.size[1],geometryVersion:e.geometryVersion,windowKey:'offline:floor2',origin:[0,0]}};
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
