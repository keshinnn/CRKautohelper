const {test}=require('node:test'),assert=require('node:assert/strict');
const {runReplay}=require('../lib/replay-runner.cjs');
const {map,preview,intent}=require('./fixtures.cjs');
let evaluateReplay;try{({evaluateReplay}=require('../lib/replay-evaluator.cjs'));}catch{evaluateReplay=()=>({passed:false});}
test('an actual successful core transaction must also agree with independent click geometry',async()=>{
 const frames=[map('a',800),map(),preview(),preview('d',1400)].map(o=>{o.frame.sourcePtsMs=o.frame.atMs;return o;});
 const gate={windowMs:[1000,1000],clientBox:[400,200,100,100],previewFromPtsMs:1100};
 const r=await runReplay({frames,intent,gate,observe:async f=>f});
 const c={id:'example',source:{videoSha256:'a'.repeat(64),startPtsMs:800,endPtsMs:1400},intent,expectedBox:[400,200,100,100],clientBox:[400,200,100,100],reviewed:true};
 assert.equal(evaluateReplay(c,r).passed,true);
 assert.equal(evaluateReplay({...c,expectedBox:[420,200,100,100]},r).passed,false);
 assert.equal(evaluateReplay({...c,clientBox:[449,249,100,100]},r).passed,false);
 assert.equal(evaluateReplay({...c,reviewed:false},r).passed,false);
});
test('fixed-scale evaluation uses transformed physical boxes while preserving semantic node identity',async()=>{
 const scale=1.25;
 const frames=[map('a',800),map(),preview(),preview('d',1400)].map(o=>{
  o.frame.sourcePtsMs=o.frame.atMs;o.frame.width*=scale;o.frame.height*=scale;
  if(o.nodes)for(const n of o.nodes)n.box=n.box.map(v=>v*scale);return o;
 });
 const r=await runReplay({frames,intent,gate:{windowMs:[1000,1000],clientBox:[500,250,125,125],previewFromPtsMs:1100},observe:async f=>f});
 const grade=evaluateReplay({id:'scaled',source:{videoSha256:'a'.repeat(64),startPtsMs:800,endPtsMs:1400},intent,expectedBox:[500,250,125,125],clientBox:[500,250,125,125],reviewed:true,scale},r,{stage:'P4-B',scale});
 assert.equal(grade.passed,true);assert.equal(grade.stage,'P4-B');assert.equal(grade.scale,1.25);assert.equal(grade.g4Complete,false);
 assert.deepEqual(r.actions[0].clientPoint,[562.5,312.5]);
});
