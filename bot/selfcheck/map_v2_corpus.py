"""Held-out map check: run bot/navigator.plan_map_tap on Codex's frozen 60-case corpus.
Truth = human-reviewed expectedBox per case (V2 artifacts); packets = saved V1 observer output.
The planner never sees intent/expectedBox except floor+column from the strategy (as live)."""
import json, glob, sys, re
from pathlib import Path
V2 = Path(sys.argv[1]); sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from navigator import plan_map_tap

def local(p): return V2 / re.sub(r'^.*?CRK-Helper-V2[\\/]', '', p).replace('\\', '/')

def inside(pt, b, pad=0): return b[0] - pad <= pt[0] <= b[0] + b[2] + pad and b[1] - pad <= pt[1] <= b[1] + b[3] + pad

rows = []
for mf in sorted(glob.glob(str(V2 / 'artifacts/concentrated-repair-20261103-02/current-case*-fresh-01/manifest.json'))):
    case = int(re.search(r'case(\d+)', mf).group(1)); m = json.load(open(mf, encoding='utf-8')); c = m['cases'][0]
    it, eb = c['intent'], c.get('expectedBox')
    pre = [f for f in c['frames'] if f['frameIndex'] in c['preFrames']]
    res = []
    for f in pre:
        if not f.get('packet'): res.append('NO_PACKET'); continue
        try: p = json.load(open(local(f['packet']), encoding='utf-8'))
        except FileNotFoundError: res.append('PACKET_MISSING'); continue
        if p['flow']['state'] != 'MAP': res.append('NOT_MAP:' + p['flow']['state']); continue
        plan = plan_map_tap(p, {'floor': it['floor'], 'column': it['column']})
        if plan['point'] is None: res.append('NO_PLAN:' + plan['reason'][:40])
        else: res.append('HIT' if inside(plan['point'], eb) else f'MISS@{[round(v) for v in plan["point"]]}')
    rows.append({'case': case, 'id': c['id'], 'size': c['frames'][0].get('size'), 'geometry': (c['frames'][0].get('geometryVersion') or '')[:12],
                 'intent': f"z{it['zone']}f{it['floor']}c{it['column']}-{it['mode']}", 'results': res,
                 'ok': any(r == 'HIT' for r in res) and not any(r.startswith('MISS') for r in res)})
ok = sum(r['ok'] for r in rows); miss = sum(any(x.startswith('MISS') for x in r['results']) for r in rows)
print(json.dumps({'cases': len(rows), 'hit': ok, 'wrongTarget': miss, 'noDecision': len(rows) - ok - miss}, ensure_ascii=False))
for r in rows: print(r['case'], r['intent'], r['size'], r['geometry'], r['results'])
json.dump(rows, open(Path(__file__).parent / 'map_v2_corpus.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
