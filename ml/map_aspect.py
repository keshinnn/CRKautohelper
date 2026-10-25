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
    groups = {
        tuple(i for i, q in enumerate(candidates) if abs(q['ratio'] / p['ratio'] - 1) < .04)
        for p in candidates
    }
    qualified = []
    for group in groups:
        if len(group) < 3:
            continue
        members = [candidates[i] for i in group]
        ratios = [p['ratio'] for p in members]
        ratio = float(np.median(ratios))
        if max(abs(v / ratio - 1) for v in ratios) > .04 or np.std(ratios) / ratio > .025:
            continue
        xs, ys = ([p['center'][axis] for p in members] for axis in (0, 1))
        if (max(xs) - min(xs) < np.median([p['box'][2] for p in members]) * 1.5
                or max(ys) - min(ys) < np.median([p['box'][3] for p in members]) * 1.5):
            continue
        qualified.append(group)
    qualified = [g for g in qualified if not any(set(g) < set(other) for other in qualified)]
    if len(qualified) != 1:
        return None
    consensus = qualified[0]
    return {
        'method': 'original_pixel_orange_circle_unique_aspect_consensus',
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


def _orange_node_pixel_geometry(image, box, root, digest):
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
    if not .9<=score<=1:return None
    sx,sy=ex/rw,ey/rh;result=[bx-rx*sx,by-ry*sy,reference.width*sx,reference.height*sy]
    if (min(result[:2])<0 or result[0]+result[2]>image.width or result[1]+result[3]>image.height
            or not .85*w<=result[2]<=1.15*w or not .85*h<=result[3]<=1.15*h):return None
    return result,{
        'method':'same_frame_orange_ellipse_and_original_template_extent',
        'pixelSha256':digest,'sourceInnerBox':[bx,by,ex,ey],'ellipseCenter':[cx,cy],
        'actualCropBox':[crop[0],crop[1],crop[2]-crop[0],crop[3]-crop[1]],
        'templateInnerBox':extents[0],'templateSize':list(reference.size),
        'templateImageSha256':hashlib.sha256(raw).hexdigest(),'innerScore':float(score),'actionsExecuted':False,
    }


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
    if calibration is None or abs(calibration['ratio'] - 1) <= .08:
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
        if node.get('type') == 'exit':
            x,y,w,h=node['box']
            measured=_gate_pixel_geometry(rgb,[x*inverse_x,y,w*inverse_x,h],root,digest)
            if measured is not None:
                (x,y,w,h),proof=measured
                node['gateRefinement']={**proof,'originalAnalysisBox':list(node['box']),
                    'originalAnalysisCenter':list(node['center'])}
                node['box']=[x/inverse_x,y,w/inverse_x,h]
                node['center']=[(x+w/2)/inverse_x,y+h/2]
        if node.get('type') == 'battle' and node.get('completed') is False:
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
                measured=_orange_node_pixel_geometry(rgb,[x*inverse_x,y,w*inverse_x,h],root,digest)
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
