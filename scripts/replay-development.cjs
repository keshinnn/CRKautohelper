'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {runReplay}=require('../lib/replay-runner.cjs');
const {adaptMap,adaptPreview}=require('../lib/observer-adapter.cjs');
const {buildReplayGate,loadReplayFrames}=require('../lib/replay-case.cjs');
const {evaluateDevelopmentReplay}=require('../lib/replay-evaluator.cjs');
const {writeCaseArtifacts}=require('../lib/artifact-writer.cjs');
const {captureCodeVersion}=require('../lib/version-evidence.cjs');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
async function main(){
 const [file,out,...extra]=process.argv.slice(2);
 if(!file||!out||extra.length)throw Error('Usage: replay-development.cjs ANALYSIS_MANIFEST NEW_OUTPUT');
 const raw=fs.readFileSync(file),m=JSON.parse(raw);
 if(m.analysis?.allFramesAnalyzed!==true||!Array.isArray(m.cases)||!m.cases.length)
  throw Error('COMPLETE_ANALYSIS_REQUIRED');
 const ids=m.cases.map(c=>c.id);
 if(ids.some(id=>typeof id!=='string'||!/^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$/.test(id))||
    new Set(ids).size!==ids.length)throw Error('CASE_ID_INVALID');
 fs.mkdirSync(out);
 const version=captureCodeVersion(path.resolve(__dirname,'..')),results=[];
 fs.writeFileSync(path.join(out,'source-manifest.snapshot.json'),raw,{flag:'wx'});
 let currentCase=null;
 try{
  for(const c of m.cases){
   currentCase=c.id;
   const folder=path.join(out,c.id);fs.mkdirSync(folder);
   const consumed=[],frames=loadReplayFrames(c,m.videoSha256),gate=buildReplayGate(c);
   const r=await runReplay({frames,intent:c.intent,gate,observe:async source=>{
    const f={...source.frame,png:source.png},p=source.packet;
    const o=p.flow.state==='MAP'&&!p.v2Preview?.verified?adaptMap(f,p):adaptPreview(f,p);
    consumed.push({source,o});return o;
   }});
   const grade=evaluateDevelopmentReplay(c,r);
   for(const [i,{source,o}] of consumed.entries()){
    writeCaseArtifacts(path.join(folder,'frame-'+String(i).padStart(4,'0')),{
     png:source.png,observation:{...o,rawPacket:source.packet},
     overlays:(o.nodes||[]).map(n=>({box:n.box,label:n.id})),
     events:(r.transaction?.events||[]).filter(e=>e.atMs<=o.frame.atMs),
     result:{...grade,passed:false,purpose:'per-frame evidence; summary holds actual grade'},
    });
   }
   const last=consumed.at(-1);
   writeCaseArtifacts(path.join(folder,'summary'),{
    png:last?.source.png||frames[0].png,
    observation:{...last?.o,transaction:r.transaction},
    overlays:last?.o.selectedNode?.box?[{box:last.o.selectedNode.box,label:'independently confirmed preview node'}]:[],
    events:r.transaction?.events||[],result:grade,
   });
   fs.writeFileSync(path.join(folder,'transaction.json'),JSON.stringify(r,null,2),{flag:'wx'});
   results.push({...grade,consumedFrames:consumed.length});
   fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({
    stage:'P4-C-development',passed:results.length===m.cases.length&&results.every(r=>r.passed),
    expectedCases:m.cases.length,results,sourceManifestSha256:sha(raw),version,
    runnerSha256:sha(fs.readFileSync(__filename)),g4Complete:false,nativeActions:0,
   },null,2));
   console.log(JSON.stringify(results.at(-1)));
   if(!grade.passed){process.exitCode=1;return;}
  }
 }catch(error){
  fs.writeFileSync(path.join(out,'failure.json'),JSON.stringify({
   caseId:currentCase,error:String(error),sourceManifestSha256:sha(raw),
   passed:false,g4Complete:false,nativeActions:0,
  },null,2),{flag:'wx'});
  throw error;
 }
}
main().catch(e=>{console.error(e);process.exitCode=1;});
