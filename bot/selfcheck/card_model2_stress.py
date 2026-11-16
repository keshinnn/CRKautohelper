"""Open-set stress for card_model2 over all 550 references: each reference, MuMu-ised, is queried with ITSELF
removed from the library (unseen costume). The gate must never accept another character."""
import json, sys, collections
from pathlib import Path
import cv2, numpy as np
BOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(BOT))
import card_model2 as CM, card_align as A
rec = CM.CardRecognizer(bank=None); rng = np.random.default_rng(11)
def mumu_card(art128):
    """Re-render an aligned 128 art into a 254x304 MuMu-shaped card (art from y=47), with jitter."""
    a = cv2.resize(art128, (257, 257)); s = rng.uniform(.97, 1.03); M = cv2.getRotationMatrix2D((128, 128), 0, s); M[:, 2] += rng.uniform(-4, 4, 2)
    a = cv2.warpAffine(a, M, (257, 257), borderMode=cv2.BORDER_REPLICATE)
    a = np.clip(cv2.GaussianBlur(a, (3, 3), rng.uniform(.3, 1.0)).astype(np.float32) * rng.uniform(.85, 1.15, 3) + rng.uniform(-12, 12, 3), 0, 255).astype(np.uint8)
    card = np.zeros((304, 254, 3), np.uint8); card[47:304] = a[:257, :254]; return card
R0 = rec.R.copy(); out = collections.Counter(); wrong = []
for i in range(len(rec.ids)):
    rec.R = R0.copy(); rec.R[i] = 0; A._CACHE.clear()
    o = rec.identify(mumu_card(rec.arts[i]), shifts=((0, 0),))
    others = (rec.ids == rec.ids[i]).sum() > 1
    if o['status'] != 'ok': out['abstain' if others else 'abstain(no other costume)'] += 1
    elif o['id'] == rec.ids[i]: out['right'] += 1
    else: out['WRONG'] += 1; wrong.append((rec.names[rec.ids[i]], o['name'], o['score'], o['margin'], o['inliers']))
print(dict(out)); print(wrong)
