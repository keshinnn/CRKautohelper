"""Read original pixels for exact duplicate and conservative pHash triage.

Perceptual similarity is a review queue, never proof of identical run/layout or
independence. No candidate model, labels, or frozen truth is read.
"""
import hashlib
import io
from pathlib import Path
import cv2
import numpy as np
from PIL import Image


def signature(record):
    raw = Path(record['image']).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if record.get('imageSha256') != digest:
        raise ValueError('DATA_IMAGE_CHANGED: ' + record['image'])
    with Image.open(io.BytesIO(raw)) as image:
        if image.format != 'PNG' or image.mode != 'RGB':
            raise ValueError('RGB_PNG_REQUIRED')
        image.load()
        rgb_hash = hashlib.sha256(image.tobytes()).hexdigest()
        gray = np.asarray(image.resize((32, 32), Image.Resampling.BILINEAR).convert('L'), dtype=np.float32)
        low_information = float(gray.std()) < 2
        dct = cv2.dct(gray)[:8, :8].ravel()[1:]
        bits = dct > float(np.median(dct))
        phash = None if low_information else int(''.join('1' if x else '0' for x in bits), 2)
    return dict(image=record['image'], split=record['split'], imageSha256=digest, sourceSize=list(image.size),
                pixelSha256=rgb_hash, phash=phash, lowInformation=low_information)


def audit_duplicates(records, protected):
    result = dict(crossSplitExactRgb=[], protectedExactRgb=[], withinSplitExactRgb=[],
                  lowInformationImages=[], nearPairsForReview=[], nearPairsCount=0,
                  nearPairsTruncated=False, trainingAdmitted=False,
                  perceptualIndependenceProven=False, nearHammingDistance=4,
                  scope='pixel_identity_and_whole_frame_similarity_triage_not_layout_certification')
    new = [signature(r) for r in records]
    old = [signature({**r, 'split': 'protected'}) for r in protected]
    result.update(newImages=len(new), protectedImages=len(old))
    for i, a in enumerate(new):
        if a['lowInformation']:
            result['lowInformationImages'].append(a['image'])
        for b in new[:i] + old:
            pair = dict(first=a['image'], second=b['image'], firstSplit=a['split'], secondSplit=b['split'])
            if a['pixelSha256'] == b['pixelSha256'] and a['sourceSize'] == b['sourceSize']:
                key = 'protectedExactRgb' if b['split'] == 'protected' else 'withinSplitExactRgb' if a['split'] == b['split'] else 'crossSplitExactRgb'
                result[key].append(pair)
            elif a['split'] != b['split'] and a['phash'] is not None and b['phash'] is not None:
                distance = (a['phash'] ^ b['phash']).bit_count()
                if distance <= 4:
                    result['nearPairsCount'] += 1
                    if len(result['nearPairsForReview']) < 5000:
                        result['nearPairsForReview'].append({**pair, 'hammingDistance': distance})
                    else:
                        result['nearPairsTruncated'] = True
    result['newSignatures'] = new
    return result
