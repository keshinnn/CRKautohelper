'use strict';
const {isDeepStrictEqual:eq}=require('node:util');
const authority=new WeakMap();
const box=(b,f)=>Array.isArray(b)&&b.length===4&&b.every(Number.isFinite)&&Math.min(...b.slice(0,2))>=0&&Math.min(...b.slice(2))>0&&b[0]+b[2]<=f.width&&b[1]+b[3]<=f.height;
function textBox(r,f){
 const a=r?.box;if(!Array.isArray(a)||a.length!==4||!a.every(p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite)))return null;
 const xs=a.map(p=>p[0]),ys=a.map(p=>p[1]),b=[Math.min(...xs),Math.min(...ys),Math.max(...xs)-Math.min(...xs),Math.max(...ys)-Math.min(...ys)];
 return box(b,f)?b:null;
}
function originalRow(row,p){return Array.isArray(p.evidence)&&p.evidence.some(r=>eq(r,row));}
function timerProvenance(t,p,f){
 if(originalRow(t,p))return true;
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
 const [x,y,w,h]=textBox(labels[0],f),left=Math.floor(x+w),top=Math.max(0,Math.floor(y-h*.15)),right=Math.max(left,Math.floor(f.width-h)),bottom=Math.min(f.height,Math.floor(y+h*1.15));
 return eq(row.cropBox,[left,top,right-left,bottom-top]);
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
  timer.text!=='03:00'||!(timer.score>=.95&&timer.score<=1)||!originalRow(enter,p)||!timerProvenance(timer,p,f)||!eq(tb,c.timerBox)||!eq(ob,c.ordinaryBox)||
  !(ob[1]<tb[1]&&tb[1]<eb[1])||eb[1]-tb[1]<f.height*.15)return null;
 const r=c.ordinaryEvidence,reading=r?.refinedReading;
 const original=originalRow(ordinary,p)&&/普通/.test(ordinary.text)&&ordinary.score>=.8&&ordinary.score<=1;
 const refined=originalRow(ordinary,p)&&/普通/.test(ordinary.text)&&ordinary.score>=.65&&ordinary.score<.8&&
  r?.kind==='bounded_original_pixel_line_recognition'&&reading?.text?.replace(/\s+/g,'')==='普通'&&reading.score>=.95&&reading.score<=1&&box(r.cropBox,f);
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
