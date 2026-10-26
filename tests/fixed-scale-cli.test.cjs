const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
test('fixed-scale milestone cannot discard the external observer contract version',()=>{
 const root=path.resolve(__dirname,'..'),base=path.join(root,'artifacts'),temp=fs.mkdtempSync(path.join(base,'fixed-schema-control-'));
 try{
  const m=JSON.parse(fs.readFileSync(path.join(base,'convergence-20261026/fixed15-final-02/manifest.json')));
  m.analysis.observerContractVersion=1;
  for(const [i,f] of m.cases[0].frames.slice(0,2).entries()){
   const p=JSON.parse(fs.readFileSync(f.packet));delete p.observerContractVersion;
   if(p.aspectRectification)delete p.aspectRectification.coordinateContract;
   const packet=path.join(temp,'downgraded-'+i+'.json');fs.writeFileSync(packet,JSON.stringify(p));f.packet=packet;
  }
  const file=path.join(temp,'source.json'),out=path.join(temp,'result');fs.writeFileSync(file,JSON.stringify(m));
  const r=spawnSync(process.execPath,['scripts/accept-replay.cjs',file,'data/p4a/cases.json',out],{cwd:root,encoding:'utf8',windowsHide:true,timeout:240000});
  assert.equal(r.status,1,r.stderr||r.stdout);
  const first=m.cases[0].id,transaction=JSON.parse(fs.readFileSync(path.join(out,first,'transaction.json')));
  assert.equal(transaction.passed,false);assert.equal(transaction.actions.length,0);assert.equal(transaction.nativeActions,0);
  assert.equal(JSON.parse(fs.readFileSync(path.join(out,'report.json'))).results[0].passed,false);
 }finally{assert(fs.realpathSync(temp).startsWith(fs.realpathSync(base)+path.sep));fs.rmSync(temp,{recursive:true,force:true});}
});
