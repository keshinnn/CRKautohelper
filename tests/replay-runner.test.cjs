const {test}=require('node:test'),assert=require('node:assert/strict');
const {runReplay}=require('../lib/replay-runner.cjs');
const {map,preview,intent}=require('./fixtures.cjs');
function sequence(){return [map('a',800),map(),preview(),preview('d',1400)].map(o=>{o.frame.sourcePtsMs=o.frame.atMs;return o;});}
const gate={windowMs:[1000,1100],clientBox:[400,200,100,100],previewFromPtsMs:1200};
test('offline sequence releases matching previews only after a valid virtual click',async()=>{
 const frames=sequence(),read=[];
 const r=await runReplay({frames,intent,gate,observe:async f=>{read.push(f.frame.id);return f;}});
 assert.equal(r.state,'PREVIEW_CONFIRMED');assert.equal(r.actions.length,1);assert.equal(r.nativeActions,0);assert.equal(r.g4Complete,false);
 assert.deepEqual(read,['a','b','c','d']);assert.equal(r.transaction.observations.length,2);
});
test('wrong click time or location cannot obtain human-generated preview frames',async()=>{
 for(const bad of [{...gate,clientBox:[0,0,10,10]},{...gate,windowMs:[1100,1200]}]){
  const read=[];const r=await runReplay({frames:sequence(),intent,gate:bad,observe:async f=>{read.push(f.frame.id);return f;}});
  assert.equal(r.state,'DISPATCH_NOT_SENT');assert.deepEqual(read,['a','b']);assert.equal(r.nativeActions,0);
 }
});
test('unknown or absent preview identity fails replay with retained transaction evidence',async()=>{
 for(const kind of ['unknown','identity','no-preview']){
  let frames=sequence();if(kind==='unknown')frames[2].state='UNKNOWN';if(kind==='identity')frames[2].selectedNode=null;if(kind==='no-preview')frames=frames.slice(0,2);
  const r=await runReplay({frames,intent,gate,observe:async f=>f});
  assert.notEqual(r.state,'PREVIEW_CONFIRMED');assert.equal(r.actions.length,1);assert(r.transaction.proof);assert.equal(r.g4Complete,false);
 }
});
test('observer failure preserves the one dispatched transaction instead of escaping the replay',async()=>{
 const r=await runReplay({frames:sequence(),intent,gate,observe:async f=>{if(f.state==='PREVIEW')throw Error('pixel binding mismatch');return f;}});
 assert.equal(r.state,'OBSERVATION_FAILED');assert.equal(r.actions.length,1);assert.equal(r.failure.frameId,'c');assert(r.transaction.proof);
});

test('pre-click motion waits for a wholly new stable 200ms pair',async()=>{
 const frames=[map('a',600),map('b',800),map('c',900),map('d',1000),preview('e',1200),preview('f',1400)];
 frames[0].nodes.find(n=>n.id==='target').box[0]-=20;
 frames.forEach(o=>o.frame.sourcePtsMs=o.frame.atMs);
 const r=await runReplay({frames,intent,gate,observe:async f=>f});
 assert.equal(r.state,'PREVIEW_CONFIRMED');assert.equal(r.actions.length,1);
 assert.equal(r.transaction.proof.previousFrameId,'b');assert.equal(r.actions[0].frameId,'d');
 assert(r.selectionAttempts.some(a=>a.code==='MAP_MOVING'));
});
test('short frame intervals accumulate 200ms without reusing changed geometry',async()=>{
 const frames=[map('a',600),map('b',700),map('c',800),map('d',833),map('e',900),map('f',1000),preview('g',1200),preview('h',1400)];
 for(const o of frames.slice(2))o.frame.geometryVersion='g2';
 frames.forEach(o=>o.frame.sourcePtsMs=o.frame.atMs);
 const r=await runReplay({frames,intent,gate,observe:async f=>f});
 assert.equal(r.state,'PREVIEW_CONFIRMED');assert.equal(r.actions.length,1);
 assert.equal(r.transaction.proof.previousFrameId,'c');assert.equal(r.actions[0].frameId,'f');
});
test('pre-click window replacement remains an immediate rejection',async()=>{
 const frames=sequence();frames[1].frame.windowKey='other-window';
 const r=await runReplay({frames,intent,gate,observe:async f=>f});
 assert.equal(r.state,'STALE_GEOMETRY');assert.equal(r.actions.length,0);assert.equal(r.observations.length,2);
});

test('motion waiting cannot read the human post-click branch or dispatch late',async()=>{
 const frames=[map('a',600),map('b',800),map('human-map',1000),preview('human-preview',1200)];
 frames[0].nodes.find(n=>n.id==='target').box[0]-=20;
 frames.forEach(o=>o.frame.sourcePtsMs=o.frame.atMs);const read=[];
 const r=await runReplay({frames,intent,gate:{...gate,windowMs:[800,800],previewFromPtsMs:900},observe:async f=>{read.push(f.frame.id);return f;}});
 assert.equal(r.state,'MAP_MOVING');assert.equal(r.actions.length,0);assert.deepEqual(read,['a','b']);
 assert(r.selectionAttempts.some(a=>a.code==='HUMAN_BRANCH_NOT_RELEASED'));
});
