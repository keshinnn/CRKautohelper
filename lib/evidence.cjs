'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const digest=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
function locate(root,relative){const base=fs.realpathSync(root);if(typeof relative!=='string'||path.isAbsolute(relative)||relative.split(/[\\/]/).includes('..'))throw Error('invalid baseline path');const target=path.resolve(base,relative);if(!target.startsWith(base+path.sep))throw Error('baseline outside root');if(fs.existsSync(target)&&!fs.realpathSync(target).startsWith(base+path.sep))throw Error('baseline symlink outside root');return target;}
function snapshotFiles(root,paths){return {files:[...new Set(paths)].sort().map(p=>({path:p,sha256:digest(locate(root,p))}))};}
function compareSnapshot(root,snapshot){const changed=[],missing=[];for(const f of snapshot.files){const p=locate(root,f.path);if(!fs.existsSync(p))missing.push(f.path);else if(digest(p)!==f.sha256)changed.push(f.path);}return {unchanged:!changed.length&&!missing.length,changed,missing};}
// These checks validate evidence integrity, not the truth of annotations.
// P4 must separately freeze and review source intervals before running them.
function milestoneResult(stage, cases) {
 const required = {'P4-A':5, 'P4-B':15}[stage];
 if (!required) throw Error('not an intermediate milestone');
 let complete = Array.isArray(cases) && cases.length === required;
 try {
  const ids = new Set(), paths = new Set(), groups = new Map();
  for (const c of cases || []) {
   if (!c || typeof c.id !== 'string' || !c.id || ids.has(c.id) || c.passed !== true) throw Error('case invalid');
   ids.add(c.id);
   const s = c.source;
   if (!s || !/^[a-f0-9]{64}$/.test(s.videoSha256) || !Number.isFinite(s.startPtsMs) ||
       !Number.isFinite(s.endPtsMs) || s.startPtsMs < 0 || s.endPtsMs <= s.startPtsMs ||
       !(stage === 'P4-A' ? [1] : [.75,1,1.25]).includes(c.scale)) throw Error('source or scale invalid');
   const key = [s.videoSha256,s.startPtsMs,s.endPtsMs].join(':');
   if (!groups.has(key)) groups.set(key,{source:s,scales:[]});
   groups.get(key).scales.push(c.scale);
   const manifest = JSON.parse(fs.readFileSync(c.manifest,'utf8'));
   if (manifest.g4Complete !== false) throw Error('invalid manifest');
   const contents = {};
   for (const k of ['input','observation','overlay','events','result']) {
    const p = fs.realpathSync(c.artifacts[k]);
    if (paths.has(p) || !fs.statSync(p).isFile() || manifest.artifacts[k] !== c.artifacts[k] ||
        manifest.hashes[k] !== c.hashes[k] || digest(p) !== c.hashes[k]) throw Error('artifact binding invalid');
    paths.add(p);
    const raw = fs.readFileSync(p);
    if (['input','overlay'].includes(k)) {
     if (raw.length < 33 || raw.subarray(0,8).toString('hex') !== '89504e470d0a1a0a' ||
         raw.toString('ascii',12,16) !== 'IHDR' || raw.readUInt32BE(16) < 1 || raw.readUInt32BE(20) < 1) throw Error('PNG invalid');
    } else contents[k] = JSON.parse(raw.toString('utf8'));
   }
   const r = contents.result, events = contents.events, o = contents.observation;
   if (r.id !== c.id || r.stage !== stage || r.passed !== true || r.g4Complete !== false ||
       r.state !== 'PREVIEW_CONFIRMED' || r.scale !== c.scale ||
       JSON.stringify(r.source) !== JSON.stringify(s) || typeof r.transactionId !== 'string' ||
       !Array.isArray(events) || o.state !== 'PREVIEW' || o.verified !== true ||
       o.selectedNode?.verified !== true) throw Error('result invalid');
   const click = events.filter(e=>e.state === 'CLICK_SENT');
   const stable = events.filter(e=>e.state === 'PREVIEW_STABLE');
   const confirmed = events.filter(e=>e.state === 'PREVIEW_CONFIRMED');
   if (click.length !== 1 || !stable.length || confirmed.length !== 1 ||
       events.some(e=>e.transactionId !== r.transactionId || !Number.isFinite(e.atMs)) ||
       events.some((e,i)=>i && e.atMs < events[i-1].atMs) ||
       stable[0].atMs <= click[0].atMs || confirmed[0].atMs-stable[0].atMs < 200 ||
       confirmed[0].atMs-click[0].atMs >= 15000 || events.at(-1).state !== 'PREVIEW_CONFIRMED' ||
       events.some(e=>!['CLICK_PREPARED','CLICK_SENT','WAIT_PREVIEW','PREVIEW_STABLE','PREVIEW_CONFIRMED'].includes(e.state))) throw Error('transaction invalid');
  }
  if (ids.size !== required || groups.size !== 5) throw Error('wrong sample count');
  const list = [...groups.values()];
  for (let i=0;i<list.length;i++) {
   const g = list[i], scales = g.scales.sort((a,b)=>a-b);
   if (JSON.stringify(scales) !== JSON.stringify(stage === 'P4-A' ? [1] : [.75,1,1.25])) throw Error('scale coverage invalid');
   for (const h of list.slice(i+1)) {
    if (g.source.videoSha256 === h.source.videoSha256 &&
        Math.max(g.source.startPtsMs,h.source.startPtsMs) < Math.min(g.source.endPtsMs,h.source.endPtsMs)) throw Error('overlapping interaction');
   }
  }
 } catch { complete = false; }
 return {stage,passed:complete,g4Complete:false,cases:Array.isArray(cases)?cases.length:0};
}
module.exports={snapshotFiles,compareSnapshot,milestoneResult};
