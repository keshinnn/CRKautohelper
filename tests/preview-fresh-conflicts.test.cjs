'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {adaptPreviewContext}=require('../lib/preview-context.cjs');
function sample(){
 const all=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../artifacts/concentrated-repair-20261103-01/preview-control-proofs.json'),'utf8'));
 const p=all.find(r=>r.number===53).packet,b=p.binding;
 return {p,f:{id:b.frameId,sha256:b.imageSha256,width:b.width,height:b.height}};
}
test('independent timer validation rejects an equally qualified contradictory fresh reading',()=>{
 const {p,f}=sample(),t=p.v2PreviewContext.timerEvidence;
 assert.equal(t.source,'time_limit_adjacent_timer_original_crop');
 t.originalPixelReadings=[t.originalPixelReading,{...structuredClone(t.originalPixelReading),text:'02:00',score:.99}];
 assert.equal(adaptPreviewContext(f,p),null);
});
