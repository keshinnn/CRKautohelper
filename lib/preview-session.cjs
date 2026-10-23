'use strict';
const crypto=require('node:crypto'),{validateProof,validateFrame}=require('./node-selector.cjs'),{verifyPreview}=require('./preview-verifier.cjs');
const {createGeometry,clientToScreen}=require('./geometry.cjs');
class PreviewSession{
 #clock;#dispatch;#trace;#state='IDLE';#proof;#transactionId;#sentAt;#first;#lastFrame;#seen=new Set();#events=[];
 constructor({clock,dispatch,trace=()=>{}}){if(typeof clock!=='function'||typeof dispatch!=='function'||typeof trace!=='function')throw TypeError('explicit offline adapters required');this.#clock=clock;this.#dispatch=dispatch;this.#trace=trace;}
 #record(state,details={}){this.#state=state;const event={atMs:this.#clock(),state,...details};this.#events.push(event);try{this.#trace(structuredClone(event));}catch{this.#state='TRACE_FAILED';}return this.snapshot();}
 snapshot(){return structuredClone({state:this.#state,transactionId:this.#transactionId??null,events:this.#events});}
 async start(proof){if(this.#state!=='IDLE')return this.snapshot();try{validateProof(proof);validateFrame(proof.frame,this.#clock());}catch(e){return this.#record(e.code||'SELECTION_PROOF_INVALID');}
  this.#proof=proof;this.#lastFrame=proof.frame;this.#seen.add(proof.frame.id);this.#transactionId=crypto.randomUUID();this.#sentAt=this.#clock();this.#record('CLICK_SENT');if(this.#state==='TRACE_FAILED')return this.snapshot();
  const f=proof.frame,g=createGeometry({frame:{...f,id:f.id},contentRect:[0,0,f.width,f.height],analysisSize:[f.width,f.height],padding:[0,0,0,0]});
  const action=Object.freeze({kind:'click',transactionId:this.#transactionId,frameId:f.id,geometryVersion:f.geometryVersion,clientPoint:Object.freeze([...proof.point]),screenPoint:Object.freeze(clientToScreen(proof.point,g))});
  let receipt;try{receipt=await this.#dispatch(action);}catch{return this.#record('DISPATCH_UNCERTAIN');}
  if(receipt?.transactionId!==this.#transactionId||receipt?.frameId!==f.id)return this.#record('DISPATCH_UNCERTAIN');
  if(receipt.status==='not_sent')return this.#record('DISPATCH_NOT_SENT');if(receipt.status!=='sent')return this.#record('DISPATCH_UNCERTAIN');return this.#record('WAIT_PREVIEW');
 }
 observe(observation){if(!['WAIT_PREVIEW','PREVIEW_STABLE'].includes(this.#state))return this.snapshot();if(this.#clock()-this.#sentAt>=15000)return this.#record('PREVIEW_TIMEOUT');
  const o=structuredClone(observation),f=o?.frame;try{validateFrame(f,this.#clock());}catch{return this.#record('FRAME_INVALID');}
  const last=this.#lastFrame;if(f.windowKey!==this.#proof.frame.windowKey||this.#seen.has(f.id)||f.atMs<=last.atMs||f.sourcePtsMs!=null&&last.sourcePtsMs!=null&&f.sourcePtsMs<=last.sourcePtsMs)return this.#record('FRAME_INVALID');
  this.#seen.add(f.id);this.#lastFrame=f;const verdict=verifyPreview(this.#proof,o);if(verdict.kind==='reject')return this.#record(verdict.code);if(verdict.kind==='wait'){this.#first=null;return this.#record('WAIT_PREVIEW');}
  if(!this.#first||f.geometryVersion!==this.#first.geometryVersion||f.width!==this.#first.width||f.height!==this.#first.height||JSON.stringify(f.origin)!==JSON.stringify(this.#first.origin)){this.#first=f;return this.#record('PREVIEW_STABLE',{frameId:f.id});}
  if(f.atMs-this.#first.atMs<200)return this.#record('PREVIEW_STABLE',{frameId:f.id});
  return this.#record('PREVIEW_CONFIRMED',{frameId:f.id});
 }
}
module.exports={PreviewSession};
