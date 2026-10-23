'use strict';
const issued=new WeakSet();
function fail(code){throw Object.assign(Error(code),{code});}
const numbers=(a,n)=>Array.isArray(a)&&a.length===n&&a.every(Number.isFinite);
function validateFrame(f,nowMs){if(!f||typeof f.id!=='string'||!f.id||!/^[a-f0-9]{64}$/.test(f.sha256||'')||!Number.isFinite(f.atMs)||!Number.isFinite(nowMs)||nowMs-f.atMs<0||nowMs-f.atMs>2500||typeof f.windowKey!=='string'||!f.windowKey||typeof f.geometryVersion!=='string'||!f.geometryVersion||![f.width,f.height].every(v=>Number.isInteger(v)&&v>0)||!numbers(f.origin,2))fail('FRAME_INVALID');}
function boxValid(b,f){return numbers(b,4)&&b[0]>=0&&b[1]>=0&&b[2]>0&&b[3]>0&&b[0]+b[2]<=f.width&&b[1]+b[3]<=f.height;}
function freeze(x){if(x&&typeof x==='object'){for(const v of Object.values(x))freeze(v);Object.freeze(x);}return x;}
function iou(a,b){const s=Math.max(0,Math.min(a[0]+a[2],b[0]+b[2])-Math.max(a[0],b[0]))*Math.max(0,Math.min(a[1]+a[3],b[1]+b[3])-Math.max(a[1],b[1]));return s/(a[2]*a[3]+b[2]*b[3]-s);}
function selectNode(previous,current,intent,{nowMs}){
 if(!intent||!Number.isInteger(intent.zone)||intent.zone<1||intent.zone>9||!Number.isInteger(intent.floor)||intent.floor<1||intent.floor>31||!Number.isInteger(intent.column)||intent.column<1||intent.column>4||intent.event!=='battle'||!['select','resume'].includes(intent.mode))fail('INTENT_INVALID');
 for(const o of [previous,current]){validateFrame(o?.frame,nowMs);if(o.state!=='MAP'||o.verified!==true||o.zone!==intent.zone||o.anchorVerified!==true||!Array.isArray(o.nodes)||!Array.isArray(o.edges))fail('ANCHOR_MISSING');const ids=o.nodes.map(n=>n.id);if(ids.some(id=>typeof id!=='string'||!id)||new Set(ids).size!==ids.length)fail('MAP_AMBIGUOUS');}
 const a=previous.frame,b=current.frame;if(a.id===b.id||b.atMs-a.atMs<200||a.windowKey!==b.windowKey||a.geometryVersion!==b.geometryVersion||a.width!==b.width||a.height!==b.height||JSON.stringify(a.origin)!==JSON.stringify(b.origin)||a.sourcePtsMs!=null&&b.sourcePtsMs!=null&&b.sourcePtsMs<=a.sourcePtsMs)fail('STALE_GEOMETRY');
 const video=a.sourcePtsMs!=null||b.sourcePtsMs!=null;
 if(video&&(!Number.isFinite(a.sourcePtsMs)||!Number.isFinite(b.sourcePtsMs)||a.sourcePtsMs<0||b.sourcePtsMs<=a.sourcePtsMs))fail('FRAME_INVALID');
 const selected=[];const links=[];const predecessors=[];
 for(const o of [previous,current]){const matches=o.nodes.filter(n=>n.floor===intent.floor&&n.column===intent.column);if(matches.length!==1)fail('MAP_AMBIGUOUS');const n=matches[0];if(n.type!=='battle'||!Number.isFinite(n.score)||n.score<.48||n.score>1||n.completed!==false||!boxValid(n.box,o.frame))fail('COORDINATE_INVALID');
  if(intent.mode==='resume'){if(o.current?.verified!==true||o.current.inProgress!==true||o.current.nodeId!==n.id)fail('CURRENT_POSITION_UNPROVEN');links.push({mode:'resume',nodeId:n.id});}
  else {let from;if(intent.floor===1){const gates=o.nodes.filter(x=>x.type==='exit'&&x.floor===0);if(gates.length!==1)fail('ANCHOR_MISSING');from=gates[0];}else{if(o.current?.verified!==true)fail('CURRENT_POSITION_UNPROVEN');from=o.nodes.find(x=>x.id===o.current.nodeId&&x.completed===true&&x.floor===intent.floor-1);if(!from)fail('CURRENT_POSITION_UNPROVEN');}if(!boxValid(from.box,o.frame))fail('COORDINATE_INVALID');const edges=o.edges.filter(e=>e.from===from.id&&e.to===n.id&&Number.isFinite(e.pixelSupport)&&e.pixelSupport>=.85&&e.pixelSupport<=1);if(edges.length!==1)fail('CONNECTION_UNPROVEN');links.push({...edges[0]});}
  const predecessor=intent.mode==='resume'?n:o.nodes.find(x=>x.id===links.at(-1).from);
  predecessors.push(predecessor);selected.push(n);
 }
 const [p,n]=selected;const tolerance=Math.max(2,Math.min(...n.box.slice(2))*.02);if(iou(p.box,n.box)<.95||Math.hypot(p.box[0]+p.box[2]/2-n.box[0]-n.box[2]/2,p.box[1]+p.box[3]/2-n.box[1]-n.box[3]/2)>tolerance)fail('MAP_MOVING');
 const [u,v]=predecessors;
 if(p.id!==n.id||u.id!==v.id||u.floor!==v.floor||u.column!==v.column||u.type!==v.type||u.completed!==v.completed||iou(u.box,v.box)<.95||links[0].from!==links[1].from||links[0].to!==links[1].to)fail('MAP_MOVING');
 const margin=Math.max(3,Math.min(...n.box.slice(2))*.05);if(Math.min(...n.box.slice(2))/2<margin)fail('COORDINATE_INVALID');const proof=freeze(structuredClone({kind:'node-selection',sourceMode:video?'video':'capture',frame:b,previousFrame:a,previousFrameId:a.id,intent,nodeId:n.id,box:n.box,point:[n.box[0]+n.box[2]/2,n.box[1]+n.box[3]/2],connection:links,predecessors}));issued.add(proof);return proof;
}
function validateProof(p){if(!issued.has(p))fail('SELECTION_PROOF_INVALID');return p;}
module.exports={selectNode,validateProof,validateFrame,boxValid};
