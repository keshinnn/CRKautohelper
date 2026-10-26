'use strict';
// Compare all original frames with current analysis; seven saved differences get
// individual bundles. This is a candidate audit, not pixel ground-truth grading.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {loadReplayFrames}=require('../lib/replay-case.cjs');
const {adaptMap,adaptPreview}=require('../lib/observer-adapter.cjs');
const {writeCaseArtifacts}=require('../lib/artifact-writer.cjs');
const {captureCodeVersion}=require('../lib/version-evidence.cjs');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function candidateView(m){return {absolute:m?.absoluteFloorKnown,columns:m?.columns??null,nodes:(m?.nodes||[]).map(n=>({id:n.id,type:n.type,floor:n.floor,column:n.column,completed:n.completed,box:n.box,center:n.center}))};}
function audit(){
 const [oldFile,currentDir,sevenFile,out,...extra]=process.argv.slice(2);
 if(!out||extra.length)throw Error('Usage: OLD_ANALYSIS CURRENT_REGRESSION_DIR SEVEN_AUDIT NEW_OUTPUT');
 const old=JSON.parse(fs.readFileSync(oldFile)),manifestFile=path.join(currentDir,'manifest.json'),current=JSON.parse(fs.readFileSync(manifestFile));
 const run=JSON.parse(fs.readFileSync(path.join(currentDir,'report.json'))),seven=JSON.parse(fs.readFileSync(sevenFile)).changed;
 if(run.passed!==true||run.complete!==true||run.expectedCases!==20||seven.length!==7)throw Error('CURRENT_NATIVE20_AND_SEVEN_REQUIRED');
 const version=captureCodeVersion(path.resolve(__dirname,'..'));
 for(const [p,h] of Object.entries(run.code))if(sha(fs.readFileSync(p))!==h)throw Error('CURRENT_CODE_CHANGED');
 const before=new Map();
 for(const c of old.cases)for(const f of c.frames)before.set(c.id+':'+f.frameIndex,{f,p:JSON.parse(fs.readFileSync(f.packet))});
 fs.mkdirSync(out);const report={checkedFrames:0,expectedFrames:1551,changed:[],anchorLoss:[],seven:[],
  version,currentRegressionReportSha256:sha(fs.readFileSync(path.join(currentDir,'report.json'))),
  sourceManifestSha256:sha(fs.readFileSync(oldFile)),currentManifestSha256:sha(fs.readFileSync(manifestFile)),
  sevenSourceSha256:sha(fs.readFileSync(sevenFile)),nativeActions:0,g4Complete:false,pixelSemanticReviewComplete:false};
 for(const c of current.cases){
  const frames=loadReplayFrames(c,current.videoSha256,current.analysis.observerContractVersion);
  for(let i=0;i<c.frames.length;i++){
   const f=c.frames[i],s=frames[i],b=before.get(c.id+':'+f.frameIndex);
   if(!b||b.f.sha256!==f.sha256||b.f.sourcePtsMs!==f.sourcePtsMs)throw Error('AUDIT_SOURCE_CHANGED');
   const oldMap=b.p.mapReview,newMap=s.packet.mapReview;
   const o=s.packet.flow.state==='MAP'&&!s.packet.v2Preview?.verified?adaptMap({...s.frame,png:s.png},s.packet):adaptPreview({...s.frame,png:s.png},s.packet);
   const row={id:c.id,frameIndex:f.frameIndex,image:f.image,packet:f.packet,
    oldNodeCount:oldMap?.nodes?.length??0,newNodeCount:newMap?.nodes?.length??0,
    oldAbsolute:oldMap?.absoluteFloorKnown,newAbsolute:newMap?.absoluteFloorKnown,observationState:o.state,
    caseReplayPassed:run.results.find(r=>r.id===c.id)?.passed===true};
   if(JSON.stringify(candidateView(oldMap))!==JSON.stringify(candidateView(newMap)))report.changed.push(row);
   if(row.oldAbsolute===true&&row.newAbsolute!==true)report.anchorLoss.push(row);
   if(seven.some(x=>x.id===c.id&&x.frameIndex===f.frameIndex)){
    const directory=path.join(out,c.id+'-'+f.frameIndex);
    writeCaseArtifacts(directory,{png:s.png,observation:{...o,rawPacket:s.packet,previousMap:oldMap},
     overlays:(newMap?.nodes||[]).map(n=>({box:n.box,label:n.id})),events:[],
     result:{passed:row.caseReplayPassed,purpose:'candidate audit: full source analysis and corresponding current case closure; visual review recorded separately',nativeActions:0}});
    report.seven.push({...row,bundle:directory});
   }
   report.checkedFrames++;
  }
 }
 report.coveragePassed=report.checkedFrames===1551&&report.seven.length===7&&report.seven.every(r=>r.caseReplayPassed)&&report.anchorLoss.length===0;
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify({checked:report.checkedFrames,candidateChanges:report.changed.length,seven:report.seven.length,anchorLoss:report.anchorLoss.length,coveragePassed:report.coveragePassed,pixelSemanticReviewComplete:false}));
 if(!report.coveragePassed)process.exitCode=1;
}
if(require.main===module)audit();
module.exports={candidateView};
