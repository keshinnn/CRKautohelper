'use strict';
// Isolated typed rift capability. It never mints a production battle proof.
const crypto=require('crypto');
const {validateFrame,boxValid}=require('../../lib/node-selector.cjs');
const {readDirectMapAnchor}=require('../../lib/observer-adapter.cjs');
const {decodeRgbPng}=require('./verify_research.cjs');
const {createGeometry,clientToScreen}=require('../../lib/geometry.cjs');
const issued=new WeakSet(),spent=new WeakMap();
function freeze(x){if(x&&typeof x==='object'){for(const v of Object.values(x))freeze(v);Object.freeze(x);}return x;}
const fail=code=>{throw Object.assign(Error(code),{code});};
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
function hsv(r,g,b){
 const max=Math.max(r,g,b),min=Math.min(r,g,b),d=max-min;
 let h=0;if(d){h=max===r?(g-b)/d:max===g?(b-r)/d+2:(r-g)/d+4;h=((h*30)%180+180)%180;}
 return [h,max?255*d/max:0,max];
}
const isPurple=(h,s,v)=>h>90&&h<150&&s>130&&v>130;
const isGreen=(h,s,v)=>h>30&&h<85&&s>100&&v>150;
function modalVisible(source){return source.packet.evidence.some(r=>r.score>=.9&&['可能發生的事件','冥界裂縫','進入','戰鬥開始'].includes(r.text.replace(/\s/g,'').replaceAll('缝','縫')));}
function imageFor(source,o){
 const cert=readDirectMapAnchor(o);
 if(!cert||cert.frame.id!==source.frame.id||cert.frame.sha256!==source.frame.sha256||sha(source.png)!==source.frame.sha256)fail('RIFT_MAP_AUTHORITY_MISSING');
 const im=decodeRgbPng(source.png);
 if(sha(im.rgb)!==cert.pixelSha256)fail('RIFT_SOURCE_CHANGED');
 return im;
}
function sourceKey(source){
 const b=source.packet.sourceBinding;
 if(!b||!/^[a-f0-9]{64}$/.test(b.videoSha256)||b.imageSha256!==source.frame.sha256||!Number.isInteger(b.frameIndex)||
  sha(b.videoSha256+String(b.frameIndex)+b.imageSha256).slice(0,32)!==source.frame.id)fail('RIFT_VIDEO_BINDING_INVALID');
 return b.videoSha256;
}
function facts(im,box){
 if(!boxValid(box,{width:im.w,height:im.h}))fail('RIFT_BOX_INVALID');
 const [x,y,w,h]=box,cx=x+w/2,cy=y+h/2;let purple=0,total=0;
 const ring=[0,0,0,0],green=[0,0,0,0],yellow=[0,0,0,0];let pink=0;
 // New type-specific native-pixel measure; no coordinate or bbox modification.
 for(let py=Math.max(0,Math.floor(y-h*.15));py<Math.min(im.h,Math.ceil(y+h*1.15));py++)for(let px=Math.max(0,Math.floor(x-w*.15));px<Math.min(im.w,Math.ceil(x+w*1.15));px++){
  const at=(py*im.w+px)*3,c=hsv(im.rgb[at],im.rgb[at+1],im.rgb[at+2]);
  if(px>=x+w*12/58&&px<x+w*46/58&&py>=y+h*12/58&&py<y+h*46/58){total++;if(isPurple(...c))purple++;if(c[0]>150&&c[0]<180&&c[1]>130&&c[2]>130)pink++;}
  const radius=Math.max(Math.abs((px-cx)/(w/2)),Math.abs((py-cy)/(h/2)));
  if(radius>.8&&radius<1.15){const q=(px>=cx?1:0)+(py>=cy?2:0);ring[q]++;if(isGreen(...c))green[q]++;if(c[0]>=22&&c[0]<=38&&c[1]>130&&c[2]>130)yellow[q]++;}
 }
 return {purpleCoverage:total?purple/total:0,pinkCoverage:total?pink/total:0,
  yellowCoverage:yellow.reduce((a,b)=>a+b,0)/ring.reduce((a,b)=>a+b,0),yellowQuadrants:ring.map((n,i)=>n?yellow[i]/n:0),
  ringCoverage:green.reduce((a,b)=>a+b,0)/ring.reduce((a,b)=>a+b,0),quadrants:ring.map((n,i)=>n?green[i]/n:0)};
}
const iou=(a,b)=>{const s=Math.max(0,Math.min(a[0]+a[2],b[0]+b[2])-Math.max(a[0],b[0]))*Math.max(0,Math.min(a[1]+a[3],b[1]+b[3])-Math.max(a[1],b[1]));return s/(a[2]*a[3]+b[2]*b[3]-s);};
function selectRift(sources,observations,intent){
 if(intent.event!=='rift'||intent.mode!=='select'||sources.length!==2||observations.length!==2)fail('RIFT_INTENT_INVALID');
 const [a,b]=observations.map(o=>o.frame);
 if(sources.some(modalVisible))fail('RIFT_PREVIEW_ALREADY_OPEN');
 const video=sourceKey(sources[0]);if(sourceKey(sources[1])!==video)fail('RIFT_VIDEO_CHANGED');
 observations.forEach(o=>validateFrame(o.frame,b.atMs));
 if(a.id===b.id||b.atMs-a.atMs<200||a.windowKey!==b.windowKey||a.geometryVersion!==b.geometryVersion||a.width!==b.width||a.height!==b.height||JSON.stringify(a.origin)!==JSON.stringify(b.origin)||!(b.sourcePtsMs>a.sourcePtsMs))fail('STALE_GEOMETRY');
 const selected=[],parents=[],colors=[];
 for(let i=0;i<2;i++){
  const o=observations[i],im=imageFor(sources[i],o);
  if(!o.verified||!o.anchorVerified||o.zone!==intent.zone||!o.current?.verified||o.current.inProgress)fail('CURRENT_POSITION_UNPROVEN');
  const matches=o.nodes.filter(n=>n.floor===intent.floor&&n.column===intent.column);
  if(matches.length!==1)fail('MAP_AMBIGUOUS');const n=matches[0];
  const parent=o.nodes.find(p=>p.id===o.current.nodeId&&p.completed===true&&p.floor===intent.floor-1);
  if(!parent||!boxValid(parent.box,o.frame))fail('CURRENT_POSITION_UNPROVEN');
  if(n.type!=='rift'||n.score<.48||n.score>1||n.completed!==false)fail('RIFT_NODE_INVALID');
  const links=o.edges.filter(e=>e.from===parent.id&&e.to===n.id&&e.pixelSupport>=.85&&e.pixelSupport<=1);
  if(links.length!==1)fail('CONNECTION_UNPROVEN');
  const color=facts(im,n.box);if(color.purpleCoverage<.2)fail('RIFT_NOT_ACTIVE');
  selected.push(n);parents.push(parent);colors.push(color);
 }
 const p=selected[0],n=selected[1],tolerance=Math.max(2,Math.min(...n.box.slice(2))*.02);
 if(p.id!==n.id||iou(p.box,n.box)<.95||parents[0].id!==parents[1].id||iou(parents[0].box,parents[1].box)<.95||Math.hypot(p.box[0]+p.box[2]/2-n.box[0]-n.box[2]/2,p.box[1]+p.box[3]/2-n.box[1]-n.box[3]/2)>tolerance)fail('MAP_MOVING');
 const proof=freeze(structuredClone({kind:'rift-research-selection',researchOnly:true,formalAuthority:false,intent:{...intent},nodeId:n.id,
  frame:b,sourceKey:video,point:[n.box[0]+n.box[2]/2,n.box[1]+n.box[3]/2],availability:colors}));
 issued.add(proof);return proof;
}
function validateRiftProof(proof){if(!issued.has(proof))fail('RIFT_PROOF_INVALID');return proof;}
function dispatchOnce(proof,{nowMs,currentFrame}={}){
 validateRiftProof(proof);if(spent.has(proof))fail('RIFT_ALREADY_DISPATCHED');
 validateFrame(proof.frame,nowMs);validateFrame(currentFrame,nowMs);
 if(['id','sha256','geometryVersion','width','height','windowKey'].some(k=>currentFrame[k]!==proof.frame[k])||JSON.stringify(currentFrame.origin)!==JSON.stringify(proof.frame.origin))fail('RIFT_CURRENT_FRAME_CHANGED');
 const f=proof.frame,geometry=createGeometry({frame:f,contentRect:[0,0,f.width,f.height],analysisSize:[f.width,f.height],padding:[0,0,0,0]});
 spent.set(proof,{sentAtMs:nowMs});
 return {kind:'virtual-rift-click',transactionId:crypto.randomUUID(),frameId:f.id,geometryVersion:f.geometryVersion,
  sentAtMs:nowMs,point:proof.point,clientPoint:proof.point,screenPoint:clientToScreen(proof.point,geometry)};
}
function previewRift(proof,source,o){
 validateRiftProof(proof);const im=imageFor(source,o),f=o.frame;
 if(sourceKey(source)!==proof.sourceKey||f.sourcePtsMs<=proof.frame.sourcePtsMs)fail('RIFT_VIDEO_CHANGED');
 if(!spent.has(proof)||f.atMs<=spent.get(proof).sentAtMs||f.atMs-spent.get(proof).sentAtMs>15000||f.windowKey!==proof.frame.windowKey||f.geometryVersion!==proof.frame.geometryVersion||f.width!==proof.frame.width||f.height!==proof.frame.height||JSON.stringify(f.origin)!==JSON.stringify(proof.frame.origin)||o.zone!==proof.intent.zone)fail('RIFT_PREVIEW_SOURCE_INVALID');
 const normalize=t=>t.replace(/\s/g,'').replaceAll('缝','縫').replaceAll('发','發');
 const rows=source.packet.evidence.filter(r=>r.score>=.9&&r.score<=1);
 for(const label of ['冥界裂縫','可能發生的事件'])if(rows.filter(r=>normalize(r.text)===label).length!==1)fail('RIFT_CONTROLS_UNPROVEN');
 const selected=o.nodes.filter(n=>n.type!=='exit'&&!n.completed&&n.score>=.48).map(n=>({n,facts:facts(im,n.box)})).filter(x=>x.facts.ringCoverage>=.08&&Math.min(...x.facts.quadrants)>=.04);
 if(selected.length!==1)fail('RIFT_PREVIEW_AMBIGUOUS');const {n,facts:measure}=selected[0];
 if(n.type!=='rift'||n.floor!==proof.intent.floor||n.column!==proof.intent.column)fail('RIFT_PREVIEW_MISMATCH');
 return {kind:'rift-research-preview',zone:o.zone,floor:n.floor,column:n.column,event:'rift',frame:f,nodeId:n.id,measure,formalAuthority:false};
}
function triangleEvidence(im,triangle,node){
 const [x,y,w,h]=node.box,[tx,ty,tw,th]=triangle.box||[];
 if(![tx,ty,tw,th].every(Number.isFinite)||!boxValid([tx,ty,tw,th],{width:im.w,height:im.h})||tw<w*.15||tw>w*.45||th<h*.1||th>h*.3||Math.abs(tx+tw/2-x-w/2)>w*.15||ty<y-h*.4||ty+th>y)fail('RIFT_TRIANGLE_INVALID');
 const band=Math.max(1,Math.floor(th/3));let upper=0,lower=0,area=0;
 for(let py=ty;py<ty+th;py++)for(let px=tx;px<tx+tw;px++){
  const at=(py*im.w+px)*3,[h,s,v]=hsv(im.rgb[at],im.rgb[at+1],im.rgb[at+2]);
  if(h>=22&&h<=38&&s>130&&v>130){area++;if(py<ty+band)upper++;if(py>=ty+th-band)lower++;}
 }
 if(!upper||lower>upper*.8||area<tw*th*.1)fail('RIFT_TRIANGLE_PIXELS_INVALID');
}
function convertedBattle(proof,sources,witnesses){
 validateRiftProof(proof);if(!spent.has(proof)||sources.length<2)fail('RIFT_CONVERSION_UNPROVEN');
 const {adaptMap}=require('../../lib/observer-adapter.cjs');let first=null;
 for(let i=0;i<sources.length;i++){
  const source=sources[i],witness=witnesses?.[i];
  const o=adaptMap({...source.frame,png:source.png},source.packet),im=imageFor(source,o),f=o.frame;
  if(o.zone!==proof.intent.zone||f.windowKey!==proof.frame.windowKey||f.geometryVersion!==proof.frame.geometryVersion||f.width!==proof.frame.width||f.height!==proof.frame.height||f.atMs<=spent.get(proof).sentAtMs||f.atMs-spent.get(proof).sentAtMs>15000)fail('RIFT_CONVERSION_SOURCE_INVALID');
  if(sourceKey(source)!==proof.sourceKey||!witness||witness.imageSha256!==f.sha256||witness.pixelSha256!==source.packet.binding.pixelSha256||witness.frameIndex!==source.packet.sourceBinding.frameIndex)fail('RIFT_CURRENT_SOURCE_INVALID');
  const labels=source.packet.evidence.filter(r=>r.text.replace(/\s/g,'')==='進行中'&&r.score>=.95);
  if(labels.length!==1)fail('RIFT_PROGRESS_LABEL_UNPROVEN');
  const xs=labels[0].box.map(p=>p[0]),ys=labels[0].box.map(p=>p[1]),lx=Math.min(...xs),ly=Math.min(...ys),rx=Math.max(...xs);
  const chosen=o.nodes.filter(n=>n.type==='battle'&&!n.completed&&n.score>=.48).filter(n=>{
   const q=facts(im,n.box),[x,y,w,h]=n.box;
   return q.pinkCoverage>=.2&&q.yellowCoverage>=.08&&Math.min(...q.yellowQuadrants)>=.04&&Math.abs((lx+rx)/2-x-w/2)<=w*.45&&ly-y-h>=-h*.35&&ly-y-h<=h*.35;
  });
  if(chosen.length!==1||chosen[0].type!=='battle'||chosen[0].floor!==proof.intent.floor||chosen[0].column!==proof.intent.column)fail('RIFT_CONVERSION_IDENTITY_INVALID');
  const current=witness.current;
  if(current?.verified!==true||current.method!=='unique_progress_label_yellow_ring_down_triangle'||current.nodeId!==chosen[0].id||current.zone!==proof.intent.zone||current.floor!==proof.intent.floor||current.column!==proof.intent.column||current.labelScore<.95||current.ringCoverage<.08||Math.min(...current.quadrants)<.04||JSON.stringify(current.box)!==JSON.stringify(chosen[0].box))fail('RIFT_CURRENT_WITNESS_INVALID');
  triangleEvidence(im,current.triangle,chosen[0]);
  if(!first){first={source,node:chosen[0]};continue;}
  if(f.atMs-first.source.frame.atMs<200)continue;
  if(f.atMs-first.source.frame.atMs>2500||f.sha256===first.source.frame.sha256||source.packet.binding.pixelSha256===first.source.packet.binding.pixelSha256)fail('RIFT_CONVERSION_PAIR_INVALID');
  return {researchOnly:true,formalAuthority:false,node:{zone:o.zone,floor:chosen[0].floor,column:chosen[0].column},
   frames:[first.source.frame,f],method:'same_episode_rift_to_battle_yellow_ring_label_triangle_and_direct_lattice'};
 }
 fail('RIFT_CONVERSION_PAIR_INCOMPLETE');
}
module.exports={hsv,isPurple,facts,selectRift,validateRiftProof,dispatchOnce,previewRift,convertedBattle,modalVisible};
