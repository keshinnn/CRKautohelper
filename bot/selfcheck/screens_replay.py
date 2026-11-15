"""Replay runner.decide on the labelled run frames (stored OCR + saved image), compare action kinds with
what the live runner did. Highlights changes caused by the screen model."""
import json, sys, collections, copy
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent; BOT = HERE.parent; sys.path.insert(0, str(BOT)); sys.path.insert(0, str(HERE))
import runner as R
from screens_label import load
S = json.load(open(BOT / 'strategy-s8-draft.json', encoding='utf-8'))
rows = [r for r in load() if r['action']]
chg = collections.Counter(); ex = []
for r in rows:
    ev = [{'text': t, 'score': .99, 'box': [[100, 100], [140, 100], [140, 130], [100, 130]]} for t in r['texts']]
    p = {'flow': {'state': r['v1'], 'targets': []}, 'evidence': ev, 'progress': {}, 'mapReview': {}, 'nodeHeader': {}}
    run = R.Runner.__new__(R.Runner); run.s = S; run.dry = True; run.n = 0; run.unknown_since = None
    run.state = copy.deepcopy(r['run'] or {'zone': 1, 'step': 0, 'pending': None}); run.state.pop('manual', None); run.state.pop('halt', None)
    run.last_img = Image.open(BOT / r['img']).convert('RGB')
    class D: size = (1440, 2560)
    run.d = D()
    try: a = run.decide(p)
    except Exception as e: a = ('error', repr(e)[:80])
    old = r['action'][0]; new = a[0]
    old_r = str(r['action'][-1])
    if old != new or ('screen model' in str(a[-1])) or ('resolving' in str(a[-1])) or ('conflict' in str(a[-1])):
        chg[(r['label'], old, new)] += 1
        if len(ex) < 40: ex.append((r['id'], r['label'], old, old_r[:50], new, str(a[-1])[:70]))
for k, v in chg.most_common(): print(v, k)
for e in ex: print(e)
