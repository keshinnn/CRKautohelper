"""Build the MuMu screen dataset index from today's live runs (+ the manual recording).
Run frames: V1 state/texts come from the runner's own record (full-res capture at run time).
Recording frames: V1 observe is run here (offline). Output: selfcheck/screens/index.jsonl"""
import json, sys, time
from pathlib import Path
BOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(BOT))
OUT = BOT / 'selfcheck' / 'screens'; OUT.mkdir(exist_ok=True)
idx = OUT / 'index.jsonl'
done = {json.loads(l)['id'] for l in idx.read_text(encoding='utf-8').splitlines()} if idx.exists() else set()
rows = []
for d in sorted((BOT / 'runs').glob('2026111*-*')):
    if not d.is_dir(): continue
    for j in sorted(d.glob('[0-9][0-9][0-9][0-9].json')):
        r = json.loads(j.read_text(encoding='utf-8')); fid = f'run/{d.name}/{j.stem}'
        if fid in done: continue
        full = d / f'{j.stem}-full.png'
        rows.append({'id': fid, 'session': d.name, 't': r.get('at'), 'img': str((full if full.exists() else d / f'{j.stem}.jpg').relative_to(BOT)),
                     'thumb': str((d / f'{j.stem}.jpg').relative_to(BOT)), 'v1': r['state'], 'texts': r.get('texts', []), 'action': r.get('action'), 'run': r.get('run')})
with idx.open('a', encoding='utf-8') as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
print('runs added', len(rows))
if '--recordings' in sys.argv:
    from PIL import Image
    from observe import observe_image
    import runner as R
    n = 0
    for d in sorted((BOT / 'recordings').glob('2026111*-*')):
        for p in sorted(d.glob('*.jpg')):
            fid = f'rec/{d.name}/{p.stem}'
            if fid in done: continue
            img = Image.open(p).convert('RGB'); t0 = time.time(); pk = observe_image(img)
            r = {'id': fid, 'session': 'rec-' + d.name, 't': int(p.stem.split('-')[1]) / 1000, 'img': str(p.relative_to(BOT)), 'thumb': str(p.relative_to(BOT)),
                 'v1': pk['flow']['state'], 'texts': [t for t, _ in R.texts(pk, .85)][:40], 'action': None, 'obsMs': round((time.time() - t0) * 1000)}
            with idx.open('a', encoding='utf-8') as f: f.write(json.dumps(r, ensure_ascii=False) + '\n')
            n += 1
    print('recordings added', n)
