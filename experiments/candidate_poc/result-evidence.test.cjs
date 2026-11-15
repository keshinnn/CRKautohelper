const {test}=require('node:test'),assert=require('node:assert/strict');
const {identity,validatePair,trustedResultFrame,validatePhaseFrames}=require('./result-evidence.cjs');
const row=(text,y)=>({text,score:.99,box:[[0,y],[20,y],[20,y+5],[0,y+5]]});
const valid=()=>[row('區域1第1層',1),row('勝利',10),row('00:26.69',20),row('最高等級',30),row('最高等級',40)];
test('requires original complete result semantics, not victory word only',()=>{
 assert.equal(identity([row('勝利',1)],{zone:1,floor:1}),null);
 assert.equal(identity(valid(),{zone:1,floor:1}).time,'00:26.69');
});
test('result timestamp must equal the trusted decoded episode timestamp',()=>{
 const f={frameIndex:1,sourcePtsMs:1000,geometryVersion:'g'};
 const row={frameIndex:1,sourcePtsMs:1000,rgbSha256:'a'};
 assert.equal(trustedResultFrame(f,row,'video','g').sourcePtsMs,1000);
 assert.throws(()=>trustedResultFrame({...f,sourcePtsMs:1200},row,'video','g'),/RESULT_TIME_OR_GEOMETRY_CHANGED/);
});
test('empty, reversed and pre-preview battle/result phases refuse',()=>{
 assert.throws(()=>validatePhaseFrames([],1000),/PHASE_SEQUENCE_INVALID/);
 assert.throws(()=>validatePhaseFrames([{sourcePtsMs:1100},{sourcePtsMs:1000}],1000),/PHASE_SEQUENCE_INVALID/);
 assert.throws(()=>validatePhaseFrames([{sourcePtsMs:900},{sourcePtsMs:1200}],1000),/PHASE_SEQUENCE_INVALID/);
 assert.equal(validatePhaseFrames([{sourcePtsMs:1100},{sourcePtsMs:1300}],1000),1300);
});
test('wrong identity, defeat and duplicated roster box refuse',()=>{
 assert.equal(identity(valid(),{zone:2,floor:1}),null);
 assert.equal(identity([...valid(),row('失敗',50)],{zone:1,floor:1}),null);
 const r=valid();r[4]=r[3];assert.equal(identity(r,{zone:1,floor:1}),null);
});
test('two source-bound distinct results required within original freshness',()=>{
 const a={sourceKey:'x',geometryVersion:'g',sourcePtsMs:1000,sha256:'a',rgbSha256:'a'};
 const b={...a,sourcePtsMs:1200,sha256:'b',rgbSha256:'b'};
 assert.equal(validatePair(a,b),true);
 for(const change of [{sourceKey:'y'},{rgbSha256:'a'},{sourcePtsMs:3501},{geometryVersion:'h'}])assert.equal(validatePair(a,{...b,...change}),false);
});
