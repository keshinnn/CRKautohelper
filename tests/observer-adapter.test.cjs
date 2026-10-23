const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {adaptMap,adaptPreview}=require('../lib/observer-adapter.cjs');
const base=process.env.CRK_V1_ROOT||'F:/CRK helper';
function source(name){const p=path.join(base,'data/reviewed-frames/20261024',name),png=fs.readFileSync(p+'.png'),packet=JSON.parse(fs.readFileSync(p+'-analysis.json'));return {packet,frame:{id:packet.binding.frameId,sha256:crypto.createHash('sha256').update(png).digest('hex'),atMs:1000,windowKey:'offline:fixture',geometryVersion:'g',width:packet.binding.width,height:packet.binding.height,origin:[0,0],png}};}
test('actual original GPG map packet retains byte binding and client node boxes',()=>{const {frame,packet}=source('gpg-native-map');const o=adaptMap(frame,packet);assert.equal(o.state,'MAP');assert.equal(o.anchorVerified,true);assert.equal(o.current.nodeId,'visible-1-4');const n=o.nodes.find(n=>n.id==='visible-1-4');assert.deepEqual(n.box,[1438.46,251.17,132.71,132.7]);assert.equal(n.floor,1);});
test('wrong PNG hash and out-of-client geometry reject instead of trusting packet',()=>{for(const mutate of [(f,p)=>f.sha256='b'.repeat(64),(f,p)=>p.binding.frameId='0'.repeat(32),(f,p)=>p.mapReview.nodes[0].box=[99999,0,100,100]]){const {frame,packet}=source('gpg-native-map');mutate(frame,packet);assert.throws(()=>adaptMap(frame,packet));}});
test('actual preview classification cannot invent selected-node identity',()=>{const {frame,packet}=source('gpg-node-preview');const o=adaptPreview(frame,packet);assert.equal(o.state,'PREVIEW');assert.equal(o.floor,1);assert.equal(o.selectedNode,null);assert.equal(o.identityStatus,'PREVIEW_IDENTITY_UNPROVEN');});
test('zone identity requires independent high confidence nonconflicting evidence',()=>{
 for(const mutate of [p=>p.progress.score=0,p=>p.progress.conflictingEvidence=true,p=>delete p.progress,p=>p.progress.displayedZone=null,p=>p.progress.score=NaN]){
  const {frame,packet}=source('gpg-native-map');mutate(packet);
  assert.equal(adaptMap(frame,packet).verified,false);
 }
});
