"""Prepare source-isolated, unlabelled QA frames; no model or game control."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import time
import cv2
from PIL import Image


def validate_reservations(rows, protected_ids):
    errors = set(); ids = {}; hashes = {}
    for row in rows:
        key, split = row.get('id'), row.get('split')
        if not isinstance(key, str) or not key:
            errors.add('SOURCE_ID_MISSING'); continue
        if key in protected_ids:
            errors.add('PROTECTED_SOURCE_ID')
        if split not in ('train', 'val', 'test'):
            errors.add('INVALID_SPLIT')
        if key in ids and ids[key] != split:
            errors.add('SOURCE_CROSS_SPLIT')
        ids[key] = split
        digest = row.get('sha256')
        if digest:
            if digest in hashes and hashes[digest] != key:
                errors.add('BYTE_DUPLICATE_SOURCE')
            hashes[digest] = key
    return sorted(errors)


def extract_frame(video, index, target):
    target = Path(target)
    if target.exists():
        raise FileExistsError(target)
    cap = cv2.VideoCapture(str(video))
    try:
        count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps = cap.get(cv2.CAP_PROP_FPS)
        if type(index) is not int or not 0 <= index < count or fps <= 0:
            raise ValueError('FRAME_INDEX_INVALID')
        if not cap.set(cv2.CAP_PROP_POS_FRAMES, index):
            raise ValueError('FRAME_SEEK_FAILED')
        ok, bgr = cap.read()
        actual = round(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
        if not ok or actual != index:
            raise ValueError('FRAME_DECODE_MISMATCH')
        pts = cap.get(cv2.CAP_PROP_POS_MSEC)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb)
        buf = io.BytesIO(); image.save(buf, format='PNG'); raw = buf.getvalue()
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(raw)
        return dict(image=str(target.resolve()), imageSha256=hashlib.sha256(raw).hexdigest(),
                    pixelSha256=hashlib.sha256(image.tobytes()).hexdigest(),
                    sourceSize=list(image.size), frameIndex=actual, sourcePtsMs=pts,
                    frameIndexPtsMs=actual / fps * 1000, sourceFps=fps,
                    reviewed=False, independentReviews=0, trainingAdmitted=False)
    finally:
        cap.release()


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recipe', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    started = time.perf_counter(); recipe_path = Path(args.recipe)
    recipe = json.loads(recipe_path.read_text(encoding='utf-8'))
    errors = validate_reservations(recipe['sources'], recipe['protectedSourceIds'])
    if errors:
        raise ValueError(','.join(errors))
    out = Path(args.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / 'qa-frames.json'
    if manifest_path.exists():
        raise FileExistsError(manifest_path)
    rows = []
    for source in recipe['sources']:
        selected = source.get('selectedFrames', [])
        if not selected:
            continue  # Validation and blind test remain metadata-only at this stage.
        if source['split'] != 'train':
            raise ValueError('QA_REQUIRES_TRAIN_ONLY')
        if file_hash(source['path']) != source['sha256']:
            raise ValueError('SOURCE_CHANGED')
        for index in selected:
            row = extract_frame(source['path'], index, out / 'raw' / f'{source["id"]}-{index:07d}.png')
            row.update(sourceId=source['id'], sourceSha256=source['sha256'], split=source['split'],
                       runGroup=source['runGroup'], layoutGroupStatus='UNREVIEWED',
                       purpose='boundary_QA_only_not_training_admission')
            rows.append(row)
    manifest_path.write_text(json.dumps(dict(schema=1, recipeSha256=file_hash(recipe_path), records=rows,
                                           seconds=time.perf_counter()-started, nativeActions=0,
                                           modelInferenceRun=False), indent=2), encoding='utf-8')
    print(json.dumps({'rawFrames': len(rows), 'trainingAdmitted': 0, 'seconds': time.perf_counter()-started}))


if __name__ == '__main__':
    main()
