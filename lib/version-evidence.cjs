'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{execFileSync}=require('node:child_process');
function captureCodeVersion(root){
 const files=[];
 function walk(relative){
  const full=path.join(root,relative);if(!fs.existsSync(full))return;
  for(const entry of fs.readdirSync(full,{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))){
   const name=path.join(relative,entry.name);
   if(entry.isDirectory())walk(name);
   else if(/\.(cjs|js|py|json)$/.test(name))files.push({path:name.replaceAll('\\','/'),sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,name))).digest('hex')});
  }
 }
 for(const folder of ['lib','ml','scripts','data'])walk(folder);
 let commit=null,dirty=null;
 try{commit=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8',windowsHide:true,stdio:['ignore','pipe','ignore']}).trim();dirty=execFileSync('git',['status','--porcelain'],{cwd:root,encoding:'utf8',windowsHide:true}).trim().length>0;}catch{}
 return {commit,dirty,files};
}
module.exports={captureCodeVersion};
