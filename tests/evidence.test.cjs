const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path'),crypto=require('node:crypto');
const {snapshotFiles,compareSnapshot,milestoneResult}=require('../lib/evidence.cjs');
test('baseline identifies changed bytes and missing files',t=>{const root=fs.mkdtempSync(path.join(os.tmpdir(),'crk-baseline-'));t.after(()=>fs.rmSync(root,{recursive:true,force:true}));fs.writeFileSync(path.join(root,'one'),'a');fs.writeFileSync(path.join(root,'two'),'b');const frozen=snapshotFiles(root,['one','two']);assert.equal(compareSnapshot(root,frozen).unchanged,true);fs.writeFileSync(path.join(root,'one'),'c');fs.unlinkSync(path.join(root,'two'));assert.deepEqual(compareSnapshot(root,frozen),{unchanged:false,changed:['one'],missing:['two']});});
test('baseline rejects traversal and absolute file paths',()=>{assert.throws(()=>snapshotFiles(__dirname,['../outside']));assert.throws(()=>snapshotFiles(__dirname,[__filename]));});
function cases(t,stage) {
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'crk-evidence-'));t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const png=fs.readFileSync(path.join(process.env.CRK_V1_ROOT||'F:/CRK helper','data/reviewed-frames/20261024/gpg-node-preview.png'));
 return Array.from({length:5},(_,i)=>(stage==='P4-A'?[1]:[.75,1,1.25]).map(scale=>{
  const id=i+'-'+scale,dir=path.join(root,id);fs.mkdirSync(dir);
  const source={videoSha256:'a'.repeat(64),startPtsMs:i*20000,endPtsMs:i*20000+10000};
  const artifacts={},hashes={};
  const values={input:png,overlay:png,observation:JSON.stringify({state:'PREVIEW',verified:true,selectedNode:{verified:true,zone:1,floor:1,column:4}}),
   events:JSON.stringify([{state:'CLICK_SENT',transactionId:id,atMs:1000},{state:'PREVIEW_STABLE',transactionId:id,atMs:1200},{state:'PREVIEW_CONFIRMED',transactionId:id,atMs:1400}]),
   result:JSON.stringify({id,stage,source,scale,passed:true,g4Complete:false,state:'PREVIEW_CONFIRMED',transactionId:id})};
  for(const [key,value] of Object.entries(values)){artifacts[key]=path.join(dir,key+(['input','overlay'].includes(key)?'.png':'.json'));fs.writeFileSync(artifacts[key],value);hashes[key]=crypto.createHash('sha256').update(value).digest('hex');}
  const manifest=path.join(dir,'manifest.json');fs.writeFileSync(manifest,JSON.stringify({artifacts,hashes,g4Complete:false}));
  return {id,passed:true,source,scale,artifacts,hashes,manifest};
 })).flat();
}
test('original and fixed milestones require five distinct interactions and designated scales',t=>{
 const a=cases(t,'P4-A'),b=cases(t,'P4-B');
 assert.equal(milestoneResult('P4-A',a).passed,true);assert.equal(milestoneResult('P4-A',a).g4Complete,false);
 assert.equal(milestoneResult('P4-B',b).passed,true);assert.equal(milestoneResult('P4-B',a).passed,false);
 assert.throws(()=>milestoneResult('G4',a));
});
test('fake shared files tampering missing manifests failed results and reused ranges reject milestone',t=>{
 const a=cases(t,'P4-A');
 for(const mutate of [
  c=>c[1].artifacts=c[0].artifacts,c=>c[1].source=c[0].source,c=>c[0].scale=.75,
  c=>delete c[0].manifest,c=>c[0].hashes.input='b'.repeat(64),
  c=>fs.appendFileSync(c[0].artifacts.observation,'tamper')
 ]) {const c=structuredClone(a);mutate(c);assert.equal(milestoneResult('P4-A',c).passed,false);}
 const b=cases(t,'P4-A');fs.writeFileSync(b[0].artifacts.result,JSON.stringify({passed:false}));assert.equal(milestoneResult('P4-A',b).passed,false);
 const fake=Array.from({length:5},(_,i)=>({id:String(i),passed:true,artifacts:Object.fromEntries(['input','overlay','observation','events','result'].map(k=>[k,__filename]))}));
 assert.equal(milestoneResult('P4-A',fake).passed,false);
});
