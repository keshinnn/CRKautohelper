const {test}=require('node:test'),assert=require('node:assert/strict');
const {resizeBox,resizePoint,validateGeometryCertificate}=require('../lib/geometry-contract.cjs');
test('real map adapter does not silently fall back to legacy rules for a tampered new certificate',()=>{
 const fs=require('node:fs'),{loadReplayFrames}=require('../lib/replay-case.cjs'),{adaptMap}=require('../lib/observer-adapter.cjs');
 const m=JSON.parse(fs.readFileSync('artifacts/p4c-aspect-endpoints-case25-analysis-01/manifest.json'));
 const s=loadReplayFrames(m.cases[0])[5],p=structuredClone(s.packet),f={...s.frame,png:s.png};
 assert.equal(adaptMap(f,p).stateVerified,true);
 p.mapReview.aspectRectification.coordinateContract={version:999};
 assert.equal(adaptMap(f,p).stateVerified,false);
});
test('source projection uses independent raster intervals and rejects rather than clamps',()=>{
 assert.deepEqual(resizePoint([480,270],[960,540],[1921,1081]),[960.5,540.5]);
 const b=resizeBox([0,352,20,1],[960,353],[1961,721]);assert.equal(b[1]+b[3],721);
 assert.throws(()=>resizeBox([0,352,20,1.000001],[960,353],[1961,721]));
});
test('capture geometry certificates cannot survive different source pixels or dimensions',()=>{
 const f={id:'a'.repeat(32),sha256:'b'.repeat(64),width:1961,height:721},p={binding:{pixelSha256:'c'.repeat(64)}};
 const g={version:1,spaces:{source:[1961,721],client:[1961,721],rectified:[1500,721],analysis:[960,461]},sourceCaptureFrameId:f.id,sourceImageSha256:f.sha256,pixelSha256:p.binding.pixelSha256,rounding:'endpoints_float64_raster_half_up',analysisRounding:'legacy_model_ties_even'};
 assert.equal(validateGeometryCertificate(g,f,p,[1500,721],[960,461]),true);
 for(const patch of [{width:1962},{sha256:'d'.repeat(64)},{id:'e'.repeat(32)}])assert.equal(validateGeometryCertificate(g,{...f,...patch},p,[1500,721],[960,461]),false);
 assert.equal(validateGeometryCertificate(g,f,p,[1501,721],[960,461]),false);
});
test('actual model raster tie cannot be declared as the other allowed half-pixel integer',()=>{
 const f={id:'a'.repeat(32),sha256:'b'.repeat(64),width:1920,height:721},p={binding:{pixelSha256:'c'.repeat(64)}};
 const g={version:1,spaces:{source:[1920,721],client:[1920,721],rectified:[1920,721],analysis:[960,361]},sourceCaptureFrameId:f.id,sourceImageSha256:f.sha256,pixelSha256:p.binding.pixelSha256,rounding:'endpoints_float64_raster_half_up',analysisRounding:'legacy_model_ties_even'};
 assert.equal(validateGeometryCertificate(g,f,p,[1920,721],[960,361]),false);
});
test('current observation envelope cannot downgrade a missing certificate to legacy tolerance',()=>{
 const fs=require('node:fs'),{loadReplayFrames}=require('../lib/replay-case.cjs'),{adaptMap}=require('../lib/observer-adapter.cjs');
 const m=JSON.parse(fs.readFileSync('artifacts/p4c-aspect-endpoints-case25-analysis-01/manifest.json')),s=loadReplayFrames(m.cases[0])[5];
 const p=structuredClone(s.packet);p.observerContractVersion=1;
 assert.equal(adaptMap({...s.frame,png:s.png,observerContractVersion:1},p).stateVerified,false);
});
