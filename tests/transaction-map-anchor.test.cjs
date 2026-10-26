'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {runReplay}=require('../lib/replay-runner.cjs'),{loadReplayFrames}=require('../lib/replay-case.cjs');
const {adaptMap,adaptPreview,readDirectMapAnchor}=require('../lib/observer-adapter.cjs'),{selectNode}=require('../lib/node-selector.cjs'),{verifyPreview}=require('../lib/preview-verifier.cjs');
function fixture(){const m=JSON.parse(fs.readFileSync(path.join(__dirname,'../artifacts/p4c-random-development-60-run-16/dev-primary-zone3-floor3-col1-higher-random-post-change/analysis/manifest.json'))),c=m.cases[0];return {c,frames:loadReplayFrames(c)};}
function observation(s){const f={...s.frame,png:s.png};return s.packet.flow.state==='MAP'&&!s.packet.v2Preview?.verified?adaptMap(f,s.packet):adaptPreview(f,s.packet);}
async function replay(mode){const {c,frames}=fixture();return runReplay({frames,intent:c.intent,gate:{windowMs:c.gateWindowMs,clientBox:c.clientBox,previewFromPtsMs:c.previewFromPtsMs},observe:async s=>{const o=observation(s);if(o.state==='MAP'&&s.frame.atMs>frames[1].frame.atMs){if(mode==='clone')return structuredClone(o);if(mode==='weak')o.verified=false;if(mode==='zone')o.zone=9;}if(o.registrationSource){if(mode==='unseen'){o.registrationSource.frameId='f'.repeat(32);o.registrationSource.imageSha256='e'.repeat(64);}if(mode==='pixels')o.registrationSource.pixelSha256='d'.repeat(64);}return o;}});}
test('actual post-resize map root admits matching previews without changing the one-click transaction',async()=>{
 const r=await replay();assert.equal(r.state,'PREVIEW_TIMEOUT');assert.equal(r.transaction.observations.filter(x=>x.verdict.kind==='match').length,2);assert.equal(r.actions.length,1);assert.equal(r.nativeActions,0);assert.equal(r.g4Complete,false);
 const source=r.observations.find(o=>o.registrationSource).registrationSource,root=r.transaction.mapAnchors.find(x=>x.frame.id===source.frameId);assert.ok(root);assert.equal(root.frame.sha256,source.imageSha256);assert.equal(root.pixelSha256,source.pixelSha256);assert.ok(root.frame.atMs>r.transaction.receiptAtMs);assert.notEqual(root.frame.geometryVersion,r.transaction.proof.frame.geometryVersion);assert.equal(r.actions[0].geometryVersion,r.transaction.proof.frame.geometryVersion);assert.equal(r.transaction.deadlineMs,r.transaction.sentAtMs+15000);
});
test('copied weak or wrong-zone maps cannot introduce a semantic reference',async()=>{
 for(const mode of ['clone','weak','zone']){const r=await replay(mode);assert.equal(r.state,mode==='weak'?'EVIDENCE_UNVERIFIED':'PREVIEW_REGISTRATION_SOURCE_MISMATCH',mode);assert.equal(r.actions.length,1);assert.equal(r.nativeActions,0);}
});
test('unseen or different-pixel source stays rejected even with real post-click map roots',async()=>{
 for(const mode of ['unseen','pixels']){const r=await replay(mode);assert.equal(r.state,'PREVIEW_REGISTRATION_SOURCE_MISMATCH',mode);assert.ok(r.transaction.mapAnchors.length>0);assert.equal(r.actions.length,1);}
});
test('additional sources require the current geometry and a positive age at most 2500ms',()=>{
 const {c,frames}=fixture(),a=observation(frames[0]),b=observation(frames[1]),proof=selectNode(a,b,c.intent,{nowMs:b.frame.atMs}),source={frame:frames[2].frame,pixelSha256:frames[2].packet.binding.pixelSha256},o=observation(frames[9]);assert.equal(o.state,'PREVIEW');
 for(const [age,expected] of [[1,'match'],[2500,'match'],[0,'reject'],[2501,'reject']]){const p=structuredClone(o);p.frame.atMs=source.frame.atMs+age;assert.equal(verifyPreview(proof,p,{mapSources:[source]}).kind,expected,String(age));}
 for(const field of ['geometryVersion','windowKey','origin','width']){const p=structuredClone(o);if(field==='origin')p.frame.origin=[1,2];else if(field==='width')p.frame.width++;else p.frame[field]='other';assert.equal(verifyPreview(proof,p,{mapSources:[source]}).kind,'reject',field);}
});

test('map root authority cannot survive copying or mutation of pixels geometry or lattice',()=>{
 const {frames}=fixture();
 for(const mutate of [o=>o.frame.sha256='a'.repeat(64),o=>o.frame.origin=[1,2],o=>o.mapAnchorAuthority.pixelSha256='b'.repeat(64),o=>o.nodes[0].floor=31,o=>o.zone=9]){
  const o=observation(frames[2]);assert.ok(readDirectMapAnchor(o));mutate(o);assert.equal(readDirectMapAnchor(o),null);
 }
 const o=observation(frames[2]);assert.equal(readDirectMapAnchor(structuredClone(o)),null);
 const certificate=readDirectMapAnchor(o);certificate.frame.sha256='c'.repeat(64);assert.notDeepEqual(readDirectMapAnchor(o),certificate);
});
test('map captured before a successful late receipt cannot become a transaction root',async()=>{
 const {PreviewSession}=require('../lib/preview-session.cjs'),{c,frames}=fixture(),a=observation(frames[0]),b=observation(frames[1]);
 const proof=selectNode(a,b,c.intent,{nowMs:b.frame.atMs});let now=b.frame.atMs;
 const session=new PreviewSession({clock:()=>now,dispatch:action=>{now=frames[3].frame.atMs;return {status:'sent',transactionId:action.transactionId,frameId:action.frameId};}});
 await session.start(proof);session.observe(observation(frames[2]));assert.equal(session.snapshot().mapAnchors.length,0);assert.equal(session.snapshot().state,'WAIT_PREVIEW');
});
