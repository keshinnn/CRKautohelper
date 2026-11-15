'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {adaptPreviewContext}=require('../lib/preview-context.cjs');
function sample(){
 const root=path.resolve(__dirname,'..'),a=JSON.parse(fs.readFileSync(path.join(root,'artifacts/exploration-20261102-01/audit-summary.json'),'utf8'));
 const row=a.rows.find(r=>r.number===56),p=JSON.parse(fs.readFileSync(row.criticalPacket,'utf8'));
 const b=p.binding,f={id:b.frameId,sha256:b.imageSha256,width:b.width,height:b.height};
 const c=p.v2PreviewContext,r=c.ordinaryReading,[x,y,w,h]=r.cropBox;
 r.cropBox=[x,y,f.width-x,h];r.box=[[x,y],[f.width,y],[f.width,y+h],[x,y+h]];
 r.cropExtentMethod='full_source_right_edge';c.ordinaryBox=[...r.cropBox];
 return {p,f};
}
test('independent validator accepts source-right-edge English line extent without changing authority',()=>{
 const {p,f}=sample(),o=adaptPreviewContext(f,p);assert.ok(o);assert.equal(o.state,'PREVIEW_PENDING');assert.deepEqual(o.capabilities,{wait:true,select:false,confirm:false});
});
test('full line extent still rejects altered bounds and unrecognized text',()=>{
 for(const tamper of [(p)=>{p.v2PreviewContext.ordinaryReading.cropBox[2]+=1;},(p)=>{p.v2PreviewContext.ordinaryReading.text='**Norma';}]){
  const {p,f}=sample();tamper(p);assert.equal(adaptPreviewContext(f,p),null);
 }
});
test('actual complete-line producer evidence independently verifies with unchanged wait-only authority',()=>{
 const rows=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../artifacts/concentrated-repair-20261103-01/preview-control-proofs.json'),'utf8'));
 assert.deepEqual(rows.map(r=>r.number),[52,53,55,56,57]);
 for(const {packet:p} of rows){
  const b=p.binding,f={id:b.frameId,sha256:b.imageSha256,width:b.width,height:b.height};
  const o=adaptPreviewContext(f,p);assert.ok(o);assert.equal(o.capabilities.select,false);assert.equal(o.capabilities.confirm,false);
  for(const key of ['sourcePixelSha256','cropBox']){
   const q=structuredClone(p),timer=q.v2PreviewContext.timerEvidence;
   if(timer.source==='time_limit_adjacent_timer_original_crop'){
    timer[key]=key==='sourcePixelSha256'?'0'.repeat(64):[0,0,10,10];
    assert.equal(adaptPreviewContext(f,q),null);
   }
  }
  if(p.v2PreviewContext.enterEvidence.source==='enter_label_original_crop'){
   const q=structuredClone(p);q.evidence.push(structuredClone(q.v2PreviewContext.enterEvidence.originalEvidence));
   assert.equal(adaptPreviewContext(f,q),null);
  }
 }
});
