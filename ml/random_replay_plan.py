"""Evaluator-side plans and frozen transformed pixels; no recognition/input."""
import copy
import hashlib
import io
import json
import math
import re
from pathlib import Path

from PIL import Image

from random_client_transform import sample_layout, transform_box, transform_png


def _sha(value):
    return isinstance(value, str) and re.fullmatch(r'[a-f0-9]{64}', value) is not None


def _box(value, size):
    return (isinstance(value, list) and len(value) == 4
            and all(type(x) in (int, float) and math.isfinite(x) for x in value)
            and min(value[:2]) >= 0 and min(value[2:]) > 0
            and value[0] + value[2] <= size[0]
            and value[1] + value[3] <= size[1])


def _frame(entry, size, fps):
    index = entry.get('frameIndex')
    if type(index) is not int or index < 0:
        raise ValueError('native frame index required')
    pts = round(index / fps * 1000, 6)
    if (entry.get('size') != size or not _sha(entry.get('sha256'))
            or not isinstance(entry.get('image'), str) or not entry['image']
            or any(type(entry.get(k)) not in (int, float)
                   or not math.isfinite(entry[k]) or abs(entry[k] - pts) > .001
                   for k in ['sourcePtsMs', 'atMs'])):
        raise ValueError('native frame binding or PTS invalid')


def plan_sequences(case, anchors, prefix, annotation_sha):
    """Return three unrendered plans. All layouts/truth stay evaluator-side."""
    name = case.get('id')
    size, fps, pre = case.get('sourceSize'), case.get('sourceFps'), case.get('preFrames')
    frames, video = case.get('frames'), case.get('videoSha256')
    if (not _sha(annotation_sha) or not _sha(video)
            or not isinstance(name, str)
            or re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,99}', name) is None
            or case.get('reviewed') is not True or anchors.get('reviewed') is not True
            or anchors.get('caseId') != name or anchors.get('videoSha256') != video
            or anchors.get('annotationSha256') != annotation_sha
            or prefix.get('reviewed') is not True or prefix.get('videoSha256') != video
            or type(fps) is not int or fps not in (30, 60)
            or not isinstance(size, list) or len(size) != 2
            or any(type(x) is not int or x < 1 for x in size)
            or anchors.get('sourceSize') != size
            or not isinstance(pre, list) or len(pre) != 2
            or any(type(x) is not int for x in pre) or pre[0] < 1
            or pre[1] - pre[0] < fps * .2
            or not isinstance(frames, list) or len(frames) < 3):
        raise ValueError('reviewed frozen source, anchors and prefix required')
    for entry in [prefix, *frames]:
        _frame(entry, size, fps)
    if (prefix['frameIndex'] != pre[0] - 1
            or [f['frameIndex'] for f in frames]
            != [pre[0], *range(pre[1], frames[-1]['frameIndex'] + 1)]):
        raise ValueError('native source sequence or prefix invalid')
    gate = case.get('gateWindowMs')
    if (not isinstance(gate, list) or len(gate) != 2
            or any(type(t) not in (int, float) or not math.isfinite(t)
                   or abs(t - frames[1]['atMs']) > .001 for t in gate)):
        raise ValueError('dispatch gate must remain on original second preframe')
    target, safe = case.get('expectedBox'), case.get('clientBox')
    if not _box(target, size) or not _box(safe, size):
        raise ValueError('reviewed target and safe boxes required')
    if not (target[0] <= safe[0] and target[1] <= safe[1]
            and safe[0] + safe[2] <= target[0] + target[2]
            and safe[1] + safe[3] <= target[1] + target[3]):
        raise ValueError('safe box outside target')
    boxes = anchors.get('boxes')
    if not isinstance(boxes, list) or not boxes or not all(_box(b, size) for b in boxes):
        raise ValueError('reviewed crop anchors invalid')

    layouts, seen_sizes = {}, set()
    for phase in ['fixed', 'pre-old', 'pre-new', 'post-old', 'post-new']:
        for attempt in range(64):
            namespace = f'{annotation_sha}:{video}:{name}:{phase}:{attempt}'
            seed = int(hashlib.sha256(namespace.encode()).hexdigest()[:16], 16)
            layout = sample_layout(size, [*boxes, target], seed)
            output_size = tuple(layout['outputSize'])
            if output_size not in seen_sizes and layout['sx'] != layout['sy']:
                layouts[phase] = layout
                seen_sizes.add(output_size)
                break
        else:
            raise ValueError('cannot derive distinct nonuniform client layouts')

    plans = []
    for mode, dispatch_phase in [('fixed', 'fixed'), ('pre-change', 'pre-new'),
                                 ('post-change', 'post-old')]:
        original = [prefix, *frames] if mode == 'pre-change' else frames
        rendered = []
        for position, entry in enumerate(original):
            phase = ('fixed' if mode == 'fixed' else
                     ('pre-old' if position == 0 else 'pre-new') if mode == 'pre-change'
                     else ('post-old' if position < 2 else 'post-new'))
            layout = layouts[phase]
            geometry = hashlib.sha256(json.dumps(layout, sort_keys=True).encode()).hexdigest()
            rendered.append({
                'sourceImage': entry['image'], 'sourceImageSha256': entry['sha256'],
                'originalSize': list(size), 'frameIndex': entry['frameIndex'],
                'sourcePtsMs': entry['sourcePtsMs'], 'atMs': entry['atMs'],
                'size': list(layout['outputSize']), 'geometryVersion': 'random:' + geometry,
                'renderLayout': copy.deepcopy(layout), 'renderPending': True,
            })
        result = copy.deepcopy(case)
        result.update({
            'id': name + '-random-' + mode, 'parentCaseId': name,
            'transformMode': mode, 'annotationSha256': annotation_sha,
            'frames': rendered, 'pixelsRendered': False, 'scale': None,
            'originalExpectedBox': list(target), 'originalClientBox': list(safe),
            'expectedBox': transform_box(target, layouts[dispatch_phase]),
            'clientBox': transform_box(safe, layouts[dispatch_phase]),
            'previewFromPtsMs': frames[2]['sourcePtsMs'],
            'layoutPlan': copy.deepcopy(layouts), 'passed': False,
            'anchorReview': copy.deepcopy(anchors),
            'prefixQualification': {
                'reviewed': True, 'videoSha256': video,
                'frameIndex': prefix['frameIndex'], 'imageSha256': prefix['sha256'],
                'sourcePtsMs': prefix['sourcePtsMs'], 'size': list(size),
            },
            'g4Complete': False, 'nativeActions': 0,
            'source': {'videoSha256': video, 'startPtsMs': original[0]['sourcePtsMs'],
                       'endPtsMs': original[-1]['sourcePtsMs']},
        })
        plans.append(result)
    return plans


def _save_manifest(output, manifest):
    pending = output / '.manifest.pending.json'
    with pending.open('x', encoding='utf-8') as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
    pending.replace(output / 'manifest.json')


def render_sequences(plans, output):
    """Render one reviewed case's three plans into a new immutable run."""
    if (not isinstance(plans, list) or len(plans) != 3
            or {p.get('transformMode') for p in plans}
            != {'fixed', 'pre-change', 'post-change'}
            or len({p.get('parentCaseId') for p in plans}) != 1
            or len({p.get('annotationSha256') for p in plans}) != 1):
        raise ValueError('three related frozen layout plans required')
    for plan in plans:
        if (plan.get('pixelsRendered') is not False
                or re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,127}',
                                plan.get('id', '')) is None):
            raise ValueError('unrendered safe case id required')
    output = Path(output)
    output.mkdir()
    snapshot = json.dumps(plans, sort_keys=True, ensure_ascii=False, indent=2).encode()
    (output / 'plans.snapshot.json').write_bytes(snapshot)
    manifest = {
        'stage': 'P4-C-transform-source', 'pixelsRendered': False,
        'inputPlanSha256': hashlib.sha256(snapshot).hexdigest(),
        'generatorCodeSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'cases': [], 'nativeActions': 0, 'g4Complete': False,
    }
    _save_manifest(output, manifest)
    current_case, current_frame = None, None
    try:
        for plan in plans:
            current_case = plan['id']
            folder = output / current_case
            folder.mkdir()
            rendered = []
            for entry in plan['frames']:
                current_frame = entry['frameIndex']
                source = Path(entry['sourceImage'])
                raw = source.read_bytes()
                if hashlib.sha256(raw).hexdigest() != entry['sourceImageSha256']:
                    raise ValueError('source PNG changed')
                with Image.open(io.BytesIO(raw)) as image:
                    if image.format != 'PNG' or list(image.size) != entry['originalSize']:
                        raise ValueError('source PNG size or format changed')
                layout = entry['renderLayout']
                geometry = 'random:' + hashlib.sha256(
                    json.dumps(layout, sort_keys=True).encode()).hexdigest()
                if (entry['geometryVersion'] != geometry
                        or layout['inputSize'] != entry['originalSize']
                        or layout['outputSize'] != entry['size']):
                    raise ValueError('layout geometry binding changed')
                actual = transform_png(source, layout, folder / f'{current_frame:07}.png')
                if actual['transform']['inputSha256'] != entry['sourceImageSha256']:
                    raise ValueError('source PNG changed while rendering')
                clean = {k: copy.deepcopy(v) for k, v in entry.items()
                         if k not in ('renderLayout', 'packet')}
                rendered.append({**clean, **actual, 'renderPending': False})
            manifest['cases'].append({
                **copy.deepcopy(plan), 'frames': rendered, 'pixelsRendered': True,
                'passed': False, 'g4Complete': False,
            })
            _save_manifest(output, manifest)
    except Exception as error:
        (output / 'failure.json').write_text(json.dumps({
            'caseId': current_case, 'frameIndex': current_frame,
            'error': str(error), 'pixelsRendered': False,
            'g4Complete': False, 'nativeActions': 0,
        }, indent=2), encoding='utf-8')
        raise
    manifest['pixelsRendered'] = True
    _save_manifest(output, manifest)
    return manifest
