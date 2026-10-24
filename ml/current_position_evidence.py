"""Current-node evidence from the same frame, without intent or stored floors."""
import re
import cv2
import numpy as np


def inspect_in_progress(rgb,packet,node_actions):
    m=packet.get('mapReview') or {};progress=packet.get('progress') or {}
    if m.get('absoluteFloorKnown') is not True or m.get('floorAnchorSource')!='visible_top_gate' or len([n for n in m.get('nodes',[]) if n.get('type')=='exit'])!=1 or progress.get('conflictingEvidence') is not False or progress.get('score',0)<.9 or type(progress.get('displayedZone')) is not int or not 1<=progress['displayedZone']<=10:return None
    labels=[r for r in packet.get('evidence',[]) if re.sub(r'\s+','',r.get('text',''))=='進行中' and r.get('score',0)>=.95]
    if len(labels)!=1:return None
    points=np.asarray(labels[0].get('box'),dtype=float)
    if points.shape!=(4,2) or not np.isfinite(points).all():return None
    lx,ly=points.min(0);rx,by=points.max(0);height,width=rgb.shape[:2]
    if min(lx,ly)<0 or rx>width or by>height:return None
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    yellow=((hsv[:,:,0]>=22)&(hsv[:,:,0]<=38)&(hsv[:,:,1]>130)&(hsv[:,:,2]>130)).astype('uint8')
    found=[]
    for n in m.get('nodes',[]):
        e=node_actions.get(n['id']) or {}
        if e.get('available') is not True or e.get('completed') is not False or type(n.get('floor')) is not int or n['floor']<1:continue
        x,y,w,h=n['box'];cx,cy=x+w/2,y+h/2
        if abs((lx+rx)/2-cx)>w*.45 or not -h*.35<=ly-y-h<=h*.35:continue
        l,t=max(0,int(x-w*.15)),max(0,int(y-h*.15));r,b=min(width,int(x+w*1.15)+1),min(height,int(y+h*1.15)+1)
        yy,xx=np.mgrid[t:b,l:r];radius=np.maximum(abs((xx-cx)/(w/2)),abs((yy-cy)/(h/2)))
        ring=(radius>.8)&(radius<1.15);local=yellow[t:b,l:r]
        coverage=float(local[ring].mean());quads=[]
        for a,z in [(xx<cx,yy<cy),(xx>=cx,yy<cy),(xx<cx,yy>=cy),(xx>=cx,yy>=cy)]:
            mask=ring&a&z;quads.append(float(local[mask].mean()) if mask.any() else 0.)
        if coverage<.08 or min(quads)<.04:continue
        top=max(0,int(y-h*.4));left=max(0,int(x-w*.1));right=min(width,int(x+w*1.1));bottom=int(y)
        contours,_=cv2.findContours(yellow[top:bottom,left:right],cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        triangles=[]
        for contour in contours:
            bx,ty,tw,th=cv2.boundingRect(contour)
            if not w*.15<=tw<=w*.45 or not h*.1<=th<=h*.3 or abs(left+bx+tw/2-cx)>w*.15:continue
            hull=cv2.convexHull(contour);filled=np.zeros((th,tw),dtype='uint8')
            cv2.fillConvexPoly(filled,hull-np.array([[[bx,ty]]]),1)
            band=max(1,th//3);upper=float(filled[:band].sum(axis=1).mean());lower=float(filled[-band:].sum(axis=1).mean())
            if upper<=0 or lower>upper*.8 or cv2.contourArea(contour)<tw*th*.1:continue
            triangles.append({'box':[left+bx,top+ty,tw,th],'upperWidth':upper,'lowerWidth':lower})
        if len(triangles)!=1:continue
        found.append({'verified':True,'inProgress':True,'method':'unique_progress_label_yellow_ring_down_triangle',
            'nodeId':n['id'],'zone':progress.get('displayedZone'),'floor':n['floor'],'column':n.get('column'),'box':list(n['box']),
            'labelBox':[float(lx),float(ly),float(rx-lx),float(by-ly)],'labelScore':labels[0]['score'],
            'ringCoverage':coverage,'quadrants':quads,'triangle':triangles[0]})
    return found[0] if len(found)==1 else None
