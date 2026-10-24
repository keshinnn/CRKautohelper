'use strict';
const crypto=require('node:crypto'),{validateFrame,boxValid}=require('./node-selector.cjs');
const {isDeepStrictEqual}=require('node:util');
function previewAnchor(m,p,f){
 if(m?.absoluteFloorKnown!==true)return null;
 if(m.floorAnchorSource==='visible_top_gate')return {valid:true};
 if(m.floorAnchorSource!=='verified_preview_pixel_registration')return null;
 const e=m.registrationEvidence,t=p.v2TrackedMap,r=e?.registration;
 if(!e||!t||!isDeepStrictEqual(m,t.mapReview)||!isDeepStrictEqual(e,Object.fromEntries(Object.entries(t).filter(([k])=>k!=='mapReview')))||e.verified!==true||e.previewOnly!==true||e.actionsExecuted!==false||e.method!=='fresh_same_zone_direct_map_pixel_registration'||e.pixelSha256!==p.binding.pixelSha256||e.zone!==p.progress?.displayedZone||e.windowKey!==f.windowKey||e.geometryVersion!==f.geometryVersion||Math.abs(e.atMs-f.atMs)>.001||!Number.isFinite(e.sourceAtMs)||!(e.atMs-e.sourceAtMs>0&&e.atMs-e.sourceAtMs<=2500)||!/^[a-f0-9]{64}$/.test(e.sourceImageSha256||'')||!/^[a-f0-9]{64}$/.test(e.sourcePixelSha256||'')||!/^[a-f0-9]{32}$/.test(e.sourceFrameId||''))return null;
 if(r?.verified!==true||r.actionsExecuted!==false||r.method!=='map_pixel_translation_and_node_consensus'||!isDeepStrictEqual(r.pixelSha256,[e.sourcePixelSha256,p.binding.pixelSha256])||!isDeepStrictEqual(r.frameIds,[e.sourcePixelSha256.slice(0,20),p.binding.pixelSha256.slice(0,20)])||!Number.isInteger(r.rowOffset)||!Number.isInteger(r.inliers)||r.inliers<18||!Number.isInteger(r.mutualMatches)||r.mutualMatches<r.inliers||!Number.isFinite(r.scale)||r.scale<.985||r.scale>1.015||!Number.isFinite(r.angleDegrees)||Math.abs(r.angleDegrees)>.6||!Array.isArray(r.pairs)||r.pairs.length<5||new Set(r.pairs.map(x=>x.beforeNode)).size!==r.pairs.length||new Set(r.pairs.map(x=>x.afterNode)).size!==r.pairs.length||new Set(r.pairs.map(x=>x.beforeRow)).size<2)return null;
 for(const pair of r.pairs){const n=m.nodes?.find(n=>n.id===pair.afterNode);if(!n||n.floor!==n.visibleRow+r.rowOffset||pair.beforeRow-pair.afterRow!==r.rowOffset||n.visibleRow!==pair.afterRow||n.column!==pair.column)return null;}
 return {valid:true,source:{verified:true,imageSha256:e.sourceImageSha256,frameId:e.sourceFrameId}};
}
function mapActions(p,m,nodes){
 const a=p.v2MapActions;
 const bound=a?.verified===true&&a.actionsExecuted===false&&a.pixelSha256===p.binding.pixelSha256&&a.method==='original_pixel_orange_fill_and_check_mask_unique_path';
 for(const n of nodes){
  const e=bound?a.nodes?.[n.id]:null;
  const valid=e?.verified===true&&JSON.stringify(e.box)===JSON.stringify(n.box);
  n.available=valid&&n.type==='battle'&&e.available===true&&e.completed===false&&Number.isFinite(e.orangeCoverage)&&e.orangeCoverage>=.2&&e.orangeCoverage<=1;
  if(valid)n.completed=e.completed===true&&Number.isFinite(e.checkMaskIoU)&&e.checkMaskIoU>=.8&&e.checkMaskIoU<=1;
 }
 const c=bound?a.current:null,path=c?.completedPath;
 if(c?.verified===true&&c.inProgress===true)return markerCurrent(p,m,nodes,c);
 if(c?.verified!==true||c.inProgress!==false||!Array.isArray(path)||path.length<2||new Set(path).size!==path.length||path.at(-1)!==c.nodeId)return null;
 const gates=nodes.filter(n=>n.type==='exit'&&n.floor===0);
 if(gates.length!==1||path[0]!==gates[0].id||nodes.filter(n=>n.completed).length!==path.length-1)return null;
 for(let i=1;i<path.length;i++){
  const n=nodes.find(n=>n.id===path[i]);
  if(!n||n.completed!==true||n.floor!==i||m.edges.filter(e=>e.from===path[i-1]&&e.to===path[i]&&Number.isFinite(e.pixel_support)&&e.pixel_support>=.85&&e.pixel_support<=1).length!==1)return null;
 }
 return {nodeId:c.nodeId,verified:true,inProgress:false};
}
function markerCurrent(p,m,nodes,c){
 const n=nodes.find(n=>n.id===c.nodeId),t=c.triangle;
 const range=(v,lo,hi)=>Number.isFinite(v)&&v>=lo&&v<=hi;
 if(c.method!=='unique_progress_label_yellow_ring_down_triangle'||m.absoluteFloorKnown!==true||m.floorAnchorSource!=='visible_top_gate'||nodes.filter(n=>n.type==='exit').length!==1||!n||n.available!==true||n.completed!==false||JSON.stringify(c.box)!==JSON.stringify(n.box)||c.zone!==p.progress?.displayedZone||c.floor!==n.floor||c.column!==n.column||!range(c.labelScore,.95,1)||!range(c.ringCoverage,.08,1)||!Array.isArray(c.quadrants)||c.quadrants.length!==4||!c.quadrants.every(v=>range(v,.04,1)))return null;
 const frame={width:p.binding.width,height:p.binding.height};
 if(!boxValid(c.labelBox,frame)||!boxValid(t?.box,frame)||!Number.isFinite(t.upperWidth)||t.upperWidth<=0||!range(t.lowerWidth,0,t.upperWidth*.8))return null;
 const labels=(p.evidence||[]).filter(r=>r.text?.replace(/\s/g,'')==='進行中'&&range(r.score,.95,1));
 if(labels.length!==1||labels[0].score!==c.labelScore||!Array.isArray(labels[0].box)||labels[0].box.length!==4||labels[0].box.some(q=>!Array.isArray(q)||q.length!==2||!q.every(Number.isFinite)))return null;
 const points=labels[0].box,xs=points.map(q=>q[0]),ys=points.map(q=>q[1]);
 const label=[Math.min(...xs),Math.min(...ys),Math.max(...xs)-Math.min(...xs),Math.max(...ys)-Math.min(...ys)];
 if(JSON.stringify(label)!==JSON.stringify(c.labelBox))return null;
 const [x,y,w,h]=n.box,[lx,ly,lw]=label,[tx,ty,tw,th]=t.box;
 if(Math.abs(lx+lw/2-x-w/2)>w*.45||!range(ly-y-h,-h*.35,h*.35)||!range(tw,w*.15,w*.45)||!range(th,h*.1,h*.3)||Math.abs(tx+tw/2-x-w/2)>w*.15||ty<y-h*.4||ty+th>y)return null;
 return {nodeId:n.id,verified:true,inProgress:true};
}
function bind(frame,p){validateFrame(frame,frame.atMs);const raw=frame.png,b=p?.binding;if(!Buffer.isBuffer(raw)||raw.length<33||raw.subarray(0,8).toString('hex')!=='89504e470d0a1a0a'||crypto.createHash('sha256').update(raw).digest('hex')!==frame.sha256||raw.readUInt32BE(16)!==frame.width||raw.readUInt32BE(20)!==frame.height||b?.frameId!==frame.id||b.imageSha256!==frame.sha256||b.width!==frame.width||b.height!==frame.height||!/^[a-f0-9]{64}$/.test(b.pixelSha256||'')||p.flow?.frameId!==b.pixelSha256.slice(0,20)||p.actionsExecuted!==false)throw Error('OBSERVATION_BINDING_INVALID');const {png,...f}=frame;return structuredClone(f);}
function adaptMap(frame,p){const f=bind(frame,p),m=p.mapReview;if(p.flow.state!=='MAP'||m?.frameId!==p.binding.pixelSha256.slice(0,20)||!Array.isArray(m.nodes)||!Array.isArray(m.edges))throw Error('MAP_EVIDENCE_INVALID');const anchored=m.absoluteFloorKnown===true&&m.floorAnchorSource==='visible_top_gate'&&m.nodes.filter(n=>n.type==='exit').length===1;
 const nodes=m.nodes.map(n=>{if(!boxValid(n.box,f)||!Number.isFinite(n.score)||n.score<0||n.score>1)throw Error('COORDINATE_INVALID');return {id:n.id,type:n.type,floor:n.type==='exit'&&anchored?0:n.floor,column:n.column??null,box:[...n.box],score:n.score,completed:n.completed===true};});
 const completedCurrent=mapActions(p,m,nodes);
 const c=m.currentPosition;const current=c?.verified===true&&c.method==='reviewed_current_node_pixels_and_unique_progress_label'&&Number.isFinite(c.correlation)&&c.correlation>=.985&&c.correlation<=1&&Number.isFinite(c.appearanceMAE)&&c.appearanceMAE>=0&&c.appearanceMAE<=.055&&nodes.some(n=>n.id===c.nodeId)?{nodeId:c.nodeId,verified:true,inProgress:true}:completedCurrent;
 const progress=p.progress,zoneVerified=Number.isInteger(progress?.displayedZone)&&progress.displayedZone>=1&&progress.displayedZone<=10&&Number.isFinite(progress.score)&&progress.score>=.9&&progress.score<=1&&progress.conflictingEvidence===false;
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
  const anchor=previewAnchor(m,p,f);
  if(m?.frameId===p.binding.pixelSha256.slice(0,20)&&anchor?.valid===true&&match?.length===1&&zone?.displayedZone===n.zone&&zone.conflictingEvidence===false&&zone.score>=.9&&Number.isInteger(n.floor)&&Number.isInteger(n.column)&&n.ringCoverage>=.08&&n.quadrants?.length===4&&n.quadrants.every(x=>Number.isFinite(x)&&x>=.04))return {frame:f,state:'PREVIEW',verified:true,zone:n.zone,floor:n.floor,event:'battle',selectedNode:structuredClone(n),controlsVerified:true,identityStatus:'INDEPENDENT_PREVIEW_NODE_PIXELS',...(anchor.source?{registrationSource:anchor.source}:{})};
 }
 if(p.flow.state!=='NODE_BATTLE')return {frame:f,state:p.flow.state==='LOADING'?'TRANSITION':p.flow.state==='MAP'?'MAP':'UNKNOWN',verified:p.flow.state!=='UNKNOWN'&&p.flow.confidence>=.88};const h=p.nodeHeader,targets=(p.flow.targets||[]).filter(t=>t.target==='enter'&&t.verified===true&&boxValid(t.box,f));const recognized=h?.verified===true&&h.context==='NODE_BATTLE'&&Number.isInteger(h.floor)&&h.floor>=1&&p.flow.confidence>=.88;
 // V1 packets have no independent selected-preview-node pixel proof. Never
 // turn pending intent, in-progress position or an invented field into one.
 return {frame:f,state:recognized?'PREVIEW':'UNKNOWN',verified:recognized,zone:p.progress?.displayedZone??null,floor:recognized?h.floor:null,event:'battle',selectedNode:null,controlsVerified:targets.length===1,identityStatus:'PREVIEW_IDENTITY_UNPROVEN'};
}
module.exports={adaptMap,adaptPreview};
