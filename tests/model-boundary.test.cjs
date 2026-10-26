const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),{execFileSync}=require('node:child_process');
const {loadReplayFrames}=require('../lib/replay-case.cjs'),{adaptMap}=require('../lib/observer-adapter.cjs');
test('actual completed geometry binds the original detector raster before decimal rounding',()=>{
 const file='artifacts/convergence-20261026/random39-final-01/manifest.json',m=JSON.parse(fs.readFileSync(file)),c=m.cases.find(c=>c.id==='dev-primary-zone4-floor2-col3-random-pre-change'),s=loadReplayFrames(c,m.videoSha256,1)[5];
 const code="import json,sys,pathlib;sys.path[:0]=['ml','F:/CRK helper/ml'];from PIL import Image;from map_aspect import recover_map_aspect;from map_action_evidence import inspect_map_actions;m=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'));c=next(c for c in m['cases'] if c['id']=='dev-primary-zone4-floor2-col3-random-pre-change');f=c['frames'][5];p=json.loads(pathlib.Path(f['packet']).read_text(encoding='utf-8'));p['mapReview']=p.pop('v2OriginalMapReview',p['mapReview']);im=Image.open(f['image']).convert('RGB');p['mapReview']=recover_map_aspect(im,p);p['v2MapActions']=inspect_map_actions(im,p);print(json.dumps(p))";
 const p=JSON.parse(execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',code,file],{encoding:'utf8',maxBuffer:12*1024*1024,windowsHide:true})),frame={...s.frame,png:s.png};
 assert.equal(adaptMap(frame,p).verified,true);
 const altered=structuredClone(p),n=altered.mapReview.nodes.find(n=>n.completedRefinement);
 assert.ok(n);n.detectorGeometry.box[0]+=.001;
 assert.equal(adaptMap(frame,altered).verified,false);
});
