'use strict';
// Bounded offline attempt. No native backend, model fit, truth-driven planner,
// or inferred battle outcome. Recorded branch gate is dispatcher-only.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../..');
const {loadReplayFrames,buildReplayGate}=require('../../lib/replay-case.cjs');
const {adaptMap,adaptPreview}=require('../../lib/observer-adapter.cjs');
const {selectNode}=require('../../lib/node-selector.cjs');
const {runReplay}=require('../../lib/replay-runner.cjs');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function plan(previous,current){
 const attempts=[];
 if(current?.verified!==true||current.anchorVerified!==true)return {intent:null,attempts,reason:'MAP_AUTHORITY_MISSING'};
 // Fixed policy: smallest reachable battle floor/column. No case intent input.
 const nodes=[...(current.nodes||[])].filter(n=>n.type==='battle'&&n.available===true&&!n.completed)
  .sort((a,b)=>a.floor-b.floor||a.column-b.column);
 for(const n of nodes){
  const intent={zone:current.zone,floor:n.floor,column:n.column,event:'battle',mode:'select'};
  try{selectNode(previous,current,intent,{nowMs:current.frame.atMs});return {intent,attempts,reason:'INDEPENDENT_SELECTOR_PROOF'};}
  catch(e){attempts.push({nodeId:n.id,code:e.code||e.message});}
 }
 return {intent:null,attempts,reason:'NO_PROVEN_REACHABLE_BATTLE'};
}
async function main(output){
 fs.mkdirSync(output);const write=(name,v)=>fs.writeFileSync(path.join(output,name),JSON.stringify(v,null,2));
 const entries=[];
 for(let number=1;number<=60;number++){
  const file=path.join(root,`artifacts/concentrated-repair-20261103-02/current-case${String(number).padStart(2,'0')}-fresh-01/manifest.json`);
  if(!fs.existsSync(file))continue;
  const raw=fs.readFileSync(file),m=JSON.parse(raw),c=m.cases[0];
  entries.push({number,file,manifestSha256:sha(raw),c,video:c.videoSha256??m.videoSha256});
 }
 const unique=new Map();
 for(const e of entries){const key=e.video+':'+e.c.frames[0].sourcePtsMs;if(!unique.has(key))unique.set(key,e);}
 const sorted=[...unique.values()].sort((a,b)=>String(a.video).localeCompare(String(b.video))||a.c.frames[0].sourcePtsMs-b.c.frames[0].sourcePtsMs);
 const inventory=sorted.map((e,i)=>({case:e.number,manifest:e.file,manifestSha256:e.manifestSha256,
  videoSha256:e.video,rawVideoExists:fs.existsSync(e.c.video||''),firstPts:e.c.frames[0].sourcePtsMs,
  lastPts:e.c.frames.at(-1).sourcePtsMs,frames:e.c.frames.length,
  nextSameSourceGapMs:sorted[i+1]?.video===e.video?sorted[i+1].c.frames[0].sourcePtsMs-e.c.frames.at(-1).sourcePtsMs:null}));
 const continuousFile=path.join(root,'artifacts/p4c-LX46-continuous-native-01/manifest.json');
 const continuous=JSON.parse(fs.readFileSync(continuousFile,'utf8')).map(c=>({candidate:c.candidate,
  first:c.frames[0].sourcePtsMs,last:c.frames.at(-1).sourcePtsMs,frames:c.frames.length}));
 write('source-audit.json',{manifestCount:entries.length,distinctStarts:sorted.length,inventory,continuous,
  conclusion:'Raw videos exist, but sampled select-to-preview clips are not certified two-node episodes. Missing interval pixels/outcome proof cannot be inferred from case ordering.'});
 const e=sorted[0]; if(!e)throw Error('NO_SOURCE');
 const frames=loadReplayFrames(e.c,e.video,1);
 const pre=frames.filter((_,i)=>e.c.preFrames.includes(e.c.frames[i].frameIndex));
 const maps=pre.map(s=>adaptMap({...s.frame,png:s.png},s.packet));
 write('initial-observations.json',maps);
 for(let i=0;i<pre.length;i++)fs.writeFileSync(path.join(output,`initial-${i}.png`),pre[i].png);
 const decision=plan(maps[0],maps[1]);write('decision.json',decision);
 let replay=null;
 if(decision.intent){
  replay=await runReplay({frames,intent:decision.intent,gate:buildReplayGate(e.c),observe:async s=>{
   const f={...s.frame,png:s.png};return s.packet.flow?.state==='MAP'&&s.packet.v2Preview?.verified!==true?adaptMap(f,s.packet):adaptPreview(f,s.packet);
  }});
  write('first-transaction.json',replay);
 }
 const blocker=!decision.intent?decision.reason:replay.state==='PREVIEW_CONFIRMED'?'POST_PREVIEW_OUTCOME_AND_NEXT_MAP_UNPROVEN':replay.state;
 write('result.json',{status:'BLOCKED',selectedCase:e.number,selectionRule:'first chronological start after stable source-hash ordering; no outcome-based selection',
  blocker,virtualActions:replay?.actions.length||0,previewsConfirmed:replay?.state==='PREVIEW_CONFIRMED'?1:0,
  completedNodes:0,secondNodeStarted:false,nativeActions:0,formalVerifierChanged:false,
  packetMode:'existing image-bound observer packets revalidated by current Node code; not fresh Python inference',
  futureFramesUsedForPlanning:false,recordedIntentUsedForPlanning:false,
  resultTransition:'No battle/result/return-to-map contract is fabricated after preview.',
  minimalAlternative:'Use one same-source continuous episode including battle/result/return-map and next selection; planner picks from current verified graph. Dispatcher may release only a matching recorded branch; mismatch is BLOCKED. Keep proposal-only YOLO outside authority until physical rim and semantic map/preview proof exists.'});
 console.log(JSON.stringify({status:'BLOCKED',blocker,output,virtualActions:replay?.actions.length||0}));
}
if(require.main===module)main(path.resolve(process.argv[2])).catch(e=>{console.error(e.stack);process.exitCode=1;});
module.exports={plan};
