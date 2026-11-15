"""Capture current MuMu frame, observe it, print summary. Optional: tap x y first (args: tap X Y)."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from adb_bridge import Device
from observe import observe_image, summary
out = Path(__file__).parent / 'shots'; out.mkdir(exist_ok=True)
d = Device(); args = sys.argv[1:]
while args:
    cmd = args.pop(0)
    if cmd == 'tap':
        x, y = float(args.pop(0)), float(args.pop(0)); d.tap(x, y); print('tapped', x, y)
    elif cmd == 'swipe':
        x1, y1, x2, y2 = (float(args.pop(0)) for _ in range(4)); d.swipe(x1, y1, x2, y2, 500); print('swiped')
    elif cmd == 'key':
        d.key(args.pop(0)); print('key')
    elif cmd == 'wait':
        time.sleep(float(args.pop(0)))
img, at = d.capture(); name = time.strftime('%H%M%S'); img.save(out / f'{name}.png', compress_level=1)
p = observe_image(img); s = summary(p); s['file'] = f'shots/{name}.png'
mr = p.get('mapReview')
if mr:
    s['map'] = {'columns': mr.get('columns'), 'current': {k: mr['currentPosition'].get(k) for k in ('verified', 'nodeId', 'floor', 'column')},
                'nodes': [(n['id'], n['type'], n.get('floor'), n.get('column'), [round(v) for v in n['box']], n.get('completed')) for n in mr['nodes']]}
s['nodeHeader'] = {k: (p.get('nodeHeader') or {}).get(k) for k in ('verified', 'floor', 'context')}
s.pop('progress', None)
(out / f'{name}.json').write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding='utf-8')
(out / 'LATEST').write_text(name, encoding='utf-8')
print(json.dumps(s, ensure_ascii=False))
