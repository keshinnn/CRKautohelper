"""Does an owned-cookie list card (kingdom list, equipped costume) let card_model2 recognise the same cookie on the
team-select screen? Team crops = live S8 cards (truth verified live). Bank excluded everywhere.
  A codex       : Codex references only
  B codex+owned : plus owned list cards
  C owned-only  : the S8 cookies' Codex references removed -> only their owned list card can match (cross-layout)"""
import json, sys, collections
from pathlib import Path
import numpy as np
BOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(BOT)); sys.path.insert(0, str(BOT / 'selfcheck'))
import card_model2 as CM, card_lab
name2id = {c['name']: c['id'] for c in json.loads((BOT.parent / 'models/cards/model.json').read_text(encoding='utf-8'))['classes']}
s8 = {name2id[n] for n in card_lab.ALIAS.values()}
def drop(rec, keep):
    idx = [i for i in range(len(rec.ids)) if keep(i)]
    rec.ids = rec.ids[idx]; rec.arts = [rec.arts[i] for i in idx]; rec.variants = [rec.variants[i] for i in idx]; rec.R = rec.R[idx]; rec._sf = {}
    if hasattr(rec, '_cache'): rec._cache = {}
    return rec
A = CM.CardRecognizer(bank=None, owned=None)
B = CM.CardRecognizer(bank=None)
C = drop(CM.CardRecognizer(bank=None), lambda i: not (B.ids[i] in s8 and not B.variants[i].startswith('owned')))
out = {}
for name, rec in (('A codex', A), ('B codex+owned', B), ('C owned-only for S8', C)):
    res = collections.Counter(); wrong = []
    for r, strip in card_lab.crops():
        truth = 'cookie-184' if r['truth'] == '氣泡' else name2id.get(card_lab.ALIAS.get(r['truth'])); o = rec.identify(card_lab.card_at(strip, r['x']))   # 氣泡 = 氣泡水餅乾, not in Codex's catalog (user-confirmed id)
        if o['status'] != 'ok': res['abstain' if truth else 'out-abstain'] += 1
        elif o['id'] == truth: res['right'] += 1; res['right via owned'] += o['variant'].startswith('owned')
        else: res['WRONG'] += 1; wrong.append((r['truth'], o['name'], o['score'], o['margin'], o['inliers']))
    out[name] = {'counts': dict(res), 'wrong': wrong}; print(name, dict(res), wrong[:5], flush=True)
(BOT / 'selfcheck' / 'card_owned_eval.json').write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding='utf-8')
