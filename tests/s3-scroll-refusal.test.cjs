const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const {loadReplayFrames}=require('../lib/replay-case.cjs'),{adaptMap}=require('../lib/observer-adapter.cjs'),{selectNode}=require('../lib/node-selector.cjs');
test('actual S3 scroll frames with missing candidates cannot issue selection authority',()=>{
 const m=JSON.parse(fs.readFileSync('artifacts/performance-20261027/profile-after-01/analysis/manifest.json'));
 const c=m.cases.find(c=>c.id==='dev-earlier-0Q-zone4-floor1-col4');
 const frames=loadReplayFrames(c,m.videoSha256,m.analysis.observerContractVersion);
 assert.deepEqual(c.frames.map(f=>f.frameIndex),[46047,46057]);
 const observations=frames.map(s=>adaptMap({...s.frame,png:s.png},s.packet));
 for(const o of observations){assert.equal(o.state,'MAP');assert.equal(o.verified,true);assert.equal(o.anchorVerified,false);}
 assert.throws(()=>selectNode(observations[0],observations[1],c.intent,{nowMs:observations[1].frame.atMs}),{code:'ANCHOR_MISSING'});
});
