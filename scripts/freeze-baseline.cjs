'use strict';
const fs=require('node:fs'),path=require('node:path'),{snapshotFiles}=require('../lib/evidence.cjs');
const root=process.argv[2],out=path.resolve(__dirname,'../artifacts');if(!root)throw Error('V1 root required');
const files=[];function walk(relative){const p=path.join(root,relative);if(!fs.existsSync(p))return;for(const item of fs.readdirSync(p,{withFileTypes:true})){const r=path.join(relative,item.name);if(item.isDirectory())walk(r);else if(/\.(cjs|js|py|json|png|npz|pt|pth|onnx)$/.test(r))files.push(r);}}
for(const d of ['lib','ml','web','scripts','models','data/flow','data/map'])walk(d);
for(const f of ['server.cjs','package.json','docs/artifact-integrity.json','data/video-validation/buAwy1zf2LI/manifest.json'])if(fs.existsSync(path.join(root,f)))files.push(f);
fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'baseline.json'),JSON.stringify({root,...snapshotFiles(root,files)},null,2));
const ranges=[[84,104],[410,430],[475,495],[535,555],[895,915]];fs.writeFileSync(path.join(out,'video-candidates.json'),JSON.stringify({source:'buAwy1zf2LI',purpose:'P4-A candidates, not reviewed or accepted',candidates:ranges.map((r,i)=>({id:`original-${i+1}`,startSeconds:r[0],endSeconds:r[1],reviewed:false,passed:false}))},null,2));console.log(JSON.stringify({baselineFiles:files.length,candidates:5,reviewed:0,g4Complete:false}));
