"""Train/evaluate bot/screen_model on the eyeballed MuMu labels. Image model is fit on the DEV split only
and scored on HELD (zone 2-3 runs + later half of the recording); then refit on everything and saved."""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
HERE = Path(__file__).resolve().parent; BOT = HERE.parent; sys.path.insert(0, str(BOT)); sys.path.insert(0, str(HERE))
import screen_model as SM
from screens_eval import split
CACHE = HERE / 'screens' / 'features.npz'
def feats(rows):
    ids = [r['id'] for r in rows]
    if CACHE.exists():
        d = np.load(CACHE, allow_pickle=False)
        if list(d['ids']) == ids: return d['X']
    X = np.stack([SM.features(Image.open(BOT / r['thumb'])) for r in rows])
    np.savez_compressed(CACHE, X=X, ids=np.array(ids)); return X
def grp(r):   # recording = one long session; treat each 60-frame stretch as its own group
    return r['session'] + (r['id'].rsplit('/', 1)[1][:5] if False else '') if not r['session'].startswith('rec-') else 'rec%d' % (int(r['id'].rsplit('/', 1)[1][:5]) // 60)
def predict_all(rows, score):
    X = feats(rows); dev = np.array([split(r) == 'dev' for r in rows])
    y = np.array([r['label'] for r in rows])
    m = SM.ImageKNN(X[dev], y[dev])
    img = {}
    for i, r in enumerate(rows):
        if dev[i]:   # leave-one-session-out style for dev rows: refit without the row's own session
            same = np.array([grp(q) == grp(r) for q in rows]) & dev
            mm = SM.ImageKNN(X[dev & ~same], y[dev & ~same]) if (dev & ~same).any() else m
            img[r['id']] = mm.predict(X[i])
        else: img[r['id']] = m.predict(X[i])
    def tcls(r):
        t = SM.text_class(r['texts'], r['v1'])[0]
        if t == 'PREVIEW_RIFT' and SM.panel_button(Image.open(BOT / r['thumb'])) == 'purple': t = 'RIFT_RESOLVING'
        return t
    def text_only(r): return tcls(r) or 'UNKNOWN'
    def image_only(r): c, conf, _ = img[r['id']]; return str(c) if conf >= SM.IMAGE_MIN else 'UNKNOWN'
    def fused(r): c, conf, _ = img[r['id']]; return SM.fuse(tcls(r), c, conf)[0]
    res = {}
    for name, f in (('text_model', text_only), ('image_model', image_only), ('fused_model', fused)): res.update(score(f, rows, name))
    SM.ImageKNN(X, y).save(); print('saved', SM.MODEL_FILE)
    return res
