"""Pixel-bound availability and unique completed path; no intended target input."""
import hashlib,os
from functools import lru_cache
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

def _green(rgb):
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    return ((hsv[:,:,0]>35)&(hsv[:,:,0]<85)&(hsv[:,:,1]>150)&(hsv[:,:,2]>130)).astype('uint8')

@lru_cache(maxsize=1)
def _check_masks():
    folder=Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper'))/'data/map'
    masks=[]
    for name in ['node-done.png','node-b-done.png']:
        with Image.open(folder/name) as im:
            masks.append(_green(np.array(im.convert('RGB').resize((58,58)))[12:46,12:46]))
    return masks

def _neutral_overlay_check(q):
    """Two agreeing saturation levels must retain the same reviewed shape."""
    hsv=cv2.cvtColor(q,cv2.COLOR_RGB2HSV);levels=[]
    for saturation in [60,80,100,120]:
        mask=((hsv[:,:,0]>35)&(hsv[:,:,0]<85)&(hsv[:,:,1]>saturation)&(hsv[:,:,2]>130)).astype('uint8')
        if .04<float(mask.mean())<.30:levels.append((saturation,mask))
    best=None
    for reference in _check_masks():
        for dx in [-2,0,2]:
            for dy in [-2,0,2]:
                shifted=cv2.warpAffine(reference,np.float32([[1,0,dx],[0,1,dy]]),(34,34));scores=[]
                for saturation,mask in levels:
                    union=np.logical_or(shifted,mask).sum()
                    if union:scores.append((float(np.logical_and(shifted,mask).sum()/union),saturation))
                scores.sort(reverse=True)
                if len(scores)>=2 and scores[1][0]>=.8 and (best is None or scores[1][0]>best['score']):
                    best={'score':scores[1][0],'alignmentPx':[dx,dy],'saturationLevels':[x[1] for x in scores[:2]],'maskIoUs':[x[0] for x in scores[:2]],'minimumTemplateIoU':.8,'method':'same_check_shape_at_two_neutral_overlay_color_levels'}
    return best


def inspect_map_actions(image,packet):
    unknown={'verified':False,'nodes':{},'current':None,'actionsExecuted':False}
    rgb=np.array(image.convert('RGB'));digest=hashlib.sha256(rgb.tobytes()).hexdigest()
    m=packet.get('mapReview') or {}
    if packet.get('binding',{}).get('pixelSha256')!=digest or m.get('frameId')!=digest[:20]:return unknown
    identities=[n.get('id') for n in m.get('nodes',[])]
    if not identities or any(not isinstance(n,str) or not n for n in identities) or len(set(identities))!=len(identities):return unknown
    nodes={}
    for n in m.get('nodes',[]):
        box=n.get('box',[])
        if len(box)!=4 or not all(np.isfinite(box)):return unknown
        x,y,w,h=box
        if x<0 or y<0 or w<=0 or h<=0 or x+w>image.width or y+h>image.height:return unknown
        q=np.array(image.crop((x,y,x+w,y+h)).convert('RGB').resize((58,58)))[12:46,12:46]
        hsv=cv2.cvtColor(q,cv2.COLOR_RGB2HSV);orange=float(((hsv[:,:,0]>5)&(hsv[:,:,0]<35)&(hsv[:,:,1]>130)&(hsv[:,:,2]>130)).mean())
        check=_green(q);green=float(check.mean());score=0.
        if .04<green<.30:
            for mask in _check_masks():
                for dx in [-2,0,2]:
                    for dy in [-2,0,2]:
                        shifted=cv2.warpAffine(mask,np.float32([[1,0,dx],[0,1,dy]]),(34,34))
                        union=np.logical_or(shifted,check).sum()
                        if union:score=max(score,float(np.logical_and(shifted,check).sum()/union))
        original_score=score;overlay=None
        if score<.8:
            overlay=_neutral_overlay_check(q)
            if overlay:score=overlay['score']
        completed=score>=.8
        nodes[n['id']]={'verified':True,'available':n.get('type')=='battle' and orange>=.2 and not completed,'completed':completed,'orangeCoverage':orange,'checkMaskIoU':score,'originalCheckMaskIoU':original_score,'neutralOverlayCheck':overlay,'box':list(box)}
    result={'verified':True,'method':'original_pixel_orange_fill_and_check_mask_unique_path','pixelSha256':digest,'nodes':nodes,'current':None,'actionsExecuted':False}
    if m.get('absoluteFloorKnown') is not True or m.get('floorAnchorSource')!='visible_top_gate':return result
    from current_position_evidence import inspect_in_progress
    current=inspect_in_progress(rgb,packet,nodes)
    if current:
        result['current']=current
        return result
    gates=[n for n in m.get('nodes',[]) if n.get('type')=='exit']
    done=sorted([n for n in m.get('nodes',[]) if nodes[n['id']]['completed']],key=lambda n:n.get('floor') or -1)
    if len(gates)!=1 or not done:return result
    previous=gates[0];path=[previous['id']]
    for floor,node in enumerate(done,1):
        if node.get('floor')!=floor:return result
        edges=[e for e in m.get('edges',[]) if e.get('from')==previous['id'] and e.get('to')==node['id'] and isinstance(e.get('pixel_support'),(int,float)) and .85<=e['pixel_support']<=1]
        if len(edges)!=1:return result
        path.append(node['id']);previous=node
    result['current']={'verified':True,'nodeId':previous['id'],'completedPath':path,'inProgress':False}
    return result
