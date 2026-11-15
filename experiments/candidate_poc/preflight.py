"""Read-only A0 inventory and content-verified baseline archive. No training."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import zipfile
from freeze_inputs import readiness


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def lock_baseline(root, verification, target):
    root, target = Path(root), Path(target)
    if target.exists():
        raise FileExistsError(target)
    entries = []
    for name, expected in verification['code'].items():
        source = root / name
        entries.append((source, 'source/' + name.replace('\\', '/'), expected))
    for i, (name, expected) in enumerate(verification['externalDependencies'].items()):
        source = Path(name)
        entries.append((source, f'external/{i:03d}/{source.name}', expected))
    for source, _, expected in entries:
        if not source.is_file() or digest(source) != expected:
            raise ValueError('BASELINE_CHANGED: ' + str(source))
    # Exclusive creation and read-back verification preserve the previous snapshot.
    with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for source, member, _ in entries:
            archive.write(source, member)
        archive.writestr('restore-index.json', json.dumps([
            {'original': str(s), 'member': m, 'sha256': h} for s, m, h in entries], indent=2))
    with zipfile.ZipFile(target) as archive:
        for _, member, expected in entries:
            if hashlib.sha256(archive.read(member)).hexdigest() != expected:
                raise ValueError('ARCHIVE_ROUNDTRIP_FAILED: ' + member)
    return {'verifiedFiles': len(entries), 'roundtripVerified': True,
            'sourceFiles': len(verification['code']),
            'dependencyFiles': len(verification['externalDependencies']),
            'archiveSha256': digest(target), 'archiveBytes': target.stat().st_size}


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def negative_suite(verification):
    return next(s for s in verification['suites'] if s['label'] == 'current-negative30' and s.get('resultsCount', len(s.get('results', []))) == 30)


def negative_cases(root):
    root = Path(root)
    report = json.loads((root / 'report.json').read_text(encoding='utf-8-sig'))
    cases = []
    for result in report['results']:
        manifest_path = root / result['id'] / 'analysis/manifest.json'
        if digest(manifest_path) != result['analysisManifestSha256']:
            raise ValueError('NEGATIVE_MANIFEST_CHANGED')
        manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
        if len(manifest['cases']) != 1:
            raise ValueError('NEGATIVE_CASE_COUNT_CHANGED')
        case = manifest['cases'][0]
        cases.append({'id': result['id'], 'manifest': str(manifest_path),
                      'manifestSha256': digest(manifest_path), 'frames': case['frames']})
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    parser.add_argument('--resume', action='store_true', help='Verify the immutable archive before resuming an interrupted inventory')
    args = parser.parse_args()
    started = time.perf_counter()
    root = Path(__file__).resolve().parents[2]
    out = Path(args.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    verification_path = root / 'artifacts/concentrated-repair-20261103-02/verification.json'
    verification = json.loads(verification_path.read_text(encoding='utf-8-sig'))
    if args.resume:
        baseline = json.loads((out / 'baseline.json').read_text(encoding='utf-8'))
        if baseline['archiveSha256'] != digest(out / 'baseline.zip'):
            raise ValueError('ARCHIVE_CHANGED')
        with zipfile.ZipFile(out / 'baseline.zip') as archive:
            for item in json.loads(archive.read('restore-index.json')):
                if digest(item['original']) != item['sha256'] or hashlib.sha256(archive.read(item['member'])).hexdigest() != item['sha256']:
                    raise ValueError('BASELINE_CHANGED_ON_RESUME')
    else:
        baseline = lock_baseline(root, verification, out / 'baseline.zip')
    baseline.update(commit=verification['commit'], dirtySource=verification['dirtySource'],
                    verificationSha256=digest(verification_path),
                    frozenManifestSha256=digest(root / 'artifacts/p4c-random-native-30-v3-pixels-01/manifest.json'),
                    historicalDevelopmentPass=48, historicalDevelopmentFail=12,
                    newReplayRun=False, nativeActions=0)
    write_json(out / 'baseline.json', baseline)

    corpus_path = root / 'data/p4c/corpus-30-v3.json'
    corpus = json.loads(corpus_path.read_text(encoding='utf-8-sig'))
    sources = {}
    for case in corpus['cases']:
        key = case['videoSha256']
        item = sources.setdefault(key, {'path': case['video'], 'sha256': key, 'frozenInteractions': 0,
                                        'historicallyExposed': True, 'certifiedNewTrainingFrames': 0})
        item['frozenInteractions'] += 1
    import cv2
    for key, source in sources.items():
        video = Path(source['path']); source['exists'] = video.is_file()
        if video.is_file():
            source['actualSha256'] = digest(video)
            source['hashMatches'] = source['actualSha256'] == key
            cap = cv2.VideoCapture(str(video))
            source.update(width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                          height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                          fps=cap.get(cv2.CAP_PROP_FPS), frames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
            cap.release()
    # No unreviewed pixels, existing detector outputs, or frozen annotations are
    # silently promoted to independently reviewed new training labels.
    admission = {'schema': 1, 'records': [], 'excludedSourceHashes': sorted(sources),
                 'policy': 'Conservatively exclude exposed source videos until run/layout provenance and independent labels are certified.',
                 'sourceCorpusSha256': digest(corpus_path)}
    write_json(out / 'dataset-admission.json', admission)
    write_json(out / 'data-readiness.json', {**readiness(admission), 'sources': list(sources.values()),
               'qualifiedNewDatasetSupplied': False,
               'gap': '240 train / 80 val / 80 independent test with verified lineage and reviewed visible-boundary labels; pixels exist but no such certified dataset is present.'})

    versions = {}
    for name in ('torch', 'torchvision', 'ultralytics', 'onnxruntime', 'onnx', 'numpy', 'opencv-python', 'Pillow'):
        try: versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: versions[name] = None
    probe = subprocess.run([sys.executable, '-B', '-c',
        'import torch,json;print(json.dumps(dict(version=torch.__version__,cudaBuilt=torch.version.cuda,cudaAvailable=torch.cuda.is_available(),cudaDevices=torch.cuda.device_count(),cpuThreads=torch.get_num_threads())))'],
        capture_output=True, text=True, timeout=45)
    torch_info = json.loads(probe.stdout) if probe.returncode == 0 else {'error': probe.stderr[-2000:]}
    write_json(out / 'environment.json', {'python': sys.version, 'executable': sys.executable,
               'platform': platform.platform(), 'processor': platform.processor(), 'logicalCpus': os.cpu_count(),
               'versions': versions, 'torchProbe': torch_info,
               'trainingEnvironmentReady': False, 'isolatedTrainingEnvironmentCreated': False,
               'missingPackages': [n for n in ('ultralytics', 'onnx') if versions[n] is None],
               'gpuInterpretation': 'CUDA not available to this installed torch runtime; no claim that physical GPU is absent.',
               'decision': 'Do not install training stack until independent dataset admission passes.'})

    focus = [52, 53, 55, 56, 57, 58, 59]
    controls = [1, 8, 19, 25, 31, 39, 40, 41, 42, 46, 47, 51]
    locked = []; screening = []
    for number in focus + controls:
        path = root / f'artifacts/concentrated-repair-20261103-02/current-case{number:02d}-fresh-01/manifest.json'
        manifest = json.loads(path.read_text(encoding='utf-8-sig')); case = manifest['cases'][0]
        frames = [{'image': f['image'], 'sha256': f['sha256'], 'size': f['size']} for f in case['frames']]
        # Case number is evaluator metadata only, never a model feature.
        locked.append({'case': number, 'kind': 'focus' if number in focus else 'control',
                       'manifest': str(path), 'manifestSha256': digest(path), 'frames': frames})
        n = len(frames)
        indices = [0, (n - 1) // 3, 2 * (n - 1) // 3, n - 1] if number in focus else [0, n - 1]
        screening.extend({'case': number, 'index': i, **frames[i]} for i in indices)
    negative_root = Path(negative_suite(verification)['report']).parent
    negatives = negative_cases(negative_root)
    for case in negatives[:12]:
        f = case['frames'][0]
        screening.append({'negativeCase': case['id'], 'image': f['image'], 'sha256': f['sha256'], 'size': f['size']})
    checked_images = {}
    for frame in [f for c in locked for f in c['frames']] + [f for c in negatives for f in c['frames']]:
        image = Path(frame['image'])
        expected = frame['sha256']
        if str(image) in checked_images:
            if checked_images[str(image)] != expected:
                raise ValueError('CONFLICTING_IMAGE_BINDING')
            continue
        if digest(image) != expected:
            raise ValueError('EVALUATION_IMAGE_CHANGED: ' + str(image))
        with image.open('rb') as source:
            header = source.read(24)
        if (header[:8] != b'\x89PNG\r\n\x1a\n' or
                [int.from_bytes(header[16:20], 'big'), int.from_bytes(header[20:24], 'big')] != frame['size']):
            raise ValueError('EVALUATION_IMAGE_GEOMETRY_CHANGED')
        checked_images[str(image)] = expected
    write_json(out / 'evaluation-image-hashes.json', checked_images)
    write_json(out / 'evaluation-lock.json', {'positiveCases': locked,
               'positiveFrames': sum(len(x['frames']) for x in locked), 'screening': screening,
               'screeningFrames': len(screening), 'screeningRule': 'focus: 0,floor((n-1)/3),floor(2(n-1)/3),n-1; controls:0,n-1; negatives:first frame of first12 original ordered cases',
               'negativeManifests': [{k: c[k] for k in ('id', 'manifest', 'manifestSha256')} for c in negatives],
               'negativeCases': len(negatives), 'negativePlannedFrames': sum(len(c['frames']) for c in negatives),
               'baselineNegativeAnalyzedFrames': sum(r['analyzedFrames'] for r in json.loads((negative_root / 'report.json').read_text(encoding='utf-8-sig'))['results']), 'graderControls': 2,
               'graderControlEvidence': str(root / 'artifacts/concentrated-repair-20261103-02/verification.json'),
               'newInferenceRun': False, 'truthReadableByCandidateProcess': False})
    write_json(out / 'a0-result.json', {'baseline': 'GO', 'dataset': 'NO_GO', 'training': 'NOT_STARTED',
               'reason': 'No certified source-isolated candidate training dataset; installed torch is CPU-only and isolated train/export environment not built.',
               'a2OfflineResearch': 'GO', 'seconds': time.perf_counter() - started,
               'modelTrainingRuns': 0, 'newCandidateInferenceRuns': 0, 'formalVerifierChanges': 0, 'nativeActions': 0})
    print(json.dumps({'baseline': baseline, 'a0': 'NO_GO_TRAINING', 'a2': 'GO_OFFLINE_RESEARCH',
                      'seconds': time.perf_counter() - started}))


if __name__ == '__main__':
    main()
