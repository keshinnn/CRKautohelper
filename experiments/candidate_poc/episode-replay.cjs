'use strict';
// Research orchestration only. Production proof/transactions remain unchanged.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {loadReplayFrames,buildReplayGate}=require('../../lib/replay-case.cjs');
const {adaptMap,adaptPreview}=require('../../lib/observer-adapter.cjs');
const {runReplay}=require('../../lib/replay-runner.cjs');
const {decodeRgbPng}=require('./verify_research.cjs');
const {plan}=require('./two_node_attempt.cjs');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
function validateCaseSource(c,outer,expected){
 if(outer!==expected||[c.videoSha256,c.source?.videoSha256].some(x=>x!=null&&x!==expected))throw Error('EPISODE_SOURCE_CHANGED');
}
function validateEpisode(e){
 if(!e.allFramesPreserved||!e.allDecodedRgbVerified||e.stitched||e.fps!==30||!Number.isInteger(e.firstFrame)||!Number.isInteger(e.lastFrame)||
  !Array.isArray(e.frames)||e.frames.length!==e.lastFrame-e.firstFrame+1||e.frames.length<2||
  e.frames.some((f,i)=>f.frameIndex!==e.firstFrame+i||!Number.isFinite(f.sourcePtsMs)||Math.abs(f.sourcePtsMs-f.frameIndex/e.fps*1000)>.1||!/^[a-f0-9]{64}$/.test(f.rgbSha256||'')))throw Error('CONTINUITY_UNPROVEN');
}
async function fileHash(file){const h=crypto.createHash('sha256');for await(const chunk of fs.createReadStream(file))h.update(chunk);return h.digest('hex');}
function resultBarrier(packet){
 if(packet.flow?.state==='UNKNOWN')return 'RESULT_UNKNOWN';
 // There is no production result-proof issuer/validator to reuse. A supplied
 // verified boolean or victory OCR is not a substitute for independent proof.
 return 'RESULT_VERIFIER_UNAVAILABLE';
}
async function main(folder,output,repairFolder,riftFolder){
 fs.mkdirSync(output);const log=[];let virtualActions=0,previewsConfirmed=0,completedNodes=0,worldStateUpdated=false,secondPlanExecuted=false,secondNodeComplete=false;
 const save=(name,v)=>fs.writeFileSync(path.join(output,name),JSON.stringify(v,null,2));
 const event=(state,atMs,evidence)=>{log.push({state,atMs,evidence});save('states.json',log);};
 const episode=read(path.join(folder,'continuous/manifest.json'));
 validateEpisode(episode);
 const clipFile=episode.clipFile||'continuous.avi';
 if(!/^[a-zA-Z0-9._-]+\.(?:avi|mp4|mkv)$/.test(clipFile)||path.basename(clipFile)!==clipFile)throw Error('CONTINUOUS_CLIP_PATH_INVALID');
 if(await fileHash(path.join(folder,'continuous',clipFile))!==episode.clipSha256)throw Error('CONTINUOUS_CLIP_CHANGED');
 const rows=new Map(episode.frames.map(x=>[x.frameIndex,x]));
 const bind=(c,f,source)=>{
  validateCaseSource(c,source,episode.videoSha256);
  const s=loadReplayFrames({...c,frames:[f]},source,1)[0],row=rows.get(f.frameIndex);
  if(!row||s.frame.width!==episode.size[0]||s.frame.height!==episode.size[1]||f.atMs!==f.sourcePtsMs||Math.abs(row.sourcePtsMs-f.sourcePtsMs)>.1||sha(decodeRgbPng(s.png).rgb)!==row.rgbSha256)throw Error('EPISODE_PIXEL_OR_TIME_MISMATCH');
  return s;
 };
 const m=read(path.join(folder,'native-analysis/manifest.json')),c=m.cases[0];
 const pre=c.frames.slice(0,2).map(f=>bind(c,f,m.videoSha256));
 const observations=pre.map(s=>adaptMap({...s.frame,png:s.png},s.packet));
 save('initial-observations.json',observations);
 event('OBSERVE_MAP',pre[1].frame.atMs,pre.map(x=>({frame:x.frame.id,sha256:x.frame.sha256})));
 const decision=plan(...observations);save('decision.json',decision);
 let blocker=decision.reason;
 if(decision.intent){
  event('PLAN_PROVEN',pre[1].frame.atMs,decision.intent);
  // Gate data is used exclusively by recorded-branch dispatcher, after plan.
  const frames=c.frames.map(f=>bind(c,f,m.videoSha256));
  const replay=await runReplay({frames,intent:decision.intent,gate:buildReplayGate(c),observe:async s=>{
   const f={...s.frame,png:s.png};return s.packet.flow?.state==='MAP'&&!s.packet.v2Preview?.verified?adaptMap(f,s.packet):adaptPreview(f,s.packet);
  }});
  save('first-transaction.json',replay);virtualActions=replay.actions.length;
  for(const e of replay.transaction?.events||[])event(e.state,e.atMs,e);
  if(replay.state==='PREVIEW_CONFIRMED'){
   previewsConfirmed=1;
   const battle=read(path.join(folder,'battle-analysis/manifest.json'));
   // Read-only observations of recorded battle; no claim that team/skill
   // inputs in the intervening movie were autonomously controlled.
   for(const f of battle.cases[0].frames){
    const s=bind(battle.cases[0],f,battle.videoSha256);
    event('RECORDED_BATTLE_OBSERVATION',f.atMs,{frame:s.frame,classification:s.packet.flow.state,packet:f.packet});
    if(s.packet.flow.state==='UNKNOWN'){blocker='BATTLE_UNKNOWN';break;}
   }
   if(blocker!=='BATTLE_UNKNOWN'){
   if(repairFolder){
    const {identity,pending,verifyPair,trustedResultFrame,validatePhaseFrames}=require('./result-evidence.cjs');
    const previewAt=replay.transaction.events.findLast(e=>e.state==='PREVIEW_CONFIRMED').atMs;
    const battleEnd=validatePhaseFrames(battle.cases[0].frames,previewAt);
    const input=read(path.join(repairFolder,'result-inputs.json'));
    const proposed=read(path.join(repairFolder,'result-ocr.json'));
    if(input.videoSha256!==episode.videoSha256||proposed.length!==input.frames.length)throw Error('RESULT_SOURCE_CHANGED');
    validatePhaseFrames(input.frames,battleEnd);
    // Both fresh battle observations must identify the selected zone/floor.
    for(const f of battle.cases[0].frames){
     const s=bind(battle.cases[0],f,battle.videoSha256);
     const labels=s.packet.evidence.filter(x=>x.score>=.9&&new RegExp(`區域${decision.intent.zone}第${decision.intent.floor}層-WAVE[0-9]+`).test(x.text));
     if(labels.length!==1)throw Error('BATTLE_IDENTITY_UNPROVEN');
    }
    let previous=null,receipt=null;
    for(let i=0;i<input.frames.length;i++){
     const f=input.frames[i],r=proposed[i],png=fs.readFileSync(f.image),im=decodeRgbPng(png),source=rows.get(f.frameIndex);
     const candidate=trustedResultFrame(f,source,episode.videoSha256,replay.transaction.proof.frame.geometryVersion);
     if(im.w!==episode.size[0]||im.h!==episode.size[1]||sha(png)!==f.sha256||r.imageSha256!==f.sha256||sha(im.rgb)!==source.rgbSha256||r.pixelSha256!==source.rgbSha256)throw Error('RESULT_SOURCE_CHANGED');
     const found=identity(r.evidence,decision.intent);
     if(!found){
      previous=null;
      const waitOnly=pending(r.evidence,decision.intent)||r.originalSemantic.state==='BATTLE';
      event(waitOnly?'RESULT_PENDING':'RESULT_UNKNOWN',f.sourcePtsMs,{frameIndex:f.frameIndex,imageSha256:f.sha256,waitOnly,noInput:true});
      if(!waitOnly){blocker='RESULT_UNKNOWN';break;}
      continue;
     }
     event('RESULT_CANDIDATE',f.sourcePtsMs,{frameIndex:f.frameIndex,identity:found});
     if(previous){
      // Decoder timestamps can be just below200ms. Wait for a later frame;
      // do not round the interval or widen the existing stability threshold.
      if(candidate.sourcePtsMs-previous.sourcePtsMs<200){
       event('RESULT_STABILITY_WAIT',f.sourcePtsMs,{firstFrame:previous.frameIndex,currentFrame:f.frameIndex});continue;
      }
      receipt=verifyPair([previous,candidate],decision.intent,path.join(output,'independent-result-reread.json'));
      save('result-proof.json',{...receipt,battleFrames:battle.cases[0].frames.map(f=>f.frameIndex),transactionId:replay.transaction.transactionId,nodeId:replay.transaction.proof.nodeId});
      event('RESULT_CONFIRMED_RESEARCH',f.sourcePtsMs,{receipt:'result-proof.json',formalVerifierChanged:false});
      completedNodes=1;break;
     }
     previous=candidate;
    }
    if(receipt){
     const returned=read(path.join(folder,'return-analysis/manifest.json'));let last=null,lastSource=null;
     validatePhaseFrames(returned.cases[0].frames,receipt.frames.at(-1).sourcePtsMs);
     const attempts=[];
     for(const f of returned.cases[0].frames){
      const s=bind(returned.cases[0],f,returned.videoSha256),o=adaptMap({...s.frame,png:s.png},s.packet);
      if(o.state!=='MAP'||!o.verified||!o.anchorVerified||!o.current?.verified) {blocker='RETURN_MAP_UNPROVEN';break;}
      const node=o.nodes.find(n=>n.id===o.current.nodeId&&n.floor===decision.intent.floor&&n.column===decision.intent.column&&n.completed===true);
      if(!node||o.zone!==decision.intent.zone){blocker='COMPLETION_MAP_CONFLICT';break;}
      event('RETURN_MAP_OBSERVED',f.atMs,{frame:s.frame,current:o.current});
      if(!last){last=o;lastSource=s;continue;}
      const next=riftFolder?require('./rift-transaction.cjs').planSupported([lastSource,s]):plan(last,o);attempts.push({atMs:f.atMs,decision:next});
      if(next.intent){
       worldStateUpdated=true;secondPlanExecuted=true;
       event('WORLD_STATE_UPDATED',f.atMs,{completedNode:{zone:o.zone,floor:node.floor,column:node.column}});
       event('SECOND_PLAN_PROVEN',f.atMs,next.intent);save('second-decision.json',next);
       // Evaluator metadata is read ONLY after the independent second plan.
       const branch=read(path.join(riftFolder||repairFolder,'recorded-branch.json'));
       if(branch.videoSha256!==episode.videoSha256||sha(decodeRgbPng(fs.readFileSync(branch.image)).rgb)!==rows.get(branch.frameIndex)?.rgbSha256)throw Error('RECORDED_BRANCH_SOURCE_INVALID');
       const same=['zone','floor','column','event'].every(k=>next.intent[k]===branch.choice[k]);
       if(!same){
        blocker='BRANCH_NOT_RECORDED';
        event(blocker,f.atMs,{autonomous:next.intent,recorded:branch.choice,secondActionSent:false});break;
       }
       if(next.intent.event==='rift'&&riftFolder){
        const rm=read(path.join(riftFolder,'analysis/manifest.json')),rc=rm.cases[0];
        const after=rc.frames.filter(x=>x.sourcePtsMs>f.sourcePtsMs).map(x=>bind(rc,x,rm.videoSha256));
        const rift=require('./rift-transaction.cjs').runRift({decision:next,after,recordedBranch:branch.choice,nowMs:f.atMs,currentFrame:s.frame});
        save('second-rift-transaction.json',{...rift,nativeContextIndependentlyVerified:false});virtualActions+=rift.actions.length;
        for(const e of rift.events.filter(e=>e.state!=='RIFT_PREVIEW_CONFIRMED_RESEARCH'))event(e.state,e.atMs,e);
        if(rift.state!=='RIFT_PREVIEW_CONFIRMED_RESEARCH'){blocker=rift.state;break;}
        let riftReceipt;
        try{riftReceipt=require('./rift-transaction.cjs').confirmRiftTransaction(rift,next.proof,output);save('second-rift-preview-proof.json',riftReceipt);}
        catch(e){blocker=e.code||e.message;event('RIFT_CONTEXT_SAFE_STOP',rift.previews.at(-1).frame.atMs,{reason:blocker});save('second-failure.json',{reason:blocker,stack:e.stack});break;}
        save('second-rift-transaction.json',{...rift,nativeContextIndependentlyVerified:true});
        const confirmed=rift.events.find(e=>e.state==='RIFT_PREVIEW_CONFIRMED_RESEARCH');event(confirmed.state,confirmed.atMs,confirmed);
        previewsConfirmed++;
        try{
         const done=require('./rift-completion.cjs').completeRift({proof:next.proof,riftReceipt,folder:riftFolder,output,episode,rows,bind,event,save});
         if(done.completed&&done.worldUpdated){completedNodes=2;secondNodeComplete=true;blocker=null;}
        }catch(e){blocker=e.code||e.message;event('SECOND_SAFE_STOP',rift.previews.at(-1).frame.atMs,{reason:blocker});save('second-failure.json',{reason:blocker,stack:e.stack});}
        break;
       }
       const secondFile=path.join(repairFolder,'second-analysis/manifest.json');
       if(!fs.existsSync(secondFile)){blocker='SECOND_SEQUENCE_MISSING';event(blocker,f.atMs,{secondActionSent:false});break;}
       const sm=read(secondFile),sc=sm.cases[0];
       if(sc.frames[0].sourcePtsMs<f.sourcePtsMs)throw Error('SECOND_SEQUENCE_TIME_INVALID');
       const secondFrames=sc.frames.map(x=>bind(sc,x,sm.videoSha256));
       const second=await require('./second-transaction.cjs').runSecond({frames:secondFrames,gate:buildReplayGate(sc),previousDecision:next.intent,
        completedNode:{zone:o.zone,floor:node.floor,column:node.column}});
       save('second-transaction.json',second);virtualActions+=second.actions.length;
       if(second.state==='PREVIEW_CONFIRMED')previewsConfirmed++;
       blocker=second.state==='PREVIEW_CONFIRMED'?'SECOND_RESULT_SEQUENCE_REQUIRED':second.state;
       for(const e of second.transaction?.events||[])event('SECOND_'+e.state,e.atMs,e);
       break;
      }
      last=o;lastSource=s;blocker='NEXT_NODE_PROOF_MISSING';
     }
     save('return-planning.json',attempts);
    }else if(blocker!=='RESULT_UNKNOWN')blocker='RESULT_PAIR_INCOMPLETE';
   }else{
    const outcome=read(path.join(folder,'outcome-analysis/manifest.json'));
    const f=outcome.cases[0].frames[0],s=bind(outcome.cases[0],f,outcome.videoSha256);
    blocker=resultBarrier(s.packet);
    save('failure-packet.json',s.packet);fs.writeFileSync(path.join(output,'failure.png'),s.png);
    event('WAIT_RESULT_PROOF',f.atMs,{frame:s.frame,classification:s.packet.flow.state,packet:f.packet});
    event(blocker,f.atMs,{futureReturnMapConsumed:false,worldStateUpdated:false});
   }
   }
  }else blocker=replay.actions.length&&replay.transaction?.receipt?.status==='not_sent'?'BRANCH_NOT_RECORDED':replay.state;
 }
 const result={status:secondNodeComplete?'PASS_RESEARCH_TWO_NODE_REPLAY':'BLOCKED',blocker,virtualActions,previewsConfirmed,completedNodes,
  worldStateUpdated,worldStateUpdates:secondNodeComplete?2:worldStateUpdated?1:0,secondPlanExecuted,secondNodeComplete,nativeActions:0,
  continuousSource:episode.videoSha256,continuousFrames:episode.frames.length,
  scope:'known-source native integration, not unseen-source generalization or live operation',
  autonomousBattleInputs:false,recordedIntentUsedByPlanner:false,futureReturnMapUsedForResult:false,
  returnMapConsumedAfterResult:worldStateUpdated,
  resultRepairUsed:!!repairFolder,riftResearchProfile:!!riftFolder,formalVerifierChanged:false,formalA3Accepted:false,g4Complete:false,
  minimalNextStep:secondNodeComplete?'Broaden independent validation of the isolated rift contract before any approved production integration. Recorded team/skill controls are not autonomous and P5 is not authorized.':repairFolder?'Continue from the preserved blocker without copying the movie into the planner.':'Isolated independent result verification required.'};
 save('result.json',result);console.log(JSON.stringify(result));
}
if(require.main===module)main(path.resolve(process.argv[2]),path.resolve(process.argv[3]),process.argv[4]&&path.resolve(process.argv[4]),process.argv[5]&&path.resolve(process.argv[5])).catch(e=>{console.error(e.stack);process.exitCode=1;});
module.exports={resultBarrier,validateCaseSource,validateEpisode};
