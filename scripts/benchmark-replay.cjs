'use strict';
// Measure the real causal Node path as well as the recorded Python producer.
// Frames are preloaded. Report/artifact I/O and live capture/IPC are excluded.
const fs=require('node:fs'),{performance}=require('node:perf_hooks');
const {runReplay}=require('../lib/replay-runner.cjs'),{loadReplayFrames,buildReplayGate}=require('../lib/replay-case.cjs');
const {adaptMap,adaptPreview}=require('../lib/observer-adapter.cjs');
async function main(){
 const [file,out,...extra]=process.argv.slice(2);if(!out||extra.length)throw Error('ANALYSIS NEW_TIMING_JSON required');
 const m=JSON.parse(fs.readFileSync(file)),rows=[],results=[];
 for(const c of m.cases){
  let active=null;
  const close=()=>{if(active){active.nodeMs=performance.now()-active.started;active.overallMs=active.pythonMs+active.nodeMs;delete active.started;active=null;}};
  const r=await runReplay({frames:loadReplayFrames(c,m.videoSha256,m.analysis.observerContractVersion),intent:c.intent,gate:buildReplayGate(c),observe:async s=>{
   close();active={caseId:c.id,frameId:s.frame.id,pythonMs:s.packet.analysisTiming.elapsedMs,started:performance.now()};rows.push(active);
   const f={...s.frame,png:s.png},p=s.packet;
   return p.flow.state==='MAP'&&!p.v2Preview?.verified?adaptMap(f,p):adaptPreview(f,p);
  }});close();results.push({id:c.id,state:r.state,passed:r.passed,virtualClicks:r.actions.length,nativeActions:0});
  if(!r.passed)throw Error('BASELINE_REPLAY_FAILED_'+c.id);
 }
 fs.writeFileSync(out,JSON.stringify({rows,results,nativeActions:0,g4Complete:false,method:'producer elapsed + same-frame causal Node interval, including adapter/selection/transaction/verification; preloaded replay, excludes live capture/IPC and report I/O'},null,2),{flag:'wx'});
}
main().catch(e=>{console.error(e);process.exitCode=1;});
