const clone=x=>structuredClone(x);
function frame(id='b',atMs=1000){return {id,sha256:'a'.repeat(64),atMs,windowKey:'gpg:123:10',geometryVersion:'g1',width:1000,height:700,origin:[-1920,100]};}
function map(id='b',atMs=1000){return {frame:frame(id,atMs),state:'MAP',verified:true,zone:1,anchorVerified:true,nodes:[{id:'gate',floor:0,column:null,type:'exit',box:[300,20,100,100],score:.99,completed:false},{id:'target',floor:1,column:4,type:'battle',box:[400,200,100,100],score:.95,completed:false},{id:'other',floor:1,column:3,type:'battle',box:[200,200,100,100],score:.95,completed:false}],edges:[{from:'gate',to:'target',pixelSupport:.96}],current:null};}
const intent={zone:1,floor:1,column:4,event:'battle',mode:'select'};
function preview(id='c',atMs=1200){return {frame:frame(id,atMs),state:'PREVIEW',verified:true,zone:1,floor:1,event:'battle',controlsVerified:true,selectedNode:{verified:true,zone:1,floor:1,column:4}};}
module.exports={clone,frame,map,intent,preview};
