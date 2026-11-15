"""Windows benchmark: decision replay accuracy + observe latency, baseline vs V2 bounded OCR."""
import os, subprocess, sys, json
from pathlib import Path
B = Path(__file__).parent
for side in (sys.argv[1:] or ['', '960', '736']):
    env = {**os.environ, 'PYTHONUTF8': '1'}; env.pop('CRK_OCR_BOUND', None)
    env['CRK_OCR_BOUND'] = side or '0'
    r = subprocess.run([sys.executable, '-B', str(B / 'selfcheck' / 'decision_replay.py'), 'bot/selfcheck/decision_truth.json', 'bot/strategy-s8-draft.json', f'-win{side or "base"}'],
                       cwd=str(B.parent), env=env, capture_output=True, text=True, encoding='utf-8')
    print(side or 'base', r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-800:], flush=True)
