"""Read-only recorder: capture MuMu every ~interval seconds, keep frames that changed. Sends NO input.
usage: record.py <minutes> [interval_s]"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from adb_bridge import Device
minutes = float(sys.argv[1]) if len(sys.argv) > 1 else 10
interval = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
out = Path(__file__).parent / 'recordings' / time.strftime('%Y%m%d-%H%M%S'); out.mkdir(parents=True)
(Path(__file__).parent / 'recordings' / 'LATEST').write_text(str(out), encoding='utf-8')
d = Device(); prev = None; rows = []; end = time.time() + minutes * 60; n = 0
stopf = Path(__file__).parent / 'jobs' / 'STOP_RECORD'; t_start = time.time()
while time.time() < end and not (stopf.exists() and stopf.stat().st_mtime > t_start):
    t0 = time.time(); img, at = d.capture()
    small = np.asarray(img.resize((160, 90))).astype(np.int16)
    diff = None if prev is None else float(np.abs(small - prev).mean())
    if diff is None or diff > 3.0:
        name = f'{n:05d}-{int(at*1000)}.png'; img.save(out / name, compress_level=1); prev = small; n += 1
        rows.append({'file': name, 'at': at, 'diff': diff})
        (out / 'index.json').write_text(json.dumps(rows, indent=1), encoding='utf-8')
    time.sleep(max(0, interval - (time.time() - t0)))
print(json.dumps({'folder': str(out), 'frames': n}))
