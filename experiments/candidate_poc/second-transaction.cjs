'use strict';
const {adaptMap,adaptPreview}=require('../../lib/observer-adapter.cjs');
const {runReplay}=require('../../lib/replay-runner.cjs');
const {plan}=require('./two_node_attempt.cjs');
const same=(a,b)=>['zone','floor','column','event','mode'].every(k=>a?.[k]===b?.[k]);
async function runSecond({frames,gate,previousDecision,completedNode}){
 if(!frames?.length||frames.length<3)throw Error('SECOND_SEQUENCE_MISSING');
 const initial=frames.slice(0,2).map(s=>adaptMap({...s.frame,png:s.png},s.packet));
 for(const o of initial){
  const n=o.nodes?.find(n=>n.id===o.current?.nodeId);
  if(!o.current?.verified||n?.completed!==true||o.zone!==completedNode.zone||n.floor!==completedNode.floor||n.column!==completedNode.column)throw Error('SECOND_CURRENT_POSITION_CONFLICT');
 }
 const decision=plan(...initial);
 if(!same(previousDecision,decision.intent))throw Error('SECOND_PLAN_CHANGED');
 // Reacquire current-frame proof; never reuse the earlier map coordinates.
 const replay=await runReplay({frames,gate,intent:decision.intent,observe:async s=>{
  const frame={...s.frame,png:s.png};
  return s.packet.flow?.state==='MAP'&&!s.packet.v2Preview?.verified?adaptMap(frame,s.packet):adaptPreview(frame,s.packet);
 }});
 return {decision,...replay};
}
module.exports={runSecond,same};
