'use strict';
const fs=require('node:fs'),crypto=require('node:crypto');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const hash=v=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);
function invalid(){throw Error('REPLAY_CASE_CONTRACT_INVALID');}
function buildReplayGate(c){
 const pre=c?.preFrames,frames=c?.frames,window=c?.gateWindowMs,box=c?.clientBox;
 if(!Array.isArray(pre)||pre.length!==2||!pre.every(Number.isInteger)||pre[0]<0||pre[1]<=pre[0]||
    !Array.isArray(frames)||frames.length<3||!Array.isArray(window)||window.length!==2||
    !window.every(Number.isFinite)||!Array.isArray(box)||box.length!==4||
    !box.every(Number.isFinite)||Math.min(...box.slice(0,2))<0||Math.min(...box.slice(2))<=0)invalid();
 for(let i=0;i<frames.length;i++){
  const f=frames[i],last=frames[i-1];
  if(!Number.isInteger(f.frameIndex)||f.frameIndex<0||!Number.isFinite(f.sourcePtsMs)||
     !Number.isFinite(f.atMs)||last&&(f.frameIndex<=last.frameIndex||
     f.sourcePtsMs<=last.sourcePtsMs||f.atMs<last.atMs))invalid();
 }
 const first=frames[0].frameIndex===pre[0]?0:frames[0].frameIndex===pre[0]-1?1:-1;
 if(first<0||frames[first]?.frameIndex!==pre[0]||
    frames[first+1]?.frameIndex!==pre[1]||frames[first+2]?.frameIndex!==pre[1]+1)invalid();
 const dispatch=frames[first+1],post=frames[first+2],size=dispatch.size;
 if(!Array.isArray(size)||size.length!==2||!size.every(x=>Number.isInteger(x)&&x>0)||
    box[0]+box[2]>size[0]||box[1]+box[3]>size[1]||
    window.some(t=>Math.abs(t-dispatch.atMs)>.001)||
    c.previewFromPtsMs!=null&&(!Number.isFinite(c.previewFromPtsMs)||
    Math.abs(c.previewFromPtsMs-post.sourcePtsMs)>.001))invalid();
 return {windowMs:[...window],clientBox:[...box],previewFromPtsMs:post.sourcePtsMs};
}
function loadReplayFrames(c,fallbackVideoSha,observerContractVersion){
 const direct=c.videoSha256,nested=c.source?.videoSha256;
 if(direct!=null&&nested!=null&&direct!==nested)throw Error('SOURCE_IDENTITY_CONFLICT');
 const video=direct??nested??fallbackVideoSha;
 if(!hash(video)||!Array.isArray(c.frames))throw Error('SOURCE_IDENTITY_INVALID');
 return c.frames.map(e=>{
  const png=fs.readFileSync(e.image);
  if(!hash(e.sha256)||sha(png)!==e.sha256||png.length<24||
     png.subarray(0,8).toString('hex')!=='89504e470d0a1a0a')throw Error('SOURCE_CHANGED');
  const p=JSON.parse(fs.readFileSync(e.packet,'utf8')),b=p.binding;
  if(!Array.isArray(e.size)||e.size.length!==2||png.readUInt32BE(16)!==e.size[0]||
     png.readUInt32BE(20)!==e.size[1]||b?.width!==e.size[0]||b?.height!==e.size[1])
    throw Error('SOURCE_DIMENSIONS_MISMATCH');
  if(b?.imageSha256!==e.sha256)throw Error('SOURCE_CHANGED');
  if(!Number.isInteger(e.frameIndex)||e.frameIndex<0||
     b.frameId!==sha(video+String(e.frameIndex)+e.sha256).slice(0,32))
    throw Error('SOURCE_FRAME_ID_MISMATCH');
  if(typeof e.geometryVersion!=='string'||!e.geometryVersion)throw Error('SOURCE_GEOMETRY_INVALID');
  return {png,packet:p,frame:{id:b.frameId,sha256:e.sha256,atMs:e.atMs,
   sourcePtsMs:e.sourcePtsMs,width:e.size[0],height:e.size[1],
   geometryVersion:e.geometryVersion,windowKey:'offline:original-video',origin:[0,0],
   ...(observerContractVersion!=null?{observerContractVersion}:{})}};
 });
}
module.exports={buildReplayGate,loadReplayFrames};
