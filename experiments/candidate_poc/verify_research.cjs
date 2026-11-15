'use strict';
// A2 isolated research verifier. No production imports, private authorities,
// game input, model execution, or template-score substitution.
const fs=require('node:fs'),crypto=require('node:crypto'),zlib=require('node:zlib');
const {performance}=require('node:perf_hooks');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const deny=()=>{throw Error('RESEARCH_EVIDENCE_REJECTED');};
const capabilities=()=>({select:false,confirm:false,dispatch:false});
const table=Array.from({length:256},(_,n)=>{for(let k=0;k<8;k++)n=n&1?0xedb88320^(n>>>1):n>>>1;return n>>>0;});
function crc32(data){let c=0xffffffff;for(const b of data)c=table[(c^b)&255]^(c>>>8);return (c^0xffffffff)>>>0;}
function decodeRgbPng(png){
 if(png.length>32*1024*1024||png.subarray(0,8).toString('hex')!=='89504e470d0a1a0a')deny();
 let offset=8,w,h,ended=false,idat=[],seenIdat=false,idatEnded=false;
 while(offset+12<=png.length){
  const length=png.readUInt32BE(offset),type=png.toString('ascii',offset+4,offset+8),end=offset+12+length;
  if(end>png.length)deny();
  const data=png.subarray(offset+8,end-4);
  if(crc32(png.subarray(offset+4,end-4))!==png.readUInt32BE(end-4))deny();
  if(type==='IHDR'){
   if(offset!==8||length!==13||w)deny();
   w=data.readUInt32BE(0);h=data.readUInt32BE(4);
   if(!w||!h||w*h>8*1024*1024||data[8]!==8||data[9]!==2||data[10]||data[11]||data[12])deny();
  }else if(type==='IDAT'){
   if(!w||idatEnded)deny();seenIdat=true;idat.push(data);
  }else if(type==='IEND'){
   if(length||!seenIdat||end!==png.length)deny();ended=true;break;
  }else{
   if(seenIdat)idatEnded=true;
   if(!w||['acTL','fcTL','fdAT'].includes(type)||type[0]===type[0].toUpperCase())deny();
  }
  offset=end;
 }
 if(!ended)deny();
 const stride=w*3,expected=h*(stride+1),raw=zlib.inflateSync(Buffer.concat(idat),{maxOutputLength:expected});
 if(raw.length!==expected)deny();
 const rgb=Buffer.alloc(w*h*3);
 const paeth=(a,b,c)=>{const p=a+b-c,da=Math.abs(p-a),db=Math.abs(p-b),dc=Math.abs(p-c);return da<=db&&da<=dc?a:db<=dc?b:c;};
 for(let y=0;y<h;y++){
  const filter=raw[y*(stride+1)];if(filter>4)deny();
  for(let x=0;x<stride;x++){
   const at=y*stride+x,a=x>=3?rgb[at-3]:0,b=y?rgb[at-stride]:0,c=y&&x>=3?rgb[at-stride-3]:0;
   const pred=filter===0?0:filter===1?a:filter===2?b:filter===3?Math.floor((a+b)/2):paeth(a,b,c);
   rgb[at]=(raw[y*(stride+1)+1+x]+pred)&255;
  }
 }
 return {w,h,rgb};
}
function verify(png,e,ctx){
 const started=performance.now();
 try{
  if(e.schema!=='candidate-evidence/v2-research-geometry-1'||e.researchOnly!==true)deny();
  if(sha(png)!==ctx.imageSha256||e.sourceImageSha256!==ctx.imageSha256)deny();
  for(const key of ['sourceKey','geometryEpoch','frameToken'])if(typeof ctx[key]!=='string'||!ctx[key]||e[key]!==ctx[key])deny();
  if(!Number.isFinite(ctx.atMs)||e.atMs!==ctx.atMs||!Number.isFinite(ctx.nowMs)||ctx.nowMs<ctx.atMs||ctx.nowMs-ctx.atMs>2500)deny();
  const {w,h,rgb}=decodeRgbPng(png);
  if(JSON.stringify(e.sourceSize)!==JSON.stringify([w,h])||sha(rgb)!==e.sourceRgbSha256)deny();
  const box=e.sourceBox;
  if(!Array.isArray(box)||box.length!==4||!box.every(Number.isFinite)||box[0]<0||box[1]<0||box[2]<=0||box[3]<=0||box[0]+box[2]>w||box[1]+box[3]>h)deny();
  const ratio=Math.min(640/w,640/h),rw=Math.floor(w*ratio+.5),rh=Math.floor(h*ratio+.5),left=Math.floor((640-rw)/2),top=Math.floor((640-rh)/2),sx=rw/w,sy=rh/h;
  if(rw<1||rh<1)deny();
  const matrix=[[sx,0,left],[0,sy,top],[0,0,1]],tensor=[box[0]*sx+left,box[1]*sy+top,box[2]*sx,box[3]*sy];
  if(!Array.isArray(e.sourceToTensor)||e.sourceToTensor.length!==3||!e.sourceToTensor.every((r,i)=>Array.isArray(r)&&r.length===3&&r.every((x,j)=>Number.isFinite(x)&&Math.abs(x-matrix[i][j])<=1e-9)))deny();
  if(!Array.isArray(e.tensorBox)||e.tensorBox.length!==4||!e.tensorBox.every((x,i)=>Number.isFinite(x)&&Math.abs(x-tensor[i])<=1e-9))deny();
  if(!Array.isArray(e.edgeSamples)||e.edgeSamples.length!==64)deny();
  const [x,y,bw,bh]=box;
  for(let side=0;side<4;side++)for(let i=0;i<16;i++){
   const t=(i+.5)/16,[px,py]=[[x+bw*t,y],[x+bw*t,y+bh],[x,y+bh*t],[x+bw,y+bh*t]][side];
   const ix=Math.floor(px),iy=Math.floor(py),axis=side<2?'y':'x',sample=e.edgeSamples[side*16+i];
   if(ix<1||iy<1||ix>=w-1||iy>=h-1)deny();
   const a=axis==='y'?((iy-1)*w+ix)*3:(iy*w+ix-1)*3,b=axis==='y'?((iy+1)*w+ix)*3:(iy*w+ix+1)*3;
   let gradient=0;for(let j=0;j<3;j++)gradient+=Math.abs(rgb[a+j]-rgb[b+j]);
   if(sample?.x!==ix||sample?.y!==iy||sample?.axis!==axis||sample?.gradient!==gradient)deny();
  }
  return {status:'RESEARCH_GEOMETRY_ONLY',geometryChecked:true,boundaryMeasurementsReproduced:true,
          outerBoundaryVerified:false,mapLocationVerified:false,registrationVerified:false,identityVerified:false,
          capabilities:capabilities(),ms:performance.now()-started};
 }catch(error){return {status:'REJECTED',reason:error.message,capabilities:capabilities(),ms:performance.now()-started};}
}
if(require.main===module){
 try{console.log(JSON.stringify(verify(fs.readFileSync(process.argv[2]),JSON.parse(fs.readFileSync(process.argv[3],'utf8')),JSON.parse(fs.readFileSync(process.argv[4],'utf8')))));}
 catch(error){console.log(JSON.stringify({status:'REJECTED',reason:error.message,capabilities:capabilities()}));}
}
module.exports={verify,decodeRgbPng};
