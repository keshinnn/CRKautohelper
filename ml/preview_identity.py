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

def _box(row):
    points=np.asarray(row.get('box',[]),dtype=float)
    if points.shape!=(4,2) or not np.isfinite(points).all():return None
    lo=points.min(axis=0);hi=points.max(axis=0)
    return [float(lo[0]),float(lo[1]),float(hi[0]-lo[0]),float(hi[1]-lo[1])]

def _english_ordinary_crop(image,evidence):
    labels=[r for r in evidence if r.get('text','').strip().casefold()=='difficulty' and r.get('score',0)>=.95 and _box(r) and _box(r)[0]>image.width*.5]
    if len(labels)!=1:return []
    x,y,w,h=_box(labels[0])
    if h<=0 or h>image.height*.1 or x+w>=image.width:return []
    left,top=int(x+w),max(0,int(y-h*.15))
    right,bottom=max(left,int(image.width-h)),min(image.height,int(y+h*1.15))
    if min(right-left,bottom-top)<=0:return []
    crop=image.crop((left,top,right,bottom))
    import text_reader
    runtime=getattr(text_reader,'_v2_bounded_ocr_runtime',None)
    if not runtime or not runtime.enabled:return []
    sizes=[(max(24,round(crop.width/crop.height*40*ratio)),40) for ratio in [.65,.8,.95]]
    pixels=[np.asarray(crop.convert('RGB').resize(size,Image.Resampling.LANCZOS))[:,:,::-1].copy() for size in sizes]
    readings,elapsed=runtime.reader.text_rec(pixels)
    runtime.recognition_crops.append({'inputSize':list(crop.size),'source':'difficulty_adjacent_english_line','variants':[{'text':text,'score':float(score),'analysisSize':list(size)} for size,(text,score) in zip(sizes,readings)],'elapsedMs':float(elapsed)*1000})
    # Difficulty stars are part of the actual observed line. Keep them and
    # the original recognizer score; reject every other prefix/suffix.
    matches=[(text,float(score),size) for size,(text,score) in zip(sizes,readings) if re.fullmatch(r'\*{0,2}Normal',text.strip(),re.I) and float(score)>=.95]
    if not matches:return []
    text,score,analysis_size=max(matches,key=lambda row:row[1])
    return [{'text':text,'score':score,'box':[[left,top],[right,top],[right,bottom],[left,bottom]],
        'boxSource':'original_line_crop_extent','source':'difficulty_adjacent_english_normal_original_crop','cropBox':[left,top,right-left,bottom-top],'analysisSize':list(analysis_size)}]


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



def inspect_preview_identity(image,packet):
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
    if progress.get('conflictingEvidence') is not False or not .9<=progress.get('score',0)<=1 or type(progress.get('displayedZone')) is not int:return unknown
    if not 1<=progress['displayedZone']<=10:return unknown
    evidence=packet.get('evidence',[])
    enters=[r for r in evidence if re.sub(r'\s+','',r.get('text','')).casefold() in ('進入','enter') and r.get('score',0)>=.95 and _box(r) and _box(r)[0]>width*.5]
    timers=[r for r in evidence if r.get('text')=='03:00' and r.get('score',0)>=.95 and _box(r) and _box(r)[0]>width*.5]
    ordinary=[r for r in evidence if '普通' in r.get('text','') and r.get('score',0)>=.65 and _box(r) and _box(r)[0]>width*.5]
    if not ordinary and len(enters)==1 and len(timers)==1 and enters[0].get('text','').strip().casefold()=='enter':
        ordinary=_english_ordinary_crop(image,evidence)
    if len(enters)!=1 or len(timers)!=1 or len(ordinary)!=1:return unknown
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
    ordinary_evidence={'kind':'original_ocr','originalScore':ordinary[0]['score']}
    if ordinary[0].get('source')=='difficulty_adjacent_english_normal_original_crop':
        ordinary_evidence={**ordinary_evidence,'kind':ordinary[0]['source'],'originalPixelReading':ordinary[0]}
    if ordinary[0]['score']<.8:
        # Re-read a bounded original-pixel crop; do not promote the old score
        # or substitute an expected word into OCR output.
        ox,oy,ow,oh=_box(ordinary[0]);left=max(0,int(ox+ow-oh*2));top=max(0,int(oy-3));right=min(width,int(ox+ow+3));bottom=min(height,int(oy+oh+3))
        crop=image.crop((left,top,right,bottom))
        root=Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper'));module_path=str(root/'ml')
        if module_path not in sys.path:sys.path.insert(0,module_path)
        import text_reader
        runtime=getattr(text_reader,'_v2_bounded_ocr_runtime',None)
        if runtime:
            readings=runtime.read_line_variants(crop,sum('\u3400'<=c<='\u9fff' for c in ordinary[0]['text']));kind='bounded_original_pixel_line_recognition';crop_scale=1
        else:
            crop=crop.resize((crop.width*3,crop.height*3));readings=text_reader.read_text(crop);kind='bounded_original_pixel_crop_ocr';crop_scale=3
        refined=[r for r in readings if re.sub(r'\s+','',r.get('text',''))=='普通' and r.get('score',0)>=.95]
        if runtime and not refined:
            # Adjacent difficulty stars can share the detected text box. Trim
            # only a small, bounded left margin and require a new high-score
            # reading from actual pixels; never strip punctuation from text.
            for fraction in [.1,.2,.3]:
                local_left=left+round(oh*fraction)
                readings=runtime.read_line_variants(image.crop((local_left,top,right,bottom)),sum('\u3400'<=c<='\u9fff' for c in ordinary[0]['text']))
                refined=[r for r in readings if re.sub(r'\s+','',r.get('text',''))=='普通' and r.get('score',0)>=.95]
                if len(refined)==1:
                    left=local_left
                    break
        if len(refined)!=1:return unknown
        ordinary_evidence={'kind':kind,'originalScore':ordinary[0]['score'],'refinedScore':refined[0]['score'],'cropBox':[left,top,right-left,bottom-top],'cropScale':crop_scale}
    eb,tb,ob=map(_box,[enters[0],timers[0],ordinary[0]])
    if not ob[1]<tb[1]<eb[1] or eb[1]-tb[1]<height*.15:return unknown
    hsv=cv2.cvtColor(a,cv2.COLOR_RGB2HSV)
    green=(hsv[:,:,0]>30)&(hsv[:,:,0]<85)&(hsv[:,:,1]>100)&(hsv[:,:,2]>150)
    x,y,w,h=eb
    left,top=max(0,int(x-w*2)),max(0,int(y-h));right,bottom=min(width,int(x+w*3)),min(height,int(y+h*2))
    mask=green[top:bottom,left:right].astype('uint8')
    count,labels,stats,centers=cv2.connectedComponentsWithStats(mask)
    buttons=[]
    for bx,by,bw,bh,area in stats[1:]:
        if bw>w*2 and bh>h*1.3 and area/(bw*bh)>.45 and left+bx<x and left+bx+bw>x+w and top+by<y and top+by+bh>y+h:
            buttons.append([int(left+bx),int(top+by),int(bw),int(bh)])
    if len(buttons)!=1:return unknown
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
            if aspect:
                # Rectified template scales can yield two slightly different
                # outer sizes in one map. Search only sizes actually detected
                # in this frame, retaining the existing icon thresholds.
                sizes+=sorted({tuple(n['box'][2:]) for n in normal
                    if .9*nw<=n['box'][2]<=1.1*nw and .9*nh<=n['box'][3]<=1.1*nh})
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
            for candidate_w,candidate_h in sizes:
                candidate_box=[cx-candidate_w/2,cy-candidate_h/2,candidate_w,candidate_h]
                if min(candidate_box[:2])<0 or candidate_box[0]+candidate_w>width or candidate_box[1]+candidate_h>height:continue
                for dx in range(-radius,radius+1):
                    for dy in range(-radius,radius+1):
                        q=np.asarray(image.crop((candidate_box[0]+dx,candidate_box[1]+dy,candidate_box[0]+candidate_w+dx,candidate_box[1]+candidate_h+dy)).resize((58,58)))[12:46,12:46];qg=cv2.cvtColor(q,cv2.COLOR_RGB2GRAY);scores=[]
                        for name,_,_,ref,refg in templates:
                            corr=float(cv2.matchTemplate(qg,refg,cv2.TM_CCOEFF_NORMED)[0,0]);score=.7*corr+.3*(1-np.abs(q.astype(float)-ref).mean()/255)
                            scores.append((float(score),name))
                        scores.sort(reverse=True)
                        if best is None or scores[0][0]>best[0][0][0]:best=(scores,dx,dy,candidate_box,measured_sizes.get((candidate_w,candidate_h)))
            ranks,dx,dy,box,size_evidence=best
            if ranks[0][0]<.9 or ranks[0][0]-ranks[1][0]<.08 or ranks[0][1]!='node-orange':continue
            candidate['box']=box
            if size_evidence:candidate['iconSizeEvidence']=size_evidence
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
        'controlsVerified':True,'enterBox':buttons[0],'timerBox':tb,'ordinaryBox':ob,'ordinaryEvidence':ordinary_evidence,'recoveredNodes':recovered,'recoveredMapReview':recovered_map,'actionsExecuted':False}
