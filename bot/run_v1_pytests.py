"""Run the V1 Python test files (tests/test_*.py) one by one with the project venv; summary as JSON lines."""
import json, subprocess, sys, time
from pathlib import Path
root = Path(__file__).resolve().parents[1]
for f in sorted((root / 'tests').glob('test_*.py')):
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, '-B', '-m', 'unittest', '-q', f'tests.{f.stem}'], cwd=root, capture_output=True, text=True, timeout=600, encoding='utf-8', errors='replace')
        tail = (r.stderr or r.stdout).strip().splitlines()[-3:]
        print(json.dumps({'file': f.name, 'code': r.returncode, 'sec': round(time.time() - t0, 1), 'tail': tail}, ensure_ascii=False), flush=True)
    except subprocess.TimeoutExpired:
        print(json.dumps({'file': f.name, 'code': 'timeout'}), flush=True)
