'use strict';
const fs=require('fs'),path=require('path');
const {convertedBattle}=require('./rift-proof.cjs');
const {verifyContextPixels}=require('./rift-context.cjs');
const {identity,pending,verifyPair,trustedResultFrame,validatePhaseFrames}=require('./result-evidence.cjs');
const {adaptMap}=require('../../lib/observer-adapter.cjs');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
const compact=t=>t.replace(/\s/g,'').replaceAll('读','讀').replaceAll('败','敗');
function waitEvidence(r,converted){
 const rows=r.evidence.filter(x=>x.score>=.75&&x.score<=1);
 if(rows.some(x=>/失敗|DEFEAT/i.test(compact(x.text))))return null;
 // These are wait-only contexts after an independently confirmed conversion,
 // never result identity, world updates, or permissions to issue game inputs.
 if(converted&&rows.some(x=>x.score>=.9&&/^\d{2}:\d{2}\.\d{2}$/.test(compact(x.text))))return 'RESULT_ANIMATION_WAIT_ONLY';
 const timer=rows.filter(x=>x.score>=.9&&/^\d{2}:\d{2}$/.test(compact(x.text)));
 if(converted&&timer.length===1&&rows.some(x=>x.score>=.9&&compact(x.text)==='自動')&&rows.some(x=>/^[x×]\d+(?:\.\d+)?$/i.test(compact(x.text))))return 'CONVERTED_COMBAT_WAIT_ONLY';
 return null;
}
function loading(packet){
 return packet.evidence.filter(r=>r.score>=.9&&compact(r.text).replace(/[.。…]+$/,'')==='讀取中').length===1;
}
function completeRift({proof,riftReceipt,folder,output,episode,rows,bind,event,save}){
 require('./rift-transaction.cjs').validateConfirmedRift(riftReceipt,proof);
 function sources(name){
  const m=read(path.join(folder,name,'manifest.json')),c=m.cases[0];
  return {m,c,list:c.frames.filter(f=>f.packet).map(f=>bind(c,f,m.videoSha256))};
 }
 const conversion=sources('converted-analysis-v2');
 const converted=convertedBattle(proof,conversion.list,read(path.join(folder,'converted-current.json')));
 validatePhaseFrames(converted.frames,riftReceipt.frames.at(-1).sourcePtsMs);
 const usedConversion=conversion.list.filter(s=>converted.frames.some(f=>f.id===s.frame.id));
 verifyContextPixels(usedConversion,output,'converted');save('rift-conversion.json',{...converted,transactionId:riftReceipt.transactionId});
 event('RIFT_CONVERTED_BATTLE_CONFIRMED',converted.frames.at(-1).atMs,converted);
 const battle=sources('second-battle-analysis');
 const battleEnd=validatePhaseFrames(battle.c.frames,converted.frames.at(-1).sourcePtsMs);
 if(battle.list.length!==battle.c.frames.length||battle.list.some(s=>s.packet.flow.state!=='BATTLE'))throw Error('SECOND_BATTLE_UNPROVEN');
 for(const s of battle.list)event('SECOND_RECORDED_BATTLE_OBSERVATION',s.frame.atMs,{frame:s.frame,state:s.packet.flow.state});
 const input=read(path.join(folder,'second-result-input.json')),observed=read(path.join(folder,'second-result-ocr.json'));
 if(input.videoSha256!==episode.videoSha256||observed.length!==input.cases[0].frames.length)throw Error('SECOND_RESULT_SOURCE_CHANGED');
 validatePhaseFrames(input.cases[0].frames,battleEnd);
 const sourceByFrame=new Map(rows),intent=proof.intent;let previous=null,receipt=null;
 const {decodeRgbPng}=require('./verify_research.cjs'),crypto=require('crypto');
 const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
 for(let i=0;i<observed.length;i++){
  const f=input.cases[0].frames[i],r=observed[i],source=sourceByFrame.get(f.frameIndex),candidate=trustedResultFrame(f,source,episode.videoSha256,proof.frame.geometryVersion);
  const png=fs.readFileSync(f.image),im=decodeRgbPng(png);
  if(im.w!==episode.size[0]||im.h!==episode.size[1]||sha(png)!==f.sha256||r.imageSha256!==f.sha256||sha(im.rgb)!==source.rgbSha256||r.pixelSha256!==source.rgbSha256)throw Error('SECOND_RESULT_SOURCE_CHANGED');
  const found=identity(r.evidence,intent);
  if(!found){
   previous=null;const wait=pending(r.evidence,intent)?'RESULT_PENDING':waitEvidence(r,true);
   event('SECOND_'+(wait||'RESULT_UNKNOWN'),f.sourcePtsMs,{frameIndex:f.frameIndex,noInput:true});
   if(!wait)throw Error('SECOND_RESULT_UNKNOWN');continue;
  }
  event('SECOND_RESULT_CANDIDATE',f.sourcePtsMs,{frameIndex:f.frameIndex,identity:found});
  if(previous&&candidate.sourcePtsMs-previous.sourcePtsMs>=200){
   receipt=verifyPair([previous,candidate],intent,path.join(output,'second-independent-result-reread.json'));
   save('second-result-proof.json',{...receipt,conversion:converted,nodeId:proof.nodeId,transactionId:riftReceipt.transactionId});
   event('SECOND_RESULT_CONFIRMED_RESEARCH',f.sourcePtsMs,{receipt:'second-result-proof.json'});break;
  }
  if(!previous)previous=candidate;
 }
 if(!receipt)throw Error('SECOND_RESULT_PAIR_INCOMPLETE');
 const returned=sources('second-return-wait-v2');
 validatePhaseFrames(returned.c.frames,receipt.frames.at(-1).sourcePtsMs);
 let first=null;
 for(const s of returned.list){
  if(s.packet.flow.state==='UNKNOWN'&&loading(s.packet)){event('SECOND_LOADING_WAIT_ONLY',s.frame.atMs,{frame:s.frame,noInput:true});continue;}
  const o=adaptMap({...s.frame,png:s.png},s.packet);
  if(o.state!=='MAP'||!o.verified||!o.anchorVerified||!o.current?.verified)throw Error('SECOND_RETURN_MAP_UNPROVEN');
  const n=o.nodes.find(n=>n.id===o.current.nodeId&&n.floor===intent.floor&&n.column===intent.column&&n.completed===true);
  if(!n||o.zone!==intent.zone)throw Error('SECOND_COMPLETION_CONFLICT');
  event('SECOND_RETURN_MAP_OBSERVED',s.frame.atMs,{frame:s.frame,current:o.current});
  if(!first){first={o,pixelSha256:s.packet.binding.pixelSha256};continue;}
  const previous=first.o;
  if(o.frame.geometryVersion!==previous.frame.geometryVersion||o.frame.width!==previous.frame.width||o.frame.height!==previous.frame.height||o.frame.windowKey!==previous.frame.windowKey||JSON.stringify(o.frame.origin)!==JSON.stringify(previous.frame.origin)){
   first={o,pixelSha256:s.packet.binding.pixelSha256};event('SECOND_WORLD_GEOMETRY_RESET',s.frame.atMs,{noInput:true});continue;
  }
  if(o.frame.atMs-previous.frame.atMs<200)continue;
  if(o.frame.atMs-previous.frame.atMs>2500||o.frame.id===previous.frame.id||o.frame.sha256===previous.frame.sha256||s.packet.binding.pixelSha256===first.pixelSha256||o.current.nodeId!==previous.current.nodeId)throw Error('SECOND_WORLD_PAIR_INVALID');
  event('SECOND_WORLD_STATE_UPDATED',s.frame.atMs,{zone:o.zone,completedFloor:n.floor,column:n.column});
  return {completed:true,result:receipt,worldUpdated:true};
 }
 throw Error('SECOND_RETURN_PAIR_INCOMPLETE');
}
module.exports={completeRift,waitEvidence,loading};
