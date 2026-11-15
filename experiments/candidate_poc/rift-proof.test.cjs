const {test}=require('node:test'),assert=require('node:assert/strict');
const {hsv,isPurple,validateRiftProof,dispatchOnce}=require('./rift-proof.cjs');
test('rift availability is purple-specific, not generic saturation or orange',()=>{
 assert.equal(isPurple(...hsv(80,40,210)),true);
 assert.equal(isPurple(...hsv(150,150,150)),false);
 assert.equal(isPurple(...hsv(240,130,20)),false);
});
test('serialized or invented rift selection grants no authority',()=>{
 assert.throws(()=>validateRiftProof({kind:'rift-research-selection',verified:true}),/RIFT_PROOF_INVALID/);
});
test('an already open rift preview cannot authorize another selection',()=>{
 const fs=require('fs'),path=require('path'),{loadReplayFrames}=require('../../lib/replay-case.cjs');
 const {planSupported}=require('./rift-transaction.cjs');
 const m=JSON.parse(fs.readFileSync(path.join(__dirname,'../../artifacts/rift-episode-20261113-01/analysis/manifest.json')));
 const f=loadReplayFrames(m.cases[0],m.videoSha256,1);
 assert.equal(planSupported(f.slice(2)).intent,null);
});
test('a selected rift cannot be dispatched from an expired or changed current frame',()=>{
 const fs=require('fs'),path=require('path'),{loadReplayFrames}=require('../../lib/replay-case.cjs'),{planSupported}=require('./rift-transaction.cjs');
 const m=JSON.parse(fs.readFileSync(path.join(__dirname,'../../artifacts/rift-episode-20261113-01/analysis/manifest.json'))),f=loadReplayFrames(m.cases[0],m.videoSha256,1);
 let p=planSupported(f.slice(0,2)).proof;
 assert.throws(()=>dispatchOnce(p,{nowMs:p.frame.atMs+2501,currentFrame:f[1].frame}),/FRAME_INVALID/);
 p=planSupported(f.slice(0,2)).proof;
 assert.throws(()=>dispatchOnce(p,{nowMs:p.frame.atMs,currentFrame:{...f[1].frame,geometryVersion:'changed'}}),/RIFT_CURRENT_FRAME_CHANGED/);
});
test('a caller supplied confirmation boolean cannot replace an issued preview receipt',()=>{
 const {validateConfirmedRift}=require('./rift-transaction.cjs');
 assert.throws(()=>validateConfirmedRift({state:'RIFT_PREVIEW_CONFIRMED_RESEARCH',nativeContextIndependentlyVerified:true},null),/RIFT_CONFIRMATION_PROOF_INVALID/);
});
