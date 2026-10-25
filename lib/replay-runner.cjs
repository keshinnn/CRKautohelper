'use strict';
const {performance}=require('node:perf_hooks');
const {selectNode}=require('./node-selector.cjs');
const {PreviewSession}=require('./preview-session.cjs');

// Gate annotations belong to the test dispatcher only. They are never passed
// to the image observer or selector, so human clicks cannot grant a false pass.
async function runReplay({frames,intent,gate,observe}) {
 if (!Array.isArray(frames)||typeof observe!=='function'||
     !Array.isArray(gate?.windowMs)||gate.windowMs.length!==2||!gate.windowMs.every(Number.isFinite)||
     gate.windowMs[1]<gate.windowMs[0]||!Array.isArray(gate.clientBox)||gate.clientBox.length!==4||
     !gate.clientBox.every(Number.isFinite)||gate.clientBox[2]<=0||gate.clientBox[3]<=0||
     !Number.isFinite(gate.previewFromPtsMs)) throw Error('REPLAY_CONTRACT_INVALID');
 let now=0,previous=null,lastPts=-1,session=null,state='NO_SELECTION',released=false;
 const actions=[],observations=[],timings=[],selectionAttempts=[];let failure=null;
 const dispatch=action=>{
  actions.push(structuredClone(action));
  const [x,y]=action.clientPoint,[left,top,w,h]=gate.clientBox;
  released=now>=gate.windowMs[0]&&now<=gate.windowMs[1]&&x>left&&x<left+w&&y>top&&y<top+h;
  return {status:released?'sent':'not_sent',transactionId:action.transactionId,frameId:action.frameId};
 };
 for(const source of frames){
  const f=source.frame;
  if(!f||!Number.isFinite(f.sourcePtsMs)||f.sourcePtsMs<=lastPts||!Number.isFinite(f.atMs)||f.atMs<now){state='REPLAY_TIME_INVALID';break;}
  now=f.atMs;lastPts=f.sourcePtsMs;
  if(!session&&f.sourcePtsMs>=gate.previewFromPtsMs){
   selectionAttempts.push({frameId:f.id,atMs:now,code:'HUMAN_BRANCH_NOT_RELEASED'});
   break;
  }
  if(session){
   state=session.tick().state;
   if(!['WAIT_PREVIEW','PREVIEW_STABLE'].includes(state))break;
   if(!released||f.sourcePtsMs<gate.previewFromPtsMs)continue;
  }
  const started=performance.now();
  let o;try{o=await observe(source);}catch(error){state='OBSERVATION_FAILED';failure={frameId:f.id,message:String(error)};break;}
  timings.push({frameId:f.id,processingMs:performance.now()-started});
  // Observer cannot replace the scheduler's identity, clock or source PTS.
  if(o?.frame?.id!==f.id||o.frame.atMs!==f.atMs||o.frame.sourcePtsMs!==f.sourcePtsMs||o.frame.sha256!==f.sha256){state='OBSERVATION_BINDING_INVALID';break;}
  observations.push(structuredClone(o));
  if(session){state=session.observe(o).state;if(!['WAIT_PREVIEW','PREVIEW_STABLE'].includes(state))break;continue;}
  if(o.state==='UNKNOWN'){state='TRANSITION_UNKNOWN';break;}
  if(o.state!=='MAP'){state='MAP_REQUIRED';break;}
  if(!previous){previous=o;continue;}
  // Geometry changes invalidate the old candidate before its anchor can be
  // checked. The replacement still needs a wholly new valid 200ms pair.
  const oldFrame=previous.frame,newFrame=o.frame;
  if(oldFrame.windowKey===newFrame.windowKey&&
     (oldFrame.geometryVersion!==newFrame.geometryVersion||oldFrame.width!==newFrame.width||
      oldFrame.height!==newFrame.height||JSON.stringify(oldFrame.origin)!==JSON.stringify(newFrame.origin))){
   state='STALE_GEOMETRY';
   selectionAttempts.push({previousFrameId:oldFrame.id,frameId:newFrame.id,atMs:now,code:state});
   previous=o;continue;
  }
  let proof;try{proof=selectNode(previous,o,intent,{nowMs:now});}catch(e){
   state=e.code||'SELECTION_FAILED';
   selectionAttempts.push({previousFrameId:previous.frame.id,frameId:o.frame.id,atMs:now,code:state});
   const a=previous.frame,b=o.frame;
   if(a.windowKey!==b.windowKey)break;
   if(state==='MAP_MOVING'){previous=o;continue;}
   if(state==='STALE_GEOMETRY'&&a.id!==b.id&&b.atMs>a.atMs){
    const changed=a.geometryVersion!==b.geometryVersion||a.width!==b.width||a.height!==b.height||JSON.stringify(a.origin)!==JSON.stringify(b.origin);
    if(changed){previous=o;continue;}
    if(b.atMs-a.atMs<200)continue;
   }
   break;
  }
  session=new PreviewSession({clock:()=>now,dispatch});
  state=(await session.start(proof)).state;
  if(state!=='WAIT_PREVIEW')break;
 }
 if(session&&['WAIT_PREVIEW','PREVIEW_STABLE'].includes(state)){
  now=session.snapshot().deadlineMs;state=session.tick().state;
 }
 return {state,passed:state==='PREVIEW_CONFIRMED',g4Complete:false,nativeActions:0,actions,failure,
  observations,timings,selectionAttempts,transaction:session?.snapshot()??null};
}
module.exports={runReplay};
