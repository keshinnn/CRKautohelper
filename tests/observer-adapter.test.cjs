const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {adaptMap,adaptPreview}=require('../lib/observer-adapter.cjs');
const base=process.env.CRK_V1_ROOT||'F:/CRK helper';
function floorTwoSource(){
 const p=JSON.parse(fs.readFileSync(path.join(__dirname,'../artifacts/p4c-dev-floor2/action-evidence/0014530.packet.json'),'utf8'));
 const png=fs.readFileSync(path.join(__dirname,'../artifacts/p4c-dev-floor2/0014530.png'));
 return {p,f:{id:p.binding.frameId,sha256:p.binding.imageSha256,width:p.binding.width,height:p.binding.height,atMs:1000,windowKey:'offline:floor2',geometryVersion:'original',origin:[0,0],png}};
}
test('registered cropped-gate preview exposes only independently verified current pixels and its source',()=>{
 const p=JSON.parse(fs.readFileSync(path.join(__dirname,'../artifacts/p4c-registration-preview.packet.json'),'utf8'));
 const png=fs.readFileSync(path.join(__dirname,'../artifacts/p4c-registration-dev-source/0023745.png'));
 const f={id:p.binding.frameId,sha256:p.binding.imageSha256,width:p.binding.width,height:p.binding.height,atMs:791500,sourcePtsMs:791500,windowKey:'offline:dev',geometryVersion:'original',origin:[0,0],png};
 const o=adaptPreview(f,p);assert.equal(o.state,'PREVIEW');assert.equal(o.selectedNode.floor,3);assert.equal(o.selectedNode.column,1);
 assert.equal(o.registrationSource.imageSha256,p.v2TrackedMap.sourceImageSha256);
 p.v2Preview.recoveredMapReview.registrationEvidence.registration.verified=false;
 assert.notEqual(adaptPreview(f,p).state,'PREVIEW');
});
test('nonfinite registration consensus cannot become verified preview evidence',()=>{
 const p=JSON.parse(fs.readFileSync(path.join(__dirname,'../artifacts/p4c-registration-preview.packet.json'),'utf8'));
 const png=fs.readFileSync(path.join(__dirname,'../artifacts/p4c-registration-dev-source/0023745.png'));
 const f={id:p.binding.frameId,sha256:p.binding.imageSha256,width:p.binding.width,height:p.binding.height,atMs:791500,sourcePtsMs:791500,windowKey:'offline:dev',geometryVersion:'original',origin:[0,0],png};
 p.v2TrackedMap.registration.inliers=NaN;
 const proof=structuredClone(Object.fromEntries(Object.entries(p.v2TrackedMap).filter(([k])=>k!=='mapReview')));
 p.v2TrackedMap.mapReview.registrationEvidence=proof;
 p.v2Preview.recoveredMapReview=structuredClone(p.v2TrackedMap.mapReview);
 assert.notEqual(adaptPreview(f,p).state,'PREVIEW');
});
test('independent completed pixels establish a unique completed path and orange availability',()=>{
 const {p,f}=floorTwoSource(),o=adaptMap(f,p);
 assert.equal(o.current?.nodeId,'visible-1-3');assert.equal(o.current.inProgress,false);
 assert.equal(o.nodes.find(n=>n.id==='visible-2-3').available,true);
 assert.equal(o.nodes.find(n=>n.id==='visible-1-4').available,false);
});
test('missing or mismatched independent pixels never authorize availability or a completed path',()=>{
 for(const mutate of [p=>delete p.v2MapActions,p=>p.v2MapActions.pixelSha256='a'.repeat(64),p=>p.v2MapActions.nodes['visible-2-3'].box[0]+=1]){
  const {p,f}=floorTwoSource();mutate(p);const o=adaptMap(f,p);
  assert.equal(o.nodes.find(n=>n.id==='visible-2-3').available,false);
 }
 const {p,f}=floorTwoSource();p.mapReview.edges=[];assert.equal(adaptMap(f,p).current,null);
});
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
test('independent original-video pixel proof can identify preview despite V1 MAP classification',()=>{
 const file=path.join(__dirname,'../artifacts/p4a-first-preview-v2/observation.json');
 // Packet generated by the read-only Python pixel recognizer, never by intent.
 const p=JSON.parse(fs.readFileSync(file,'utf8')).rawPacket;
 const png=fs.readFileSync(path.join(__dirname,'../artifacts/p4a-native/0002550.png'));
 const f={id:p.binding.frameId,sha256:p.binding.imageSha256,width:p.binding.width,height:p.binding.height,atMs:1000,windowKey:'offline:video',geometryVersion:'original',origin:[0,0],png};
 const o=adaptPreview(f,p);assert.equal(o.state,'PREVIEW');assert.equal(o.selectedNode.column,2);assert.equal(o.selectedNode.floor,1);assert.equal(o.controlsVerified,true);
});

test('a claimed preview with missing map evidence rejects without crashing',()=>{
 const file=path.join(__dirname,'../artifacts/p4a-first-preview-v2/observation.json');
 const p=JSON.parse(fs.readFileSync(file,'utf8')).rawPacket;
 const png=fs.readFileSync(path.join(__dirname,'../artifacts/p4a-native/0002550.png'));
 const f={id:p.binding.frameId,sha256:p.binding.imageSha256,width:p.binding.width,height:p.binding.height,atMs:1000,windowKey:'offline:video',geometryVersion:'original',origin:[0,0],png};
 p.mapReview=null;p.v2Preview.recoveredMapReview=null;
 assert.notEqual(adaptPreview(f,p).state,'PREVIEW');
});
test('original video maps with strong lattice and zone evidence do not depend on one title OCR confidence',()=>{
 for(const [zone,name] of [[1,'0002532'],[2,'0012336']]){
  const dir=path.join(__dirname,'../artifacts/p4a-original-source/zone-'+zone),p=JSON.parse(fs.readFileSync(path.join(dir,name+'.packet.json'),'utf8')),png=fs.readFileSync(path.join(dir,name+'.png'));
  const f={id:p.binding.frameId,sha256:p.binding.imageSha256,width:p.binding.width,height:p.binding.height,atMs:1000,windowKey:'offline:video',geometryVersion:'original',origin:[0,0],png};
  assert.equal(adaptMap(f,p).verified,true);
  p.flow.confidence=.1;assert.equal(adaptMap(f,p).verified,false);
 }
});
test('pixel recovery of omitted selected node remains bound to observed lattice',()=>{
 const dir=path.join(__dirname,'../artifacts/p4a-original-source/zone-8'),p=JSON.parse(fs.readFileSync(path.join(dir,'0064890.v2.packet.json'),'utf8')),png=fs.readFileSync(path.join(dir,'0064890.png'));
 const f={id:p.binding.frameId,sha256:p.binding.imageSha256,width:p.binding.width,height:p.binding.height,atMs:1000,windowKey:'offline:video',geometryVersion:'original',origin:[0,0],png};
 assert.equal(adaptPreview(f,p).selectedNode?.column,4);
 p.v2Preview.recoveredNodes[0].column=1;assert.notEqual(adaptPreview(f,p).state,'PREVIEW');
});
test('a raw UNKNOWN is accepted as preview only with newly recovered independent map pixels',()=>{
 const p=JSON.parse(fs.readFileSync(path.join(__dirname,'../artifacts/p4b-unknown-recheck.packet.json'),'utf8'));
 const png=fs.readFileSync(path.join(__dirname,'../artifacts/p4b-fixed-source/zone-3-first-battle-scale-1.25/0020226.png'));
 const f={id:p.binding.frameId,sha256:p.binding.imageSha256,width:p.binding.width,height:p.binding.height,atMs:1000,windowKey:'offline:video',geometryVersion:'fixed-1.25',origin:[0,0],png};
 assert.equal(p.flow.state,'UNKNOWN');assert.equal(adaptPreview(f,p).selectedNode.column,2);
 p.v2Preview.recoveredMapReview.frameId='wrong';assert.equal(adaptPreview(f,p).state,'UNKNOWN');
});
test('zero title confidence with complete pixel lattice permits waiting but never a new click proof',()=>{
 const dir=path.join(__dirname,'../artifacts/p4b-analysis-02/zone-2-first-battle-scale-1.25');
 const p=JSON.parse(fs.readFileSync(path.join(dir,'0012329.packet.json'),'utf8'));
 const png=fs.readFileSync(path.join(__dirname,'../artifacts/p4b-fixed-source/zone-2-first-battle-scale-1.25/0012329.png'));
 const f={id:p.binding.frameId,sha256:p.binding.imageSha256,width:p.binding.width,height:p.binding.height,atMs:1000,windowKey:'offline:video',geometryVersion:'fixed-1.25',origin:[0,0],png};
 assert.equal(p.flow.confidence,0);const o=adaptMap(f,p);assert.equal(o.stateVerified,true);assert.equal(o.verified,false);
});
