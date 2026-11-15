'use strict';
// Schema probes derived from existing observer output, NOT model inference or
// candidate generation. Frozen truth is never read here.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {performance}=require('node:perf_hooks');
const root=path.resolve(__dirname,'../..');
const {loadReplayFrames}=require(path.join(root,'lib/replay-case.cjs'));
const {adaptMap,adaptPreview}=require(path.join(root,'lib/observer-adapter.cjs'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function run(){
 const records=[];
 for(const number of [1,19,25,31,39,41,52,53,55,56,57,58,59]){
  const file=path.join(root,`artifacts/concentrated-repair-20261103-02/current-case${String(number).padStart(2,'0')}-fresh-01/manifest.json`);
  const raw=fs.readFileSync(file),m=JSON.parse(raw),c=m.cases[0];
  // First source frame and first existing verified preview, evaluator scheduling
  // only. No future frame feeds any earlier probe.
  const indices=[0];
  const preview=c.frames.findIndex(f=>{
   const p=JSON.parse(fs.readFileSync(f.packet,'utf8'));return p.v2Preview?.verified===true;
  });
  if(preview>=0&&preview!==0)indices.push(preview);
  for(const index of indices){
   const s=loadReplayFrames({...c,frames:[c.frames[index]]},m.videoSha256,1)[0],p=s.packet;
   function observe(packet){
    const started=performance.now();
    try{
     const o=(index===0?adaptMap:adaptPreview)({...s.frame,png:s.png},packet);
     return {state:o.state,verified:o.verified===true,anchorVerified:o.anchorVerified===true,
             reason:o.reason??null,nodes:o.nodes?.length??0,ms:performance.now()-started};
    }catch(e){return {rejected:true,error:e.message,ms:performance.now()-started};}
   }
   const baseline=observe(p),variants={};
   const noProof=structuredClone(p);
   for(const map of [noProof.mapReview,noProof.v2Preview?.recoveredMapReview]){
    if(!map)continue;
    delete map.aspectRectification;
    for(const n of map.nodes||[]){
     delete n.orangeRefinement;delete n.originalEllipseSize;delete n.detectorGeometry;
     n.modelConfidence=1;
    }
   }
   noProof.candidateEvidenceV2={schema:'candidate-evidence/v2',confidence:1,verified:true};
   variants.missingTemplateProofWithConfidenceOne=observe(noProof);
   const proposalOnly=structuredClone(p);
   const boxes=(p.mapReview?.nodes||[]).map(n=>n.box);
   proposalOnly.mapReview={frameId:p.mapReview.frameId,absoluteFloorKnown:false,
     nodes:boxes.map((box,i)=>({id:`proposal-${i}`,type:'proposal',floor:null,column:null,box,score:1,modelConfidence:1})),edges:[]};
   delete proposalOnly.v2Preview;
   proposalOnly.candidateEvidenceV2={schema:'candidate-evidence/v2',confidence:1};
   variants.proposalsOnlyNoCopiedAuthority=observe(proposalOnly);
   const mismatch=structuredClone(p);mismatch.binding.pixelSha256='0'.repeat(64);
   variants.wrongSourceWithConfidenceOne=observe(mismatch);
   records.push({case:number,index,manifestSha256:sha(raw),imageSha256:s.frame.sha256,
    baseline,variants,scope:'schema_probe_existing_packets_no_new_model',nativeActions:0});
  }
 }
 return {records,formalVerifierChanges:0,nativeActions:0,newModelInference:false,
         interpretation:'Direct NN proposal substitution cannot mint the old aspect/ellipse proof. Reuse remains possible only after independent original builders produce valid evidence.'};
}
if(require.main===module){const result=run();fs.writeFileSync(process.argv[2],JSON.stringify(result,null,2));console.log(JSON.stringify({probes:result.records.length}));}
module.exports={run};
