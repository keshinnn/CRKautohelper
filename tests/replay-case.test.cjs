const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
let buildReplayGate,loadReplayFrames;try{({buildReplayGate,loadReplayFrames}=require('../lib/replay-case.cjs'));}catch{buildReplayGate=()=>null;loadReplayFrames=()=>[];}
function prechange(){return {preFrames:[100,106],previewFromPtsMs:1033.333333,gateWindowMs:[1000,1000],clientBox:[10,20,30,40],frames:[[99,766.666667],[100,800],[106,1000],[107,1033.333333]].map(([frameIndex,t])=>({frameIndex,atMs:t,sourcePtsMs:t,size:[1440,1080]}))};}
test('a real prefix does not move the human branch barrier onto the dispatch frame',()=>{
 const c=prechange();assert.deepEqual(buildReplayGate(c),{windowMs:[1000,1000],clientBox:[10,20,30,40],previewFromPtsMs:1033.333333});
 const ordinary=prechange();ordinary.frames.shift();delete ordinary.previewFromPtsMs;assert.equal(buildReplayGate(ordinary).previewFromPtsMs,1033.333333);
});
test('wrong branch override, missing postframe or moved dispatch time is refused',()=>{
 for(const kind of ['barrier','missing','gate','duplicate']){const c=prechange();if(kind==='barrier')c.previewFromPtsMs=1000;if(kind==='missing')c.frames.pop();if(kind==='gate')c.gateWindowMs=[1001,1001];if(kind==='duplicate')c.frames.splice(2,0,{...c.frames[1]});assert.throws(()=>buildReplayGate(c),/REPLAY_CASE_CONTRACT_INVALID/);}
});
function nativeCase(){const m=JSON.parse(fs.readFileSync(path.join(__dirname,'../artifacts/p4c-native-random-pilot-control-source-01.json')));return {...m.cases[0],frames:m.cases[0].frames.slice(0,1)};}
test('saved observer packet must bind actual native PNG and source-derived frame identity',()=>{
 const c=nativeCase(),frames=loadReplayFrames(c);assert.equal(frames.length,1);assert.equal(frames[0].frame.sourcePtsMs,c.frames[0].sourcePtsMs);assert(Buffer.isBuffer(frames[0].png));
 const wrong=nativeCase();wrong.videoSha256='d'.repeat(64);wrong.source.videoSha256=wrong.videoSha256;assert.throws(()=>loadReplayFrames(wrong),/SOURCE_FRAME_ID_MISMATCH/);
 const bytes=nativeCase();bytes.frames[0].sha256='d'.repeat(64);assert.throws(()=>loadReplayFrames(bytes),/SOURCE_CHANGED/);
 const dimensions=nativeCase();dimensions.frames[0].size[0]+=1;assert.throws(()=>loadReplayFrames(dimensions),/SOURCE_DIMENSIONS_MISMATCH/);
});
