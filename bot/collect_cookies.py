"""Collect labelled in-game character cards from the kingdom cookie list (餅乾 → 餅乾 tab), read-only:
for each card: crop it, tap it, read the cookie name on the detail page (game text = truth), close the detail.
Writes recordings/cookie-list-<ts>/NNN.png + labels.json. No purchases / upgrades are touched."""
import json, re, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import numpy as np
from adb_bridge import Device
from rapidocr_onnxruntime import RapidOCR
ocr = RapidOCR(); d = Device()
out = HERE / 'recordings' / time.strftime('cookie-list-%Y%m%d-%H%M%S'); out.mkdir(parents=True)
CLOSE = (2460, 75)

def texts(img, box=None):
    a = np.asarray(img.convert('RGB').crop(box) if box else img.convert('RGB'))
    res, _ = ocr(a)
    ox, oy = (box[0], box[1]) if box else (0, 0)
    return [(t, s, [[p[0] + ox, p[1] + oy] for p in b]) for b, t, s in (res or [])]

def cards(img):
    """card boxes from the '等級' label at each card's top-left (cookie list grid, 2560x1440)."""
    boxes = []
    for t, s, b in texts(img, (250, 0, 2350, 1300)):
        if re.fullmatch(r'等[級级]', t.strip()) and s > .7:
            x = min(p[0] for p in b); y = min(p[1] for p in b)
            boxes.append((int(x - 28), int(y - 36), int(x - 28 + 392), int(y - 36 + 436)))
    return [b for b in boxes if b[1] >= 30 and b[3] <= 1290]

def detail_name(img):
    for t, s, b in texts(img, (60, 150, 760, 250)):
        t = t.strip()
        if len(t) >= 3 and s > .6: return t, s
    return None, 0

def main():
    img, _ = d.capture()
    if any('升級' in t for t, _, _ in texts(img, (1600, 1150, 2300, 1400))): d.tap(*CLOSE); time.sleep(2)
    seen, rows, idle, n = set(), [], 0, 0
    while idle < 3 and n < 260:
        img, _ = d.capture(); new = 0
        for box in cards(img):
            crop = img.crop(box)
            d.tap((box[0] + box[2]) / 2, (box[1] + box[3]) / 2); time.sleep(2.2)
            det, _ = d.capture(); name, sc = detail_name(det)
            if not any('升級' in t or '服裝' in t or '服装' in t for t, _, _ in texts(det, (0, 1000, 2300, 1440))):
                print('not a detail page, stop', flush=True); return finish(rows)
            d.tap(*CLOSE); time.sleep(1.6)
            if not name or name in seen: continue
            seen.add(name); n += 1; new += 1
            f = f'{n:03d}.png'; crop.save(out / f); rows.append({'file': f, 'name': name, 'ocrScore': round(float(sc), 3), 'box': box})
            print(n, name, flush=True)
        idle = idle + 1 if new == 0 else 0
        d.swipe(1280, 1150, 1280, 430, 1500); time.sleep(1.5)
        (out / 'labels.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
    finish(rows)

def finish(rows):
    (out / 'labels.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8'); print('done', len(rows), out)

if __name__ == '__main__': main()
