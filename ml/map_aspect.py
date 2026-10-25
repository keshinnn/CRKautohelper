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
        if node.get('type') == 'battle' and node.get('completed') is False:
            x, y, w, h = node['box']
            matches = []
            for index in calibration['consensus']:
                circle = calibration['candidates'][index]
                cx, cy = circle['center'][0] / inverse_x, circle['center'][1]
                bx, by, bw, bh = circle['box']
                if (x <= bx / inverse_x and bx / inverse_x + bw / inverse_x <= x + w
                        and y <= by and by + bh <= y + h
                        and math.hypot(cx - node['center'][0], cy - node['center'][1]) <= min(w, h) * .05):
                    matches.append((index, cx, cy))
            if len(matches) == 1:
                index, cx, cy = matches[0]
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
