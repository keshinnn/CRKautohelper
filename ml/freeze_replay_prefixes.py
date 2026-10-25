"""Freeze exact native pre-change context; decoding never grants MAP review."""
import hashlib
import json
import re
from pathlib import Path

import cv2


def _sha(value):
    return isinstance(value, str) and re.fullmatch(r'[a-f0-9]{64}', value) is not None


def freeze_prefixes(cases, output, annotation_sha):
    if not _sha(annotation_sha) or not isinstance(cases, list) or not cases:
        raise ValueError('frozen annotation identity and cases required')
    videos, seen = {}, set()
    for case in cases:
        name, size, fps, pre = (case.get(k) for k in
                                ['id', 'sourceSize', 'sourceFps', 'preFrames'])
        if (not isinstance(name, str)
                or re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,99}', name) is None
                or name in seen or case.get('reviewed') is not True
                or not _sha(case.get('videoSha256'))
                or type(fps) is not int or fps not in (30, 60)
                or not isinstance(size, list) or len(size) != 2
                or any(type(x) is not int or x <= 0 for x in size)
                or not isinstance(pre, list) or len(pre) != 2
                or any(type(x) is not int for x in pre) or pre[0] < 1
                or pre[1] - pre[0] < fps * .2
                or not isinstance(case.get('video'), str) or not case['video']):
            raise ValueError('reviewed native case specification required')
        seen.add(name)
        video = Path(case['video']).resolve()
        if video not in videos:
            with video.open('rb') as stream:
                videos[video] = hashlib.file_digest(stream, 'sha256').hexdigest()
        if videos[video] != case['videoSha256']:
            raise ValueError('source video changed')

    output = Path(output)
    output.mkdir()
    raw = json.dumps(cases, ensure_ascii=False, sort_keys=True, indent=2).encode()
    (output / 'cases.snapshot.json').write_bytes(raw)
    result = {
        'stage': 'P4-C-prefix-source', 'annotationSha256': annotation_sha,
        'inputCasesSha256': hashlib.sha256(raw).hexdigest(),
        'freezerCodeSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'decoderVersion': cv2.__version__, 'prefixBytesVerified': False,
        'modelInferenceRun': False, 'nativeActions': 0, 'g4Complete': False,
        'cases': [],
    }
    manifest = output / 'manifest.json'
    manifest.write_text(json.dumps(result, indent=2), encoding='utf-8')
    current = None
    try:
        for case in cases:
            current = case['id']
            index = case['preFrames'][0] - 1
            cap = cv2.VideoCapture(str(case['video']))
            try:
                if not cap.isOpened() or abs(cap.get(cv2.CAP_PROP_FPS) - case['sourceFps']) > .0001:
                    raise ValueError('native source fps changed')
                cap.set(cv2.CAP_PROP_POS_FRAMES, index)
                ok, bgr = cap.read()
                if not ok or abs(cap.get(cv2.CAP_PROP_POS_FRAMES) - (index + 1)) > .1:
                    raise ValueError('missing exact native prefix frame')
                if list(reversed(bgr.shape[:2])) != case['sourceSize']:
                    raise ValueError('native dimensions changed')
                pts = cap.get(cv2.CAP_PROP_POS_MSEC)
                if abs(pts - index / case['sourceFps'] * 1000) > .1:
                    raise ValueError('native prefix PTS not aligned')
                folder = output / current
                folder.mkdir()
                image = folder / f'{index:07}.png'
                if not cv2.imwrite(str(image), bgr):
                    raise ValueError('native prefix PNG write failed')
                result['cases'].append({
                    'caseId': current, 'videoSha256': case['videoSha256'],
                    'frameIndex': index, 'sourcePtsMs': round(pts, 6),
                    'atMs': round(pts, 6), 'image': str(image.resolve()),
                    'size': list(case['sourceSize']),
                    'sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
                    'reviewed': False, 'modelInferenceRun': False,
                })
                manifest.write_text(json.dumps(result, indent=2), encoding='utf-8')
            finally:
                cap.release()
    except Exception as error:
        (output / 'failure.json').write_text(json.dumps({
            'caseId': current, 'error': str(error), 'prefixBytesVerified': False,
            'g4Complete': False, 'nativeActions': 0,
        }, indent=2), encoding='utf-8')
        raise
    result['prefixBytesVerified'] = True
    manifest.write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result
