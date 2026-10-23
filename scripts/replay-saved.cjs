'use strict';
// Offline P3 diagnostic entry. Reads previously bound PNG/recognizer packets.
// It neither launches a recognizer service nor exposes any native input backend.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {runReplay}=require('../lib/replay-runner.cjs');
const {adaptMap,adaptPreview}=require('../lib/observer-adapter.cjs');
const {writeCaseArtifacts}=require('../lib/artifact-writer.cjs');

async function main(){
 const [manifestFile,output]=process.argv.slice(2);
 if(!manifestFile||!output)throw Error('saved sequence manifest and new output directory required');
 const manifest=JSON.parse(fs.readFileSync(manifestFile,'utf8'));
 const frames=manifest.frames.map(entry=>{
  const png=fs.readFileSync(entry.image),packet=JSON.parse(fs.readFileSync(entry.packet,'utf8'));
  if(png.length<33||png.subarray(0,8).toString('hex')!=='89504e470d0a1a0a')throw Error('PNG_REQUIRED');
  return {png,packet,frame:{id:packet.binding.frameId,
   sha256:crypto.createHash('sha256').update(png).digest('hex'),width:png.readUInt32BE(16),height:png.readUInt32BE(20),
   atMs:entry.atMs,sourcePtsMs:entry.sourcePtsMs,windowKey:'offline:saved-sequence',
   geometryVersion:entry.geometryVersion,origin:[0,0]}};
 });
 const consumed=[];
 const result=await runReplay({frames,intent:manifest.intent,gate:manifest.gate,observe:async source=>{
  const bound={...source.frame,png:source.png};
  const o=source.packet.flow.state==='MAP'?adaptMap(bound,source.packet):adaptPreview(bound,source.packet);
  consumed.push({source,observation:o});return o;
 }});
 fs.mkdirSync(output);
 const bundles=[];
 for(const [index,{source,observation}] of consumed.entries()){
  const dir=path.join(output,'frame-'+String(index).padStart(4,'0'));
  const overlays=(observation.nodes||[]).map(n=>({box:n.box,label:n.id}));
  if(result.transaction?.action.frameId===source.frame.id)overlays.push({point:result.transaction.action.clientPoint,label:'virtual click'});
  bundles.push(writeCaseArtifacts(dir,{png:source.png,observation:{...observation,rawPacket:source.packet},overlays,
   events:result.transaction?.events||[],result:{passed:false,purpose:'P3 saved-sequence diagnostic; not a P4 acceptance case',g4Complete:false,state:result.state}}));
 }
 const report={...result,purpose:'P3 saved-sequence diagnostic',p4Accepted:false,sourceManifest:manifest,bundles};
 fs.writeFileSync(path.join(output,'run.json'),JSON.stringify(report,null,2),{flag:'wx'});
 console.log(JSON.stringify({state:result.state,frames:consumed.length,virtualClicks:result.actions.length,nativeActions:0,p4Accepted:false,g4Complete:false,report:path.join(output,'run.json')}));
}
main().catch(error=>{console.error(error.stack);process.exitCode=1;});
