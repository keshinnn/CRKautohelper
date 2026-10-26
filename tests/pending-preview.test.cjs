const {test}=require('node:test'),assert=require('node:assert/strict'),{execFileSync}=require('node:child_process'),fs=require('node:fs');
const {adaptMap,readDirectMapAnchor}=require('../lib/observer-adapter.cjs'),{verifyPreview}=require('../lib/preview-verifier.cjs');
const {selectNode}=require('../lib/node-selector.cjs'),{PreviewSession}=require('../lib/preview-session.cjs'),{loadReplayFrames}=require('../lib/replay-case.cjs');
let saved;
function fixture(){
 if(!saved){
  const code="import sys,json,pathlib;sys.path[:0]=[str(pathlib.Path('ml').resolve()),str(pathlib.Path('tests').resolve()),'F:/CRK helper/ml'];from test_preview_context import actual_frame;from preview_context import inspect_preview_context;from bounded_ocr import BoundedOCRRuntime;im,p=actual_frame();rt=BoundedOCRRuntime(960);rt.__enter__();p['v2PreviewContext']=inspect_preview_context(im,p);print(json.dumps(p));rt.close()";
  const packet=JSON.parse(execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',code],{encoding:'utf8',windowsHide:true}));
  const m=JSON.parse(fs.readFileSync('artifacts/p4c-random-development-60-run-25/dev-L0-zone6-floor3-col3-select-1932-random-post-change/analysis/manifest.json'));
  const c=m.cases[0],frames=loadReplayFrames(c),source=frames.find(s=>s.frame.sourcePtsMs===1931566.666667);
  saved={packet,source,c,frames};
 }
 return {...saved,packet:structuredClone(saved.packet)};
}
test('actual empty-map preview transition grants waiting only, never selection or identity',()=>{
 const {packet,source}=fixture(),o=adaptMap({...source.frame,png:source.png},packet);
 assert.equal(o.state,'PREVIEW_PENDING');assert.equal(o.verified,false);assert.equal(o.capabilities.select,false);
 assert.equal(readDirectMapAnchor(o),null);assert.equal(verifyPreview({intent:{zone:6}},o).kind,'wait');
 assert.throws(()=>selectNode(o,o,{zone:6,floor:3,column:3,event:'battle',mode:'select'},{nowMs:o.frame.atMs}));
});
test('copied, edited or different-zone context cannot authorize waiting',()=>{
 const {packet,source}=fixture();
 for(const mutate of [o=>structuredClone(o),o=>{o.frame.width++;return o;},o=>{o.zone=7;return o;}]){
  const o=mutate(adaptMap({...source.frame,png:source.png},packet));
  assert.equal(verifyPreview({intent:{zone:6}},o).kind,'reject');
 }
 for(const mutate of [p=>p.v2PreviewContext.pixelSha256='f'.repeat(64),p=>p.v2PreviewContext.timerEvidence.score=.94,p=>p.progress.conflictingEvidence=true,p=>p.evidence=[],p=>delete p.v2PreviewContext.timerEvidence.timeLimitEvidence,p=>p.v2PreviewContext.timerEvidence.timeLimitEvidence.score=.74]){
  const q=structuredClone(packet);mutate(q);assert.notEqual(adaptMap({...source.frame,png:source.png},q).state,'PREVIEW_PENDING');
 }
});
test('waiting does not reset the original deadline or emit another click',async()=>{
 const {packet,source,c,frames}=fixture();const a=adaptMap({...frames[0].frame,png:frames[0].png},frames[0].packet),b=adaptMap({...frames[1].frame,png:frames[1].png},frames[1].packet);
 const proof=selectNode(a,b,c.intent,{nowMs:b.frame.atMs});let now=b.frame.atMs,sent=0;
 const s=new PreviewSession({clock:()=>now,dispatch:action=>{sent++;return {status:'sent',transactionId:action.transactionId,frameId:action.frameId};}});
 await s.start(proof);const deadline=s.snapshot().deadlineMs;now=source.frame.atMs;
 assert.equal(s.observe(adaptMap({...source.frame,png:source.png},packet)).state,'WAIT_PREVIEW');
 assert.equal(s.snapshot().deadlineMs,deadline);await s.start(proof);assert.equal(sent,1);
 now=deadline;assert.equal(s.tick().state,'PREVIEW_TIMEOUT');assert.equal(sent,1);
});
