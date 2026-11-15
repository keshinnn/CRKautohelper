"""Offline decision replay: the runner's own policy (runner.Runner.decide) on saved full-res frames.
No ADB, no human: observe(frame) -> decide -> compare with truth action.
Truth taps are points the game accepted live (validated by the following frame)."""
import json, sys, time, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / 'bot'))
from PIL import Image
import runner
from observe import observe_image

class FakeDevice:
    size = (1440, 2560)

def make_runner(strategy):
    r = object.__new__(runner.Runner); r.s = strategy; r.dry = True; r.d = FakeDevice(); r.unknown_since = None; return r

def main(truth_file, strategy_file, tag='', tol=170):
    strategy = json.loads(Path(strategy_file).read_text(encoding='utf-8')); rows = json.loads(Path(truth_file).read_text(encoding='utf-8'))
    out = []
    for row in rows:
        img = Image.open(ROOT / row['file']).convert('RGB'); r = make_runner(strategy)
        r.state = {'pending': None, **row['context']}; r.last_img = img
        t = time.perf_counter(); p = observe_image(img); ms = round((time.perf_counter() - t) * 1000)
        a = r.decide(p); second = False
        if a[0] == 'wait' and 'seen once' in str(a[-1]):
            # contract needs a second, independent observation; offline we re-observe the same saved pixels (flagged)
            a = r.decide(p); second = True
        kind = a[0] if a[0] != 'unknown' else 'wait(unknown)'
        tr = row['truth']; ok = False
        if tr['kind'] == 'tap' and kind == 'tap':
            ok = tr['tap'] is None or math.dist(a[1], tr['tap']) <= tol
        elif tr['kind'] == 'wait': ok = kind in ('wait', 'wait(unknown)')
        else: ok = kind == tr['kind']
        out.append({'file': row['file'], 'split': row['split'], 'truth': tr, 'decided': [kind, [round(v) for v in a[1]] if kind == 'tap' else None, str(a[-1])[:80]],
                    'v1State': p['flow']['state'], 'ok': ok, 'secondObservationSimulated': second, 'unknownWait': a[0] == 'unknown', 'obsMs': ms})
        print(('OK  ' if ok else 'FAIL'), row['file'][-28:], tr['kind'], '->', out[-1]['decided'], flush=True)
    ms = sorted(o['obsMs'] for o in out); q = lambda p: ms[min(len(ms) - 1, int(p * len(ms)))]
    s = {'frames': len(out), 'correct': sum(o['ok'] for o in out), 'unknownButWaited': sum(o['unknownWait'] for o in out),
         'obsMsP50': q(.5), 'obsMsP95': q(.95), 'obsMsMax': ms[-1], 'ocrBound': __import__('os').environ.get('CRK_OCR_BOUND')}
    print(json.dumps(s, ensure_ascii=False))
    Path(truth_file).with_name(f'decision_replay_result{tag}.json').write_text(json.dumps({'summary': s, 'rows': out}, ensure_ascii=False, indent=1), encoding='utf-8')

if __name__ == '__main__': main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else '')
