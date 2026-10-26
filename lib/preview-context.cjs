'use strict';
const {isDeepStrictEqual:eq}=require('node:util');
const authority=new WeakMap();
const box=(b,f)=>Array.isArray(b)&&b.length===4&&b.every(Number.isFinite)&&Math.min(...b.slice(0,2))>=0&&Math.min(...b.slice(2))>0&&b[0]+b[2]<=f.width&&b[1]+b[3]<=f.height;
function textBox(r,f){
 const a=r?.box;if(!Array.isArray(a)||a.length!==4||!a.every(p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite)))return null;
 const xs=a.map(p=>p[0]),ys=a.map(p=>p[1]),b=[Math.min(...xs),Math.min(...ys),Math.max(...xs)-Math.min(...xs),Math.max(...ys)-Math.min(...ys)];
 return box(b,f)?b:null;
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
  timer.text!=='03:00'||!(timer.score>=.95&&timer.score<=1)||!eq(tb,c.timerBox)||!eq(ob,c.ordinaryBox)||
  !(ob[1]<tb[1]&&tb[1]<eb[1])||eb[1]-tb[1]<f.height*.15)return null;
 const r=c.ordinaryEvidence,reading=r?.refinedReading;
 const original=/普通/.test(ordinary.text)&&ordinary.score>=.8&&ordinary.score<=1;
 const refined=/普通/.test(ordinary.text)&&ordinary.score>=.65&&ordinary.score<.8&&
  r?.kind==='bounded_original_pixel_line_recognition'&&reading?.text?.replace(/\s+/g,'')==='普通'&&reading.score>=.95&&reading.score<=1&&box(r.cropBox,f);
 const english=ordinary.source==='difficulty_adjacent_english_normal_original_crop'&&/^\*{0,2}Normal$/i.test(ordinary.text?.trim())&&ordinary.score>=.95&&ordinary.score<=1;
 if(!original&&!refined&&!english)return null;
 const [x,y,w,h]=c.enterBox;
 if(!(x<eb[0]&&y<eb[1]&&x+w>eb[0]+eb[2]&&y+h>eb[1]+eb[3]&&w>eb[2]*2&&h>eb[3]*1.3))return null;
 const o={frame:f,state:'PREVIEW_PENDING',verified:false,stateVerified:true,zone:c.zone,
  capabilities:{wait:true,select:false,confirm:false},reason:'ORDINARY_PREVIEW_CONTROLS_WAIT_ONLY'};
 authority.set(o,JSON.stringify(o));return o;
}
function readPreviewWaitAuthority(o){return authority.has(o)&&authority.get(o)===JSON.stringify(o);}
module.exports={adaptPreviewContext,readPreviewWaitAuthority};
