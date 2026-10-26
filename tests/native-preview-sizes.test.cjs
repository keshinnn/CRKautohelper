const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),{execFileSync}=require('node:child_process');
const {adaptPreview}=require('../lib/observer-adapter.cjs'),{loadReplayFrames}=require('../lib/replay-case.cjs');
let packet;function fixture(){const m=JSON.parse(fs.readFileSync('artifacts/p4c-random-development-60-run-18/dev-primary-zone4-floor2-col3-random-post-change/analysis/manifest.json')),s=loadReplayFrames(m.cases[0]).at(-1);packet??=execFileSync('F:/CRK helper/.venv/Scripts/python.exe',['-B','-c',"import sys,json;sys.path[:0]=['ml','tests','F:/CRK helper/ml'];from test_native_preview_sizes import NativePreviewSizeTests;from preview_identity import inspect_preview_identity;im,p=NativePreviewSizeTests().source();p['v2Preview']=inspect_preview_identity(im,p);print(json.dumps(p,ensure_ascii=True))"],{encoding:'utf8',maxBuffer:10000000});return {frame:{...s.frame,png:s.png},p:JSON.parse(packet)};}
test('actual native preview accepts an independently sized recovered ordinary node',()=>{const {frame,p}=fixture();assert.equal(adaptPreview(frame,p).verified,true);assert.ok(p.v2Preview.recoveredNodes.some(n=>n.iconPeerSizeEvidence));});
test('missing or changed original peer size evidence rejects the recovered preview identity',()=>{
 for(const mutate of [n=>delete n.iconPeerSizeEvidence,n=>n.iconPeerSizeEvidence.pixelSha256='a'.repeat(64),n=>n.iconPeerSizeEvidence.peerNodeId='unknown',n=>n.iconPeerSizeEvidence.peerSourceBox[0]++,n=>n.iconPeerSizeEvidence.candidateSize[0]++,n=>n.iconPeerSizeEvidence.peerMedianSize[0]++,n=>n.iconPeerSizeEvidence.peerScore=.47]){
  const {frame,p}=fixture();mutate(p.v2Preview.recoveredNodes.find(n=>n.iconPeerSizeEvidence));assert.notEqual(adaptPreview(frame,p).state,'PREVIEW');
 }
});
