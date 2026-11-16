"""Open-set stress test over all 180 characters / 550 references: each reference, MuMu-ised (shift, scale,
blur, colour/brightness jitter) is queried against the bank WITHOUT itself (as if its costume were unseen).
Counts gate decisions: right / WRONG (another character accepted) / abstain."""
import json, sys
from pathlib import Path
import cv2, numpy as np
BOT = Path(__file__).resolve().parents[1]; V1 = BOT.parent; sys.path.insert(0, str(BOT))
import card_align as A
SCORE, MARGIN = float(sys.argv[1]) if len(sys.argv) > 1 else .40, float(sys.argv[2]) if len(sys.argv) > 2 else .06
m = json.loads((V1 / 'models/cards/model.json').read_text(encoding='utf-8')); T = m['templates']
labs = np.array([t['name'] for t in T])
raw = [A.ref_art(cv2.imread(str(V1 / 'models/cards' / t['reference_file']))) for t in T]
R = np.stack(raw).astype(np.float32); base = A.mask(); rng = np.random.default_rng(7)
def mumuise(a):
    s = rng.uniform(.97, 1.03); M = cv2.getRotationMatrix2D((64, 64), 0, s); M[:, 2] += rng.uniform(-3, 3, 2)
    b = cv2.warpAffine(a, M, (128, 128), borderMode=cv2.BORDER_REPLICATE)
    b = cv2.GaussianBlur(b, (3, 3), rng.uniform(.3, 1.0)).astype(np.float32)
    b = b * rng.uniform(.85, 1.15, 3) + rng.uniform(-12, 12, 3)
    return np.clip(b + rng.normal(0, 3, b.shape), 0, 255).astype(np.uint8)
mb = base.astype(bool); full = A._norm_rows(R[:, mb])
res = {'right': 0, 'WRONG': 0, 'abstain': 0, 'abstain_no_other_variant': 0}; wrong = []
for i, t in enumerate(T):
    q = A._norm_rows(mumuise(raw[i]).astype(np.float32)[mb][None])[0]
    s = full @ q; s[i] = -9
    best = {}
    for j in np.argsort(-s)[:40]: best[labs[j]] = max(best.get(labs[j], -9), s[j])
    (n1, v1), (n2, v2) = sorted(best.items(), key=lambda x: -x[1])[:2]
    others = (labs == labs[i]).sum() > 1
    if v1 >= SCORE and v1 - v2 >= MARGIN:
        if n1 == labs[i]: res['right'] += 1
        else: res['WRONG'] += 1; wrong.append((t['name'], t['variant'][:20], n1, round(float(v1), 3), round(float(v1 - v2), 3)))
    else: res['abstain' if others else 'abstain_no_other_variant'] += 1
print(SCORE, MARGIN, res); print(wrong[:20])
