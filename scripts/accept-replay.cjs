'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {runReplay}=require('../lib/replay-runner.cjs');
const {evaluateReplay}=require('../lib/replay-evaluator.cjs');
const {adaptMap,adaptPreview}=require('../lib/observer-adapter.cjs');
const {writeCaseArtifacts}=require('../lib/artifact-writer.cjs');
const {milestoneResult}=require('../lib/evidence.cjs');
const {compareSnapshot}=require('../lib/evidence.cjs');
const {captureCodeVersion}=require('../lib/version-evidence.cjs');
const sha=raw=>crypto.createHash('sha256').update(raw).digest('hex');

async function main(){
 const [analysisFile,annotationFile,output]=process.argv.slice(2);
 if(!output)throw Error('analysis manifest, frozen annotations and new output directory required');
 const manifest=JSON.parse(fs.readFileSync(analysisFile,'utf8')),rawAnnotations=fs.readFileSync(annotationFile),annotations=JSON.parse(rawAnnotations);
 const stage=manifest.stage,required={'P4-A':5,'P4-B':15}[stage];
 if(!required||manifest.transform!==(stage==='P4-A'?'none':'fixed_scale')||manifest.sourceSize?.join(',')!=='1440,1080'||
    manifest.annotationSha256!==sha(rawAnnotations)||manifest.cases.length!==required||annotations.cases.length!==5)throw Error('MILESTONE_SOURCE_CONTRACT_INVALID');
 const root=path.resolve(__dirname,'..'),programVersion=captureCodeVersion(root),baselineFile=path.join(root,'artifacts/baseline.json');
 const baselineRaw=fs.readFileSync(baselineFile),baseline=JSON.parse(baselineRaw),v1Comparison=compareSnapshot(baseline.root,baseline);
 if(!v1Comparison.unchanged)throw Error('V1_BASELINE_CHANGED');
 const versionEvidence={programVersion,v1BaselineSha256:sha(baselineRaw),v1ComparedFiles:baseline.files.length,v1Comparison,analysis:manifest.analysis??null};
 fs.mkdirSync(output);
 const results=[];
 for(const c of manifest.cases){
  const scale=stage==='P4-A'?1:c.scale,expected=annotations.cases.find(x=>x.id===(c.originalId||c.id));
  if(!(stage==='P4-A'?[1]:[.75,1,1.25]).includes(scale)||!expected||['intent','preFrames','lastFrame','gateWindowMs','humanClickInterval','reviewed'].some(k=>JSON.stringify(c[k])!==JSON.stringify(expected[k])))throw Error('ANNOTATION_CHANGED');
  if(['expectedBox','clientBox'].some(k=>JSON.stringify(c[k])!==JSON.stringify(expected[k].map(v=>v*scale))))throw Error('TRUTH_TRANSFORM_CHANGED');
  const indices=[...c.preFrames,...Array.from({length:c.lastFrame-c.preFrames[1]},(_,i)=>c.preFrames[1]+i+1)];
  if(indices.length!==c.frames.length||c.frames.some((f,i)=>f.frameIndex!==indices[i]||Math.abs(f.sourcePtsMs-f.frameIndex/30*1000)>.001||f.atMs!==f.sourcePtsMs))throw Error('TRANSITION_FRAMES_MISSING');
  const frames=c.frames.map(entry=>{
   const png=fs.readFileSync(entry.image),packet=JSON.parse(fs.readFileSync(entry.packet,'utf8'));
   if(sha(png)!==entry.sha256)throw Error('FROZEN_SOURCE_CHANGED');
   if(entry.size?.[0]!==Math.round(1440*scale)||entry.size?.[1]!==Math.round(1080*scale))throw Error('CLIENT_SIZE_CHANGED');
   return {png,packet,frame:{id:packet.binding.frameId,sha256:entry.sha256,atMs:entry.atMs,sourcePtsMs:entry.sourcePtsMs,
    width:entry.size[0],height:entry.size[1],geometryVersion:entry.geometryVersion,windowKey:'offline:original-video',origin:[0,0]}};
  });
  const consumed=[];
  const r=await runReplay({frames,intent:c.intent,gate:{windowMs:c.gateWindowMs,clientBox:c.clientBox,previewFromPtsMs:c.frames[2].sourcePtsMs},observe:async source=>{
   const bound={...source.frame,png:source.png},p=source.packet;
   const o=p.flow.state==='MAP'&&p.v2Preview?.verified!==true?adaptMap(bound,p):adaptPreview(bound,p);
   consumed.push({source,observation:o});return o;
  }});
  const grade=evaluateReplay(c,r,{stage,scale}),folder=path.join(output,c.id);fs.mkdirSync(folder);
  const bundles=[];
  for(const [i,item] of consumed.entries()){
   const o=item.observation,shapes=(o.nodes||[]).map(n=>({box:n.box,label:n.id}));
   if(o.selectedNode?.box)shapes.push({box:o.selectedNode.box,label:'independently selected'});
   if(r.transaction?.action.frameId===o.frame.id)shapes.push({point:r.transaction.action.clientPoint,label:'virtual click'});
   bundles.push(writeCaseArtifacts(path.join(folder,'frame-'+String(i).padStart(4,'0')),{png:item.source.png,
    observation:{...o,rawPacket:item.source.packet},overlays:shapes,events:(r.transaction?.events||[]).filter(e=>e.atMs<=o.frame.atMs),result:{...grade,passed:false,purpose:'per-frame evidence; case grade in summary'}}));
  }
  const last=consumed.at(-1);
  const summary=writeCaseArtifacts(path.join(folder,'summary'),{png:last?.source.png||frames[0].png,
   observation:{...(last?.observation||{state:'UNKNOWN',verified:false}),transaction:r.transaction,sequenceBundles:bundles},
   overlays:last?.observation.selectedNode?.box?[{box:last.observation.selectedNode.box,label:'confirmed selected node'}]:[],
   events:r.transaction?.events||[],result:grade});
  const entry={...grade,...summary,manifest:path.resolve(folder,'summary/manifest.json')};results.push(entry);
  fs.writeFileSync(path.join(folder,'transaction.json'),JSON.stringify(r,null,2),{flag:'wx'});
  const result={...milestoneResult(stage,results),results,versionEvidence,analysisManifestSha256:sha(fs.readFileSync(analysisFile)),annotationSha256:sha(rawAnnotations),nativeActions:0};
  fs.writeFileSync(path.join(output,'report.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify({case:c.id,state:r.state,passed:grade.passed,consumedFrames:consumed.length,checks:grade.checks}));
  if(!grade.passed){process.exitCode=1;return;}
 }
 const final=JSON.parse(fs.readFileSync(path.join(output,'report.json')));
 console.log(JSON.stringify({stage,passed:final.passed,g4Complete:false,cases:results.length,nativeActions:0}));
 if(!final.passed)process.exitCode=1;
}
main().catch(error=>{console.error(error.stack);process.exitCode=1;});
