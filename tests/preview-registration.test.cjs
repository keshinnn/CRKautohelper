'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {verifyPreview}=require('../lib/preview-verifier.cjs');
const {selectNode}=require('../lib/node-selector.cjs');
const {map,intent,preview}=require('./fixtures.cjs');
test('registered preview must use one of this selection transaction source frames',()=>{
 const proof=selectNode(map('a',800),map(),intent,{nowMs:1000});
 for(const frame of [proof.frame,proof.previousFrame]){
  const o=preview();o.registrationSource={verified:true,imageSha256:frame.sha256,frameId:frame.id};
  assert.equal(verifyPreview(proof,o).kind,'match');
 }
 for(const source of [{verified:true,imageSha256:'b'.repeat(64),frameId:'a'},{verified:true,imageSha256:proof.frame.sha256,frameId:'other'},{verified:false,imageSha256:proof.frame.sha256,frameId:proof.frame.id}]){
  const o=preview();o.registrationSource=source;
  assert.deepEqual(verifyPreview(proof,o),{kind:'reject',code:'PREVIEW_REGISTRATION_SOURCE_MISMATCH'});
 }
});
