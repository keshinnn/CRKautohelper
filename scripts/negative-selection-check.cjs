'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {loadReplayFrames}=require('../lib/replay-case.cjs'),{adaptMap,adaptPreview}=require('../lib/observer-adapter.cjs'),{selectNode}=require('../lib/node-selector.cjs');
const {writeCaseArtifacts}=require('../lib/artifact-writer.cjs'),{captureCodeVersion}=require('../lib/version-evidence.cjs');
const [input,out]=process.argv.slice(2),raw=fs.readFileSync(input),m=JSON.parse(raw);assert.equal(m.cases.length,1);
const c=m.cases[0],analyzed=c.frames.filter(f=>f.packet&&fs.existsSync(f.packet));assert(analyzed.length>=1&&analyzed.length<=2);
const frames=loadReplayFrames({...c,frames:analyzed},m.videoSha256,m.analysis?.observerContractVersion);for(const s of frames)assert.equal(s.packet.analysisTiming.freshFullPipeline,true);
const observations=frames.map(s=>{const f={...s.frame,png:s.png};return s.packet.flow.state==='MAP'&&!s.packet.v2Preview?.verified?adaptMap(f,s.packet):adaptPreview(f,s.packet);});
let proof=null,rejection='OBSERVATION_INCOMPLETE';
if(observations.length===2){try{proof=selectNode(observations[0],observations[1],c.intent,{nowMs:observations[1].frame.atMs});}catch(e){rejection=e.code||e.message;}}
const noPreview=observations.every(o=>o.state!=='PREVIEW'),singleUnproven=observations.length===2||observations.some(o=>o.verified!==true||o.anchorVerified!==true);
const identityUnproven=c.expectedFailureCategory!=='ZONE_IDENTITY_UNPROVEN'||observations.every(o=>o.zone==null&&o.verified!==true);
const mapContext=observations.length===2&&observations.every(o=>o.state==='MAP'&&o.verified===true&&o.anchorVerified===true&&o.zone===c.intent.zone);
const semanticReason=!c.expectedRecognizedMapContext||Array.isArray(c.expectedRejectionReasons)&&c.expectedRejectionReasons.includes(rejection);
const result={id:c.id,baseNegativeId:c.baseNegativeId,passed:!proof&&noPreview&&singleUnproven&&identityUnproven&&semanticReason&&(!c.expectedRecognizedMapContext||mapContext),
 expectedFailureCategory:c.expectedFailureCategory,expectedRecognizedMapContext:c.expectedRecognizedMapContext,recognizedMapContext:mapContext,rejection,
 unexpectedSelectionProof:!!proof,falsePreviewConfirmation:!noPreview,analyzedFrames:frames.length,freshFullPipeline:true,positiveCountContribution:0,
 formalNegativeGateComplete:false,holdoutTouched:false,nativeActions:0,virtualClicks:0,g4Complete:false,
 sourceAnalysisSha256:crypto.createHash('sha256').update(raw).digest('hex'),version:captureCodeVersion(process.cwd())};
fs.mkdirSync(out);
for(const [i,s] of frames.entries())writeCaseArtifacts(path.join(out,'frame-'+i),{png:s.png,observation:{...observations[i],rawPacket:s.packet},overlays:(observations[i].nodes||[]).map(n=>({box:n.box,label:n.id})),events:[{state:proof?'UNEXPECTED_SELECTION_PROOF':'NEGATIVE_REJECTED',atMs:observations[i].frame.atMs,reason:rejection}],result});
fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({...result,version:undefined}));if(!result.passed)process.exitCode=1;
