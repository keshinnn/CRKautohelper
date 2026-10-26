'use strict';
const crypto=require('node:crypto'),{validateFrame,boxValid}=require('./node-selector.cjs');
const {isDeepStrictEqual}=require('node:util');
// Certificates are process-local capabilities; serialized audit fields grant no authority.
const directMapAnchors=new WeakMap();
function markDirectMapAnchor(o,m,p,f){
 const nodes=m?.nodes,edges=m?.edges,progress=p.progress;
 const strong=o.verified===true&&m?.absoluteFloorKnown===true&&m.floorAnchorSource==='visible_top_gate'&&
  Array.isArray(nodes)&&nodes.length>=6&&nodes.filter(n=>n.type==='exit').length===1&&new Set(nodes.map(n=>n.id)).size===nodes.length&&
  m.columns?.length===4&&m.columns.every(Number.isFinite)&&new Set(m.columns).size===4&&
  new Set(nodes.filter(n=>n.type!=='exit'&&Number.isInteger(n.floor)).map(n=>n.floor)).size>=2&&
  edges?.filter(e=>Number.isFinite(e.pixel_support)&&e.pixel_support>=.85&&e.pixel_support<=1).length>=3&&
  Number.isInteger(progress?.displayedZone)&&progress.displayedZone>=1&&progress.displayedZone<=10&&
  Number.isFinite(progress.score)&&progress.score>=.9&&progress.score<=1&&progress.conflictingEvidence===false&&o.zone===progress.displayedZone&&
  (o.state==='MAP'&&o.stateVerified===true&&o.anchorVerified===true||o.state==='PREVIEW'&&o.controlsVerified===true&&!o.registrationSource);
 if(!strong)return o;
 const certificate={frame:structuredClone(f),zone:o.zone,pixelSha256:p.binding.pixelSha256,method:'direct_visible_gate_map_lattice'};
 o.mapAnchorAuthority={...structuredClone(certificate),verified:true,actionsExecuted:false};
 directMapAnchors.set(o,{certificate,snapshot:structuredClone(o)});
 return o;
}
function readDirectMapAnchor(o){
 const stored=directMapAnchors.get(o);
 return stored&&isDeepStrictEqual(stored.snapshot,o)?structuredClone(stored.certificate):null;
}
function completedGeometry(n,m,p,f,e,size,inverse,normalized){
 const hash=v=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);
 const nums=(v,n)=>Array.isArray(v)&&v.length===n&&v.every(Number.isFinite);
 const near=(a,b,t=1e-9)=>Number.isFinite(a)&&Math.abs(a-b)<=t;
 const refinement=n.completedRefinement;
 if(n.geometryMethod==='original_source_done_template_extent'&&refinement==null)return false;
 if(refinement!=null&&n.checkProposal!=null)return false;
 if((n.checkProposal!=null||refinement!=null)&&!boxValid(n.box,f))return false;
  const check=n.checkProposal||refinement;
  if(n.scoreMethod==='original_source_done_template_rgb'&&check==null)return false;
  if(check!=null){
   const ref=check.templateSize,peer=m.nodes.find(q=>q.id===check.peerNodeId),box=check.sourceBox;
   // A completed crop keeps the peer size actually measured by its producer.
   // Later verified orange refinement must not rewrite that source measurement.
   const oldPeer=peer?.orangeRefinement,oldBox=oldPeer?.originalAnalysisBox;
   const currentPeer=peer&&boxValid(check.peerSourceBox,f)&&peer.box.every((v,i)=>near(v,check.peerSourceBox[i],.011));
   const measuredPeer=peer?.type==='battle'&&peer.completed===false&&
    oldPeer?.method==='same_frame_orange_ellipse_and_original_template_extent'&&oldPeer.actionsExecuted===false&&
    oldPeer.pixelSha256===p.binding.pixelSha256&&e.calibration?.consensus?.includes(oldPeer.candidateIndex)&&
    boxValid(oldBox,normalized)&&boxValid(check.peerSourceBox,f)&&oldBox.every((v,i)=>near(v*(i%2===0?inverse:1),check.peerSourceBox[i],.011));
   if(refinement!=null){
    const old=check.previousSourceBox,center=check.previousSourceCenter;
    if(n.geometryMethod!=='original_source_done_template_extent'||n.scoreMethod!=null||n.orangeRefinement||n.centerRefinement||n.gateRefinement||n.pixelProposal||n.gateProposal||
       check.originalNodeId!==n.id||check.originalModelCompleted!==true||check.originalModelType!==n.type||
       !Number.isFinite(check.originalModelScore)||check.originalModelScore<.48||check.originalModelScore>1||!near(n.score,check.originalModelScore)||
       typeof check.originalModelTemplate!=='string'||n.template!==check.originalModelTemplate||
       !boxValid(old,f)||!nums(center,2)||!boxValid(check.previousAnalysisBox,normalized)||!nums(check.previousAnalysisCenter,2)||
       !Number.isFinite(check.previousCheckMaskIoU)||check.previousCheckMaskIoU<0||check.previousCheckMaskIoU>=.8||!boxValid(box,f)||
       box[2]<old[2]*.85||box[2]>old[2]*1.15||box[3]<old[3]*.85||box[3]>old[3]*1.15||
       Math.hypot(box[0]+box[2]/2-center[0],box[1]+box[3]/2-center[1])>Math.min(...old.slice(2))*.05||
       !near(center[0],old[0]+old[2]/2,.011)||!near(center[1],old[1]+old[3]/2,.011)||
       check.previousAnalysisBox.some((v,i)=>!near(v,old[i]/(i%2===0?inverse:1),.011))||
       check.previousAnalysisCenter.some((v,i)=>!near(v,center[i]/(i===0?inverse:1),.011)))return false;
   }else if(n.scoreMethod!=='original_source_done_template_rgb'||n.template!==check.matchedTemplate+'.png'||!near(n.score,check.iconScore))return false;
   if(check.method!=='same_frame_green_check_original_done_rgb_candidate'||check.actionsExecuted!==false||
      check.sourceImageSha256!==p.binding.imageSha256||check.pixelSha256!==p.binding.pixelSha256||check.sourceCaptureFrameId!==f.id||
      !isDeepStrictEqual(check.sourceSize,e.sourceSize)||!isDeepStrictEqual(check.rectifiedInputSize,size)||
      check.rectifiedPixelSha256!==e.rectifiedPixelSha256||!isDeepStrictEqual(check.analysisSize,e.modelAnalysisSize)||!hash(check.analysisPixelSha256)||
      n.type==='exit'||n.type==='boss'||n.completed!==true||
      !['node-done','node-b-done'].includes(check.matchedTemplate)||
      !Number.isFinite(check.iconScore)||check.iconScore<.9||check.iconScore>1||
      !Number.isFinite(check.otherFamilyScore)||check.otherFamilyScore< -1||check.iconScore-check.otherFamilyScore<.08||
      typeof check.otherFamilyTemplate!=='string'||['node-done','node-b-done'].includes(check.otherFamilyTemplate)||
      !['node-done.png','node-b-done.png'].includes(check.templateFile)||!hash(check.templateImageSha256)||
      !isDeepStrictEqual(ref,[58,58])||!nums(check.originalTemplateSize,2)||!check.originalTemplateSize.every(v=>Number.isInteger(v)&&v>0)||
      !boxValid(check.sourceCheckBox,f)||!boxValid(check.templateCheckBox,{width:58,height:58})||!boxValid(box,f)||
      !boxValid(check.originalAnalysisBox,normalized)||!nums(check.originalAnalysisCenter,2)||!nums(check.injectedAnalysisBox,4)||
      !peer||peer.id===n.id||peer.type==='exit'||peer.type==='boss'||peer.score<.48||!boxValid(check.peerSourceBox,f)||
      !(currentPeer||measuredPeer)||!nums(check.peerMedianSize,2)||check.peerMedianSize.some(v=>v<=0)||
      !nums(check.alignmentPx,2)||!Number.isFinite(check.greenCoverage)||check.greenCoverage<=.04||check.greenCoverage>=.30||
      !Number.isFinite(check.checkMaskIoU)||check.checkMaskIoU<.8||check.checkMaskIoU>1||
      !Number.isFinite(check.originalCheckMaskIoU)||check.originalCheckMaskIoU<0||check.originalCheckMaskIoU>1)return false;
   const [x,y,w,h]=check.sourceCheckBox,[rx,ry,rw,rh]=check.templateCheckBox,[pw,ph]=check.peerSourceBox.slice(2),radius=Math.max(1,Math.round(Math.min(pw,ph)*.02));
   if(!Number.isInteger(check.sourceCheckArea)||check.sourceCheckArea<5||check.sourceCheckArea>w*h||
      !Number.isInteger(check.templateCheckArea)||check.templateCheckArea<5||check.templateCheckArea>rw*rh||
      rx+rw/2<=58*.15||rx+rw/2>=58*.85||ry+rh/2<=58*.15||ry+rh/2>=58*.85||
      check.alignmentRadius!==radius||check.alignmentPx.some(v=>!Number.isInteger(v)||Math.abs(v)>radius)||
      pw<check.peerMedianSize[0]*.9||pw>check.peerMedianSize[0]*1.1||ph<check.peerMedianSize[1]*.9||ph>check.peerMedianSize[1]*1.1||
      58*w/rw<check.peerMedianSize[0]*.85||58*w/rw>check.peerMedianSize[0]*1.15||
      58*h/rh<check.peerMedianSize[1]*.85||58*h/rh>check.peerMedianSize[1]*1.15)return false;
   const expected=[x+w/2-(rx+rw/2)*pw/58+check.alignmentPx[0],y+h/2-(ry+rh/2)*ph/58+check.alignmentPx[1],pw,ph];
   if(box.some((v,i)=>!near(v,expected[i],.011))||n.box.some((v,i)=>!near(v,box[i],.011))||
      check.originalAnalysisBox.some((v,i)=>!near(v,box[i]/(i%2===0?inverse:1),.011))||
      !near(check.originalAnalysisCenter[0],(box[0]+box[2]/2)/inverse,.011)||!near(check.originalAnalysisCenter[1],box[1]+box[3]/2,.011)||
      check.injectedAnalysisBox.some((v,i)=>!near(v,check.originalAnalysisBox[i]*(i%2===0?960/size[0]:e.modelAnalysisSize[1]/size[1]),.011)))return false;
   const overlay=check.neutralOverlayCheck;
   if(check.originalCheckMaskIoU>=.8){if(overlay!=null||!near(check.checkMaskIoU,check.originalCheckMaskIoU))return false;}
   else if(overlay?.method!=='same_check_shape_at_two_neutral_overlay_color_levels'||overlay.minimumTemplateIoU!==.8||
      !near(overlay.score,check.checkMaskIoU)||!nums(overlay.maskIoUs,2)||overlay.maskIoUs.some(v=>v<.8||v>1)||
      !nums(overlay.saturationLevels,2)||new Set(overlay.saturationLevels).size!==2||overlay.saturationLevels.some(v=>![60,80,100,120].includes(v)))return false;
  }
 return true;
}
function referenceLines(m,p,f,e,size){
 const nums=(v,n)=>Array.isArray(v)&&v.length===n&&v.every(Number.isFinite),near=(a,b,t=.011)=>Number.isFinite(a)&&Math.abs(a-b)<=t;
 const hash=v=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);
 for(const edge of m?.edges||[]){
  const r=edge.lineReference;
  if(edge.lineScoreMethod==='reference_node58_original_kernel'&&r==null)return false;
  if(r==null)continue;
  const [aw,ah]=e.modelAnalysisSize,analysis={width:aw,height:ah};
  if(edge.lineScoreMethod!=='reference_node58_original_kernel'||r.method!=='original_line_kernel_at_node58_reference'||r.actionsExecuted!==false||r.referenceNodeSize!==58||
     r.sourceImageSha256!==p.binding.imageSha256||r.pixelSha256!==p.binding.pixelSha256||r.sourceCaptureFrameId!==f.id||
     !isDeepStrictEqual(r.sourceSize,[f.width,f.height])||!isDeepStrictEqual(r.rectifiedInputSize,size)||r.rectifiedPixelSha256!==e.rectifiedPixelSha256||
     !isDeepStrictEqual(r.analysisSize,e.modelAnalysisSize)||!hash(r.analysisPixelSha256)||!hash(r.referencePixelSha256)||
     r.nodeGeometryStage!=null&&r.nodeGeometryStage!=='final_verified_boxes'||
     r.nodeGeometryStage==='final_verified_boxes'&&![edge.from,edge.to].some(id=>m.nodes.find(n=>n.id===id)?.completedRefinement)||
     !isDeepStrictEqual(r.sourceNodeIds,[edge.from,edge.to])||!Array.isArray(r.sourceNodeBoxes)||r.sourceNodeBoxes.length!==2||
     !Array.isArray(r.sourceNodeCenters)||r.sourceNodeCenters.length!==2||!Array.isArray(r.referenceNodeBoxes)||r.referenceNodeBoxes.length!==2||
     !Array.isArray(r.referenceNodeCenters)||r.referenceNodeCenters.length!==2||!nums(r.referenceSize,2)||!r.referenceSize.every(v=>Number.isInteger(v)&&v>0)||
     !Number.isFinite(r.originalSupport)||r.originalSupport<.5||r.originalSupport>=.85||!Number.isFinite(r.pixelSupport)||r.pixelSupport<.85||r.pixelSupport>1||!near(r.pixelSupport,edge.pixel_support,1e-9))return false;
  if(r.sourceNodeBoxes.some(b=>!boxValid(b,analysis)))return false;
  const median=r.sourceNodeBoxes.reduce((sum,b)=>sum+Math.min(...b.slice(2)),0)/2,factor=58/median;
  if(median<=58||!near(r.medianNodeShortSide,median,1e-9)||r.referenceSize[0]!==Math.round(aw*factor)||r.referenceSize[1]!==Math.round(ah*factor))return false;
  for(let i=0;i<2;i++){
   const n=m.nodes.find(n=>n.id===r.sourceNodeIds[i]);if(!n)return false;
   const before=r.nodeGeometryStage==='final_verified_boxes'?null:n.orangeRefinement||n.gateRefinement||n.centerRefinement;
   const box=before?.originalAnalysisBox||n.analysisBox||n.box,center=before?.originalAnalysisCenter||n.analysisCenter||n.center;
   if(!nums(box,4)||!nums(center,2)||!nums(r.sourceNodeCenters[i],2)||!nums(r.referenceNodeBoxes[i],4)||!nums(r.referenceNodeCenters[i],2)||
      r.sourceNodeBoxes[i].some((v,k)=>!near(v,box[k]*(k%2===0?aw/size[0]:ah/size[1])))||
      r.sourceNodeCenters[i].some((v,k)=>!near(v,center[k]*(k===0?aw/size[0]:ah/size[1])))||
      r.referenceNodeBoxes[i].some((v,k)=>!near(v,r.sourceNodeBoxes[i][k]*r.referenceSize[k%2]/r.analysisSize[k%2],1e-9))||
      r.referenceNodeCenters[i].some((v,k)=>!near(v,r.sourceNodeCenters[i][k]*r.referenceSize[k]/r.analysisSize[k],1e-9)))return false;
  }
 }
 return true;
}
function healGeometry(n,m,p,f,e,size,inverse){
 const h=n.healProposal;
 if(h==null)return n.scoreMethod!=='original_source_heal_template_rgb';
 const near=(a,b)=>Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=.011;
 const nums=(v,k)=>Array.isArray(v)&&v.length===k&&v.every(Number.isFinite);
 const hash=v=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);
 if(h.method!=='same_frame_green_component_original_heal_rgb_candidate'||h.actionsExecuted!==false||
    n.type!=='heal'||n.completed!==false||n.scoreMethod!=='original_source_heal_template_rgb'||
    h.sourceImageSha256!==f.sha256||h.pixelSha256!==p.binding.pixelSha256||h.sourceCaptureFrameId!==f.id||
    !isDeepStrictEqual(h.sourceSize,[f.width,f.height])||!isDeepStrictEqual(h.rectifiedInputSize,size)||
    h.rectifiedPixelSha256!==e.rectifiedPixelSha256||!isDeepStrictEqual(h.analysisSize,e.modelAnalysisSize)||!hash(h.analysisPixelSha256)||
    !hash(h.templateImageSha256)||!['node-heal','node-b-heal'].includes(h.matchedTemplate)||n.template!==h.matchedTemplate+'.png'||
    !Number.isFinite(h.iconScore)||h.iconScore<.9||h.iconScore>1||!near(n.score,h.iconScore)||
    !Number.isFinite(h.otherFamilyScore)||h.otherFamilyScore<0||h.iconScore-h.otherFamilyScore<.08||
    typeof h.otherFamilyTemplate!=='string'||['node-heal','node-b-heal'].includes(h.otherFamilyTemplate)||
    !isDeepStrictEqual(h.analysisSizeForIcon,[58,58])||!isDeepStrictEqual(h.innerBox,[12,12,34,34])||
    !boxValid(h.sourceBox,f)||!boxValid(h.greenBox,f)||h.greenBox.some(v=>!Number.isInteger(v))||
    !Number.isInteger(h.greenArea)||h.greenArea<=h.greenBox[2]*h.greenBox[3]*.35||h.greenArea>h.greenBox[2]*h.greenBox[3]||
    !nums(h.peerMedianSize,2)||!nums(h.alignmentPx,2)||h.alignmentPx.some(v=>!Number.isInteger(v))||
    !Array.isArray(h.peerSourceBoxes)||h.peerSourceBoxes.length<4)return false;
 const peers=h.peerSourceBoxes;
 if(new Set(peers.map(b=>JSON.stringify(b))).size!==peers.length||peers.some(b=>!boxValid(b,f)||!m.nodes.some(other=>{
  if(other===n||other.type==='exit'||other.type==='boss'||other.score<.48)return false;
  const boxes=[other.analysisBox,other.orangeRefinement?.originalAnalysisBox,other.centerRefinement?.originalAnalysisBox];
  return boxes.some(q=>nums(q,4)&&q.every((v,i)=>near(v*(i%2===0?inverse:1),b[i])));
 })))return false;
 const median=values=>{const a=values.sort((a,b)=>a-b),k=Math.floor(a.length/2);return a.length%2?a[k]:(a[k-1]+a[k])/2;};
 const mw=median(peers.map(b=>b[2])),mh=median(peers.map(b=>b[3])),b=h.sourceBox,g=h.greenBox;
 if(!near(mw,h.peerMedianSize[0])||!near(mh,h.peerMedianSize[1])||
    !(g[2]>.45*mw&&g[2]<.8*mw&&g[3]>.45*mh&&g[3]<.8*mh)||
    !(b[2]>=.9*mw&&b[2]<=1.1*mw&&b[3]>=.9*mh&&b[3]<=1.1*mh)||
    !peers.some(q=>near(q[2],b[2])&&near(q[3],b[3]))||
    h.alignmentRadius!==Math.max(1,Math.round(Math.min(b[2],b[3])*.02))||h.alignmentPx.some(v=>Math.abs(v)>h.alignmentRadius)||
    !near(b[0]+b[2]/2,g[0]+g[2]/2+h.alignmentPx[0])||!near(b[1]+b[3]/2,g[1]+g[3]/2+h.alignmentPx[1])||
    !nums(n.analysisBox,4)||!nums(n.analysisCenter,2)||!nums(h.originalAnalysisBox,4)||!nums(h.originalAnalysisCenter,2)||!nums(h.injectedAnalysisBox,4)||
    h.originalAnalysisBox.some((v,i)=>!near(v*(i%2===0?inverse:1),b[i]))||
    h.originalAnalysisBox.some((v,i)=>!near(v,n.analysisBox[i]))||h.originalAnalysisCenter.some((v,i)=>!near(v,n.analysisCenter[i]))||
    h.injectedAnalysisBox.some((v,i)=>!near(v,h.originalAnalysisBox[i]*e.modelAnalysisSize[i%2]/size[i%2])))return false;
 return true;
}
function previewPanelScope(m,p,f,e){
 const scope=e.candidateScope,kind=scope?.method==='same_frame_ordinary_preview_control_panel_scope';
 if(!kind)return e.previewPanelScopeRequired!==true;
 if(e.previewPanelScopeRequired!==true||scope.actionsExecuted!==false||scope.pixelSha256!==p.binding.pixelSha256||
    scope.sourceImageSha256!==f.sha256||scope.sourceCaptureFrameId!==f.id||!isDeepStrictEqual(scope.sourceSize,[f.width,f.height])||
    !isDeepStrictEqual(scope.analysisSize,e.modelAnalysisSize)||!/^[a-f0-9]{64}$/.test(scope.analysisPixelSha256||'')||
    !/^[a-f0-9]{64}$/.test(scope.greenMaskSha256||''))return false;
 const readings=[scope.enterEvidence,scope.timerEvidence,scope.ordinaryEvidence],boxes=[scope.enterBox,scope.timerBox,scope.ordinaryBox];
 for(let i=0;i<3;i++){
  const r=readings[i],points=r?.box;
  if(!r||!Number.isFinite(r.score)||r.score<(i===2?.65:.95)||r.score>1||
     !(p.evidence||[]).some(actual=>isDeepStrictEqual(actual,r))||!boxValid(boxes[i],f)||boxes[i][0]<=f.width*.5||
     !Array.isArray(points)||points.length!==4||points.some(q=>!Array.isArray(q)||q.length!==2||!q.every(Number.isFinite)))return false;
  const xs=points.map(q=>q[0]),ys=points.map(q=>q[1]);
  if(!isDeepStrictEqual(boxes[i],[Math.min(...xs),Math.min(...ys),Math.max(...xs)-Math.min(...xs),Math.max(...ys)-Math.min(...ys)]))return false;
 }
 const text=r=>r.text?.replace(/\s+/g,'').toLowerCase();
 if(!['進入','enter'].includes(text(readings[0]))||text(readings[1])!=='03:00'||!text(readings[2])?.includes('普通'))return false;
 const [enter,timer,ordinary]=boxes,button=scope.greenButtonBox;
 if(!(ordinary[1]<timer[1]&&timer[1]<enter[1]&&enter[1]-timer[1]>f.height*.15)||!boxValid(button,f)||
    button.some(v=>!Number.isInteger(v))||button[0]<=f.width*.5||scope.cutX!==button[0]||
    button[2]<=enter[2]*2||button[3]<=enter[3]*1.3||button[0]>=enter[0]||button[1]>=enter[1]||
    button[0]+button[2]<=enter[0]+enter[2]||button[1]+button[3]<=enter[1]+enter[3]||
    !Number.isInteger(scope.greenArea)||scope.greenArea<=button[2]*button[3]*.45||scope.greenArea>button[2]*button[3])return false;
 const size=e.modelAnalysisSize,cut=scope.cutX/f.width*size[0];
 if(!Array.isArray(scope.excluded)||!scope.excluded.length||scope.excluded.some(n=>
    !boxValid(n.box,{width:size[0],height:size[1]})||!Array.isArray(n.center)||n.center.length!==2||!n.center.every(Number.isFinite)||
    n.center[0]<cut||n.center[0]<n.box[0]||n.center[0]>n.box[0]+n.box[2]||n.center[1]<n.box[1]||n.center[1]>n.box[1]+n.box[3]||
    !Number.isFinite(n.score)||n.score<.48||n.score>1)||m.nodes.some(n=>n.center[0]>=scope.cutX))return false;
 return true;
}
function aspectGeometry(m,p,f){
 const e=m?.aspectRectification,marked=m?.nodes?.some(n=>n.analysisBox||n.analysisCenter);
 if(e==null){
  if(marked||m?.nodes?.some(n=>n.healProposal||n.scoreMethod==='original_source_heal_template_rgb'))return false;
  const size=[f.width,f.height],native={sourceSize:size,rectifiedPixelSha256:p.binding.pixelSha256,modelAnalysisSize:[960,Math.round(f.height*960/f.width)]};
  return (m?.nodes||[]).every(n=>completedGeometry(n,m,p,f,native,size,1,f))&&referenceLines(m,p,f,native,size);
 }
 const hash=v=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);
 const nums=(v,n)=>Array.isArray(v)&&v.length===n&&v.every(Number.isFinite);
 const near=(a,b,t=1e-9)=>Number.isFinite(a)&&Math.abs(a-b)<=t;
 const size=e.rectifiedInputSize,c=e.calibration;
 if(!previewPanelScope(m,p,f,e))return false;
 if(e.verified!==true||e.actionsExecuted!==false||e.method!=='same_frame_circle_aspect_map_rectification'||
    e.sourceImageSha256!==p.binding.imageSha256||e.pixelSha256!==p.binding.pixelSha256||
    e.sourceCaptureFrameId!==f.id||!isDeepStrictEqual(e.sourceSize,[f.width,f.height])||
    !hash(e.rectifiedImageSha256)||!hash(e.rectifiedPixelSha256)||!nums(size,2)||
    !size.every(v=>Number.isInteger(v)&&v>0)||size[1]!==f.height||
    !['original_pixel_orange_circle_unique_aspect_consensus','original_pixel_orange_and_gate_unique_aspect_consensus'].includes(c?.method)||c.actionsExecuted!==false||
    c.pixelSha256!==p.binding.pixelSha256||!isDeepStrictEqual(c.sourceSize,e.sourceSize)||
    !Number.isFinite(c.ratio)||c.ratio<.55||c.ratio>2.5||Math.abs(c.ratio-1)<=.03)return false;
 if(Math.abs(c.ratio-1)<=.08){
  const prior=p.v2OriginalMapReview,expected=prior?.absoluteFloorKnown===true?'anchored_near_native_recovery':'unanchored_near_native_recovery';
  if(typeof prior?.absoluteFloorKnown!=='boolean'||e.rectificationPurpose!==expected||
     prior.frameId!==p.binding.pixelSha256.slice(0,20))return false;
 }
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
 if(c.method==='original_pixel_orange_and_gate_unique_aspect_consensus'){
  if(chosen.filter(q=>q.circleKind==='cyan_gate').length!==1||chosen.filter(q=>q.circleKind==='orange_battle').length<2)return false;
  for(const q of chosen){
   const o=q.iconEvidence,gate=q.circleKind==='cyan_gate';
   if(!gate&&q.circleKind!=='orange_battle')return false;
   const ref=o?.templateSize;
   if(!o||o.method!==(gate?'same_frame_cyan_gate_arrow_and_original_template_extent':'same_frame_orange_ellipse_and_original_template_extent')||
      o.actionsExecuted!==false||o.pixelSha256!==p.binding.pixelSha256||!hash(o.templateImageSha256)||
      !nums(ref,2)||!ref.every(v=>Number.isInteger(v)&&v>0)||!boxValid(o.sourceInnerBox,f)||
      !boxValid(o.templateInnerBox,{width:ref[0],height:ref[1]})||!Number.isFinite(o.innerScore)||o.innerScore<.9||o.innerScore>1)return false;
   const [x,y,w,h]=o.sourceInnerBox,[rx,ry,rw,rh]=o.templateInnerBox;
   const outer=[x-rx*w/rw,y-ry*h/rh,ref[0]*w/rw,ref[1]*h/rh];
   if(!boxValid(outer,f)||Math.hypot(q.center[0]-x-w/2,q.center[1]-y-h/2)>Math.min(...outer.slice(2))*.05+.011)return false;
   if(gate){
    if(!near(q.ratio,w/h*rh/rw)||q.box.some((v,i)=>!near(v,o.sourceInnerBox[i])))return false;
   }else{
    if(Math.abs(q.ratio/(w/h)-1)>.04||!nums(o.ellipseCenter,2)||!boxValid(o.actualCropBox,f)||
       !near(o.ellipseCenter[0],x+w/2)||!near(o.ellipseCenter[1],y+h/2))return false;
    const crop=o.actualCropBox;
    if(Math.abs(crop[0]-x)>.50001||Math.abs(crop[1]-y)>.50001||Math.abs(crop[0]+crop[2]-x-w)>.50001||Math.abs(crop[1]+crop[3]-y-h)>.50001)return false;
    const core=o.iconCoreEvidence;
    if((core!=null)!==(o.circleInnerScore!=null))return false;
    if(core){
     const radius=Math.max(1,Math.round(Math.min(...outer.slice(2))*.02));
     if(core.method!=='original_outer58_inner12_46_rgb_bounded_alignment'||!near(core.score,o.innerScore)||core.template!=='node-orange'||
        !Number.isFinite(core.runnerUpScore)||core.runnerUpScore<0||core.score-core.runnerUpScore<.08||
        core.runnerUpTemplate==='node-orange'||typeof core.runnerUpTemplate!=='string'||
        !Number.isFinite(o.circleInnerScore)||o.circleInnerScore<0||o.circleInnerScore>=.9||
        !nums(core.alignmentPx,2)||core.alignmentPx.some(v=>!Number.isInteger(v)||Math.abs(v)>radius)||core.alignmentRadius!==radius||
        !isDeepStrictEqual(core.analysisSize,[58,58])||!isDeepStrictEqual(core.innerBox,[12,12,34,34])||!boxValid(core.sourceCropBox,f)||
        core.sourceCropBox.some((v,i)=>!near(v,outer[i]+(i<2?core.alignmentPx[i]:0),.011)))return false;
    }
   }
  }
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
  if(!healGeometry(n,m,p,f,e,size,inverse))return false;
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
  if(!completedGeometry(n,m,p,f,e,size,inverse,normalized))return false;
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
    if(core.method!=='original_outer58_inner12_46_rgb_bounded_alignment'||
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
  const gate=n.gateProposal;
  if(n.scoreMethod==='original_source_gate_arrow_rgb'&&gate==null)return false;
  if(gate!=null){
   const g=gate.geometryEvidence,q=c.candidates[g?.candidateIndex];
   const supplemental=g&&g.candidateIndex===c.supplementalGateCandidateIndex&&!c.consensus.includes(g.candidateIndex);
   if(gate.method!=='same_frame_original_cyan_gate_candidate'||gate.actionsExecuted!==false||
      gate.sourceImageSha256!==p.binding.imageSha256||gate.pixelSha256!==p.binding.pixelSha256||
      gate.sourceCaptureFrameId!==f.id||!isDeepStrictEqual(gate.sourceSize,e.sourceSize)||
      !isDeepStrictEqual(gate.rectifiedInputSize,size)||gate.rectifiedPixelSha256!==e.rectifiedPixelSha256||
      !isDeepStrictEqual(gate.analysisSize,e.modelAnalysisSize)||!hash(gate.analysisPixelSha256)||
      n.scoreMethod!=='original_source_gate_arrow_rgb'||n.template!=='node-exit.png'||
      !g||!near(n.score,g.innerScore)||!c.consensus.includes(g.candidateIndex)&&!supplemental||q?.circleKind!=='cyan_gate'||
      !isDeepStrictEqual(q.iconEvidence,Object.fromEntries(Object.entries(g).filter(([k])=>!['candidateIndex','originalAnalysisBox','originalAnalysisCenter'].includes(k))))||
      !nums(gate.injectedAnalysisBox,4)||!boxValid(g.originalAnalysisBox,normalized)||
      gate.injectedAnalysisBox.some((v,i)=>!near(v,g.originalAnalysisBox[i]*(i%2===0?960/size[0]:e.modelAnalysisSize[1]/size[1]),.011)))return false;
   if(supplemental){
    if(!Number.isInteger(g.candidateIndex)||!boxValid(q.box,f)||!nums(q.center,2)||!Number.isFinite(q.ratio)||Math.abs(q.ratio/c.ratio-1)>.04||
       !Number.isFinite(q.solidity)||q.solidity<=.9||q.solidity>1||!Number.isFinite(q.ellipseFill)||q.ellipseFill<=.9||q.ellipseFill>=1.1||
       !Number.isFinite(q.angleDegrees)||!nums(g.sourceInnerBox,4)||!nums(g.templateInnerBox,4)||
       q.box.some((v,i)=>!near(v,g.sourceInnerBox[i]))||!near(q.center[0],q.box[0]+q.box[2]/2)||!near(q.center[1],q.box[1]+q.box[3]/2)||
       !near(q.ratio,q.box[2]/q.box[3]*g.templateInnerBox[3]/g.templateInnerBox[2]))return false;
   }
  }
  for(const g of [n.gateRefinement,gate?.geometryEvidence].filter(v=>v!=null)){
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
 return referenceLines(m,p,f,e,size);
}
function previewAnchor(m,p,f){
 if(m?.absoluteFloorKnown!==true)return null;
 if(m.floorAnchorSource==='visible_top_gate')return {valid:true};
 if(m.floorAnchorSource!=='verified_preview_pixel_registration')return null;
 const e=m.registrationEvidence,t=p.v2TrackedMap,r=e?.registration;
 if(!e||!t||!isDeepStrictEqual(m,t.mapReview)||!isDeepStrictEqual(e,Object.fromEntries(Object.entries(t).filter(([k])=>k!=='mapReview')))||e.verified!==true||e.previewOnly!==true||e.actionsExecuted!==false||e.method!=='fresh_same_zone_direct_map_pixel_registration'||e.pixelSha256!==p.binding.pixelSha256||e.zone!==p.progress?.displayedZone||e.windowKey!==f.windowKey||e.geometryVersion!==f.geometryVersion||Math.abs(e.atMs-f.atMs)>.001||!Number.isFinite(e.sourceAtMs)||!(e.atMs-e.sourceAtMs>0&&e.atMs-e.sourceAtMs<=2500)||!/^[a-f0-9]{64}$/.test(e.sourceImageSha256||'')||!/^[a-f0-9]{64}$/.test(e.sourcePixelSha256||'')||!/^[a-f0-9]{32}$/.test(e.sourceFrameId||''))return null;
 if(r?.verified!==true||r.actionsExecuted!==false||r.method!=='map_pixel_translation_and_node_consensus'||!isDeepStrictEqual(r.pixelSha256,[e.sourcePixelSha256,p.binding.pixelSha256])||!isDeepStrictEqual(r.frameIds,[e.sourcePixelSha256.slice(0,20),p.binding.pixelSha256.slice(0,20)])||!Number.isInteger(r.rowOffset)||!Number.isInteger(r.inliers)||r.inliers<18||!Number.isInteger(r.mutualMatches)||r.mutualMatches<r.inliers||!Number.isFinite(r.scale)||r.scale<.985||r.scale>1.015||!Number.isFinite(r.angleDegrees)||Math.abs(r.angleDegrees)>.6||!Array.isArray(r.pairs)||r.pairs.length<5||new Set(r.pairs.map(x=>x.beforeNode)).size!==r.pairs.length||new Set(r.pairs.map(x=>x.afterNode)).size!==r.pairs.length||new Set(r.pairs.map(x=>x.beforeRow)).size<2)return null;
 for(const pair of r.pairs){const n=m.nodes?.find(n=>n.id===pair.afterNode);if(!n||n.floor!==n.visibleRow+r.rowOffset||pair.beforeRow-pair.afterRow!==r.rowOffset||n.visibleRow!==pair.afterRow||n.column!==pair.column)return null;}
 return {valid:true,source:{verified:true,imageSha256:e.sourceImageSha256,pixelSha256:e.sourcePixelSha256,frameId:e.sourceFrameId}};
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
 const progress=p.progress,zoneVerified=Number.isInteger(progress?.displayedZone)&&progress.displayedZone>=1&&progress.displayedZone<=10&&Number.isFinite(progress.score)&&Number.isFinite(progress.score)&&progress.score>=.9&&progress.score<=1&&progress.conflictingEvidence===false;
 const latticeVerified=anchored&&m.columns?.length===4&&m.columns.every(Number.isFinite)&&new Set(m.columns).size===4&&nodes.length>=6&&new Set(nodes.filter(n=>n.type!=='exit').map(n=>n.floor)).size>=2&&m.edges.filter(e=>Number.isFinite(e.pixel_support)&&e.pixel_support>=.85&&e.pixel_support<=1).length>=3;
 return markDirectMapAnchor({frame:f,state:'MAP',stateVerified:p.flow.confidence>=.75&&nodes.length>=4||latticeVerified,verified:zoneVerified&&(p.flow.confidence>=.88||p.flow.confidence>=.85&&latticeVerified),zone:progress?.displayedZone??null,anchorVerified:anchored,nodes,edges:m.edges.map(e=>({from:e.from,to:e.to,pixelSupport:e.pixel_support})),current},m,p,f);
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
  if(m?.frameId===p.binding.pixelSha256.slice(0,20)&&anchor?.valid===true&&match?.length===1&&zone?.displayedZone===n.zone&&zone.conflictingEvidence===false&&zone.score>=.9&&Number.isInteger(n.floor)&&Number.isInteger(n.column)&&n.ringCoverage>=.08&&n.quadrants?.length===4&&n.quadrants.every(x=>Number.isFinite(x)&&x>=.04))return markDirectMapAnchor({frame:f,state:'PREVIEW',verified:true,zone:n.zone,floor:n.floor,event:'battle',selectedNode:structuredClone(n),controlsVerified:true,identityStatus:'INDEPENDENT_PREVIEW_NODE_PIXELS',...(anchor.source?{registrationSource:anchor.source}:{})},m,p,f);
 }
 if(p.flow.state!=='NODE_BATTLE')return {frame:f,state:p.flow.state==='LOADING'?'TRANSITION':p.flow.state==='MAP'?'MAP':'UNKNOWN',verified:p.flow.state!=='UNKNOWN'&&p.flow.confidence>=.88};const h=p.nodeHeader,targets=(p.flow.targets||[]).filter(t=>t.target==='enter'&&t.verified===true&&boxValid(t.box,f));const recognized=h?.verified===true&&h.context==='NODE_BATTLE'&&Number.isInteger(h.floor)&&h.floor>=1&&p.flow.confidence>=.88;
 // V1 packets have no independent selected-preview-node pixel proof. Never
 // turn pending intent, in-progress position or an invented field into one.
 return {frame:f,state:recognized?'PREVIEW':'UNKNOWN',verified:recognized,zone:p.progress?.displayedZone??null,floor:recognized?h.floor:null,event:'battle',selectedNode:null,controlsVerified:targets.length===1,identityStatus:'PREVIEW_IDENTITY_UNPROVEN'};
}
module.exports={adaptMap,adaptPreview,readDirectMapAnchor};
