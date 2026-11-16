"""Score bot/card_model2 on (a) the real MuMu crops (truth: live-verified S8 cards) with the bank EXCLUDED
(so the model never sees MuMu pixels of these characters), and (b) the roster-restricted closed set."""
import json, sys, collections
from pathlib import Path
BOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(BOT)); sys.path.insert(0, str(BOT / 'selfcheck'))
import card_model2 as CM, card_lab
rec = CM.CardRecognizer(bank=None)
name2id = {c['name']: c['id'] for c in json.loads((BOT.parent / 'models/cards/model.json').read_text(encoding='utf-8'))['classes']}   # card_lab truth uses catalog names
roster = {name2id[n] for n in card_lab.ALIAS.values()}
res = collections.Counter(); wrong = []
for r, strip in card_lab.crops():
    truth = card_lab.ALIAS.get(r['truth']); card = card_lab.card_at(strip, r['x'])
    for mode, cand in (('open', None), ('roster', roster)):
        o = rec.identify(card, cand)
        if o['status'] != 'ok': res[(mode, 'abstain' if truth else 'out-abstain')] += 1
        elif truth and o['id'] == name2id.get(truth): res[(mode, 'right')] += 1
        else: res[(mode, 'WRONG')] += 1; wrong.append((mode, r['truth'], o['name'], o['score'], o['margin'], o['inliers']))
print(dict(res)); print(wrong[:10])
