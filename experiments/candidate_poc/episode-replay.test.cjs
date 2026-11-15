const {test}=require('node:test'),assert=require('node:assert/strict');
const {resultBarrier,validateCaseSource,validateEpisode}=require('./episode-replay.cjs');
test('UNKNOWN victory OCR cannot complete a node',()=>{
 assert.equal(resultBarrier({flow:{state:'UNKNOWN'},evidence:[{text:'勝利',score:1}]}),'RESULT_UNKNOWN');
});
test('case source cannot override episode source',()=>{
 assert.throws(()=>validateCaseSource({videoSha256:'b'.repeat(64)},'a'.repeat(64),'a'.repeat(64)),/EPISODE_SOURCE_CHANGED/);
});
test('continuity flags cannot hide missing frames',()=>{
 assert.throws(()=>validateEpisode({allFramesPreserved:true,allDecodedRgbVerified:true,stitched:false,fps:30,firstFrame:1,lastFrame:3,frames:[{frameIndex:1},{frameIndex:3}]}),/CONTINUITY_UNPROVEN/);
});
test('classification alone cannot mint independent result authority',()=>{
 assert.equal(resultBarrier({flow:{state:'VICTORY'},resultAuthority:{verified:true}}),'RESULT_VERIFIER_UNAVAILABLE');
});
