"""Missing completed-node proposals from original check pixels and peer sizes."""
import hashlib,io,math
import cv2
import numpy as np
from PIL import Image


def completed_node_candidates(image,initial,inverse,root,binding,normal_size,normal_pixel,analysis_size,analysis_pixel):
    from map_action_evidence import _green,_check_masks,_neutral_overlay_check
    from map_vision import map_templates
    peers=[n for n in initial.get('nodes',[]) if n.get('type') not in ('exit','boss') and isinstance(n.get('id'),str) and .48<=n.get('score',0)<=1]
    if len(peers)<4:return []
    mw,mh=np.median([[n['box'][2]*inverse,n['box'][3]] for n in peers],axis=0)
    sizes={}
    for peer in sorted(peers,key=lambda n:(n.get('type')=='battle',n['id'])):
        x,y,w,h=peer['box'];box=[x*inverse,y,w*inverse,h]
        if .9*mw<=box[2]<=1.1*mw and .9*mh<=box[3]<=1.1*mh:sizes.setdefault(tuple(box[2:]),(peer['id'],box))
    templates=map_templates(root/'data/map');components=cv2.connectedComponentsWithStats(_green(np.asarray(image)))[2][1:];found=[]
    fx,fy=analysis_size[0]/normal_size[0],analysis_size[1]/normal_size[1]
    for filename in ['node-done.png','node-b-done.png']:
        raw=(root/'data/map'/filename).read_bytes();original=Image.open(io.BytesIO(raw)).convert('RGB');reference=original.resize((58,58))
        refs=[r for r in cv2.connectedComponentsWithStats(_green(np.asarray(reference)))[2][1:]
            if r[4]>=5 and 58*.15<r[0]+r[2]/2<58*.85 and 58*.15<r[1]+r[3]/2<58*.85]
        for rx,ry,rw,rh,reference_area in refs:
            for x,y,w,h,area in components:
                if area<5 or not .85*mw<=58*w/rw<=1.15*mw or not .85*mh<=58*h/rh<=1.15*mh:continue
                cx,cy=float(x+w/2),float(y+h/2)
                if any(math.hypot(cx-n['center'][0]*inverse,cy-n['center'][1])<min(mw,mh)*.25 for n in initial['nodes']):continue
                best=None
                for (bw,bh),(peer_id,peer_box) in sorted(sizes.items()):
                    bx,by=cx-(rx+rw/2)*bw/58,cy-(ry+rh/2)*bh/58;radius=max(1,round(min(bw,bh)*.02))
                    for dx in range(-radius,radius+1):
                        for dy in range(-radius,radius+1):
                            box=[bx+dx,by+dy,bw,bh]
                            if min(box[:2])<0 or box[0]+bw>image.width or box[1]+bh>image.height:continue
                            q=np.asarray(image.crop((box[0],box[1],box[0]+bw,box[1]+bh)).resize((58,58)))[12:46,12:46];gray=cv2.cvtColor(q,cv2.COLOR_RGB2GRAY);scores=[]
                            for name,_,_,ref,refg in templates:
                                score=.7*float(cv2.matchTemplate(gray,refg,cv2.TM_CCOEFF_NORMED)[0,0])+.3*(1-np.abs(q.astype(float)-ref).mean()/255);scores.append((float(score),name))
                            done=max(s for s in scores if s[1] in ('node-done','node-b-done'));other=max(s for s in scores if s[1] not in ('node-done','node-b-done'))
                            if done[0]<.9 or done[0]-other[0]<.08:continue
                            check=_green(q);coverage=float(check.mean());check_score=0.
                            if not .04<coverage<.30:continue
                            for mask in _check_masks():
                                for mx in [-2,0,2]:
                                    for my in [-2,0,2]:
                                        shifted=cv2.warpAffine(mask,np.float32([[1,0,mx],[0,1,my]]),(34,34));union=np.logical_or(shifted,check).sum()
                                        if union:check_score=max(check_score,float(np.logical_and(shifted,check).sum()/union))
                            original_check_score=check_score;overlay=None
                            if check_score<.8:
                                overlay=_neutral_overlay_check(q)
                                if overlay:check_score=overlay['score']
                            if check_score<.8 or best is not None and done[0]<=best['iconScore']:continue
                            best={'method':'same_frame_green_check_original_done_rgb_candidate','sourceImageSha256':binding['imageSha256'],
                                'pixelSha256':binding['pixelSha256'],'sourceCaptureFrameId':binding['frameId'],'sourceSize':list(image.size),
                                'rectifiedInputSize':list(normal_size),'rectifiedPixelSha256':normal_pixel,'analysisSize':list(analysis_size),'analysisPixelSha256':analysis_pixel,
                                'sourceCheckBox':[int(x),int(y),int(w),int(h)],'sourceCheckArea':int(area),
                                'templateFile':filename,'templateImageSha256':hashlib.sha256(raw).hexdigest(),'originalTemplateSize':list(original.size),
                                'templateSize':[58,58],'templateCheckBox':[int(rx),int(ry),int(rw),int(rh)],'templateCheckArea':int(reference_area),
                                'peerNodeId':peer_id,'peerSourceBox':peer_box,'peerMedianSize':[float(mw),float(mh)],
                                'alignmentPx':[dx,dy],'alignmentRadius':radius,'sourceBox':box,'iconScore':done[0],'matchedTemplate':done[1],
                                'otherFamilyScore':other[0],'otherFamilyTemplate':other[1],'greenCoverage':coverage,
                                'checkMaskIoU':check_score,'originalCheckMaskIoU':original_check_score,'neutralOverlayCheck':overlay,'actionsExecuted':False}
                if best:
                    box=best['sourceBox'];normalized=[box[0]/inverse,box[1],box[2]/inverse,box[3]]
                    best['originalAnalysisBox']=normalized;best['originalAnalysisCenter']=[normalized[0]+normalized[2]/2,normalized[1]+normalized[3]/2]
                    best['injectedAnalysisBox']=[normalized[0]*fx,normalized[1]*fy,normalized[2]*fx,normalized[3]*fy]
                    proposal={'box':best['injectedAnalysisBox'],'center':[best['originalAnalysisCenter'][0]*fx,best['originalAnalysisCenter'][1]*fy],
                        'score':best['iconScore'],'template':best['matchedTemplate']+'.png','scoreMethod':'original_source_done_template_rgb','checkProposal':best}
                    duplicate=next((i for i,n in enumerate(found) if math.hypot(n['center'][0]-proposal['center'][0],n['center'][1]-proposal['center'][1])<min(proposal['box'][2:])*.25),None)
                    if duplicate is None:found.append(proposal)
                    elif found[duplicate]['score']<proposal['score']:found[duplicate]=proposal
    return found
