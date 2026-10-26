"""Bounded original-pixel heal proposals; no column, floor, or intent input."""
import copy,hashlib,math
import cv2
import numpy as np

def heal_node_candidates(image,initial,inverse,root,binding,normal_size,normal_pixel,analysis_size,analysis_pixel):
 from map_action_evidence import _green
 from map_vision import map_templates
 peers=[n for n in initial.get('nodes',[]) if n.get('type') not in ('exit','boss') and .48<=n.get('score',0)<=1]
 if len(peers)<4:return []
 boxes=[[n['box'][0]*inverse,n['box'][1],n['box'][2]*inverse,n['box'][3]] for n in peers]
 mw,mh=np.median([b[2:] for b in boxes],axis=0);sizes=sorted(set(tuple(b[2:]) for b in boxes if .9*mw<=b[2]<=1.1*mw and .9*mh<=b[3]<=1.1*mh))
 templates=map_templates(root/'data/map');found=[];fx,fy=analysis_size[0]/normal_size[0],analysis_size[1]/normal_size[1]
 for x,y,w,h,area in cv2.connectedComponentsWithStats(_green(np.asarray(image)))[2][1:]:
  if not (.45*mw<w<.8*mw and .45*mh<h<.8*mh and area>w*h*.35):continue
  cx,cy=float(x+w/2),float(y+h/2)
  if any(math.hypot(cx-n['center'][0]*inverse,cy-n['center'][1])<min(mw,mh)*.25 for n in initial['nodes']):continue
  best=None
  for bw,bh in sizes:
   radius=max(1,round(min(bw,bh)*.02))
   for dx in range(-radius,radius+1):
    for dy in range(-radius,radius+1):
     box=[cx-bw/2+dx,cy-bh/2+dy,bw,bh]
     if min(box[:2])<0 or box[0]+bw>image.width or box[1]+bh>image.height:continue
     q=np.asarray(image.crop((box[0],box[1],box[0]+bw,box[1]+bh)).resize((58,58)))[12:46,12:46];gray=cv2.cvtColor(q,cv2.COLOR_RGB2GRAY);scores=[]
     for name,_,_,ref,refg in templates:
      value=.7*float(cv2.matchTemplate(gray,refg,cv2.TM_CCOEFF_NORMED)[0,0])+.3*(1-np.abs(q.astype(float)-ref).mean()/255);scores.append((float(value),name))
     heal=max(s for s in scores if s[1] in ('node-heal','node-b-heal'));other=max(s for s in scores if s[1] not in ('node-heal','node-b-heal'))
     if heal[0]<.9 or heal[0]-other[0]<.08 or best is not None and heal[0]<=best['iconScore']:continue
     best={'method':'same_frame_green_component_original_heal_rgb_candidate','actionsExecuted':False,
      'sourceImageSha256':binding['imageSha256'],'pixelSha256':binding['pixelSha256'],'sourceCaptureFrameId':binding['frameId'],'sourceSize':list(image.size),
      'rectifiedInputSize':list(normal_size),'rectifiedPixelSha256':normal_pixel,'analysisSize':list(analysis_size),'analysisPixelSha256':analysis_pixel,
      'greenBox':[int(x),int(y),int(w),int(h)],'greenArea':int(area),'sourceBox':box,'peerSourceBoxes':copy.deepcopy(boxes),'peerMedianSize':[float(mw),float(mh)],
      'alignmentPx':[dx,dy],'alignmentRadius':radius,'iconScore':heal[0],'matchedTemplate':heal[1],'otherFamilyScore':other[0],'otherFamilyTemplate':other[1],
      'templateImageSha256':hashlib.sha256((root/'data/map'/str(heal[1]+'.png')).read_bytes()).hexdigest(),'analysisSizeForIcon':[58,58],'innerBox':[12,12,34,34]}
  if best:
   b=best['sourceBox'];box=[b[0]/inverse,b[1],b[2]/inverse,b[3]];center=[box[0]+box[2]/2,box[1]+box[3]/2]
   best.update(originalAnalysisBox=box,originalAnalysisCenter=center,injectedAnalysisBox=[box[0]*fx,box[1]*fy,box[2]*fx,box[3]*fy])
   proposal={'box':best['injectedAnalysisBox'],'center':[center[0]*fx,center[1]*fy],'score':best['iconScore'],'template':best['matchedTemplate']+'.png','scoreMethod':'original_source_heal_template_rgb','healProposal':best}
   duplicate=next((i for i,n in enumerate(found) if math.hypot(n['center'][0]-proposal['center'][0],n['center'][1]-proposal['center'][1])<min(proposal['box'][2:])*.25),None)
   if duplicate is None:found.append(proposal)
   elif found[duplicate]['score']<proposal['score']:found[duplicate]=proposal
 return found
