"""Offline character-card recognition lab on MuMu team-select crops (truth: live-verified S8 cards).
Methods: aligned masked colour NCC against all 550 Codex references (180 characters). Writes card_lab_<tag>.json."""
import json, sys, collections
from pathlib import Path
import cv2, numpy as np
BOT = Path(__file__).resolve().parents[1]; V1 = BOT.parent; sys.path.insert(0, str(BOT))
import card_align as A, team
from PIL import Image
ALIAS = {'百合':'聖百合','芒果':'芒果','船長':'艦長','水母':'蕾絲水母','莫札':'默茲瑞拉','金桂':'金桂','薄荷醇':'薄荷醇','煙燻':'煙燻起司','木乃伊':'義大利寬麵','奶油蘇打':'氣泡水','風鈴草':'風鈴草','巴斯克':'巴斯克起司','阿福花':'阿福花餅乾','茉莉':'小花茉莉餅乾'}
M = A.mask().astype(bool)
def vec(a):
    g = cv2.cvtColor(a, cv2.COLOR_BGR2LAB).astype(np.float32)[M].reshape(-1); g -= g.mean(); return g / (np.linalg.norm(g) + 1e-6)
def crops():
    rows = json.loads((BOT / 'selfcheck' / 'cards_codex_eval.json').read_text(encoding='utf-8'))['rows']; cache = {}
    for r in rows:
        f = r['frame'].replace('\\', '/')
        if f not in cache:
            im = Image.open(BOT / f).convert('RGB')
            if im.size != (2560, 1440): im = im.resize((2560, 1440), Image.LANCZOS)
            cache[f] = team.strip_of(im)
        yield r, cache[f]
def card_at(strip, x, dx=0, dy=0):
    c = strip[:, max(0, x + dx):x + dx + 254]
    if dy: c = np.roll(c, -dy, axis=0)
    return c
def run(tag='ncc'):
    m = json.loads((V1 / 'models/cards/model.json').read_text(encoding='utf-8'))
    labs = np.array([t['name'] for t in m['templates']])
    R = np.stack([A.ref_art(cv2.imread(str(V1 / 'models/cards' / t['reference_file']))).astype(np.float32) for t in m['templates']])
    base = A.mask()
    out = []
    for r, strip in crops():
        best = {}
        for dy in (-6, -3, 0, 3, 6):
            for dx in (-4, 0, 4):
                s = A.ncc_scores(A.mumu_art(card_at(strip, r['x'], dx, dy)), R, base)
                for i in np.argsort(-s)[:40]: best[labs[i]] = max(best.get(labs[i], -1), float(s[i]))
        order = sorted(best.items(), key=lambda x: -x[1])[:5]
        art0 = A.mumu_art(card_at(strip, r['x']))
        out.append({'frame': r['frame'], 'x': r['x'], 'truth': ALIAS.get(r['truth'], 'OUT_OF_CATALOG:' + r['truth']), 'checked': not A.check_mask(art0).all(),
                    'top': [[n, round(v, 4)] for n, v in order]})
    ins = [o for o in out if not o['truth'].startswith('OUT') and not o['checked']]
    n = len(ins); top1 = sum(o['top'][0][0] == o['truth'] for o in ins)
    def stat(xs): return [round(float(np.percentile(xs, q)), 3) for q in (0, 5, 50)] if xs else None
    print('in-catalog unchecked: top1 score min/p5/med', stat([o['top'][0][1] for o in ins if o['top'][0][0] == o['truth']]),
          'margin', stat([o['top'][0][1] - o['top'][1][1] for o in ins if o['top'][0][0] == o['truth']]))
    oo = [o for o in out if o['truth'].startswith('OUT') and not o['checked']]
    print('out-of-catalog unchecked n', len(oo), 'top1 score max', max([o['top'][0][1] for o in oo], default=None), 'margin max', max([o['top'][0][1] - o['top'][1][1] for o in oo], default=None))
    print('checked (abstain):', sum(o['checked'] for o in out))
    per = collections.Counter(); bad = collections.Counter()
    for o in ins:
        per[o['truth']] += 1
        if o['top'][0][0] != o['truth']: bad[o['truth'] + '→' + o['top'][0][0]] += 1
    print(tag, 'top1', top1, '/', n); print(dict(bad))
    (BOT / 'selfcheck' / f'card_lab_{tag}.json').write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding='utf-8')
if __name__ == '__main__': run(*(sys.argv[1:] or []))
