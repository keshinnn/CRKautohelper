const {test}=require('node:test');
const assert=require('node:assert/strict');
const {PreviewSession}=require('../lib/preview-session.cjs');
const {selectNode}=require('../lib/node-selector.cjs');
const {map,intent,preview}=require('./fixtures.cjs');

function setup({video=false,dispatch}={}) {
 let now=1000;const sent=[];
 const a=map('a',800),b=map();
 if(video){a.frame.sourcePtsMs=800;b.frame.sourcePtsMs=1000;}
 const proof=selectNode(a,b,intent,{nowMs:now});
 const session=new PreviewSession({clock:()=>now,dispatch:action=>{
  sent.push(action);return dispatch?dispatch(action):Promise.resolve({status:'sent',transactionId:action.transactionId,frameId:action.frameId});
 }});
 return {session,proof,sent,time:t=>now=t};
}
test('pre-dispatch previews cannot confirm delayed input',async()=>{
 const x=setup();x.time(2000);await x.session.start(x.proof);
 assert.equal(x.session.observe(preview()).state,'FRAME_INVALID');
 x.session.observe(preview('d',1400));assert.equal(x.sent.length,1);
});
test('pending transport and missing observations settle on explicit deadline tick',async()=>{
 let release;const x=setup({dispatch:a=>new Promise(r=>release=()=>r({status:'sent',transactionId:a.transactionId,frameId:a.frameId}))});
 const running=x.session.start(x.proof);x.time(16000);
 assert.equal(x.session.tick().state,'DISPATCH_UNCERTAIN');
 assert.equal((await running).state,'DISPATCH_UNCERTAIN');
 release();await Promise.resolve();assert.equal(x.session.snapshot().state,'DISPATCH_UNCERTAIN');
 const y=setup();await y.session.start(y.proof);y.time(16000);
 assert.equal(y.session.snapshot().state,'PREVIEW_TIMEOUT');
});
test('video PTS cannot be omitted NaN repeated or reversed across previews',async()=>{
 for(const pts of [undefined,NaN,1000,500]){
  const x=setup({video:true});await x.session.start(x.proof);x.time(1200);
  const o=preview();o.frame.sourcePtsMs=pts;
  assert.equal(x.session.observe(o).state,'FRAME_INVALID');
 }
 const a=map('a',800),b=map();a.frame.sourcePtsMs=800;
 assert.throws(()=>selectNode(a,b,intent,{nowMs:1000}));
});
test('stable target with changed predecessor identity or geometry rejects authority',()=>{
 for(const mutate of [o=>o.nodes[2].column=2,o=>o.nodes[2].box[0]+=30,o=>{o.nodes[2].id='new';o.current.nodeId='new';o.edges[0].from='new';}]){
  const a=map('a',800),b=map();
  for(const o of [a,b]){o.nodes[1].floor=2;o.nodes[2].floor=1;o.nodes[2].completed=true;o.current={verified:true,nodeId:'other'};o.edges=[{from:'other',to:'target',pixelSupport:.99}];}
  mutate(b);assert.throws(()=>selectNode(a,b,{...intent,floor:2},{nowMs:1000}));
 }
});
test('transaction evidence retains source frames intent action receipt and observations independently',async()=>{
 const x=setup();await x.session.start(x.proof);x.time(1200);x.session.observe(preview());x.time(1400);x.session.observe(preview('d',1400));
 const s=x.session.snapshot();assert.equal(s.proof.previousFrame.id,'a');assert.equal(s.proof.previousFrame.sha256,'a'.repeat(64));
 assert.deepEqual(s.action.clientPoint,[450,250]);assert.equal(s.receipt.status,'sent');assert.equal(s.deadlineMs,16000);
 assert.equal(s.observations.length,2);assert.equal(s.observations[1].verdict.kind,'match');
 s.proof.intent.column=1;s.action.clientPoint[0]=0;s.observations[0].observation.selectedNode.column=1;
 assert.equal(x.session.snapshot().proof.intent.column,4);assert.equal(x.session.snapshot().action.clientPoint[0],450);
});
test('trace delay cannot authorize preview captured before actual dispatch',async()=>{
 let now=1000;const proof=selectNode(map('a',800),map(),intent,{nowMs:1000});
 const s=new PreviewSession({clock:()=>now,trace:()=>{now=2000;},dispatch:a=>({status:'sent',transactionId:a.transactionId,frameId:a.frameId})});
 await s.start(proof);assert.equal(s.observe(preview()).state,'FRAME_INVALID');
});
test('late receipt cannot revive transaction even without an intervening tick',async()=>{
 let release;const x=setup({dispatch:a=>new Promise(r=>release=()=>r({status:'sent',transactionId:a.transactionId,frameId:a.frameId}))});
 const started=x.session.start(x.proof);x.time(16000);release();
 assert.equal((await started).state,'DISPATCH_UNCERTAIN');assert.equal(x.sent.length,1);
});
