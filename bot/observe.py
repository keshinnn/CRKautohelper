"""Observation wrapper around V1 recognizers for MuMu frames (image file or live capture)."""
import base64, hashlib, io, json, os, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
# V1 recognizers (ml/, data/) live in the V1 tree; override with CRK_V1_ROOT when bot/ is checked out elsewhere.
ROOT = Path(os.environ.get('CRK_V1_ROOT') or (HERE.parent if (HERE.parent / 'ml' / 'observation.py').exists() else 'F:/CRK helper'))
sys.path.insert(0, str(ROOT / 'ml')); sys.path.insert(0, str(Path(__file__).parent))
FLOW = ROOT / 'data' / 'flow'


_BOUND = None
def _bounded_ocr():
    """Optional: reuse Codex's measured V2 bounded OCR preprocessing (CRK_OCR_BOUND=736|960|1280)."""
    global _BOUND
    # Default 960: decision replay 38/38 unchanged, observe p50 2215 -> 1344 ms (bench_ocr.py, 2026-11-16). 736 lost accuracy.
    side = os.environ.get('CRK_OCR_BOUND', '960')
    if side not in ('', '0') and _BOUND is None:
        v2 = os.environ.get('CRK_V2_ROOT', r'C:/Users/User/Documents/Codex/CRK-Helper-V2')
        try:
            sys.path.insert(1, str(Path(v2) / 'ml'))
            from bounded_ocr import BoundedOCRRuntime
            _BOUND = BoundedOCRRuntime(int(side)); _BOUND.__enter__()
        except Exception as e:   # V2 tree missing: fall back to V1's original OCR preprocessing
            print(f'[observe] bounded OCR unavailable ({e!r}); using original OCR', file=sys.stderr); _BOUND = False
    return _BOUND


def observe_image(image):
    _bounded_ocr()
    from observation import inspect_capture
    buf = io.BytesIO(); image.save(buf, format='PNG', compress_level=1); raw = buf.getvalue()
    digest = hashlib.sha256(raw).hexdigest()
    binding = {'frameId': digest[:32], 'imageSha256': digest, 'width': image.width, 'height': image.height}
    return inspect_capture('data:image/png;base64,' + base64.b64encode(raw).decode(), binding, FLOW)


def summary(p):
    f = p['flow']
    return {'state': f['state'], 'confidence': f.get('confidence'), 'method': f.get('method'),
            'targets': [{k: t.get(k) for k in ('target', 'center', 'box', 'ocrScore')} for t in f.get('targets', [])],
            'progress': p.get('progress'), 'texts': [(r['text'], r['score']) for r in p['evidence'] if r['score'] >= .8][:60]}


if __name__ == '__main__':
    from PIL import Image
    for name in sys.argv[1:]:
        t = time.perf_counter(); img = Image.open(name).convert('RGB')
        p = observe_image(img); s = summary(p); s['ms'] = round((time.perf_counter() - t) * 1000)
        print(json.dumps({'file': name, **s}, ensure_ascii=False))
