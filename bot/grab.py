"""Capture only (no OCR). args: same tap/swipe/wait commands as shot.py; saves shots/grab-<t>.png"""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from adb_bridge import Device
d = Device(); a = sys.argv[1:]; out = Path(__file__).parent / 'shots'; out.mkdir(exist_ok=True)
while a:
    c = a.pop(0)
    if c == 'tap': d.tap(float(a.pop(0)), float(a.pop(0)))
    elif c == 'swipe': d.swipe(*(float(a.pop(0)) for _ in range(4)), 900)
    elif c == 'wait': time.sleep(float(a.pop(0)))
    elif c == 'grab':
        img, _ = d.capture(); n = out / f'grab-{a.pop(0)}.png'; img.save(n, compress_level=1); print(n)
