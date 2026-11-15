'use strict';
const {isDeepStrictEqual:eq}=require('node:util');
const {validateGeometryCertificate}=require('./geometry-contract.cjs');
const authority=new WeakMap();
const box=(b,f)=>Array.isArray(b)&&b.length===4&&b.every(Number.isFinite)&&Math.min(...b.slice(0,2))>=0&&Math.min(...b.slice(2))>0&&b[0]+b[2]<=f.width&&b[1]+b[3]<=f.height;
function textBox(r,f){
 const a=r?.box;if(!Array.isArray(a)||a.length!==4||!a.every(p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite)))return null;
 const xs=a.map(p=>p[0]),ys=a.map(p=>p[1]),b=[Math.min(...xs),Math.min(...ys),Math.max(...xs)-Math.min(...xs),Math.max(...ys)-Math.min(...ys)];
 return box(b,f)?b:null;
}
function originalRow(row,p){return Array.isArray(p.evidence)&&p.evidence.some(r=>eq(r,row));}
function enterProvenance(row,p,f){
 if(originalRow(row,p))return true;
 const r=row.originalEvidence,b=textBox(r,f);
 if(row.source!=='enter_label_original_crop'||!b||!originalRow(r,p)||!(r.score>=.85&&r.score<.95)||r.text?.trim().toLowerCase()!=='enter'||b[0]<=f.width*.5||b[1]<=f.height*.5||!eq(row.box,r.box)||row.sourcePixelSha256!==p.binding.pixelSha256||!eq(row.sourceSize,[f.width,f.height]))return false;
 const originals=(p.evidence||[]).filter(v=>v.text?.trim().toLowerCase()==='enter'&&v.score>=.85&&v.score<.95&&textBox(v,f)?.[0]>f.width*.5);
 if(originals.length!==1||!eq(originals[0],r))return false;
 const [x,y,w,h]=b;
 return eq(row.cropBox,[Math.floor(x),Math.floor(y),Math.floor(x+w)-Math.floor(x),Math.floor(y+h)-Math.floor(y)]);
}
function timerProvenance(t,p,f){
 if(originalRow(t,p))return true;
 if(t.source==='time_limit_adjacent_timer_original_crop'){
  const label=t.timeLimitEvidence,lb=textBox(label,f),r=t.originalPixelReading;
  const labels=(p.evidence||[]).filter(v=>v.text?.trim().toLowerCase()==='time limit'&&v.score>=.95&&v.score<=1&&textBox(v,f)?.[0]>f.width*.5);
  const readings=t.originalPixelReadings;
  if(!Array.isArray(readings))return false;
  const clocks=readings.filter(v=>v.score>=.95&&v.score<=1&&/^\d{2}:\d{2}$/.test(v.text?.trim()));
  if(clocks.length!==1||!eq(clocks[0],r))return false;
  if(labels.length!==1||!eq(label,labels[0])||!lb||!box(t.cropBox,f)||t.detectorScale!==3||t.sourcePixelSha256!==p.binding.pixelSha256||!eq(t.sourceSize,[f.width,f.height])||r?.text?.trim()!=='03:00'||!(r.score>=.95&&r.score<=1)||t.score!==r.score)return false;
  const [x,y,w,h]=lb,left=Math.floor(x+w),top=Math.max(0,Math.floor(y-h*.2)),right=f.width,bottom=Math.min(f.height,Math.floor(y+h*1.2));
  if(!(h>0&&h<f.height*.1)||!eq(t.cropBox,[left,top,right-left,bottom-top]))return false;
  if((p.evidence||[]).some(v=>{const b=textBox(v,f);return b&&b[0]>x+w&&Math.abs(b[1]+b[3]/2-y-h/2)<=h&&v.score>=.95&&v.score<=1&&/^\d{2}:\d{2}$/.test(v.text?.trim())&&v.text.trim()!=='03:00';}))return false;
  const q=r.box;if(!Array.isArray(q)||q.length!==4||!q.every(v=>Array.isArray(v)&&v.length===2&&v.every(Number.isFinite)&&v[0]>=0&&v[0]<=(right-left)*3&&v[1]>=0&&v[1]<=(bottom-top)*3))return false;
  return eq(t.box,q.map(([px,py])=>[px/3+left,py/3+top]));
 }
 if(t.source!=='timer_digits_original_crop'||!box(t.cropBox,f))return false;
 const originals=(p.evidence||[]).filter(r=>r.text===t.originalText&&r.score===t.originalScore&&r.score>=.75&&r.score<=1&&/^[@◎○〇]03:00$/.test(r.text?.trim()));
 if(originals.length!==1)return false;
 const original=originals[0],b=textBox(original,f),label=t.timeLimitEvidence,lb=textBox(label,f);
 if(!b||!lb||!(label.score>=.75&&label.score<=1)||
  !(/限制時[間间]$/.test(label.text?.replace(/\s+/g,''))||/^(battle)?timelimit$/i.test(label.text?.replace(/\s+/g,''))))return false;
 if(!originalRow(label,p)){
  if(label.source!=='time_limit_original_crop'||!(label.originalScore>=.65&&label.originalScore<.75)||!box(label.cropBox,f)||
   !(p.evidence||[]).some(r=>r.text===label.originalText&&r.score===label.originalScore&&eq(r.box,label.box)))return false;
  const expected=[Math.floor(lb[0]),Math.floor(lb[1]),Math.floor(lb[0]+lb[2])-Math.floor(lb[0]),Math.floor(lb[1]+lb[3])-Math.floor(lb[1])];
  if(!eq(label.cropBox,expected))return false;
 }
 if(!(lb[0]>f.width*.5&&lb[0]+lb[2]<=b[0]+b[3]*.25&&b[0]-lb[0]-lb[2]<=f.width*.25&&
  Math.abs(lb[1]+lb[3]/2-b[1]-b[3]/2)<=Math.max(lb[3],b[3])*.6))return false;
 return [0,.2,.4,.6,.8,1].some(fraction=>{
  const left=Math.max(0,Math.floor(b[0]+b[3]*fraction)),top=Math.max(0,Math.floor(b[1]-2)),right=Math.min(f.width,Math.floor(b[0]+b[2]+2)),bottom=Math.min(f.height,Math.floor(b[1]+b[3]+2));
  return eq(t.cropBox,[left,top,right-left,bottom-top]);
 });
}
function englishProvenance(row,p,f){
 const labels=(p.evidence||[]).filter(r=>r.text?.trim().toLowerCase()==='difficulty'&&r.score>=.95&&r.score<=1&&textBox(r,f)?.[0]>f.width*.5);
 if(labels.length!==1||!box(row.cropBox,f))return false;
 if(row.cropExtentMethod!=null&&row.cropExtentMethod!=='full_source_right_edge')return false;
 const [x,y,w,h]=textBox(labels[0],f),left=Math.floor(x+w),top=Math.max(0,Math.floor(y-h*.15)),right=row.cropExtentMethod==='full_source_right_edge'?f.width:Math.max(left,Math.floor(f.width-h)),bottom=Math.min(f.height,Math.floor(y+h*1.15));
 return eq(row.cropBox,[left,top,right-left,bottom-top]);
}
function ordinaryCropProvenance(r,ordinary,p,f){
 const b=textBox(ordinary,f);if(!b||r.cropScale!==1)return false;
 let scale=1;const e=r.positionEvidence;
 if(e!=null){
  const a=p.mapReview?.aspectRectification,s=[f.width,f.height],z=a?.rectifiedInputSize;
  if(!a||!Array.isArray(z)||z.length!==2||!z.every(v=>Number.isInteger(v)&&v>0)||z[1]!==f.height)return false;
  scale=f.width/z[0];
  if(e.method!=='same_frame_rectified_horizontal_glyph_crop'||e.horizontalScale!==scale||
   e.sourceCaptureFrameId!==f.id||e.sourceImageSha256!==f.sha256||e.pixelSha256!==p.binding.pixelSha256||!eq(e.sourceSize,s)||!eq(e.rectifiedInputSize,z)||
   a.verified!==true||a.method!=='same_frame_circle_aspect_map_rectification'||a.actionsExecuted!==false||
   a.sourceCaptureFrameId!==f.id||a.sourceImageSha256!==f.sha256||a.pixelSha256!==p.binding.pixelSha256||!eq(a.sourceSize,s)||
   a.calibration?.pixelSha256!==p.binding.pixelSha256||!eq(a.calibration?.sourceSize,s)||
   !eq(a.forwardMatrix,[[1/scale,0,0],[0,1,0],[0,0,1]])||!eq(a.inverseMatrix,[[scale,0,0],[0,1,0],[0,0,1]])||
   !validateGeometryCertificate(a.coordinateContract,f,p,z,a.modelAnalysisSize))return false;
 }
 const [x,y,w,h]=b,left=Math.max(0,Math.floor(x+w-h*2*scale)),top=Math.max(0,Math.floor(y-3)),right=Math.min(f.width,Math.floor(x+w+3)),bottom=Math.min(f.height,Math.floor(y+h+3));
 return [0,.1,.2,.3].some(fraction=>{
  const value=h*fraction*scale,base=Math.floor(value),delta=value-base===.5?(base%2===0?base:base+1):Math.round(value);
  const actualLeft=left+delta;
  return eq(r.cropBox,[actualLeft,top,right-actualLeft,bottom-top]);
 });
}
function adaptPreviewContext(f,p){
 const c=p.v2PreviewContext,z=p.progress,b=p.binding;
 if(c?.verified!==true||c.waitOnly!==true||c.actionsExecuted!==false||c.method!=='same_frame_ordinary_preview_controls'||
  c.sourceCaptureFrameId!==f.id||c.sourceImageSha256!==f.sha256||c.pixelSha256!==b.pixelSha256||!eq(c.sourceSize,[f.width,f.height])||
  !Number.isInteger(c.zone)||c.zone<1||c.zone>10||c.zone!==z?.displayedZone||z.conflictingEvidence!==false||!(z.score>=.9&&z.score<=1))return null;
 const enter=c.enterEvidence,timer=c.timerEvidence,ordinary=c.ordinaryReading;
 const eb=textBox(enter,f),tb=textBox(timer,f),ob=textBox(ordinary,f);
 if(!eb||!tb||!ob||!box(c.enterBox,f)||![eb,tb,ob].every(b=>b[0]>f.width*.5)||
  !/^(進入|enter)$/i.test(enter.text?.replace(/\s+/g,''))||!(enter.score>=.95&&enter.score<=1)||
  timer.text!=='03:00'||!(timer.score>=.95&&timer.score<=1)||!enterProvenance(enter,p,f)||!timerProvenance(timer,p,f)||!eq(tb,c.timerBox)||!eq(ob,c.ordinaryBox)||
  !(ob[1]<tb[1]&&tb[1]<eb[1])||eb[1]-tb[1]<f.height*.15)return null;
 const r=c.ordinaryEvidence,reading=r?.refinedReading;
 const original=originalRow(ordinary,p)&&/普通/.test(ordinary.text)&&ordinary.score>=.8&&ordinary.score<=1;
 const refined=originalRow(ordinary,p)&&/普通/.test(ordinary.text)&&ordinary.score>=.65&&ordinary.score<.8&&
  r?.kind==='bounded_original_pixel_line_recognition'&&reading?.text?.replace(/\s+/g,'')==='普通'&&reading.score>=.95&&reading.score<=1&&box(r.cropBox,f)&&ordinaryCropProvenance(r,ordinary,p,f);
 const english=ordinary.source==='difficulty_adjacent_english_normal_original_crop'&&/^\*{0,2}Normal$/i.test(ordinary.text?.trim())&&ordinary.score>=.95&&ordinary.score<=1&&englishProvenance(ordinary,p,f);
 if(!original&&!refined&&!english)return null;
 const [x,y,w,h]=c.enterBox;
 if(!(x<eb[0]&&y<eb[1]&&x+w>eb[0]+eb[2]&&y+h>eb[1]+eb[3]&&w>eb[2]*2&&h>eb[3]*1.3))return null;
 const o={frame:f,state:'PREVIEW_PENDING',verified:false,stateVerified:true,zone:c.zone,
  capabilities:{wait:true,select:false,confirm:false},reason:'ORDINARY_PREVIEW_CONTROLS_WAIT_ONLY'};
 authority.set(o,JSON.stringify(o));return o;
}
function readPreviewWaitAuthority(o){return authority.has(o)&&authority.get(o)===JSON.stringify(o);}
module.exports={adaptPreviewContext,readPreviewWaitAuthority};
