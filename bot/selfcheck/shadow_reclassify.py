"""Re-run the runner's screen classifier on a shadow timeline's stored OCR texts (no new OCR) to compare rule versions."""
import json, sys
from pathlib import Path
from collections import Counter
BOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(BOT))
import runner
tl = Path(sys.argv[1]); rows = [json.loads(l) for l in tl.read_text(encoding='utf-8').splitlines()]
ev = lambda t: {'text': t, 'score': .9, 'box': [[0, 0], [1, 0], [1, 1], [0, 1]]}
out = []
for r in rows:
    p = {'flow': {'state': r['v1'], 'targets': []}, 'evidence': [ev(t) for t in r['texts']], 'progress': {}}
    out.append({'t': r['t'], 'before': r['class'], 'after': runner.classify(p)})
b, a = Counter(o['before'] for o in out), Counter(o['after'] for o in out)
print('frames', len(out)); print('before', b.most_common()); print('after ', a.most_common())
print('changed', Counter((o['before'], o['after']) for o in out if o['before'] != o['after']).most_common())
tl.with_name('reclassified.json').write_text(json.dumps(out, ensure_ascii=False), encoding='utf-8')
