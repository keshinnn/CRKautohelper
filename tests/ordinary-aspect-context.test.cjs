'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{test}=require('node:test');
const {adaptMap}=require('../lib/observer-adapter.cjs');
const {readPreviewWaitAuthority}=require('../lib/preview-context.cjs');
const {verifyPreview}=require('../lib/preview-verifier.cjs');
const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'../artifacts/development-20261027-medium-01/high-resume-01/ordinary-aspect-fixtures.json'))).rows;
function frame(row){const f=row.frame,b=row.packet.binding;return {id:b.frameId,sha256:b.imageSha256,atMs:f.atMs,sourcePtsMs:f.sourcePtsMs,width:b.width,height:b.height,geometryVersion:f.geometryVersion,windowKey:'offline:original-video',origin:[0,0],observerContractVersion:1,png:fs.readFileSync(f.image)};}
test('actual rectified ordinary crops grant only privately bound wait permission',()=>{
 for(const row of fixture){
  const o=adaptMap(frame(row),structuredClone(row.packet));
  assert.equal(o.state,'PREVIEW_PENDING');assert.equal(readPreviewWaitAuthority(o),true);
  assert.deepEqual(o.capabilities,{wait:true,select:false,confirm:false});assert.equal(o.verified,false);
  assert.equal(o.selectedNode,undefined);assert.equal(verifyPreview({intent:{zone:5}},o).kind,'wait');
 }
});
test('missing changed or stale aspect proof and altered crop cannot grant wait authority',()=>{
 const row=fixture[0];
 const mutations=[
  p=>delete p.v2PreviewContext.ordinaryEvidence.positionEvidence,
  p=>p.v2PreviewContext.ordinaryEvidence.positionEvidence.horizontalScale=1.2,
  p=>p.v2PreviewContext.ordinaryEvidence.positionEvidence.sourceImageSha256='f'.repeat(64),
  p=>p.v2PreviewContext.ordinaryEvidence.cropBox[0]++,
  p=>p.mapReview.aspectRectification.inverseMatrix[0][0]=1.2,
  p=>p.mapReview.aspectRectification.coordinateContract.spaces.rectified[0]++,
 ];
 for(const mutate of mutations){const p=structuredClone(row.packet);mutate(p);const o=adaptMap(frame(row),p);assert.notEqual(o.state,'PREVIEW_PENDING');assert.equal(readPreviewWaitAuthority(o),false);}
});
