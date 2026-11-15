"""Shadow run over a whole recording: every N seconds observe the frame and record the runner's screen class.
No input, no strategy. Output: <out>/timeline.jsonl (+ 640px thumbnails) for coverage and for human review sampling.
usage: video_shadow.py <video> <out_dir> [step_seconds]"""
import json, sys, time
from pathlib import Path
import cv2
from PIL import Image
BOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(BOT))
from observe import observe_image
import runner
video, out = sys.argv[1], Path(sys.argv[2]); step = float(sys.argv[3]) if len(sys.argv) > 3 else 4
out.mkdir(parents=True, exist_ok=True); (out / 'thumbs').mkdir(exist_ok=True)
tl = out / 'timeline.jsonl'; done = {json.loads(l)['t'] for l in tl.read_text(encoding='utf-8').splitlines()} if tl.exists() else set()
cap = cv2.VideoCapture(video); fps = cap.get(cv2.CAP_PROP_FPS); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); dur = n / fps
with tl.open('a', encoding='utf-8') as fh:
    t = 0.0
    while t < dur:
        key = round(t, 1)
        if key not in done:
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000); ok, bgr = cap.read()
            if not ok: break
            img = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)); t0 = time.perf_counter()
            try:
                p = observe_image(img); cls = runner.classify(p); v1 = p['flow']['state']
                txt = [r['text'] for r in p['evidence'] if r['score'] >= .85][:30]
                extra = {}
                if cls == 'MAP':
                    m = p.get('mapReview') or {}
                    extra = {'nodes': len(m.get('nodes') or []), 'floorsAnchored': any(n.get('floor') for n in m.get('nodes') or []),
                             'current': (m.get('currentPosition') or {}).get('verified'), 'header': runner.header_progress(p['evidence'])}
            except Exception as e:
                cls, v1, txt, extra = 'ERROR', 'ERROR', [repr(e)[:200]], {}
            img.resize((640, round(640 * img.height / img.width))).save(out / 'thumbs' / f'{int(t*10):06d}.jpg', quality=80)
            fh.write(json.dumps({'t': key, 'class': cls, 'v1': v1, 'ms': round((time.perf_counter() - t0) * 1000), 'texts': txt, **extra}, ensure_ascii=False) + '\n'); fh.flush()
        t += step
print('done', tl)
