'use strict';
function verifyPreview(proof,o){
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
 return {kind:'match'};
}
module.exports={verifyPreview};
