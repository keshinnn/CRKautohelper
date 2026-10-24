const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os');
let captureCodeVersion;try{({captureCodeVersion}=require('../lib/version-evidence.cjs'));}catch{captureCodeVersion=()=>({files:[]});}
test('working source bytes are frozen even when they differ from a commit',t=>{
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'crk-code-version-'));t.after(()=>fs.rmSync(root,{recursive:true,force:true}));fs.mkdirSync(path.join(root,'lib'));fs.writeFileSync(path.join(root,'lib/core.cjs'),'one');
 const a=captureCodeVersion(root);assert.equal(a.files.length,1);assert.match(a.files[0].sha256,/^[a-f0-9]{64}$/);
 fs.writeFileSync(path.join(root,'lib/core.cjs'),'two');const b=captureCodeVersion(root);
 assert.notEqual(a.files[0].sha256,b.files[0].sha256);
});
