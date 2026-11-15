"""Bounded A2 measurement only. Never creates a formal registration/proof.

SIFT numeric settings mirror the existing pixel registration; proposal masks
replace its unavailable four-column graph ONLY for a diagnostic. A good pixel
fit is not a calibrated map, semantic correspondence, identity, or authority.
"""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT/'artifacts/candidate-research-pilot-20261112-01'
OUT = ROOT/'artifacts/candidate-registration-research-20261112-01'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2), encoding='utf-8')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pair_blockers(a, b):
    reasons = []
    if not a.get('sourceKey') or a.get('sourceKey') != b.get('sourceKey'):
        reasons.append('SOURCE_CHANGED')
    if a.get('geometryVersion') != b.get('geometryVersion') or a['sourceSize'] != b['sourceSize']:
        reasons.append('GEOMETRY_CHANGED')
    delta = b['atMs']-a['atMs']
    if not math.isfinite(delta) or delta <= 0:
        reasons.append('NONCAUSAL_PAIR')
    elif delta > 2500:
        reasons.append('PAIR_AGE_EXCEEDED')
    if a['imageSha256'] == b['imageSha256']:
        reasons.append('DUPLICATE_IMAGE')
    if a.get('pixelSha256') and a['pixelSha256'] == b.get('pixelSha256'):
        reasons.append('DUPLICATE_PIXELS')
    return reasons


def non_authority_result(measurements):
    return {**measurements, 'researchOnly': True, 'registrationVerified': False,
            'identityVerified': False, 'outerBoundaryVerified': False,
            'mapLocationVerified': False,
            'capabilities': dict(select=False, confirm=False, dispatch=False)}


def box_error(predicted, truth):
    x, y, w, h = predicted
    tx, ty, tw, th = truth
    return dict(widthRatio=w/tw, heightRatio=h/th,
                centerDelta=[x+w/2-tx-tw/2, y+h/2-ty-th/2],
                correctionApplied=False)


def pixel_probe(a, b, pa, pb):
    """Raw-image diagnostic. Candidate confidence never becomes a score/proof."""
    import cv2
    import numpy as np
    start = time.perf_counter()
    cv2.setNumThreads(6)
    cv2.setRNGSeed(20261112)
    prepared = []
    measured_sources = []
    for source, prediction in [(a, pa), (b, pb)]:
        if sha(source['image']) != source['imageSha256'] or prediction['imageSha256'] != source['imageSha256']:
            raise ValueError('SOURCE_CHANGED')
        with Image.open(source['image']) as original:
            im = original.convert('RGB')
        if list(im.size) != source['sourceSize']:
            raise ValueError('SIZE_CHANGED')
        digest = hashlib.sha256(im.tobytes()).hexdigest()
        if source.get('pixelSha256') and source['pixelSha256'] != digest:
            raise ValueError('SOURCE_PIXELS_CHANGED')
        measured_sources.append(dict(source, pixelSha256=digest))
        factor = 960/im.width
        view = im.resize((960, round(im.height*factor)))
        gray = cv2.cvtColor(np.array(view), cv2.COLOR_RGB2GRAY)
        mask = np.zeros_like(gray)
        for obj in prediction['boxes']:
            if obj['className'] != 'map_node':
                continue
            x, y, w, h = [v*factor for v in obj['box']]
            # Raster clipping affects an analysis mask only, never candidate coordinates.
            mask[max(0, math.floor(y)):min(gray.shape[0], math.ceil(y+h)),
                 max(0, math.floor(x)):min(960, math.ceil(x+w))] = 255
        key, desc = cv2.SIFT_create(nfeatures=4500, contrastThreshold=.025).detectAndCompute(gray, mask)
        prepared.append((factor, key, desc))
    x, y = prepared
    result = dict(pairBlockers=pair_blockers(*measured_sources), keypoints=[len(x[1]), len(y[1])],
                  normalizationWidth=960, mask='proposal rectangles; NOT formal four-column calibration',
                  transformCandidates=[], mutualMatches=0)
    if x[2] is not None and y[2] is not None:
        matcher = cv2.BFMatcher()
        fwd = matcher.knnMatch(x[2], y[2], k=2)
        rev = matcher.knnMatch(y[2], x[2], k=2)
        reverse = {m.queryIdx: m.trainIdx for pair in rev if len(pair) == 2
                   for m, n in [pair] if m.distance < .70*n.distance}
        good = [m for pair in fwd if len(pair) == 2 for m, n in [pair]
                if m.distance < .70*n.distance and reverse.get(m.trainIdx) == m.queryIdx]
        result['mutualMatches'] = len(good)
        src = np.float32([x[1][m.queryIdx].pt for m in good])
        dst = np.float32([y[1][m.trainIdx].pt for m in good])
        remaining = np.ones(len(src), dtype=bool)
        for _ in range(4):
            if int(remaining.sum()) < 18:
                break
            ss, dd = src[remaining], dst[remaining]
            matrix, inlier = cv2.estimateAffinePartial2D(ss, dd, method=cv2.RANSAC,
                ransacReprojThreshold=2, maxIters=4000, confidence=.999)
            if matrix is None or inlier is None:
                break
            selected = inlier.ravel().astype(bool)
            count = int(selected.sum())
            if count < 18:
                break
            remaining[np.flatnonzero(remaining)[selected]] = False
            scale = float(np.hypot(matrix[0, 0], matrix[1, 0]))
            angle = math.degrees(math.atan2(matrix[1, 0], matrix[0, 0]))
            shifts = dd[selected]-ss[selected]
            translation = np.median(shifts, axis=0)
            residual = np.linalg.norm(shifts-translation, axis=1)
            numeric = count/len(ss) >= .30 and .985 <= scale <= 1.015 and abs(angle) <= .6 and float(np.quantile(residual, .9)) <= 2.5
            result['transformCandidates'].append(dict(inliers=count, scale=scale, angleDegrees=angle,
                translation=translation.tolist(), residualP90=float(np.quantile(residual, .9)),
                span=np.ptp(ss[selected], axis=0).tolist(), pixelFitWithinLegacyNumericBounds=numeric,
                inlierNormalizedPixelPairs=[dict(before=u.tolist(), after=v.tolist()) for u, v in zip(ss[selected], dd[selected])],
                semanticNodePairsNotProven=True))
    result['elapsedMs'] = (time.perf_counter()-start)*1000
    return non_authority_result(result)


def main():
    from research_pilot import predict_images, score
    from research_evidence import make_witness
    OUT.mkdir(exist_ok=True)
    if (OUT/'inputs.json').exists():
        raise ValueError('BOUNDED_EXPERIMENT_ALREADY_STARTED')
    # Fixed original transaction reference, not a later/easier anchor.
    actual = read(PILOT/'actual-preview-inputs.json')['records']
    inputs = []
    for item in actual:
        case = read(ROOT/f"artifacts/concentrated-repair-20261103-02/current-case{item['case']}-fresh-01/manifest.json")['cases'][0]
        pre = next(f for f in case['frames'] if f['frameIndex'] == case['preFrames'][-1])
        first = case['frames'][item['index']]
        second = None
        for f in case['frames'][item['index']+1:]:
            if f['atMs']-first['atMs'] >= 200 and read(f['packet']).get('v2PreviewContext', {}).get('verified') is True:
                second = f
                break
        for phase, frame in [('reference', pre), ('preview1', first), ('preview2', second)]:
            if frame is None:
                continue
            inputs.append(dict(case=item['case'], phase=phase, image=frame['image'],
                imageSha256=frame['sha256'], sourceSize=frame['size'], atMs=frame['atMs'],
                pixelSha256=hashlib.sha256(Image.open(frame['image']).convert('RGB').tobytes()).hexdigest(),
                sourceKey=case['videoSha256'], geometryVersion=frame['geometryVersion'],
                frameIndex=frame['frameIndex'], packet=frame['packet']))
    save('inputs.json', dict(selection='last frozen preFrame; first saved same-frame preview context; next context >=200ms; no model-dependent selection', records=inputs))
    model = PILOT/'fit/research-model/weights/best.pt'
    if sha(model) != '2cb09b53a29899067b1885ee2ac9740bc93fc4923ea28a75df6b0f5046e65e94':
        raise ValueError('MODEL_CHANGED')
    predictions = predict_images(model, inputs, OUT/'predictions.json')
    paired = []
    for number in sorted({x['case'] for x in inputs}):
        group = [(x, p) for x, p in zip(inputs, predictions) if x['case'] == number]
        for i in range(1, len(group)):
            a, pa = group[0]
            b, pb = group[i]
            paired.append(dict(case=number, phases=[a['phase'], b['phase']],
                ageMs=b['atMs']-a['atMs'], result=pixel_probe(a, b, pa, pb)))
        if len(group) == 3:
            a, pa = group[1]; b, pb = group[2]
            paired.append(dict(case=number, phases=['preview1', 'preview2'],
                ageMs=b['atMs']-a['atMs'], result=pixel_probe(a, b, pa, pb)))
    save('pixel-diagnostics.json', dict(records=paired, actionAuthority=False,
        note='Pixel fit numeric checks only; semantic pairs, four-column spans and independent fit validation NOT established.'))
    # Independent Node checks reproduce source geometry/gradients only.
    witnesses = []
    for src, pred in zip(inputs, predictions):
        context = dict(frameToken=src['imageSha256'][:20], sourceKey=src['sourceKey'],
                       geometryEpoch=src['geometryVersion'], atMs=src['atMs'], nowMs=src['atMs'],
                       imageSha256=src['imageSha256'])
        for index, obj in enumerate(pred['boxes']):
            try:
                witness = make_witness(src['image'], obj['box'], context)
                witnesses.append(dict(case=src['case'], phase=src['phase'], index=index,
                    image=src['image'], context=context, witness=witness))
            except ValueError as error:
                witnesses.append(dict(case=src['case'], phase=src['phase'], index=index, rejected=str(error)))
    save('geometry-witnesses.json', witnesses)
    js = "const fs=require('fs'),v=require('./experiments/candidate_poc/verify_research.cjs');const r=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));console.log(JSON.stringify(r.map(x=>({...x,witness:undefined, stage:x.rejected?'PYTHON_WITNESS_PRODUCTION':'NODE_INDEPENDENT_CHECK', result:x.rejected?{status:'REJECTED',reason:x.rejected,capabilities:{select:false,confirm:false,dispatch:false}}:v.verify(fs.readFileSync(x.image),x.witness,x.context)}))));"
    verified = subprocess.run(['node', '-e', js, str(OUT/'geometry-witnesses.json')],
                              cwd=ROOT, capture_output=True, text=True, check=True, timeout=180)
    save('independent-node-results.json', json.loads(verified.stdout))
    # Separate scorer reads frozen target truth only AFTER predictions persisted.
    old = read(PILOT/'challenge-predictions.json')['records']
    truth = read(PILOT/'challenge-scorer-truth.json')['records']
    errors = []
    for t in truth:
        if not t['id'].endswith('-map'):
            continue
        p = next(p for p in old if p['imageSha256'] == t['imageSha256'])
        ranked = []
        for box in p['boxes']:
            if box['className'] != 'map_node':
                continue
            matches = score([box], [dict(box=t['expectedBox'], className='map_node')], .5)['pairs']
            ranked.append((matches[0]['iou'] if matches else 0, box))
        _, obj = max(ranked, key=lambda x: x[0])
        errors.append(dict(case=t['case'], box=obj['box'], truth=t['expectedBox'],
                           **box_error(obj['box'], t['expectedBox'])))
    save('box-error-diagnostics.json', dict(records=errors, correctionApplied=False))


if __name__ == '__main__':
    main()
