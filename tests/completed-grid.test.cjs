'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),{execFileSync}=require('node:child_process'),fs=require('node:fs'),path=require('node:path');
const {adaptMap}=require('../lib/observer-adapter.cjs');let cached;
function sample(){
 if(!cached)cached=JSON.parse(execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',"import sys,json;sys.path[:0]=['ml','tests','F:/CRK helper/ml'];from test_completed_integer_grid import CompletedIntegerGridTests;from map_action_evidence import inspect_map_actions;im,p=CompletedIntegerGridTests().sample();p['v2MapActions']=inspect_map_actions(im,p);print(json.dumps(p))"],{cwd:require('node:path').resolve(__dirname,'..'),encoding:'utf8',windowsHide:true}));
 const p=structuredClone(cached),audit=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../artifacts/exploration-20261102-01/audit-summary.json'),'utf8'));
 const entry=audit.rows.find(r=>r.number===60),tx=JSON.parse(fs.readFileSync(entry.transaction,'utf8'));
 return {p,f:{...tx.observations.at(-1).frame,png:fs.readFileSync(entry.criticalImage)}};
}
test('current node from actual bounded odd-grid check proof independently validates',()=>{
 const {p,f}=sample(),o=adaptMap(f,p);assert.equal(o.verified,true);assert.ok(o.current);assert.equal(o.current.nodeId,'visible-1-2');
});
test('current path rejects weakened duplicate or out-of-range neutral check evidence',()=>{
 for(const alter of [e=>{e.neutralOverlayCheck=null;},e=>{e.neutralOverlayCheck.maskIoUs[1]=.79;},e=>{e.neutralOverlayCheck.saturationLevels=[80,80];},e=>{e.neutralOverlayCheck.alignmentPx=[3,1];}]){
  const {p,f}=sample(),e=p.v2MapActions.nodes['visible-1-2'];assert.ok(e.neutralOverlayCheck);alter(e);assert.equal(adaptMap(f,p).current,null);
 }
});
