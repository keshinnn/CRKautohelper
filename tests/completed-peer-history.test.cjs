const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const {loadReplayFrames}=require('../lib/replay-case.cjs'),{adaptPreview}=require('../lib/observer-adapter.cjs');
function fixture(){const m=JSON.parse(fs.readFileSync('artifacts/p4c-random-development-60-run-17/dev-primary-zone4-floor2-col3-random-fixed/analysis/manifest.json')),s=loadReplayFrames(m.cases[0]).find(s=>s.packet.binding.frameId==='f75b76488fadaa22152df26cdc19f0ac');return {frame:{...s.frame,png:s.png},p:s.packet};}
test('actual completed proof retains its measured peer before independent orange geometry refinement',()=>{const {frame,p}=fixture();const o=adaptPreview(frame,p);assert.equal(o.verified,true);assert.equal(o.state,'PREVIEW');assert.equal(o.selectedNode.floor,2);assert.equal(o.selectedNode.column,3);});
test('missing changed or unbound historical peer cannot authorize completed geometry',()=>{
 for(const mutate of [(n,peer)=>delete peer.orangeRefinement,(n,peer)=>peer.orangeRefinement.originalAnalysisBox[0]++,(n,peer)=>peer.orangeRefinement.pixelSha256='a'.repeat(64),(n,peer)=>n.checkProposal.peerSourceBox[0]++,(n,peer)=>n.checkProposal.iconScore=.89]){
  const {frame,p}=fixture();for(const m of [p.mapReview,p.v2TrackedMap?.mapReview,p.v2Preview?.recoveredMapReview].filter(Boolean)){const n=m.nodes.find(n=>n.checkProposal);assert.ok(n);mutate(n,m.nodes.find(x=>x.id===n.checkProposal.peerNodeId));}
  assert.equal(adaptPreview(frame,p).verified,false);
 }
});
