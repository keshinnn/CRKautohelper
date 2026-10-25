'use strict';
const crypto=require('node:crypto'),{validateFrame,boxValid}=require('./node-selector.cjs');
const {isDeepStrictEqual}=require('node:util');
function aspectGeometry(m,p,f){
 const e=m?.aspectRectification,marked=m?.nodes?.some(n=>n.analysisBox||n.analysisCenter);
 if(e==null)return !marked;
 const hash=v=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);
 const nums=(v,n)=>Array.isArray(v)&&v.length===n&&v.every(Number.isFinite);
 const near=(a,b,t=1e-9)=>Number.isFinite(a)&&Math.abs(a-b)<=t;
 const size=e.rectifiedInputSize,c=e.calibration;
 if(e.verified!==true||e.actionsExecuted!==false||e.method!=='same_frame_circle_aspect_map_rectification'||
    e.sourceImageSha256!==p.binding.imageSha256||e.pixelSha256!==p.binding.pixelSha256||
    e.sourceCaptureFrameId!==f.id||!isDeepStrictEqual(e.sourceSize,[f.width,f.height])||
    !hash(e.rectifiedImageSha256)||!hash(e.rectifiedPixelSha256)||!nums(size,2)||
    !size.every(v=>Number.isInteger(v)&&v>0)||size[1]!==f.height||
    c?.method!=='original_pixel_orange_circle_unique_aspect_consensus'||c.actionsExecuted!==false||
    c.pixelSha256!==p.binding.pixelSha256||!isDeepStrictEqual(c.sourceSize,e.sourceSize)||
    !Number.isFinite(c.ratio)||c.ratio<.55||c.ratio>2.5||Math.abs(c.ratio-1)<=.08)return false;
 const inverse=f.width/size[0],matrix=(value,expected)=>Array.isArray(value)&&value.length===3&&
  value.every((row,i)=>nums(row,3)&&row.every((v,j)=>near(v,expected[i][j])));
 if(Math.abs(inverse/c.ratio-1)>1/size[0]||
    !matrix(e.forwardMatrix,[[1/inverse,0,0],[0,1,0],[0,0,1]])||
    !matrix(e.inverseMatrix,[[inverse,0,0],[0,1,0],[0,0,1]])||
    !nums(c.analysisSize,2)||c.analysisSize[0]!==960||!Number.isInteger(c.analysisSize[1])||
    Math.abs(c.analysisSize[1]-f.height*960/f.width)>.500001||
    !near(c.analysisScaleX,960/f.width)||!near(c.analysisScaleY,c.analysisSize[1]/f.height)||
    !nums(e.modelAnalysisSize,2)||e.modelAnalysisSize[0]!==960||
    Math.abs(e.modelAnalysisSize[1]-f.height*960/size[0])>.500001)return false;
 if(!Array.isArray(c.candidates)||!Array.isArray(c.consensus)||c.consensus.length<3||
    new Set(c.consensus).size!==c.consensus.length||
    c.consensus.some(i=>!Number.isInteger(i)||i<0||i>=c.candidates.length))return false;
 const chosen=c.consensus.map(i=>c.candidates[i]);
 for(const q of chosen){
  if(!boxValid(q.box,f)||!nums(q.center,2)||!Number.isFinite(q.ratio)||
     Math.abs(q.ratio/c.ratio-1)>.04||!Number.isFinite(q.solidity)||q.solidity<=.9||q.solidity>1||
     !Number.isFinite(q.ellipseFill)||q.ellipseFill<=.9||q.ellipseFill>=1.1||
     !Number.isFinite(q.angleDegrees))return false;
 }
 const median=values=>{const a=[...values].sort((a,b)=>a-b),i=Math.floor(a.length/2);return a.length%2?a[i]:(a[i-1]+a[i])/2;};
 if(!near(median(chosen.map(q=>q.ratio)),c.ratio))return false;
 for(let i=0;i<chosen.length;i++)for(let j=0;j<i;j++){
  if(Math.hypot(...chosen[i].center.map((v,k)=>v-chosen[j].center[k]))<
     Math.min(...chosen[i].box.slice(2),...chosen[j].box.slice(2))*.5)return false;
 }
 const xs=chosen.map(q=>q.center[0]),ys=chosen.map(q=>q.center[1]);
 if(Math.max(...xs)-Math.min(...xs)<median(chosen.map(q=>q.box[2]))*1.5||
    Math.max(...ys)-Math.min(...ys)<median(chosen.map(q=>q.box[3]))*1.5)return false;
 const cols=e.rectifiedColumns;
 if(!nums(cols,4)||cols.some((x,i)=>x<0||x>=size[0]||i&&x<=cols[i-1])||
    !nums(m.columns,4)||m.columns.some((x,i)=>!near(x,cols[i]*inverse,.011))||
    !Array.isArray(m.nodes)||m.nodes.length<4)return false;
 const normalized={width:size[0],height:size[1]};
 for(const n of m.nodes){
  if(!boxValid(n.analysisBox,normalized)||!nums(n.analysisCenter,2)||!nums(n.box,4)||!nums(n.center,2))return false;
  const expected=n.analysisBox.map((v,i)=>i===0||i===2?v*inverse:v);
  if(n.box.some((v,i)=>!near(v,expected[i],.011))||
     !near(n.center[0],n.analysisCenter[0]*inverse,.011)||!near(n.center[1],n.analysisCenter[1],.011))return false;
  const r=n.centerRefinement;
  if(r!=null){
   if(r.method!=='same_frame_unique_enclosed_orange_circle_center'||r.actionsExecuted!==false||
      !c.consensus.includes(r.candidateIndex)||!boxValid(r.originalAnalysisBox,normalized)||
      !nums(r.originalAnalysisCenter,2)||n.type!=='battle'||n.completed!==false)return false;
   const q=c.candidates[r.candidateIndex],old=r.originalAnalysisBox;
   if(!near(n.center[0],q.center[0],.011)||!near(n.center[1],q.center[1],.011)||
      !near(n.analysisBox[2],old[2],.011)||!near(n.analysisBox[3],old[3],.011)||
      !near(n.analysisBox[0]+n.analysisBox[2]/2,n.analysisCenter[0],.011)||
      !near(n.analysisBox[1]+n.analysisBox[3]/2,n.analysisCenter[1],.011)||
      q.box[0]/inverse<old[0]||q.box[0]/inverse+q.box[2]/inverse>old[0]+old[2]||
      q.box[1]<old[1]||q.box[1]+q.box[3]>old[1]+old[3]||
      Math.hypot(n.analysisCenter[0]-r.originalAnalysisCenter[0],n.analysisCenter[1]-r.originalAnalysisCenter[1])>Math.min(...old.slice(2))*.05+.011)return false;
  }
  const proposal=n.pixelProposal;
  if(n.scoreMethod==='original_source_inner_template_rgb'&&proposal==null)return false;
  if(proposal!=null){
   const geometry=proposal.geometryEvidence,fx=960/size[0],fy=e.modelAnalysisSize[1]/size[1];
   if(proposal.method!=='same_frame_original_orange_inner_candidate'||proposal.actionsExecuted!==false||
      proposal.sourceImageSha256!==p.binding.imageSha256||proposal.pixelSha256!==p.binding.pixelSha256||
      proposal.sourceCaptureFrameId!==f.id||!isDeepStrictEqual(proposal.sourceSize,e.sourceSize)||
      !isDeepStrictEqual(proposal.rectifiedInputSize,size)||proposal.rectifiedPixelSha256!==e.rectifiedPixelSha256||
      !isDeepStrictEqual(proposal.analysisSize,e.modelAnalysisSize)||!hash(proposal.analysisPixelSha256)||
      n.scoreMethod!=='original_source_inner_template_rgb'||n.template!=='node-orange.png'||
      !geometry||!near(n.score,geometry.innerScore)||!nums(proposal.injectedAnalysisBox,4)||
      !boxValid(geometry.originalAnalysisBox,normalized)||
      proposal.injectedAnalysisBox.some((v,i)=>!near(v,geometry.originalAnalysisBox[i]*(i%2===0?fx:fy),.011)))return false;
  }
  for(const o of [n.orangeRefinement,proposal?.geometryEvidence].filter(v=>v!=null)){
   const ref=o.templateSize,old=o.originalAnalysisBox;
   if(n.type!=='battle'||n.completed!==false||o.method!=='same_frame_orange_ellipse_and_original_template_extent'||
      o.actionsExecuted!==false||o.pixelSha256!==p.binding.pixelSha256||!c.consensus.includes(o.candidateIndex)||
      !hash(o.templateImageSha256)||!nums(ref,2)||!ref.every(v=>Number.isInteger(v)&&v>0)||
      !boxValid(o.sourceInnerBox,f)||!boxValid(o.actualCropBox,f)||!nums(o.ellipseCenter,2)||
      !boxValid(o.templateInnerBox,{width:ref[0],height:ref[1]})||
      !boxValid(old,normalized)||!nums(o.originalAnalysisCenter,2)||
      !Number.isFinite(o.innerScore)||o.innerScore<.9||o.innerScore>1)return false;
   const [x,y,w,h]=o.sourceInnerBox,[rx,ry,rw,rh]=o.templateInnerBox,sx=w/rw,sy=h/rh;
   const measured=[x-rx*sx,y-ry*sy,ref[0]*sx,ref[1]*sy],q=c.candidates[o.candidateIndex];
   const core=o.iconCoreEvidence;
   if((core!=null)!==(o.circleInnerScore!=null))return false;
   if(core!=null){
    const radius=Math.max(1,Math.round(Math.min(...measured.slice(2))*.02));
    if(o!==proposal?.geometryEvidence||core.method!=='original_outer58_inner12_46_rgb_bounded_alignment'||
       !near(core.score,o.innerScore)||core.template!=='node-orange'||
       !Number.isFinite(core.runnerUpScore)||core.runnerUpScore<0||core.score-core.runnerUpScore<.08||
       typeof core.runnerUpTemplate!=='string'||core.runnerUpTemplate==='node-orange'||
       !nums(core.alignmentPx,2)||core.alignmentPx.some(v=>!Number.isInteger(v)||Math.abs(v)>radius)||
       core.alignmentRadius!==radius||!isDeepStrictEqual(core.analysisSize,[58,58])||
       !isDeepStrictEqual(core.innerBox,[12,12,34,34])||!boxValid(core.sourceCropBox,f)||
       !Number.isFinite(o.circleInnerScore)||o.circleInnerScore<0||o.circleInnerScore>=.9||
       core.sourceCropBox.some((v,i)=>!near(v,measured[i]+(i<2?core.alignmentPx[i]:0),.011)))return false;
   }
   const crop=o.actualCropBox;
   if(n.box.some((v,i)=>!near(v,measured[i],.011))||
      !near(o.ellipseCenter[0],x+w/2,.011)||!near(o.ellipseCenter[1],y+h/2,.011)||
      Math.hypot(o.ellipseCenter[0]-q.center[0],o.ellipseCenter[1]-q.center[1])>Math.min(old[2]*inverse,old[3])*.05+.011||
      Math.abs(crop[0]-x)>.50001||Math.abs(crop[1]-y)>.50001||
      Math.abs(crop[0]+crop[2]-x-w)>.50001||Math.abs(crop[1]+crop[3]-y-h)>.50001||
      n.analysisBox[2]<old[2]*.85-.011||n.analysisBox[2]>old[2]*1.15+.011||
      n.analysisBox[3]<old[3]*.85-.011||n.analysisBox[3]>old[3]*1.15+.011)return false;
  }
  const g=n.gateRefinement;
  if(g!=null){
   const ref=g.templateSize;
   if(n.type!=='exit'||g.method!=='same_frame_cyan_gate_arrow_and_original_template_extent'||
      g.actionsExecuted!==false||g.pixelSha256!==p.binding.pixelSha256||
      !hash(g.templateImageSha256)||!nums(ref,2)||!ref.every(v=>Number.isInteger(v)&&v>0)||
      !boxValid(g.sourceInnerBox,f)||!boxValid(g.templateInnerBox,{width:ref[0],height:ref[1]})||
      !boxValid(g.originalAnalysisBox,normalized)||!nums(g.originalAnalysisCenter,2)||
      !Number.isFinite(g.innerScore)||g.innerScore<.9||g.innerScore>1)return false;
   const [x,y,w,h]=g.sourceInnerBox,[rx,ry,rw,rh]=g.templateInnerBox,sx=w/rw,sy=h/rh;
   const actual=[x-rx*sx,y-ry*sy,ref[0]*sx,ref[1]*sy],old=g.originalAnalysisBox;
   if(n.box.some((v,i)=>!near(v,actual[i],.011))||
      n.analysisBox[2]<old[2]*.85-.011||n.analysisBox[2]>old[2]*1.15+.011||
      n.analysisBox[3]<old[3]*.85-.011||n.analysisBox[3]>old[3]*1.15+.011)return false;
  }
 }
 if(m.absoluteFloorKnown===true&&m.floorAnchorSource==='visible_top_gate'&&
    e.rectifiedFloorAnchorSource!=='visible_top_gate')return false;
 return true;
}
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
 const labels=(p.evidence||[]).filter(r=>['進行中','inprogress'].includes(r.text?.replace(/\s/g,'').toLowerCase())&&range(r.score,.95,1));
 if(labels.length!==1||labels[0].score!==c.labelScore||!Array.isArray(labels[0].box)||labels[0].box.length!==4||labels[0].box.some(q=>!Array.isArray(q)||q.length!==2||!q.every(Number.isFinite)))return null;
 const points=labels[0].box,xs=points.map(q=>q[0]),ys=points.map(q=>q[1]);
 const label=[Math.min(...xs),Math.min(...ys),Math.max(...xs)-Math.min(...xs),Math.max(...ys)-Math.min(...ys)];
 if(JSON.stringify(label)!==JSON.stringify(c.labelBox))return null;
 const [x,y,w,h]=n.box,[lx,ly,lw]=label,[tx,ty,tw,th]=t.box;
 if(Math.abs(lx+lw/2-x-w/2)>w*.45||!range(ly-y-h,-h*.35,h*.35)||!range(tw,w*.15,w*.45)||!range(th,h*.1,h*.3)||Math.abs(tx+tw/2-x-w/2)>w*.15||ty<y-h*.4||ty+th>y)return null;
 return {nodeId:n.id,verified:true,inProgress:true};
}
function bind(frame,p){validateFrame(frame,frame.atMs);const raw=frame.png,b=p?.binding;if(!Buffer.isBuffer(raw)||raw.length<33||raw.subarray(0,8).toString('hex')!=='89504e470d0a1a0a'||crypto.createHash('sha256').update(raw).digest('hex')!==frame.sha256||raw.readUInt32BE(16)!==frame.width||raw.readUInt32BE(20)!==frame.height||b?.frameId!==frame.id||b.imageSha256!==frame.sha256||b.width!==frame.width||b.height!==frame.height||!/^[a-f0-9]{64}$/.test(b.pixelSha256||'')||p.flow?.frameId!==b.pixelSha256.slice(0,20)||p.actionsExecuted!==false)throw Error('OBSERVATION_BINDING_INVALID');const {png,...f}=frame;return structuredClone(f);}
function adaptMap(frame,p){const f=bind(frame,p),m=p.mapReview;if(p.flow.state!=='MAP'||m?.frameId!==p.binding.pixelSha256.slice(0,20)||!Array.isArray(m.nodes)||!Array.isArray(m.edges))throw Error('MAP_EVIDENCE_INVALID');
 if(!aspectGeometry(m,p,f))return {frame:f,state:'MAP',stateVerified:false,verified:false,zone:null,anchorVerified:false,nodes:[],edges:[],current:null,reason:'ASPECT_RECTIFICATION_UNBOUND'};
 const anchored=m.absoluteFloorKnown===true&&m.floorAnchorSource==='visible_top_gate'&&m.nodes.filter(n=>n.type==='exit').length===1;
 const nodes=m.nodes.map(n=>{if(!boxValid(n.box,f)||!Number.isFinite(n.score)||n.score<0||n.score>1)throw Error('COORDINATE_INVALID');return {id:n.id,type:n.type,floor:n.type==='exit'&&anchored?0:n.floor,column:n.column??null,box:[...n.box],score:n.score,completed:n.completed===true};});
 const completedCurrent=mapActions(p,m,nodes);
 const c=m.currentPosition;const current=c?.verified===true&&c.method==='reviewed_current_node_pixels_and_unique_progress_label'&&Number.isFinite(c.correlation)&&c.correlation>=.985&&c.correlation<=1&&Number.isFinite(c.appearanceMAE)&&c.appearanceMAE>=0&&c.appearanceMAE<=.055&&nodes.some(n=>n.id===c.nodeId)?{nodeId:c.nodeId,verified:true,inProgress:true}:completedCurrent;
 const progress=p.progress,zoneVerified=Number.isInteger(progress?.displayedZone)&&progress.displayedZone>=1&&progress.displayedZone<=10&&Number.isFinite(progress.score)&&progress.score>=.9&&progress.score<=1&&progress.conflictingEvidence===false;
 const latticeVerified=anchored&&m.columns?.length===4&&m.columns.every(Number.isFinite)&&new Set(m.columns).size===4&&nodes.length>=6&&new Set(nodes.filter(n=>n.type!=='exit').map(n=>n.floor)).size>=2&&m.edges.filter(e=>Number.isFinite(e.pixel_support)&&e.pixel_support>=.85&&e.pixel_support<=1).length>=3;
 return {frame:f,state:'MAP',stateVerified:p.flow.confidence>=.75&&nodes.length>=4||latticeVerified,verified:zoneVerified&&(p.flow.confidence>=.88||p.flow.confidence>=.85&&latticeVerified),zone:progress?.displayedZone??null,anchorVerified:anchored,nodes,edges:m.edges.map(e=>({from:e.from,to:e.to,pixelSupport:e.pixel_support})),current};
}
function adaptPreview(frame,p){const f=bind(frame,p),v=p.v2Preview;
 if(!aspectGeometry(v?.recoveredMapReview||p.mapReview,p,f))return {frame:f,state:'UNKNOWN',verified:false,reason:'ASPECT_RECTIFICATION_UNBOUND'};
 if(v?.verified===true&&v.method==='unique_uncompleted_battle_green_outline_and_ordinary_timer_enter'&&v.pixelSha256===p.binding.pixelSha256&&v.actionsExecuted===false&&v.controlsVerified===true&&boxValid(v.enterBox,f)&&v.selectedNode?.verified===true&&boxValid(v.selectedNode.box,f)){
  const n=v.selectedNode,m=v.recoveredMapReview||p.mapReview,zone=p.progress;
  const recovered=(v.recoveredNodes||[]).filter(x=>{
   const cols=m?.columns,gate=m?.nodes?.filter(g=>g.type==='exit');
   if(!Array.isArray(cols)||cols.length!==4||!cols.every(Number.isFinite)||gate?.length!==1||x.recovered!==true||!Number.isFinite(x.iconScore)||x.iconScore<.9||!boxValid(x.box,f)||!Number.isInteger(x.floor)||!Number.isInteger(x.column)||x.column<1||x.column>4)return false;
   const size=x.iconSizeEvidence;
   if(size!=null){
    const calibration=m.aspectRectification?.calibration,index=size.candidateIndex,ref=size.templateSize;
    if(size.method!=='same_frame_orange_circle_and_original_template_extent'||size.actionsExecuted!==false||
       size.pixelSha256!==p.binding.pixelSha256||!Number.isInteger(index)||!calibration?.consensus?.includes(index)||
       !Array.isArray(ref)||ref.length!==2||!ref.every(v=>Number.isInteger(v)&&v>0)||
       !boxValid(size.circleBox,{width:ref[0],height:ref[1]})||!/^[a-f0-9]{64}$/.test(size.templateImageSha256||''))return false;
    const circle=calibration.candidates[index];
    if(!isDeepStrictEqual(circle.box,size.sourceCircleBox)||
       Math.abs(x.box[2]-circle.box[2]/size.circleBox[2]*ref[0])>.011||
       Math.abs(x.box[3]-circle.box[3]/size.circleBox[3]*ref[1])>.011)return false;
   }
   const spacing=(cols[3]-cols[0])/3,cx=x.box[0]+x.box[2]/2,cy=x.box[1]+x.box[3]/2,gy=gate[0].box[1]+gate[0].box[3]/2;
   // aspectGeometry has already bound this rectification to the current PNG.
   const verticalSpacing=m.aspectRectification?spacing*m.aspectRectification.rectifiedInputSize[0]/f.width:spacing;
   return Math.abs(cx-cols[x.column-1])<=spacing*.08&&Math.abs(cy-gy-x.floor*verticalSpacing)<=verticalSpacing*.08;
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
