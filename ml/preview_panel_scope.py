"""Bound a right ordinary-preview panel from actual text and enabled pixels."""
import copy,hashlib,math,re
import cv2
import numpy as np

def _box(reading):
 points=reading.get('box')
 if not isinstance(points,list) or len(points)!=4 or any(not isinstance(p,list) or len(p)!=2 or any(not isinstance(v,(int,float)) or not math.isfinite(v) for v in p) for p in points):return None
 xs,ys=zip(*points);return [min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)]

def ordinary_preview_panel_scope(image,packet):
 rgb=image.convert('RGB');binding=packet.get('binding') or {};digest=hashlib.sha256(rgb.tobytes()).hexdigest()
 if (binding.get('pixelSha256')!=digest or [binding.get('width'),binding.get('height')]!=list(rgb.size)
  or not re.fullmatch('[a-f0-9]{64}',binding.get('imageSha256','')) or not re.fullmatch('[a-f0-9]{32}',binding.get('frameId',''))
  or packet.get('actionsExecuted') is not False):return None
 groups=[[],[],[]]
 for r in packet.get('evidence',[]):
  box=_box(r);score=r.get('score',0);text=''.join(r.get('text','').split())
  if not box or not isinstance(score,(int,float)) or not math.isfinite(score) or not 0<=score<=1 or box[0]<=rgb.width*.5 or min(box[2:])<=0:continue
  if text.casefold() in ('進入','enter') and score>=.95:groups[0].append(r)
  if text=='03:00' and score>=.95:groups[1].append(r)
  if '普通' in text and score>=.65:groups[2].append(r)
 if any(len(g)!=1 for g in groups):return None
 enter,timer,ordinary=[g[0] for g in groups];eb,tb,ob=map(_box,[enter,timer,ordinary])
 if not ob[1]<tb[1]<eb[1] or eb[1]-tb[1]<rgb.height*.15:return None
 hsv=cv2.cvtColor(np.asarray(rgb),cv2.COLOR_RGB2HSV);green=(hsv[:,:,0]>30)&(hsv[:,:,0]<85)&(hsv[:,:,1]>100)&(hsv[:,:,2]>150)
 x,y,w,h=eb;left,top=max(0,int(x-w*2)),max(0,int(y-h));right,bottom=min(rgb.width,int(x+w*3)),min(rgb.height,int(y+h*2))
 mask=green[top:bottom,left:right].astype('uint8');buttons=[]
 for bx,by,bw,bh,area in cv2.connectedComponentsWithStats(mask)[2][1:]:
  if bw>w*2 and bh>h*1.3 and area/(bw*bh)>.45 and left+bx<x and left+bx+bw>x+w and top+by<y and top+by+bh>y+h:
   buttons.append(([int(left+bx),int(top+by),int(bw),int(bh)],int(area)))
 if len(buttons)!=1:return None
 button,area=buttons[0]
 if button[0]<=rgb.width*.5:return None
 bx,by,bw,bh=button
 return {'method':'same_frame_ordinary_preview_control_panel_scope','actionsExecuted':False,
  'pixelSha256':digest,'sourceImageSha256':binding['imageSha256'],'sourceCaptureFrameId':binding['frameId'],'sourceSize':list(rgb.size),
  'enterEvidence':copy.deepcopy(enter),'timerEvidence':copy.deepcopy(timer),'ordinaryEvidence':copy.deepcopy(ordinary),
  'enterBox':eb,'timerBox':tb,'ordinaryBox':ob,'greenButtonBox':button,'greenArea':area,
  'greenMaskSha256':hashlib.sha256(green[by:by+bh,bx:bx+bw].astype('uint8').tobytes()).hexdigest(),'cutX':bx}
