'use strict';
const {selectNode}=require('../../lib/node-selector.cjs');
const {adaptMap}=require('../../lib/observer-adapter.cjs');
const {selectRift,dispatchOnce,previewRift,modalVisible}=require('./rift-proof.cjs');
const transactions=new WeakMap(),confirmedTransactions=new WeakSet(),confirmations=new WeakMap();
function freeze(x){if(x&&typeof x==='object'){for(const v of Object.values(x))freeze(v);Object.freeze(x);}return x;}
function planSupported(sources){
 if(sources.some(modalVisible))return {intent:null,attempts:[],reason:'RESEARCH_MODAL_WAIT_ONLY'};
 const observations=sources.map(s=>adaptMap({...s.frame,png:s.png},s.packet));
 const current=observations[1],attempts=[];
 if(!current.verified||!current.anchorVerified)return {intent:null,attempts,reason:'MAP_AUTHORITY_MISSING'};
 // Same deterministic floor/column order, expanded only by an independently
 // checked rift capability. No recorded branch is an input to this function.
 const nodes=current.nodes.filter(n=>!n.completed&&(n.type==='rift'||n.type==='battle'&&n.available))
  .sort((a,b)=>a.floor-b.floor||a.column-b.column);
 for(const n of nodes){
  const intent={zone:current.zone,floor:n.floor,column:n.column,event:n.type,mode:'select'};
  try{
   const proof=n.type==='rift'?selectRift(sources,observations,intent):selectNode(...observations,intent,{nowMs:current.frame.atMs});
   return {intent,proof,attempts,reason:n.type==='rift'?'TYPED_RIFT_RESEARCH_PROOF':'EXISTING_BATTLE_PROOF'};
  }catch(e){attempts.push({nodeId:n.id,event:n.type,code:e.code||e.message});}
 }
 return {intent:null,attempts,reason:'NO_PROVEN_SUPPORTED_NODE'};
}
function runRift({decision,after,recordedBranch,nowMs,currentFrame}){
 const events=[],proof=decision.proof;
 if(!proof||decision.intent?.event!=='rift')throw Error('RIFT_DECISION_REQUIRED');
 const same=['zone','floor','column','event'].every(k=>recordedBranch[k]===decision.intent[k]);
 if(!same)return {state:'BRANCH_NOT_RECORDED',events,actions:[],researchOnly:true};
 const action=dispatchOnce(proof,{nowMs,currentFrame});events.push({state:'RIFT_CLICK_SENT',atMs:nowMs,action});
 let first=null;
 for(const source of after){
  const o=adaptMap({...source.frame,png:source.png},source.packet),preview=previewRift(proof,source,o);
  events.push({state:'RIFT_PREVIEW_CANDIDATE',atMs:source.frame.atMs,preview});
  if(!first){first={preview,source};continue;}
  if(source.frame.atMs-first.preview.frame.atMs<200)continue;
  if(source.frame.atMs-first.preview.frame.atMs>2500||source.frame.sha256===first.preview.frame.sha256||source.packet.binding.pixelSha256===first.source.packet.binding.pixelSha256)throw Error('RIFT_PREVIEW_PAIR_INVALID');
  if(['zone','floor','column','event'].some(k=>preview[k]!==first.preview[k]))throw Error('RIFT_PREVIEW_IDENTITY_CONFLICT');
  events.push({state:'RIFT_PREVIEW_CONFIRMED_RESEARCH',atMs:source.frame.atMs});
  const result=freeze({state:'RIFT_PREVIEW_CONFIRMED_RESEARCH',actions:[action],events,previews:[first.preview,preview],researchOnly:true,formalVerifierChanged:false});
  transactions.set(result,{proof,sources:[first.source,source].map(s=>({frame:freeze(structuredClone(s.frame)),png:Buffer.from(s.png)}))});
  return result;
 }
 return {state:'RIFT_PREVIEW_PAIR_INCOMPLETE',actions:[action],events,researchOnly:true};
}
function confirmRiftTransaction(transaction,proof,output){
 const record=transactions.get(transaction);
 if(!record||record.proof!==proof)throw Error('RIFT_TRANSACTION_INVALID');
 if(confirmedTransactions.has(transaction))throw Error('RIFT_CONFIRMATION_ALREADY_ISSUED');
 require('./rift-context.cjs').verifyContextPixels(record.sources,output,'rift');
 const receipt=freeze(structuredClone({kind:'rift-preview-confirmation/research',formalAuthority:false,
  transactionId:transaction.actions[0].transactionId,sourceKey:proof.sourceKey,identity:proof.intent,
  frames:transaction.previews.map(p=>p.frame)}));
 confirmations.set(receipt,proof);confirmedTransactions.add(transaction);return receipt;
}
function validateConfirmedRift(receipt,proof){
 if(!receipt||confirmations.get(receipt)!==proof)throw Error('RIFT_CONFIRMATION_PROOF_INVALID');return receipt;
}
module.exports={planSupported,runRift,confirmRiftTransaction,validateConfirmedRift};
