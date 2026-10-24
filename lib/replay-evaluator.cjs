'use strict';
function evaluateReplay(c,r,{stage='P4-A',scale=1}={}){
 if(!['P4-A','P4-B'].includes(stage)||!(stage==='P4-A'?[1]:[.75,1,1.25]).includes(scale))throw Error('MILESTONE_SCALE_INVALID');
 const proof=r.transaction?.proof,point=r.actions?.[0]?.clientPoint;
 let iou=0,margin=null,coordinatePassed=false;
 if(proof&&Array.isArray(c.expectedBox)&&c.expectedBox.length===4&&c.expectedBox.every(Number.isFinite)&&Array.isArray(c.clientBox)&&c.clientBox.length===4&&c.clientBox.every(Number.isFinite)&&c.expectedBox[2]>0&&c.expectedBox[3]>0&&c.clientBox[2]>0&&c.clientBox[3]>0&&point){
  const a=proof.box,b=c.expectedBox;
  const intersection=Math.max(0,Math.min(a[0]+a[2],b[0]+b[2])-Math.max(a[0],b[0]))*Math.max(0,Math.min(a[1]+a[3],b[1]+b[3])-Math.max(a[1],b[1]));
  iou=intersection/(a[2]*a[3]+b[2]*b[3]-intersection);
  const [x,y,w,h]=c.clientBox;
  margin=Math.min(point[0]-x,x+w-point[0],point[1]-y,y+h-point[1]);
  coordinatePassed=iou>=.90&&margin>=Math.max(3,Math.min(w,h)*.05);
 }
 const identityPassed=proof&&['zone','floor','column','event','mode'].every(k=>proof.intent[k]===c.intent?.[k]);
 const passed=c.reviewed===true&&r.passed===true&&r.state==='PREVIEW_CONFIRMED'&&r.nativeActions===0&&r.actions?.length===1&&coordinatePassed&&identityPassed===true;
 return {id:c.id,stage,source:c.source,scale,passed,g4Complete:false,state:r.state,
  transactionId:r.transaction?.transactionId??null,checks:{coordinatePassed,identityPassed:identityPassed===true,iou,minimumMarginPx:margin},
  nativeActions:r.nativeActions,virtualClicks:r.actions?.length??0};
}
module.exports={evaluateReplay};
