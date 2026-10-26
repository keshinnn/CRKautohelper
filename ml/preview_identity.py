"""Independent selected-node pixels and ordinary battle preview controls.

No route, pending transaction, annotated coordinates or intent are accepted.
"""
import hashlib
import io
import re
import os
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

from preview_context import inspect_preview_context, _box, _timer_original_crop, _english_ordinary_crop

def _orange_reference_extent(root):
    raw=(root/'data/map/node-orange.png').read_bytes()
    image=Image.open(io.BytesIO(raw)).convert('RGB');hsv=cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2HSV)
    mask=cv2.inRange(hsv,(5,130,130),(35,255,255))
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);matches=[]
    for contour in contours:
        area=cv2.contourArea(contour);hull=cv2.contourArea(cv2.convexHull(contour))
        if area<=20 or hull<=0 or area/hull<=.9:continue
        x,y,w,h=cv2.boundingRect(contour)
        if abs(x+w/2-image.width/2)>image.width*.1 or abs(y+h/2-image.height/2)>image.height*.1:continue
        matches.append([x,y,w,h])
    if len(matches)!=1:return None
    return {'templateImageSha256':hashlib.sha256(raw).hexdigest(),'templateSize':list(image.size),'circleBox':matches[0]}



def inspect_preview_identity(image,packet,context=None):
    unknown={'verified':False,'reason':'PREVIEW_IDENTITY_UNPROVEN'}
    a=np.asarray(image.convert('RGB'));height,width=a.shape[:2]
    digest=hashlib.sha256(a.tobytes()).hexdigest();m=packet.get('mapReview') or {};progress=packet.get('progress') or {};recovered_map=None
    if packet.get('binding',{}).get('pixelSha256')!=digest:return unknown
    tracked=packet.get('v2TrackedMap') or {};registration=tracked.get('registration') or {};tracking_valid=False
    if (tracked.get('verified') is True and tracked.get('previewOnly') is True and tracked.get('actionsExecuted') is False
        and tracked.get('method')=='fresh_same_zone_direct_map_pixel_registration' and tracked.get('pixelSha256')==digest
        and tracked.get('zone')==progress.get('displayedZone') and registration.get('verified') is True
        and registration.get('method')=='map_pixel_translation_and_node_consensus'
        and registration.get('pixelSha256')==[tracked.get('sourcePixelSha256'),digest]
        and len(registration.get('pairs',[]))>=5
        and 0<tracked.get('atMs',0)-tracked.get('sourceAtMs',0)<=2500):
        candidate=tracked.get('mapReview') or {};proof={k:v for k,v in tracked.items() if k!='mapReview'}
        if candidate.get('registrationEvidence')==proof and candidate.get('floorAnchorSource')=='verified_preview_pixel_registration':
            m=candidate;recovered_map=m;tracking_valid=True
    context=inspect_preview_context(image,packet) if context is None else context
    if context.get('verified') is not True:return unknown
    if not m:
        # A weak MAP title classifier must not prevent independent preview
        # evidence from being evaluated. Recover geometry only for a bounded
        # ordinary-preview context; never turn arbitrary UNKNOWN into MAP.
        if packet.get('flow',{}).get('state') not in ['UNKNOWN','NODE_BATTLE']:return unknown
        root=Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper'));module_path=str(root/'ml')
        if module_path not in sys.path:sys.path.insert(0,module_path)
        from map_vision import inspect_map
        m=inspect_map(image,root/'data/map',read_header=False)
        if len(m.get('columns') or [])!=4 or len(m.get('nodes',[]))<6 or len([e for e in m.get('edges',[]) if e.get('pixel_support',0)>=.85])<3:return unknown
        recovered_map=m
    if m.get('frameId')!=digest[:20] or m.get('absoluteFloorKnown') is not True or not (m.get('floorAnchorSource')=='visible_top_gate' or tracking_valid):return unknown
    ordinary_evidence=context['ordinaryEvidence'];tb=context['timerBox'];ob=context['ordinaryBox'];buttons=[context['enterBox']];timers=[context['timerEvidence']]
    hsv=cv2.cvtColor(a,cv2.COLOR_RGB2HSV)
    green=(hsv[:,:,0]>30)&(hsv[:,:,0]<85)&(hsv[:,:,1]>100)&(hsv[:,:,2]>150)
    selected=[];nodes=list(m.get('nodes',[]));recovered=[]
    # A selected outline can disrupt the generic outer-hex edge detector.
    # Recover only a visible green component aligned to the existing lattice,
    # with an independently matching ordinary-battle icon, never from intent.
    columns=m.get('columns',[]);gates=[n for n in nodes if n.get('type')=='exit']
    normal=[n for n in nodes if n.get('type')!='exit' and len(n.get('box',[]))==4]
    if len(columns)==4 and len(gates)==1 and normal:
        spacing=float(np.median(np.diff(columns)));nw=float(np.median([n['box'][2] for n in normal]));nh=float(np.median([n['box'][3] for n in normal]))
        # Rectification changes X only. Source-space column spacing therefore
        # differs from vertical row spacing; derive Y from the same-frame proof.
        aspect=m.get('aspectRectification');vertical_spacing=spacing
        if aspect:
            if (aspect.get('verified') is not True or aspect.get('pixelSha256')!=digest
                    or aspect.get('sourceImageSha256')!=packet['binding'].get('imageSha256')
                    or aspect.get('sourceSize')!=[width,height]):return unknown
            rectified=aspect.get('rectifiedInputSize',[])
            if len(rectified)!=2 or rectified[1]!=height or not 0<rectified[0]:return unknown
            vertical_spacing=spacing*rectified[0]/width
        gate=gates[0]['box'];gate_y=gate[1]+gate[3]/2
        for bx,by,bw,bh,area in cv2.connectedComponentsWithStats(green.astype('uint8'))[2][1:]:
            if not nw*.7<bw<nw*1.3 or not nh*.7<bh<nh*1.3:continue
            cx,cy=float(bx+bw/2),float(by+bh/2);column=int(np.argmin(abs(np.asarray(columns)-cx)))+1;floor=round((cy-gate_y)/vertical_spacing)
            if not 1<=floor<=31 or abs(columns[column-1]-cx)>spacing*.08 or abs(cy-gate_y-floor*vertical_spacing)>vertical_spacing*.08:continue
            if any(n.get('floor')==floor and n.get('column')==column for n in nodes):continue
            box=[cx-nw/2,cy-nh/2,nw,nh]
            if min(box[:2])<0 or box[0]+nw>width or box[1]+nh>height:continue
            root=Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper'));module_path=str(root/'ml')
            if module_path not in sys.path:sys.path.insert(0,module_path)
            from map_vision import map_templates,classify_node
            candidate={'box':box};types=classify_node(image,candidate,root/'data/map')
            if types['type']!='battle' or types['completed']:continue
            templates=map_templates(root/'data/map');best=None;radius=max(1,round(min(nw,nh)*.02))
            sizes=[(nw,nh)]
            # Native images can also contain independently detected extents
            # on either side of the median. Never invent a size to fit intent.
            peer_sizes={}
            for peer in normal:
                pw,ph=peer['box'][2:]
                if .9*nw<=pw<=1.1*nw and .9*nh<=ph<=1.1*nh:
                    peer_sizes.setdefault((pw,ph),peer)
            sizes=list(dict.fromkeys(sizes+sorted(peer_sizes)))
            measured_sizes={}
            if aspect:
                calibration=aspect.get('calibration') or {}
                circles=[(i,calibration['candidates'][i]) for i in calibration.get('consensus',[])
                    if 0<=i<len(calibration.get('candidates',[])) and
                    np.hypot(calibration['candidates'][i]['center'][0]-cx,calibration['candidates'][i]['center'][1]-cy)<=min(nw,nh)*.05]
                reference=_orange_reference_extent(root) if len(circles)==1 else None
                if reference:
                    index,circle=circles[0];rw,rh=reference['circleBox'][2:]
                    measured=(circle['box'][2]/rw*reference['templateSize'][0],circle['box'][3]/rh*reference['templateSize'][1])
                    if .9*nw<=measured[0]<=1.1*nw and .9*nh<=measured[1]<=1.1*nh:
                        sizes.append(measured);measured_sizes[measured]={
                            'method':'same_frame_orange_circle_and_original_template_extent',
                            'pixelSha256':digest,'candidateIndex':index,'sourceCircleBox':circle['box'],
                            **reference,'actionsExecuted':False}
            ellipse_boxes={}
            def outline_size_hypotheses():
                # Keep an already independently valid peer/circle crop. The
                # source ellipse is a fallback, not a replacement measurement.
                yield from sizes
                if best is not None or aspect:return
                from map_aspect import _orange_node_pixel_geometry
                measurement=_orange_node_pixel_geometry(image,box,root,digest,allow_icon_core=True)
                if measurement is None:return
                source_box,geometry_evidence=measurement;ew,eh=source_box[2:]
                if not (.9*nw<=ew<=1.1*nw and .9*nh<=eh<=1.1*nh):return
                key=(ew,eh)
                ellipse_boxes[key]={
                    'method':'same_frame_original_ellipse_extent','actionsExecuted':False,
                    'pixelSha256':digest,'sourceImageSha256':packet['binding']['imageSha256'],
                    'sourceCaptureFrameId':packet['binding']['frameId'],'sourceSize':[width,height],
                    'sourceBox':source_box,'sourceSearchBox':list(box),'peerMedianSize':[float(nw),float(nh)],
                    'geometryEvidence':geometry_evidence}
                yield key
            for candidate_w,candidate_h in outline_size_hypotheses():
                ellipse_evidence=ellipse_boxes.get((candidate_w,candidate_h))
                candidate_box=(list(ellipse_evidence['sourceBox']) if ellipse_evidence else
                    [cx-candidate_w/2,cy-candidate_h/2,candidate_w,candidate_h])
                if min(candidate_box[:2])<0 or candidate_box[0]+candidate_w>width or candidate_box[1]+candidate_h>height:continue
                for dx in range(-radius,radius+1):
                    for dy in range(-radius,radius+1):
                        q=np.asarray(image.crop((candidate_box[0]+dx,candidate_box[1]+dy,candidate_box[0]+candidate_w+dx,candidate_box[1]+candidate_h+dy)).resize((58,58)))[12:46,12:46];qg=cv2.cvtColor(q,cv2.COLOR_RGB2GRAY);scores=[]
                        for name,_,_,ref,refg in templates:
                            corr=float(cv2.matchTemplate(qg,refg,cv2.TM_CCOEFF_NORMED)[0,0]);score=.7*corr+.3*(1-np.abs(q.astype(float)-ref).mean()/255)
                            scores.append((float(score),name))
                        scores.sort(reverse=True)
                        # Each measured size is a separate crop hypothesis.
                        # A stronger match to another template at another size
                        # must not discard a crop that independently clears
                        # both unchanged ordinary-icon thresholds.
                        if (scores[0][1]!='node-orange' or scores[0][0]<.9 or scores[0][0]-scores[1][0]<.08):continue
                        if best is None or scores[0][0]>best[0][0][0]:best=(scores,dx,dy,candidate_box,measured_sizes.get((candidate_w,candidate_h)),None if ellipse_evidence else peer_sizes.get((candidate_w,candidate_h)),ellipse_evidence)
            if best is None:continue
            ranks,dx,dy,box,size_evidence,peer,ellipse_evidence=best
            if ranks[0][0]<.9 or ranks[0][0]-ranks[1][0]<.08 or ranks[0][1]!='node-orange':continue
            candidate['box']=box
            if size_evidence:candidate['iconSizeEvidence']=size_evidence
            if ellipse_evidence is not None:
                candidate['iconMatchedTemplate']=ranks[0][1]
                candidate['iconRunnerUpScore']=ranks[1][0]
                candidate['iconSizeMethod']='same_frame_original_ellipse_extent'
                candidate['iconEllipseSizeEvidence']=ellipse_evidence
            if peer is not None:
                candidate['iconSizeMethod']='same_frame_detected_peer_extent'
                candidate['iconPeerSizeEvidence']={
                    'method':'same_frame_detected_peer_extent','actionsExecuted':False,
                    'pixelSha256':digest,'sourceImageSha256':packet['binding']['imageSha256'],
                    'sourceCaptureFrameId':packet['binding']['frameId'],'sourceSize':[width,height],
                    'peerNodeId':peer['id'],'peerSourceBox':list(peer['box']),'peerScore':peer['score'],
                    'candidateSize':list(box[2:]),'peerMedianSize':[float(nw),float(nh)]}

            candidate.update(types);candidate.update({'id':f'outline-{floor}-{column}','floor':floor,'column':column,'score':ranks[0][0],'recovered':True,'iconScore':ranks[0][0],'iconAlignmentPx':[dx,dy]})
            nodes.append(candidate);recovered.append(candidate)
    for n in nodes:
        if n.get('type')!='battle' or n.get('completed') is not False or n.get('score',0)<.48:continue
        box=n.get('box',[])
        if len(box)!=4 or not np.isfinite(box).all():continue
        x,y,w,h=box
        if w<=0 or h<=0 or x<0 or y<0 or x+w>width or y+h>height:continue
        l,t=max(0,int(x-w*.15)),max(0,int(y-h*.15));r,b=min(width,int(x+w*1.15)+1),min(height,int(y+h*1.15)+1)
        yy,xx=np.mgrid[t:b,l:r];cx=x+w/2;cy=y+h/2
        radius=np.maximum(abs((xx-cx)/(w/2)),abs((yy-cy)/(h/2)))
        ring=(radius>.8)&(radius<1.15);local=green[t:b,l:r]
        coverage=float(local[ring].mean())
        quadrants=[]
        for horizontal,vertical in [(xx<cx,yy<cy),(xx>=cx,yy<cy),(xx<cx,yy>=cy),(xx>=cx,yy>=cy)]:
            q=ring&horizontal&vertical;quadrants.append(float(local[q].mean()) if q.any() else 0)
        if coverage>=.08 and min(quadrants)>=.04:
            selected.append({**n,'ringCoverage':coverage,'quadrants':quadrants})
    if len(selected)!=1:return unknown
    node=selected[0]
    if type(node.get('floor')) is not int or not 1<=node['floor']<=31 or type(node.get('column')) is not int or not 1<=node['column']<=4:return unknown
    return {'verified':True,'method':'unique_uncompleted_battle_green_outline_and_ordinary_timer_enter',
        'pixelSha256':digest,'selectedNode':{'verified':True,'zone':progress['displayedZone'],'floor':node['floor'],'column':node['column'],
          'nodeId':node['id'],'box':node['box'],'ringCoverage':node['ringCoverage'],'quadrants':node['quadrants']},
        'controlsVerified':True,'enterBox':buttons[0],'timerBox':tb,'timerEvidence':timers[0],
        'ordinaryBox':ob,'ordinaryEvidence':ordinary_evidence,'recoveredNodes':recovered,'recoveredMapReview':recovered_map,'actionsExecuted':False}
