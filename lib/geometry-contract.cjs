'use strict';
// Independent consumer implementation; never imports the Python producer.
const {isDeepStrictEqual:eq}=require('node:util');
const size=s=>Array.isArray(s)&&s.length===2&&s.every(v=>Number.isInteger(v)&&v>0);
function analysisRaster(source){
 if(!size(source))throw Error('COORDINATE_INVALID');
 const value=source[1]*(960/source[0]),floor=Math.floor(value);
 return [960,value-floor===.5?(floor%2===0?floor:floor+1):Math.round(value)];
}
function nativeGeometryEvidence(frame,pixelSha256){
 const sourceSize=[frame.width,frame.height];
 return {sourceSize,rectifiedPixelSha256:pixelSha256,modelAnalysisSize:analysisRaster(sourceSize)};
}
function resizePoint(p,source,target){
 if(!size(source)||!size(target)||!Array.isArray(p)||p.length!==2||p.some((v,i)=>!Number.isFinite(v)||v<0||v>source[i]))throw Error('COORDINATE_INVALID');
 return p.map((v,i)=>v*target[i]/source[i]);
}
function resizeBox(b,source,target){
 if(!Array.isArray(b)||b.length!==4||!b.every(Number.isFinite)||Math.min(...b.slice(2))<=0)throw Error('COORDINATE_INVALID');
 const a=resizePoint(b.slice(0,2),source,target),z=resizePoint([b[0]+b[2],b[1]+b[3]],source,target);
 return [...a,z[0]-a[0],z[1]-a[1]];
}
function validateGeometryCertificate(g,f,p,rectified,analysis){
 const source=[f.width,f.height];
 return !!(g&&g.version===1&&g.rounding==='endpoints_float64_raster_half_up'&&g.analysisRounding==='legacy_model_ties_even'&&
  [source,rectified,analysis].every(size)&&rectified[1]===f.height&&
  eq(analysis,analysisRaster(rectified))&&
  eq(g.spaces,{source,client:source,rectified,analysis})&&
  g.sourceCaptureFrameId===f.id&&g.sourceImageSha256===f.sha256&&g.pixelSha256===p.binding.pixelSha256);
}
module.exports={resizeBox,resizePoint,validateGeometryCertificate,analysisRaster,nativeGeometryEvidence};
