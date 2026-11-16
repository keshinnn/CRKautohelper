"""Build bot/cards/owned.json from a kingdom cookie-list recording (collect_cookies.py): every owned cookie in its
currently equipped costume becomes a reference for card_model2, keyed by catalog id. The id comes from the name the
game itself shows on the cookie's detail page (OCR), normalised and matched to the catalog, plus hand-checked
overrides in selfcheck/list_truth_fix.json ('SKIP' = unreadable, 'OUT' = not in the catalog -> listed for review).
Usage: cards_owned_build.py <recording dir>   (re-run after collecting again; nothing is retrained)"""
import json, shutil, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.argv = [sys.argv[0], sys.argv[1], '--table']
src = (HERE / 'selfcheck' / 'list_eval.py').read_text(encoding='utf-8').split("if '--table'")[0]
src = src.replace("Path(__file__)", "Path(r'%s')" % (HERE / 'selfcheck' / 'list_eval.py'))
g = {}; exec(src, g)
rows, truth, D = g['rows'], g['truth'], g['D']
out = HERE / 'cards' / 'owned'; out.mkdir(parents=True, exist_ok=True)
data = {'format': 'crk-owned-cards-v1', 'source': str(D.name),
        'note': 'Kingdom cookie-list cards (equipped costume) with the in-game name; references for card_model2, not training data.',
        'cards': {}, 'review': []}
ov = json.loads((HERE.parent / 'data' / 'name-overrides-tw.json').read_text(encoding='utf-8'))
names = {**g['names'], **{k: v.removesuffix('餅乾') for k, v in ov['names'].items()}, **{k: v['name'].removesuffix('餅乾') for k, v in ov['added'].items()}}
extra = json.loads((HERE / 'cards' / 'owned_extra.json').read_text(encoding='utf-8')) if (HERE / 'cards' / 'owned_extra.json').exists() else {}
for r in rows:
    t = extra.get(r['file']) or truth(r['name'])
    if t in (None, 'SKIP', 'OUT'):
        data['review'].append({'file': r['file'], 'ocr': r['name'], 'why': t or 'no catalog match'}); continue
    dst = f'owned/{t}-{D.name[-6:]}-{r["file"]}'; shutil.copyfile(D / r['file'], HERE / 'cards' / dst)
    row = data['cards'].setdefault(t, {'name': names.get(t, t), 'files': []})
    row['files'].append({'file': dst, 'ocr': r['name']})
(HERE / 'cards' / 'owned.json').write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
print(json.dumps({'cards': len(data['cards']), 'files': sum(len(v['files']) for v in data['cards'].values()), 'review': data['review']}, ensure_ascii=False))
