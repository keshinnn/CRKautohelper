"""Map planner on today's live MuMu map frames. Truth = the node the live run tapped, validated because the
next frame was that floor's preview. For each MAP frame we re-observe the saved image (full PNG if kept,
else the 1280x720 log JPEG upscaled), run Runner.decide in a fresh state and compare the planned point."""
import json, re, sys, math, copy
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent; BOT = HERE.parent; sys.path.insert(0, str(BOT)); sys.path.insert(0, str(HERE))
import runner as R
from observe import observe_image
from screens_label import load
S = json.load(open(BOT / 'strategy-s8-draft.json', encoding='utf-8'))
rows = load(); by_sess = {}
for r in rows: by_sess.setdefault(r['session'], []).append(r)
cases = []
for sess, rs in by_sess.items():
    for i, r in enumerate(rs):
        a = r.get('action') or []
        if r['label'] != 'MAP' or not a: continue
        reason = str(a[-1]); m = re.search(r'z(\d+) f(\d+) c(\w+)', reason)
        if a[0] == 'tap' and m: pt = a[1]; nxt = rs[i + 1] if i + 1 < len(rs) else None
        elif 'seen once' in reason and i + 1 < len(rs) and rs[i + 1]['action'] and rs[i + 1]['action'][0] == 'tap' and 'map node' in str(rs[i + 1]['action'][-1]):
            m = re.search(r'z(\d+) f(\d+) c(\w+)', str(rs[i + 1]['action'][-1])); pt = rs[i + 1]['action'][1]; nxt = rs[i + 2] if i + 2 < len(rs) else None
        else: continue
        ok_next = nxt is not None and nxt['label'].startswith(('PREVIEW_', 'NODE_ENTRY', 'RIFT'))
        cases.append({'id': r['id'], 'img': r['img'], 'zone': int(m.group(1)), 'floor': int(m.group(2)), 'truth': pt, 'validated': ok_next, 'run': r['run']})
res = []
for c in cases:
    img = Image.open(BOT / c['img']).convert('RGB')
    if img.size != (2560, 1440): img = img.resize((2560, 1440), Image.LANCZOS)
    p = observe_image(img)
    run = R.Runner.__new__(R.Runner); run.s = S; run.dry = True; run.n = 0; run.unknown_since = None; run.last_img = img
    class D: size = (1440, 2560)
    run.d = D(); run.state = {'zone': c['zone'], 'step': c['floor'] - 1, 'pending': None, 'scrolls': 0}
    a = run.decide(p); cand = run.state.get('mapCandidate')
    pt = cand['point'] if cand else (a[1] if a[0] == 'tap' else None)
    d = math.dist(pt, c['truth']) if pt else None
    verdict = 'HIT' if d is not None and d <= 80 else ('NO_DECISION' if pt is None else 'WRONG')
    res.append({**{k: c[k] for k in ('id', 'zone', 'floor', 'truth', 'validated')}, 'planned': pt, 'dist': d and round(d), 'verdict': verdict, 'reason': str(a[-1])[:90]})
    print(verdict, c['id'], c['zone'], c['floor'], c['truth'], pt, str(a[-1])[:70], flush=True)
import collections
print(json.dumps(collections.Counter(r['verdict'] for r in res)))
(HERE / 'map_live_eval_result.json').write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
