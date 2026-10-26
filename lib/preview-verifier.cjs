'use strict';
function verifyPreview(proof,o,options={}){
 if(o?.state==='UNKNOWN')return {kind:'reject',code:'TRANSITION_UNKNOWN'};
 // A recognized map may only keep an existing transaction waiting. It does
 // not acquire the stronger zone/geometry authority needed for a new click.
 if(o?.state==='MAP'&&o.stateVerified===true)return {kind:'wait',code:'RECOGNIZED_MAP_WAIT_ONLY'};
 if(o?.verified!==true)return {kind:'reject',code:'EVIDENCE_UNVERIFIED'};
 if(['TRANSITION','MAP'].includes(o.state))return {kind:'wait'};
 if(o.state!=='PREVIEW')return {kind:'reject',code:'PREVIEW_MISMATCH'};
 const n=o.selectedNode,i=proof.intent;if(!n||n.verified!==true)return {kind:'reject',code:'PREVIEW_IDENTITY_UNPROVEN'};
 if(o.zone!==i.zone||o.floor!==i.floor||o.event!==i.event||n.zone!==i.zone||n.floor!==i.floor||n.column!==i.column)return {kind:'reject',code:'PREVIEW_MISMATCH'};
 if(o.controlsVerified!==true)return {kind:'reject',code:'PREVIEW_CONTROLS_UNPROVEN'};
 const registration=o.registrationSource;
 const original=[proof.frame,proof.previousFrame].some(f=>f&&f.id===registration?.frameId&&f.sha256===registration?.imageSha256);
 const additional=Array.isArray(options?.mapSources)&&options.mapSources.some(s=>{
  const f=s?.frame,c=o.frame,age=c?.atMs-f?.atMs;
  return f&&c&&f.id===registration?.frameId&&f.sha256===registration?.imageSha256&&
   typeof s.pixelSha256==='string'&&/^[a-f0-9]{64}$/.test(s.pixelSha256)&&s.pixelSha256===registration?.pixelSha256&&
   f.windowKey===c.windowKey&&f.geometryVersion===c.geometryVersion&&f.width===c.width&&f.height===c.height&&
   JSON.stringify(f.origin)===JSON.stringify(c.origin)&&age>0&&age<=2500;
 });
 if(registration!=null&&(registration.verified!==true||!original&&!additional))return {kind:'reject',code:'PREVIEW_REGISTRATION_SOURCE_MISMATCH'};
 return {kind:'match'};
}
module.exports={verifyPreview};
