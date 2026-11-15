'use strict';
// Isolated research result contract. No production authority is issued here.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{spawnSync}=require('child_process');
const {decodeRgbPng}=require('./verify_research.cjs');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const compact=t=>t.replace(/\s/g,'').replaceAll('级','級').replaceAll('区','區').replaceAll('层','層').replaceAll('胜','勝').replaceAll('败','敗');
function identity(evidence,intent){
 const all=evidence.filter(x=>x.score>=.75),r=evidence.filter(x=>x.score>=.9&&x.score<=1);
 if(all.some(x=>/失敗|敗北|DEFEAT/i.test(compact(x.text))))return null;
 const header=r.filter(x=>/^區域\d+第\d+層$/.test(compact(x.text)));
 const victory=r.filter(x=>compact(x.text)==='勝利');
 const time=r.filter(x=>/^\d{2}:\d{2}\.\d{2}$/.test(compact(x.text)));
 const roster=r.filter(x=>compact(x.text)==='最高等級');
 if(header.length!==1||victory.length!==1||time.length!==1||roster.length<2||
  new Set(roster.map(x=>JSON.stringify(x.box))).size<2||compact(header[0].text)!==`區域${intent.zone}第${intent.floor}層`)return null;
 return {zone:intent.zone,floor:intent.floor,time:compact(time[0].text)};
}
function pending(evidence,intent){
 const r=evidence.filter(x=>x.score>=.75&&x.score<=1);
 return !r.some(x=>/失敗|敗北|DEFEAT/i.test(compact(x.text)))&&
  r.filter(x=>compact(x.text)===`區域${intent.zone}第${intent.floor}層`||compact(x.text)===`區域${intent.zone}第${intent.floor}唇`).length===1&&
  r.filter(x=>/^\d{2}:\d{2}\.\d{2}$/.test(compact(x.text))).length===1;
}
function validatePair(a,b){
 return a.sourceKey===b.sourceKey&&a.geometryVersion===b.geometryVersion&&
  a.sha256!==b.sha256&&a.rgbSha256!==b.rgbSha256&&
  b.sourcePtsMs-a.sourcePtsMs>=200&&b.sourcePtsMs-a.sourcePtsMs<=2500;
}
function trustedResultFrame(f,row,sourceKey,geometryVersion){
 if(!row||f.frameIndex!==row.frameIndex||f.sourcePtsMs!==row.sourcePtsMs||f.geometryVersion!==geometryVersion)throw Error('RESULT_TIME_OR_GEOMETRY_CHANGED');
 return {...f,sourceKey,sourcePtsMs:row.sourcePtsMs,rgbSha256:row.rgbSha256,geometryVersion};
}
function validatePhaseFrames(frames,afterPts){
 if(!Number.isFinite(afterPts)||frames.length<2||frames.some((f,i)=>!Number.isFinite(f.sourcePtsMs)||f.sourcePtsMs<=(i?frames[i-1].sourcePtsMs:afterPts))||
  frames.at(-1).sourcePtsMs-frames[0].sourcePtsMs<200)throw Error('PHASE_SEQUENCE_INVALID');
 return frames.at(-1).sourcePtsMs;
}
function verifyPair(frames,intent,output){
 if(frames.length!==2||!validatePair(...frames))throw Error('RESULT_PAIR_INVALID');
 const script=path.join(__dirname,'result_pixels.py');
 const run=spawnSync('F:/CRK helper/.venv/Scripts/python.exe',['-B',script,output,...frames.map(f=>f.image)],
  {encoding:'utf8',timeout:60000,env:{...process.env,PYTHONUTF8:'1'}});
 if(run.status!==0)throw Error('RESULT_PIXEL_REREAD_FAILED:'+run.stderr);
 const raw=JSON.parse(fs.readFileSync(output,'utf8'));
 const ids=raw.map((r,i)=>{
  const f=frames[i],png=fs.readFileSync(f.image),im=decodeRgbPng(png);
  if(sha(png)!==f.sha256||r.imageSha256!==f.sha256||sha(im.rgb)!==f.rgbSha256||r.pixelSha256!==f.rgbSha256)throw Error('RESULT_PIXEL_BINDING_INVALID');
  const found=identity(r.evidence,intent);
  if(r.originalSemantic.state!=='VICTORY'||!found)throw Error('RESULT_IDENTITY_UNPROVEN');
  return found;
 });
 if(JSON.stringify(ids[0])!==JSON.stringify(ids[1]))throw Error('RESULT_IDENTITY_CONFLICT');
 return {researchResultVerified:true,formalAuthority:false,identity:ids[0],frames,
  method:'independent_native_pixel_reread_and_complete_original_result_semantics',
  limitation:'Independent execution of existing OCR, not a second OCR model. Requires trusted episode/battle binding from caller.'};
}
module.exports={identity,pending,validatePair,verifyPair,trustedResultFrame,validatePhaseFrames};
