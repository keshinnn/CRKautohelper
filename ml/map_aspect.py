"""Same-frame pixel aspect evidence; never reads test transforms or intent."""
import copy
import hashlib
import io
import json
import math
import os
import re
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def _qualified_aspect_groups(candidates):
    groups={tuple(i for i,q in enumerate(candidates) if abs(q['ratio']/p['ratio']-1)<.04) for p in candidates}
    closed=set()
    for group in groups:
        seen=set()
        while group and group not in seen:
            seen.add(group);median=float(np.median([candidates[i]['ratio'] for i in group]))
            next_group=tuple(i for i,q in enumerate(candidates) if abs(q['ratio']/median-1)<.04)
            if next_group==group:
                closed.add(group)
                break
            group=next_group
    qualified=[]
    for group in closed:
        if len(group)<3:continue
        members=[candidates[i] for i in group];ratios=[p['ratio'] for p in members];ratio=float(np.median(ratios))
        if max(abs(v/ratio-1) for v in ratios)>.04 or np.std(ratios)/ratio>.025:continue
        xs,ys=([p['center'][axis] for p in members] for axis in (0,1))
        if max(xs)-min(xs)<np.median([p['box'][2] for p in members])*1.5 or max(ys)-min(ys)<np.median([p['box'][3] for p in members])*1.5:continue
        qualified.append(group)
    return [g for g in qualified if not any(set(g)<set(other) for other in qualified)]


def _gate_supported_aspect_candidates(image,candidates,analysis,sx,sy,digest):
    root=Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper'));orange=[]
    for q in candidates:
        cx,cy=q['center'];w,h=q['box'][2]*58/37,q['box'][3]*58/37
        measured=_orange_node_pixel_geometry(image,[cx-w/2,cy-h/2,w,h],root,digest,allow_icon_core=True)
        if measured is not None:orange.append({**q,'circleKind':'orange_battle','iconEvidence':measured[1]})
    if len(orange)<2:return []
    mask=cv2.inRange(cv2.cvtColor(analysis,cv2.COLOR_RGB2HSV),(75,110,130),(105,255,255))
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8));gates=[]
    for contour in cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[0]:
        x,y,w,h=cv2.boundingRect(contour);area=cv2.contourArea(contour);hull=cv2.contourArea(cv2.convexHull(contour))
        if len(contour)<5 or min(w,h)<18 or max(w,h)>130 or area<200 or hull<=0 or area/hull<=.9:continue
        (cx,cy),(ew,eh),angle=cv2.fitEllipse(contour)
        if min(ew,eh)<=0 or not .9<area/(math.pi*ew*eh/4)<1.1:continue
        theta=math.radians(angle);ex=math.hypot(ew*math.cos(theta),eh*math.sin(theta))/sx;ey=math.hypot(ew*math.sin(theta),eh*math.cos(theta))/sy;cx/=sx;cy/=sy
        rough_ratio=ex/ey*41/40
        if not .55<=rough_ratio<=2.5 or abs(rough_ratio-1)>.1 and abs(math.sin(theta*2))>.2:continue
        rough=[cx-ex/2-9*ex/40,cy-ey/2-9*ey/41,58*ex/40,58*ey/41]
        measured=_gate_pixel_geometry(image,rough,root,digest)
        if measured is None:continue
        _,proof=measured;bx,by,bw,bh=proof['sourceInnerBox'];rw,rh=proof['templateInnerBox'][2:];ratio=bw/bh*rh/rw
        if not .55<=ratio<=2.5:continue
        gates.append({'analysisBox':[x,y,w,h],'box':[bx,by,bw,bh],'center':[bx+bw/2,by+bh/2],
            'ratio':ratio,'solidity':area/hull,'ellipseFill':area/(math.pi*ew*eh/4),'angleDegrees':angle,
            'circleKind':'cyan_gate','iconEvidence':proof})
    return [*orange,*gates] if len(gates)==1 else []


def estimate_pixel_aspect(image):
    rgb = np.asarray(image.convert('RGB'))
    height, width = rgb.shape[:2]
    ah = round(height * 960 / width)
    if ah < 24:
        return None
    analysis = cv2.resize(rgb, (960, ah), interpolation=cv2.INTER_LINEAR)
    sx, sy = 960 / width, ah / height
    hsv = cv2.cvtColor(analysis, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, (5, 130, 130), (35, 255, 255))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        if min(w, h) < 18 or max(w, h) > 130 or len(contour) < 5 or area < 200:
            continue
        hull = cv2.contourArea(cv2.convexHull(contour))
        (cx, cy), (ew, eh), angle = cv2.fitEllipse(contour)
        if min(ew, eh, hull) <= 0:
            continue
        solidity, fill = area / hull, area / (math.pi * ew * eh / 4)
        if not .9 < solidity <= 1 or not .9 < fill < 1.1:
            continue
        theta = math.radians(angle)
        ex = math.hypot(ew * math.cos(theta), eh * math.sin(theta))
        ey = math.hypot(ew * math.sin(theta), eh * math.cos(theta))
        ratio = ex / ey * sy / sx
        if not .55 <= ratio <= 2.5:
            continue
        if abs(ratio - 1) > .1 and abs(math.sin(theta * 2)) > .2:
            continue
        candidates.append({
            'analysisBox': [x, y, w, h],
            'box': [x / sx, y / sy, w / sx, h / sy],
            'center': [cx / sx, cy / sy], 'ratio': ratio,
            'solidity': solidity, 'ellipseFill': fill, 'angleDegrees': angle,
        })
    qualified=_qualified_aspect_groups(candidates)
    method='original_pixel_orange_circle_unique_aspect_consensus'
    if not qualified:
        supported=_gate_supported_aspect_candidates(image.convert('RGB'),candidates,analysis,sx,sy,hashlib.sha256(rgb.tobytes()).hexdigest())
        supported_groups=_qualified_aspect_groups(supported)
        if len(supported_groups)==1:
            kinds=[supported[i]['circleKind'] for i in supported_groups[0]]
            if kinds.count('orange_battle')>=2 and kinds.count('cyan_gate')==1:
                candidates,qualified=supported,supported_groups
                method='original_pixel_orange_and_gate_unique_aspect_consensus'
    if len(qualified) != 1:
        return None
    consensus = qualified[0]
    return {
        'method': method,
        'ratio': float(np.median([candidates[i]['ratio'] for i in consensus])),
        'pixelSha256': hashlib.sha256(rgb.tobytes()).hexdigest(),
        'sourceSize': [width, height], 'analysisSize': [960, ah],
        'analysisScaleX': sx, 'analysisScaleY': sy,
        'candidates': candidates, 'consensus': list(consensus),
        'actionsExecuted': False,
    }


def _cyan_component(image, box):
    x,y,w,h=box
    left,top,right,bottom=int(x),int(y),math.ceil(x+w),math.ceil(y+h)
    if min(left,top)<0 or right>image.width or bottom>image.height:return None
    rgb=np.asarray(image.crop((left,top,right,bottom)))
    mask=cv2.inRange(cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV),(75,110,130),(105,255,255))
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);matches=[]
    for contour in contours:
        bx,by,bw,bh=cv2.boundingRect(contour);area=cv2.contourArea(contour)
        if (not w*.5<bw<w*.9 or not h*.5<bh<h*.9 or area/(bw*bh)<.65
                or math.hypot(left+bx+bw/2-x-w/2,top+by+bh/2-y-h/2)>min(w,h)*.08):continue
        matches.append([left+bx,top+by,bw,bh])
    return matches[0] if len(matches)==1 else None


def _gate_pixel_geometry(image, box, root, digest):
    measured=_cyan_component(image,box)
    if measured is None:return None
    raw=(root/'data/map/node-exit.png').read_bytes()
    reference=Image.open(io.BytesIO(raw)).convert('RGB')
    extent=_cyan_component(reference,[0,0,*reference.size])
    if extent is None:return None
    x,y,w,h=measured;rx,ry,rw,rh=extent
    actual=cv2.resize(np.asarray(image.crop((x,y,x+w,y+h))),(rw,rh),interpolation=cv2.INTER_AREA)
    expected=np.asarray(reference.crop((rx,ry,rx+rw,ry+rh)))
    correlation=float(cv2.matchTemplate(cv2.cvtColor(actual,cv2.COLOR_RGB2GRAY),cv2.cvtColor(expected,cv2.COLOR_RGB2GRAY),cv2.TM_CCOEFF_NORMED)[0,0])
    score=.7*correlation+.3*(1-np.abs(actual.astype(float)-expected).mean()/255)
    if not .9<=score<=1:return None
    sx,sy=w/rw,h/rh
    result=[x-rx*sx,y-ry*sy,reference.width*sx,reference.height*sy]
    if (min(result[:2])<0 or result[0]+result[2]>image.width or result[1]+result[3]>image.height
            or not .85*box[2]<=result[2]<=1.15*box[2] or not .85*box[3]<=result[3]<=1.15*box[3]):return None
    return result,{
        'method':'same_frame_cyan_gate_arrow_and_original_template_extent',
        'pixelSha256':digest,'sourceInnerBox':measured,'templateInnerBox':extent,
        'templateSize':list(reference.size),'templateImageSha256':hashlib.sha256(raw).hexdigest(),
        'innerScore':float(score),'actionsExecuted':False,
    }


def _orange_node_pixel_geometry(image, box, root, digest, allow_icon_core=False):
    x,y,w,h=box;left,top=int(x),int(y);right,bottom=math.ceil(x+w),math.ceil(y+h)
    if min(left,top)<0 or right>image.width or bottom>image.height:return None
    rgb=np.asarray(image.crop((left,top,right,bottom)))
    mask=cv2.inRange(cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV),(5,130,130),(35,255,255))
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);ellipses=[]
    for contour in contours:
        area=cv2.contourArea(contour);hull=cv2.contourArea(cv2.convexHull(contour))
        if len(contour)<5 or area<200 or hull<=0 or area/hull<=.9:continue
        (cx,cy),(ew,eh),angle=cv2.fitEllipse(contour)
        if min(ew,eh)<=0 or not .9<area/(math.pi*ew*eh/4)<1.1:continue
        theta=math.radians(angle);ex=math.hypot(ew*math.cos(theta),eh*math.sin(theta));ey=math.hypot(ew*math.sin(theta),eh*math.cos(theta))
        cx+=left;cy+=top
        if math.hypot(cx-x-w/2,cy-y-h/2)>min(w,h)*.05:continue
        if cx-ex/2<x or cy-ey/2<y or cx+ex/2>x+w or cy+ey/2>y+h:continue
        ellipses.append((cx,cy,ex,ey))
    if len(ellipses)!=1:return None
    raw=(root/'data/map/node-orange.png').read_bytes();reference=Image.open(io.BytesIO(raw)).convert('RGB')
    ref_rgb=np.asarray(reference);ref_mask=cv2.inRange(cv2.cvtColor(ref_rgb,cv2.COLOR_RGB2HSV),(5,130,130),(35,255,255))
    ref_mask=cv2.morphologyEx(ref_mask,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    refs,_=cv2.findContours(ref_mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);extents=[]
    for contour in refs:
        if cv2.contourArea(contour)<=20:continue
        rx,ry,rw,rh=cv2.boundingRect(contour)
        if abs(rx+rw/2-reference.width/2)<=reference.width*.1 and abs(ry+rh/2-reference.height/2)<=reference.height*.1:extents.append([rx,ry,rw,rh])
    if len(extents)!=1:return None
    rx,ry,rw,rh=extents[0];cx,cy,ex,ey=ellipses[0];bx,by=cx-ex/2,cy-ey/2
    crop=[round(bx),round(by),round(bx+ex),round(by+ey)]
    if crop[2]<=crop[0] or crop[3]<=crop[1]:return None
    actual=cv2.resize(np.asarray(image.crop(crop)),(rw,rh),interpolation=cv2.INTER_AREA)
    expected=ref_rgb[ry:ry+rh,rx:rx+rw]
    score=.7*float(cv2.matchTemplate(cv2.cvtColor(actual,cv2.COLOR_RGB2GRAY),cv2.cvtColor(expected,cv2.COLOR_RGB2GRAY),cv2.TM_CCOEFF_NORMED)[0,0])+.3*(1-np.abs(actual.astype(float)-expected).mean()/255)
    sx,sy=ex/rw,ey/rh;result=[bx-rx*sx,by-ry*sy,reference.width*sx,reference.height*sy]
    if (min(result[:2])<0 or result[0]+result[2]>image.width or result[1]+result[3]>image.height
            or not .85*w<=result[2]<=1.15*w or not .85*h<=result[3]<=1.15*h):return None
    core=None;circle_score=float(score)
    if not .9<=score<=1:
        if not allow_icon_core:return None
        # Reuse the preview recognizer's original 34x34 icon comparison and
        # bounded alignment. The ellipse still fixes the physical outer box.
        from map_vision import map_templates
        templates=map_templates(root/'data/map');best=None
        radius=max(1,round(min(result[2:])*.02))
        for dx in range(-radius,radius+1):
            for dy in range(-radius,radius+1):
                x0,y0,ow,oh=result
                if min(x0+dx,y0+dy)<0 or x0+ow+dx>image.width or y0+oh+dy>image.height:continue
                actual=np.asarray(image.crop((x0+dx,y0+dy,x0+ow+dx,y0+oh+dy)).resize((58,58)))[12:46,12:46]
                gray=cv2.cvtColor(actual,cv2.COLOR_RGB2GRAY);scores=[]
                for name,_,_,ref,refg in templates:
                    value=.7*float(cv2.matchTemplate(gray,refg,cv2.TM_CCOEFF_NORMED)[0,0])+.3*(1-np.abs(actual.astype(float)-ref).mean()/255)
                    scores.append((float(value),name))
                scores.sort(reverse=True)
                if scores[0][1]!='node-orange' or scores[0][0]<.9 or scores[0][0]-scores[1][0]<.08:continue
                if best is None or scores[0][0]>best['score']:
                    best={'method':'original_outer58_inner12_46_rgb_bounded_alignment','score':scores[0][0],
                        'template':'node-orange','runnerUpScore':scores[1][0],'runnerUpTemplate':scores[1][1],
                        'alignmentPx':[dx,dy],'alignmentRadius':radius,
                        'sourceCropBox':[x0+dx,y0+dy,ow,oh],'analysisSize':[58,58],'innerBox':[12,12,34,34]}
        if best is None:return None
        core=best;score=best['score']
    proof={
        'method':'same_frame_orange_ellipse_and_original_template_extent',
        'pixelSha256':digest,'sourceInnerBox':[bx,by,ex,ey],'ellipseCenter':[cx,cy],
        'actualCropBox':[crop[0],crop[1],crop[2]-crop[0],crop[3]-crop[1]],
        'templateInnerBox':extents[0],'templateSize':list(reference.size),
        'templateImageSha256':hashlib.sha256(raw).hexdigest(),'innerScore':float(score),'actionsExecuted':False,
    }
    if core:proof.update(iconCoreEvidence=core,circleInnerScore=circle_score)
    return result,proof


def _supplement_orange_candidates(image, normalized, initial, calibration, binding, root, normal_pixel, normalized_sha):
    """Scoped candidate producer; the original lattice/line code still decides."""
    if re.fullmatch(r'[a-f0-9]{32}',binding.get('frameId','')) is None:return initial
    peers=[n for n in initial.get('nodes',[]) if n.get('type') not in ('exit','boss')]
    if len(peers)<4:return initial
    inverse=image.width/normalized.width;nw=float(np.median([n['box'][2] for n in peers]));nh=float(np.median([n['box'][3] for n in peers]))
    proposals=[]
    analysis_size=[960,round(normalized.height*960/normalized.width)]
    fx,fy=960/normalized.width,analysis_size[1]/normalized.height
    analysis_pixel=hashlib.sha256(np.asarray(normalized.resize(tuple(analysis_size),Image.Resampling.LANCZOS)).tobytes()).hexdigest()
    for index in calibration['consensus']:
        circle=calibration['candidates'][index];cx,cy=circle['center'][0]/inverse,circle['center'][1]
        if any(math.hypot(cx-n['center'][0],cy-n['center'][1])<=min(nw,nh)*.25 for n in initial['nodes']):continue
        measured=_orange_node_pixel_geometry(image,[(cx-nw/2)*inverse,cy-nh/2,nw*inverse,nh],root,calibration['pixelSha256'],allow_icon_core=True)
        if measured is None:continue
        (x,y,w,h),evidence=measured;box=[x/inverse,y,w/inverse,h];center=[(x+w/2)/inverse,y+h/2]
        geometry={**evidence,'candidateIndex':index,'originalAnalysisBox':box,'originalAnalysisCenter':center}
        proposals.append({'box':[box[0]*fx,box[1]*fy,box[2]*fx,box[3]*fy],
            'center':[center[0]*fx,center[1]*fy],'score':evidence['innerScore'],'template':'node-orange.png',
            'scoreMethod':'original_source_inner_template_rgb','pixelProposal':{
                'method':'same_frame_original_orange_inner_candidate','sourceImageSha256':binding['imageSha256'],
                'pixelSha256':calibration['pixelSha256'],'sourceCaptureFrameId':binding['frameId'],
                'sourceSize':list(image.size),'rectifiedInputSize':list(normalized.size),
                'rectifiedPixelSha256':normal_pixel,'analysisSize':analysis_size,'analysisPixelSha256':analysis_pixel,
                'injectedAnalysisBox':[box[0]*fx,box[1]*fy,box[2]*fx,box[3]*fy],
                'geometryEvidence':geometry,'actionsExecuted':False}})
    from completed_node_candidates import completed_node_candidates
    proposals+=completed_node_candidates(image,initial,inverse,root,binding,list(normalized.size),normal_pixel,analysis_size,analysis_pixel)
    if not proposals:return initial
    import map_vision
    from sparse_map_geometry import recover_map_geometry
    original=map_vision.node_candidates;cached=None
    def candidates(current,folder):
        nonlocal cached
        if list(current.size)!=analysis_size or hashlib.sha256(np.asarray(current.convert('RGB')).tobytes()).hexdigest()!=analysis_pixel:
            return original(current,folder)
        if cached is None:cached=copy.deepcopy(original(current,folder))
        result=copy.deepcopy(cached)
        for proposal in proposals:
            px,py=proposal['center'];size=min(proposal['box'][2:])
            if not any(math.hypot(px-n['center'][0],py-n['center'][1])<=size*.25 for n in result):result.append(copy.deepcopy(proposal))
        return result
    map_vision.node_candidates=candidates
    try:
        result=map_vision.inspect_map(normalized,root/'data/map',read_header=False)
        if len(result.get('columns') or [])!=4:
            relative=copy.deepcopy(result);gates=[n for n in relative['nodes'] if n.get('type')=='exit']
            if len(gates)==1:relative['nodes']=[n for n in relative['nodes'] if n.get('type')=='exit' or n['center'][1]>gates[0]['center'][1]]
            result=recover_map_geometry(normalized,{'binding':{'pixelSha256':normal_pixel,'imageSha256':normalized_sha},'mapReview':relative})
        if any(n.get('pixelProposal') and (n.get('type')!='battle' or n.get('completed') is not False) for n in result.get('nodes',[])):return initial
        if any(n.get('checkProposal') and (n.get('type') in ('exit','boss') or n.get('completed') is not True) for n in result.get('nodes',[])):return initial
        return result
    finally:
        map_vision.node_candidates=original


def recover_map_aspect(image, packet):
    original = packet.get('mapReview')
    if not isinstance(original, dict):
        return original
    rgb = image.convert('RGB')
    digest = hashlib.sha256(rgb.tobytes()).hexdigest()
    binding = packet.get('binding', {})
    if (binding.get('pixelSha256') != digest or original.get('frameId') != digest[:20]
            or binding.get('width') != rgb.width or binding.get('height') != rgb.height
            or re.fullmatch(r'[a-f0-9]{64}', binding.get('imageSha256', '')) is None):
        return original
    calibration = estimate_pixel_aspect(rgb)
    if calibration is None:
        return original
    deviation=abs(calibration['ratio']-1)
    near_native=deviation<=.08
    if deviation<=.03 or near_native and type(original.get('absoluteFloorKnown')) is not bool:
        return original
    normalized = rgb.resize((round(rgb.width / calibration['ratio']), rgb.height),
                            Image.Resampling.LANCZOS)
    normal_pixel = hashlib.sha256(normalized.tobytes()).hexdigest()
    from map_vision import inspect_map
    root = Path(os.environ.get('CRK_V1_ROOT', 'F:/CRK helper'))
    result = inspect_map(normalized, root / 'data/map', read_header=False)
    raw = io.BytesIO()
    normalized.save(raw, format='PNG')
    normalized_sha = hashlib.sha256(raw.getvalue()).hexdigest()
    result = _supplement_orange_candidates(rgb,normalized,result,calibration,binding,root,normal_pixel,normalized_sha)
    candidate_scope = None
    if len(result.get('columns') or []) != 4:
        # A visible top gate places every ordinary row below that gate.
        # Preview-header icons above it are not another map column. Keep the
        # excluded measurements, then reuse the existing unique lattice and
        # connecting-pixel verification on this same rectified image.
        from sparse_map_geometry import recover_map_geometry
        relative = copy.deepcopy(result)
        gates = [n for n in relative.get('nodes', []) if n.get('type') == 'exit']
        if len(gates) == 1:
            gy = gates[0]['center'][1]
            excluded = [n for n in relative['nodes'] if n.get('type') != 'exit' and n['center'][1] <= gy]
            relative['nodes'] = [n for n in relative['nodes'] if n not in excluded]
            candidate_scope = {
                'method': 'same_frame_visible_top_gate_excludes_nonexit_above_gate',
                'pixelSha256': normal_pixel, 'gateBox': list(gates[0]['box']),
                'excluded': excluded, 'actionsExecuted': False,
            }
        result = recover_map_geometry(normalized, {
            'binding': {'pixelSha256': normal_pixel, 'imageSha256': normalized_sha},
            'mapReview': relative,
        })
    columns, nodes = result.get('columns'), result.get('nodes', [])
    if (result.get('frameId') != normal_pixel[:20]
            or not isinstance(columns, list) or len(columns) != 4
            or not np.isfinite(columns).all() or columns != sorted(set(columns))
            or len(nodes) < 4 or any(not n.get('id') for n in nodes)
            or len({n['id'] for n in nodes}) != len(nodes)):
        return original
    result = copy.deepcopy(result)
    inverse_x = rgb.width / normalized.width
    for node in result['nodes']:
        if node.get('pixelProposal'):
            # Legacy lattice assignment rounds its analysis boxes to .01px.
            # Retain the producer's measured precision until source projection.
            geometry=node['pixelProposal']['geometryEvidence']
            node['box']=list(geometry['originalAnalysisBox'])
            node['center']=list(geometry['originalAnalysisCenter'])
        if node.get('checkProposal'):
            node['box']=list(node['checkProposal']['originalAnalysisBox'])
            node['center']=list(node['checkProposal']['originalAnalysisCenter'])
        if node.get('type') == 'exit':
            x,y,w,h=node['box']
            measured=_gate_pixel_geometry(rgb,[x*inverse_x,y,w*inverse_x,h],root,digest)
            if measured is not None:
                (x,y,w,h),proof=measured
                node['gateRefinement']={**proof,'originalAnalysisBox':list(node['box']),
                    'originalAnalysisCenter':list(node['center'])}
                node['box']=[x/inverse_x,y,w/inverse_x,h]
                node['center']=[(x+w/2)/inverse_x,y+h/2]
        if node.get('type') == 'battle' and node.get('completed') is False and not node.get('pixelProposal'):
            x, y, w, h = node['box']
            matches = []
            for index in calibration['consensus']:
                circle = calibration['candidates'][index]
                cx, cy = circle['center'][0] / inverse_x, circle['center'][1]
                bx, by, bw, bh = circle['box']
                if (x <= bx / inverse_x and bx / inverse_x + bw / inverse_x <= x + w
                        and y <= by and by + bh <= y + h
                        and 0 <= cx-w/2 and cx+w/2 <= normalized.width
                        and 0 <= cy-h/2 and cy+h/2 <= normalized.height
                        and math.hypot(cx - node['center'][0], cy - node['center'][1]) <= min(w, h) * .05):
                    matches.append((index, cx, cy))
            if len(matches) == 1:
                index, cx, cy = matches[0]
                measured=_orange_node_pixel_geometry(rgb,[x*inverse_x,y,w*inverse_x,h],root,digest,allow_icon_core=True)
                if measured is not None:
                    (bx,by,bw,bh),proof=measured
                    node['orangeRefinement']={**proof,'candidateIndex':index,
                        'originalAnalysisBox':list(node['box']),'originalAnalysisCenter':list(node['center'])}
                    node['box']=[bx/inverse_x,by,bw/inverse_x,bh]
                    node['center']=[(bx+bw/2)/inverse_x,by+bh/2]
                else:
                    node['centerRefinement'] = {
                        'method': 'same_frame_unique_enclosed_orange_circle_center',
                        'candidateIndex': index, 'originalAnalysisBox': list(node['box']),
                        'originalAnalysisCenter': list(node['center']), 'actionsExecuted': False,
                    }
                    node['center'] = [cx, cy]
                    node['box'] = [cx - w / 2, cy - h / 2, w, h]
        node['analysisBox'] = list(node['box'])
        node['analysisCenter'] = list(node['center'])
        x, y, w, h = node['box']
        node['box'] = [round(x * inverse_x, 2), y, round(w * inverse_x, 2), h]
        node['center'] = [round(node['center'][0] * inverse_x, 2), node['center'][1]]
    result['columns'] = [round(x * inverse_x, 2) for x in columns]
    result['header'] = copy.deepcopy(original.get('header'))
    result['frameId'] = digest[:20]
    result['analysisScale'] = 960 / rgb.width
    result['analysisScaleY'] = round(normalized.height * 960 / normalized.width) / rgb.height
    result['aspectRectification'] = {
        'verified': True, 'method': 'same_frame_circle_aspect_map_rectification',
        'rectificationPurpose':('anchored_near_native_recovery' if original['absoluteFloorKnown'] else 'unanchored_near_native_recovery') if near_native else 'pixel_aspect_recovery',
        'sourceImageSha256': binding['imageSha256'], 'pixelSha256': digest,
        'sourceCaptureFrameId': binding.get('frameId'),
        'sourceSize': list(rgb.size), 'rectifiedInputSize': list(normalized.size),
        'rectifiedColumns': list(columns),
        'rectifiedFloorAnchorSource': result.get('floorAnchorSource'),
        'modelAnalysisSize': [960, round(normalized.height * 960 / normalized.width)],
        'rectifiedImageSha256': normalized_sha,
        'rectifiedPixelSha256': normal_pixel,
        'candidateScope': candidate_scope,
        'forwardMatrix': [[1 / inverse_x, 0, 0], [0, 1, 0], [0, 0, 1]],
        'inverseMatrix': [[inverse_x, 0, 0], [0, 1, 0], [0, 0, 1]],
        'calibration': calibration, 'actionsExecuted': False,
    }
    return result
