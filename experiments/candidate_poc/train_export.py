"""One bounded, offline candidate training attempt. No formal verifier imports.

This entry refuses unadmitted data; environment export smoke tests are not training.
The immutable attempt marker is consumed only after all data/weight checks succeed.
"""
import argparse
import hashlib
import io
import json
import math
import os
import uuid
from pathlib import Path
import shutil
import subprocess
import sys
import time
from PIL import Image
from annotation_audit import audit_full_frame
from freeze_inputs import POLICY, readiness

CLASSES = {'map_node': 0, 'entry_gate': 1}
PROJECT_BUDGET_ROOT = Path(__file__).resolve().parents[2]/'artifacts'/'candidate-poc-one-training-budget'
APPROVED_WEIGHTS_SHA256 = '9b09cc8bf347f0fc8a5f7657480587f25db09b34bf33b0652110fb03a8ad4fef'


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()


def validate_config(config):
    fixed = dict(modelArchitectureProposal='yolo26n', inputSize=640,
                 precision='FP32', seed=20261108, maxEpochs=50,
                 maxGpuSeconds=14400, maxTrainingRuns=1)
    if any(config.get(key) != value or type(config.get(key)) is not type(value)
           for key, value in fixed.items()):
        raise ValueError('UNAPPROVED_MODEL_OR_BUDGET')


def validate_weight_digest(digest):
    if digest != APPROVED_WEIGHTS_SHA256:
        raise ValueError('UNAPPROVED_WEIGHTS')


def validate_loaded_model(model):
    architecture=model.model.yaml
    if (model.task != 'detect' or architecture.get('scale') != 'n' or
            Path(architecture.get('yaml_file','')).name != 'yolo26n.yaml'):
        raise ValueError('UNAPPROVED_ARCHITECTURE')


def verify_pixels(record):
    raw = Path(record['image']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != record['imageSha256']:
        raise ValueError('IMAGE_HASH_MISMATCH')
    with Image.open(io.BytesIO(raw)) as image:
        if image.format != 'PNG' or image.mode != 'RGB' or list(image.size) != record['sourceSize']:
            raise ValueError('IMAGE_GEOMETRY_MISMATCH')
        image.load()
        if hashlib.sha256(image.tobytes()).hexdigest() != record['pixelSha256']:
            raise ValueError('PIXEL_HASH_MISMATCH')


def yolo_label(annotation, size):
    box = annotation['box']; width, height = size
    if (annotation['className'] not in CLASSES or annotation['visibility'] not in ('complete','partial') or
            len(box) != 4 or any(type(v) not in (int,float) or not math.isfinite(v) for v in box) or
            min(box[:2]) < 0 or min(box[2:]) <= 0 or box[0]+box[2] > width or box[1]+box[3] > height):
        raise ValueError('INVALID_SOURCE_BOX')
    x,y,w,h=box
    return f'{CLASSES[annotation["className"]]} {(x+w/2)/width:.17g} {(y+h/2)/height:.17g} {w/width:.17g} {h/height:.17g}'


def bound_json(reference):
    if sha(reference['path']) != reference['sha256']:
        raise ValueError('EVIDENCE_FILE_HASH_MISMATCH')
    return json.loads(Path(reference['path']).read_text(encoding='utf-8-sig'))


def review_for(reference, image_hash):
    data = bound_json(reference)
    records = data.get('records', data.get('frames', [data]))
    matches = [r for r in records if r.get('imageSha256') == image_hash]
    if len(matches) != 1:
        raise ValueError('REVIEW_SOURCE_NOT_UNIQUE')
    return matches[0]


def verify_qualified_records(manifest, config):
    raw = bound_json(config['rawCorpus'])
    originals = {r['imageSha256']:r for r in raw['records']}
    records = manifest['records']
    if len(originals) != 400 or set(originals) != {r['imageSha256'] for r in records}:
        raise ValueError('FROZEN_RAW_CORPUS_CHANGED')
    checked_sources = {}
    for record in records:
        original = originals[record['imageSha256']]
        for key in ('sourceId','sourceSha256','split','frameIndex','pixelSha256','sourceSize','runGroup'):
            if record.get(key) != original.get(key):
                raise ValueError('FROZEN_SOURCE_BINDING_CHANGED')
        verify_pixels(record)
        lineage = bound_json(record['provenanceEvidence'])
        if lineage.get('status') != 'QUALIFIED':
            raise ValueError('LINEAGE_NOT_QUALIFIED')
        for key in ('sourceId','sourceSha256','runGroup','layoutGroup'):
            if lineage.get(key) != record.get(key):
                raise ValueError('LINEAGE_BINDING_MISMATCH')
        source_path = str(Path(record['sourcePath']).resolve())
        if source_path not in checked_sources:
            checked_sources[source_path] = sha(source_path)
        if checked_sources[source_path] != record['sourceSha256']:
            raise ValueError('SOURCE_MEDIA_CHANGED')
        reviews = record.get('annotationReviews', [])
        if len(reviews) != 2:
            raise ValueError('TWO_REVIEWS_REQUIRED')
        first, second = [review_for(ref, record['imageSha256']) for ref in reviews]
        if (first.get('boundaryPolicy',first.get('policy')) != POLICY or
                second.get('boundaryPolicy',second.get('policy')) != POLICY or
                first.get('unresolved') or second.get('unresolved')):
            raise ValueError('ANNOTATION_POLICY_OR_UNRESOLVED')
        agreement = audit_full_frame(record, first, second)
        if not agreement['consistent']:
            raise ValueError('REVIEW_DISAGREEMENT: '+str(agreement['errors']))
        canonical = lambda items: [(x['className'],x['box'],x['visibility']) for x in items]
        if canonical(record['boxes']) != canonical(first['annotations']):
            raise ValueError('UNREVIEWED_LABEL_REPLACEMENT')
        for box in record['boxes']:
            yolo_label(box, record['sourceSize'])


def claim_attempt(output, receipt):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    with (output/'training-attempt.json').open('x',encoding='utf-8') as stream:
        json.dump(receipt,stream,indent=2)


def claim_training_attempt(output, receipt, budget_root=PROJECT_BUDGET_ROOT):
    # A new output name must not reset the project-wide one-experiment budget.
    claim_attempt(budget_root,dict(receipt,output=str(Path(output).resolve())))
    claim_attempt(output,receipt)


def should_stop(epoch_index, elapsed_seconds):
    return epoch_index >= 49 or elapsed_seconds >= 14400


def training_options(data, output):
    return dict(data=str(data),project=str(output),name='fit',exist_ok=False,
                epochs=50,time=None,imgsz=640,batch=4,device='cpu',workers=0,
                seed=20261108,deterministic=True,amp=False,cache=False,
                resume=False,pretrained=True,val=True,split='val',plots=False,
                save=True,save_period=1,patience=50)


def prepare_run(manifest, config, output, weights, weight_sha):
    validate_config(config)
    status=readiness(manifest)
    if not status['ready']:
        raise ValueError('DATA_NOT_READY: '+json.dumps(status,sort_keys=True))
    verify_qualified_records(manifest,config)
    validate_weight_digest(weight_sha)
    if sha(weights) != weight_sha:
        raise ValueError('PRETRAINED_WEIGHTS_CHANGED')
    output=Path(output).resolve()
    if (output/'training-attempt.json').exists():
        raise FileExistsError('SINGLE_TRAINING_ATTEMPT_ALREADY_CONSUMED')
    recipe=dict(config=config,weights=str(Path(weights).resolve()),weightSha256=weight_sha,
                manifest=manifest,output=str(output),epochs=50,
                wallSeconds=14400,scope='offline_candidate_only_no_action_authority')
    # Exclusive reservation precedes all training-side effects, including dataset copy.
    reservation=uuid.uuid4().hex
    recipe['reservation']=reservation
    claim_training_attempt(output,dict(status='RESERVED',reservation=reservation,supervisorPid=os.getpid(),trainingRunsConsumed=1,wallSeconds=14400,
                             configSha256=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()))
    dataset=output/'dataset'; dataset.mkdir()
    for record in manifest['records']:
        split=record['split']
        if split == 'test': continue  # Held-out pixels/labels are not copied into the fit dataset.
        image_dir=dataset/'images'/split; label_dir=dataset/'labels'/split
        image_dir.mkdir(parents=True,exist_ok=True); label_dir.mkdir(parents=True,exist_ok=True)
        name=record['imageSha256']; shutil.copyfile(record['image'],image_dir/(name+'.png'))
        labels=[yolo_label(box,record['sourceSize']) for box in record['boxes']]
        (label_dir/(name+'.txt')).write_text('\n'.join(labels)+('\n' if labels else ''),encoding='utf-8')
    # Intentionally no test key: test split is never selected by the trainer.
    yaml='path: '+json.dumps(str(dataset))+'\ntrain: images/train\nval: images/val\nnames:\n  0: map_node\n  1: entry_gate\n'
    data=dataset/'data.yaml'; data.write_text(yaml,encoding='utf-8')
    recipe['datasetFiles']={str(path.relative_to(dataset)):sha(path) for path in sorted(dataset.rglob('*')) if path.is_file()}
    recipe['data']=str(data); recipe_path=output/'recipe.json'
    recipe_path.write_text(json.dumps(recipe,indent=2),encoding='utf-8')
    launch=dict(reservation=reservation,supervisorPid=os.getpid(),recipeSha256=sha(recipe_path))
    with (output/'launch-receipt.json').open('x',encoding='utf-8') as stream:
        json.dump(launch,stream,indent=2)
    return recipe_path


def supervised_parent(expected_pid):
    if os.getppid() == expected_pid: return True
    # Windows venv redirectors insert exactly one interpreter-launcher process.
    # Accept that hop only when its executable is this same venv interpreter.
    import psutil
    try:
        launcher=psutil.Process(os.getppid())
        return (launcher.ppid() == expected_pid and
                Path(launcher.exe()).resolve() == Path(sys.executable).resolve())
    except (psutil.Error,OSError):
        return False


def claim_worker(recipe_path):
    try:
        recipe_path=Path(recipe_path).resolve()
        recipe=json.loads(recipe_path.read_text(encoding='utf-8'))
        output=Path(recipe['output']).resolve()
        if recipe_path != output/'recipe.json': raise ValueError('RECIPE_LOCATION')
        launch=json.loads((output/'launch-receipt.json').read_text(encoding='utf-8'))
        attempt=json.loads((output/'training-attempt.json').read_text(encoding='utf-8'))
        if (launch['recipeSha256'] != sha(recipe_path) or
                launch['reservation'] != attempt['reservation'] or
                launch['reservation'] != recipe['reservation'] or
                launch['supervisorPid'] != attempt['supervisorPid'] or
                not supervised_parent(launch['supervisorPid'])):
            raise ValueError('WORKER_BINDING')
        # The receipt is one-use even if the child fails before fitting.
        with (output/'worker-started.json').open('x',encoding='utf-8') as stream:
            json.dump(dict(recipeSha256=sha(recipe_path),pid=os.getpid()),stream)
        return recipe
    except (OSError,ValueError,KeyError,TypeError) as error:
        raise ValueError('UNAUTHORIZED_WORKER: '+str(error)) from error


def verify_fit_dataset(recipe):
    root=Path(recipe['output']).resolve()/'dataset'
    files={str(path.relative_to(root)):sha(path) for path in root.rglob('*') if path.is_file()}
    if files != recipe['datasetFiles'] or Path(recipe['data']).resolve() != root/'data.yaml':
        raise ValueError('FIT_DATASET_CHANGED')


def worker(recipe_path):
    recipe=claim_worker(recipe_path)
    validate_config(recipe['config'])
    if not readiness(recipe['manifest'])['ready']: raise ValueError('DATA_NOT_READY')
    verify_qualified_records(recipe['manifest'],recipe['config'])
    verify_fit_dataset(recipe)
    validate_weight_digest(recipe['weightSha256'])
    # Revalidate admission in the child, then import the training implementation.
    from ultralytics import YOLO
    if sha(recipe['weights']) != recipe['weightSha256']:
        raise ValueError('PRETRAINED_WEIGHTS_CHANGED')
    model=YOLO(recipe['weights']); validate_loaded_model(model)
    start=time.monotonic()
    def stop_at_epoch_end(trainer):
        if should_stop(trainer.epoch,time.monotonic()-start): trainer.stop=True
    def stop_at_batch_end(trainer):
        if time.monotonic()-start >= recipe['wallSeconds']: trainer.stop=True
    model.add_callback('on_train_epoch_end',stop_at_epoch_end)
    model.add_callback('on_train_batch_end',stop_at_batch_end)
    model.train(**training_options(recipe['data'],recipe['output']))
    model.export(format='onnx',imgsz=640,batch=1,half=False,dynamic=False,simplify=False,opset=17,device='cpu')


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--manifest'); parser.add_argument('--config')
    parser.add_argument('--output'); parser.add_argument('--weights'); parser.add_argument('--weights-sha256')
    parser.add_argument('--worker'); args=parser.parse_args()
    if args.worker: worker(args.worker); return
    manifest=json.loads(Path(args.manifest).read_text(encoding='utf-8-sig'))
    config=json.loads(Path(args.config).read_text(encoding='utf-8-sig'))
    recipe=prepare_run(manifest,config,args.output,args.weights,args.weights_sha256)
    started=time.monotonic(); status='FAILED'; code=1
    try:
        with (Path(args.output)/'training.log').open('x',encoding='utf-8') as log:
            run=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--worker',str(recipe)],
                               stdout=log,stderr=subprocess.STDOUT,timeout=14400)
        code=run.returncode; status='FINISHED' if code==0 else 'FAILED'
    except subprocess.TimeoutExpired:
        status='WALL_LIMIT_REACHED'
    finally:
        (Path(args.output)/'training-result.json').write_text(json.dumps(dict(status=status,returncode=code,
                wallSeconds=time.monotonic()-started,trainingRunsConsumed=1),indent=2),encoding='utf-8')
    raise SystemExit(code)

if __name__ == '__main__': main()
