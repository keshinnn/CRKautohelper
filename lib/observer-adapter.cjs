'use strict';
const crypto=require('node:crypto'),{validateFrame,boxValid}=require('./node-selector.cjs');
function bind(frame,p){validateFrame(frame,frame.atMs);const raw=frame.png,b=p?.binding;if(!Buffer.isBuffer(raw)||raw.length<33||raw.subarray(0,8).toString('hex')!=='89504e470d0a1a0a'||crypto.createHash('sha256').update(raw).digest('hex')!==frame.sha256||raw.readUInt32BE(16)!==frame.width||raw.readUInt32BE(20)!==frame.height||b?.frameId!==frame.id||b.imageSha256!==frame.sha256||b.width!==frame.width||b.height!==frame.height||!/^[a-f0-9]{64}$/.test(b.pixelSha256||'')||p.flow?.frameId!==b.pixelSha256.slice(0,20)||p.actionsExecuted!==false)throw Error('OBSERVATION_BINDING_INVALID');const {png,...f}=frame;return structuredClone(f);}
function adaptMap(frame,p){const f=bind(frame,p),m=p.mapReview;if(p.flow.state!=='MAP'||m?.frameId!==p.binding.pixelSha256.slice(0,20)||!Array.isArray(m.nodes)||!Array.isArray(m.edges))throw Error('MAP_EVIDENCE_INVALID');const anchored=m.absoluteFloorKnown===true&&m.floorAnchorSource==='visible_top_gate'&&m.nodes.filter(n=>n.type==='exit').length===1;
 const nodes=m.nodes.map(n=>{if(!boxValid(n.box,f)||!Number.isFinite(n.score)||n.score<0||n.score>1)throw Error('COORDINATE_INVALID');return {id:n.id,type:n.type,floor:n.type==='exit'&&anchored?0:n.floor,column:n.column??null,box:[...n.box],score:n.score,completed:n.completed===true};});
 const c=m.currentPosition;const current=c?.verified===true&&c.method==='reviewed_current_node_pixels_and_unique_progress_label'&&Number.isFinite(c.correlation)&&c.correlation>=.985&&c.correlation<=1&&Number.isFinite(c.appearanceMAE)&&c.appearanceMAE>=0&&c.appearanceMAE<=.055&&nodes.some(n=>n.id===c.nodeId)?{nodeId:c.nodeId,verified:true,inProgress:true}:null;
 const progress=p.progress,zoneVerified=Number.isInteger(progress?.displayedZone)&&progress.displayedZone>=1&&progress.displayedZone<=9&&Number.isFinite(progress.score)&&progress.score>=.9&&progress.score<=1&&progress.conflictingEvidence===false;
 const latticeVerified=anchored&&m.columns?.length===4&&m.columns.every(Number.isFinite)&&new Set(m.columns).size===4&&nodes.length>=6&&new Set(nodes.filter(n=>n.type!=='exit').map(n=>n.floor)).size>=2&&m.edges.filter(e=>Number.isFinite(e.pixel_support)&&e.pixel_support>=.85&&e.pixel_support<=1).length>=3;
 return {frame:f,state:'MAP',stateVerified:p.flow.confidence>=.75&&nodes.length>=4||latticeVerified,verified:zoneVerified&&(p.flow.confidence>=.88||p.flow.confidence>=.85&&latticeVerified),zone:progress?.displayedZone??null,anchorVerified:anchored,nodes,edges:m.edges.map(e=>({from:e.from,to:e.to,pixelSupport:e.pixel_support})),current};
}
function adaptPreview(frame,p){const f=bind(frame,p),v=p.v2Preview;
 if(v?.verified===true&&v.method==='unique_uncompleted_battle_green_outline_and_ordinary_timer_enter'&&v.pixelSha256===p.binding.pixelSha256&&v.actionsExecuted===false&&v.controlsVerified===true&&boxValid(v.enterBox,f)&&v.selectedNode?.verified===true&&boxValid(v.selectedNode.box,f)){
  const n=v.selectedNode,m=v.recoveredMapReview||p.mapReview,zone=p.progress;
  const recovered=(v.recoveredNodes||[]).filter(x=>{
   const cols=m?.columns,gate=m?.nodes?.filter(g=>g.type==='exit');
   if(!Array.isArray(cols)||cols.length!==4||!cols.every(Number.isFinite)||gate?.length!==1||x.recovered!==true||!Number.isFinite(x.iconScore)||x.iconScore<.9||!boxValid(x.box,f)||!Number.isInteger(x.floor)||!Number.isInteger(x.column)||x.column<1||x.column>4)return false;
   const spacing=(cols[3]-cols[0])/3,cx=x.box[0]+x.box[2]/2,cy=x.box[1]+x.box[3]/2,gy=gate[0].box[1]+gate[0].box[3]/2;
   return Math.abs(cx-cols[x.column-1])<=spacing*.08&&Math.abs(cy-gy-x.floor*spacing)<=spacing*.08;
  });
  const match=m?.nodes?.concat(recovered).filter(x=>x.id===n.nodeId&&x.floor===n.floor&&x.column===n.column&&x.type==='battle'&&x.completed===false&&JSON.stringify(x.box)===JSON.stringify(n.box));
  if(m.frameId===p.binding.pixelSha256.slice(0,20)&&m.absoluteFloorKnown===true&&m.floorAnchorSource==='visible_top_gate'&&match?.length===1&&zone?.displayedZone===n.zone&&zone.conflictingEvidence===false&&zone.score>=.9&&Number.isInteger(n.floor)&&Number.isInteger(n.column)&&n.ringCoverage>=.08&&n.quadrants?.length===4&&n.quadrants.every(x=>Number.isFinite(x)&&x>=.04))return {frame:f,state:'PREVIEW',verified:true,zone:n.zone,floor:n.floor,event:'battle',selectedNode:structuredClone(n),controlsVerified:true,identityStatus:'INDEPENDENT_PREVIEW_NODE_PIXELS'};
 }
 if(p.flow.state!=='NODE_BATTLE')return {frame:f,state:p.flow.state==='LOADING'?'TRANSITION':p.flow.state==='MAP'?'MAP':'UNKNOWN',verified:p.flow.state!=='UNKNOWN'&&p.flow.confidence>=.88};const h=p.nodeHeader,targets=(p.flow.targets||[]).filter(t=>t.target==='enter'&&t.verified===true&&boxValid(t.box,f));const recognized=h?.verified===true&&h.context==='NODE_BATTLE'&&Number.isInteger(h.floor)&&h.floor>=1&&p.flow.confidence>=.88;
 // V1 packets have no independent selected-preview-node pixel proof. Never
 // turn pending intent, in-progress position or an invented field into one.
 return {frame:f,state:recognized?'PREVIEW':'UNKNOWN',verified:recognized,zone:p.progress?.displayedZone??null,floor:recognized?h.floor:null,event:'battle',selectedNode:null,controlsVerified:targets.length===1,identityStatus:'PREVIEW_IDENTITY_UNPROVEN'};
}
module.exports={adaptMap,adaptPreview};
