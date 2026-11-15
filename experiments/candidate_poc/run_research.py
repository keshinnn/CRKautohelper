"""A2 finite real-PNG witness experiment, not a learned detector or acceptance."""
import argparse
import json
from pathlib import Path
import subprocess
import time
from research_evidence import make_witness


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    out = Path(args.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    results = []
    for number in [52, 53, 55, 56, 57, 58, 59]:
        case_path = root / f'artifacts/concentrated-repair-20261103-02/current-case{number:02d}-fresh-01/manifest.json'
        case = json.loads(case_path.read_text(encoding='utf-8-sig'))['cases'][0]
        # First frame is predeclared evaluator scheduling, not a frame-ID branch
        # in any witness builder. Boxes are original observer output, never GT.
        frame = case['frames'][0]
        packet = json.loads(Path(frame['packet']).read_text(encoding='utf-8-sig'))
        candidates = [n for n in packet.get('mapReview', {}).get('nodes', [])
                      if n['box'][0] >= 2 and n['box'][1] >= 2 and
                      n['box'][0] + n['box'][2] < frame['size'][0] - 2 and
                      n['box'][1] + n['box'][3] < frame['size'][1] - 2]
        if not candidates:
            results.append(dict(case=number, status='NO_CURRENT_OBSERVER_BOX',
                                meaning='No box was invented or copied from another frame.'))
            continue
        context = dict(imageSha256=frame['sha256'], sourceKey=case['videoSha256'],
                       frameToken=packet['binding']['frameId'], geometryEpoch=frame['geometryVersion'],
                       atMs=frame['atMs'], nowMs=frame['atMs'] + 1)
        start = time.perf_counter()
        witness = make_witness(frame['image'], candidates[0]['box'], context)
        producer_ms = (time.perf_counter() - start) * 1000
        witness_path = out / f'case{number}-witness.json'; context_path = out / f'case{number}-context.json'
        witness_path.write_text(json.dumps(witness, indent=2), encoding='utf-8')
        context_path.write_text(json.dumps(context, indent=2), encoding='utf-8')
        checked = subprocess.run(['node', str(root / 'experiments/candidate_poc/verify_research.cjs'),
                                  frame['image'], str(witness_path), str(context_path)],
                                 capture_output=True, text=True, check=True)
        result = json.loads(checked.stdout)
        results.append(dict(case=number, sourceImage=frame['image'], sourceSha256=frame['sha256'],
                            producerMs=producer_ms, verification=result,
                            boxOrigin='first in-bounds node of existing same-frame observer output',
                            clock='offline PTS + 1ms research context; NOT fresh live capture',
                            scope='source/geometry/raw-gradient reproducibility only'))
    summary = dict(records=results, modelInference=False, truthUsedForGeneration=False,
                   outerBoundaryDecision='UNPROVEN', mapLocationDecision='UNPROVEN',
                   previewRegistrationDecision='UNPROVEN', formalAuthorityProduced=False,
                   formalVerifierChanges=0, nativeActions=0)
    (out / 'research-result.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps({'cases': len(results), 'witnesses': sum('verification' in r for r in results),
                      'authority': False}))


if __name__ == '__main__':
    main()
