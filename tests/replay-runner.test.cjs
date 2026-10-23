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
