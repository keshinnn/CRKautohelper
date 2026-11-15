'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{spawnSync}=require('child_process');
const {decodeRgbPng}=require('./verify_research.cjs');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const norm=t=>t.replace(/\s/g,'').replaceAll('发','發').replaceAll('获','獲').replaceAll('奖','獎').replaceAll('励','勵');
function verifyContextPixels(sources,output,mode){
 const files=sources.map((s,i)=>{const f=path.join(output,mode+'-source-'+i+'.png');fs.writeFileSync(f,s.png,{flag:'wx'});return f;});
 const file=path.join(output,mode+'-independent-ocr.json');
 const child=spawnSync('F:/CRK helper/.venv/Scripts/python.exe',['-B',path.join(__dirname,'result_pixels.py'),file,...files],{encoding:'utf8',timeout:60000,env:{...process.env,PYTHONUTF8:'1'}});
 if(child.status!==0)throw Error('RIFT_CONTEXT_REREAD_FAILED');
 const evidence=JSON.parse(fs.readFileSync(file,'utf8'));
 if(evidence.length!==sources.length)throw Error('RIFT_CONTEXT_COUNT_INVALID');
 for(let i=0;i<sources.length;i++){
  const s=sources[i],r=evidence[i],im=decodeRgbPng(s.png);
  if(sha(s.png)!==s.frame.sha256||r.imageSha256!==s.frame.sha256||r.pixelSha256!==sha(im.rgb))throw Error('RIFT_CONTEXT_SOURCE_CHANGED');
  const rows=r.evidence.filter(x=>x.score>=.9&&x.score<=1);
  const required=mode==='rift'?[t=>t==='可能發生的事件',t=>/^[+]?恢復餅乾活力$/.test(t)]:
   [t=>/^\d{2}:\d{2}$/.test(t),t=>t==='進入',t=>t==='套用效果',t=>/^可獲得(?:獎勵)?$/.test(t)];
  for(const predicate of required){const matched=rows.filter(x=>predicate(norm(x.text)));if(matched.length!==1)throw Error('RIFT_CONTEXT_LABEL_UNPROVEN');
   const box=matched[0].box;if(!Array.isArray(box)||box.length!==4||!box.every(p=>p.length===2&&p.every(Number.isFinite)&&p[0]>im.w/2&&p[0]<=im.w&&p[1]>=0&&p[1]<=im.h))throw Error('RIFT_CONTEXT_PANEL_UNPROVEN');
  }
  if(mode==='converted'&&rows.filter(x=>x.score>=.95&&norm(x.text)==='進行中').length!==1)throw Error('RIFT_CONTEXT_PROGRESS_UNPROVEN');
 }
 return {researchOnly:true,formalAuthority:false,mode,images:sources.map(s=>s.frame.sha256),method:'independent_native_pixel_context_reread'};
}
module.exports={verifyContextPixels};
