const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
test('committed development CLI confirms a real native control with complete evidence and no G4 promotion',()=>{
 const root=path.resolve(__dirname,'..'),artifacts=fs.realpathSync(path.join(root,'artifacts'));
 const temp=fs.mkdtempSync(path.join(artifacts,'crk-development-cli-')),out=path.join(temp,'result'),source=path.join(artifacts,'p4c-native-random-pilot-control-source-01.json');
 try{
  const r=spawnSync(process.execPath,[path.join(root,'scripts/replay-development.cjs'),source,out],{cwd:root,encoding:'utf8',windowsHide:true,timeout:120000});
  assert.equal(r.status,0,r.stderr);const report=JSON.parse(fs.readFileSync(path.join(out,'report.json')));
  assert.equal(report.passed,true);assert.equal(report.results.length,1);assert.equal(report.g4Complete,false);assert.equal(report.nativeActions,0);
  assert.equal(report.sourceManifestSha256,crypto.createHash('sha256').update(fs.readFileSync(source)).digest('hex'));
  assert.equal(report.results[0].state,'PREVIEW_CONFIRMED');
  const bundle=path.join(out,report.results[0].id,'summary');
  for(const name of ['input.png','observation.json','overlay.png','events.json','result.json','manifest.json'])assert(fs.statSync(path.join(bundle,name)).size>0);
 }finally{assert(fs.realpathSync(temp).startsWith(artifacts+path.sep));fs.rmSync(temp,{recursive:true,force:true});}
});
