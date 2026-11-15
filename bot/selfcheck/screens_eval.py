"""Score screen recognizers against the eyeballed MuMu labels (selfcheck/screens).
A predictor returns a canonical class or 'UNKNOWN' (abstain). Reports accuracy, abstain rate and
WRONG (confident but wrong) — the dangerous kind — per class, overall and on the held-out split."""
import json, sys, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from screens_label import load
HELD = ('20261116-060954', '20261116-061928', '20261116-063633')   # zone 2–3 runs: never used while writing rules below
def split(r):
    if r['session'].startswith('rec-'): return 'held' if int(r['id'].rsplit('/', 1)[1][:5]) >= 127 else 'dev'
    return 'held' if r['session'] in HELD else 'dev'
V1MAP = {'NODE_BATTLE': 'PREVIEW_BATTLE', 'NODE_BOSS': 'PREVIEW_BOSS', 'EXPEDITION_ROSTER': 'ROSTER'}
def v1(r): return V1MAP.get(r['v1'], r['v1'])
def packet(r):
    ev = [{'text': t, 'score': .99, 'box': [[0, 0], [10, 0], [10, 10], [0, 10]]} for t in r.get('texts') or []]
    return {'flow': {'state': r['v1'], 'targets': []}, 'evidence': ev}
def runner_rules(r):
    import runner as R
    c = R.classify(packet(r))
    return {'PREVIEW_UNKNOWN_PANEL': 'UNKNOWN'}.get(c, c)
def score(pred, rows, name):
    out = {}
    for part in ('dev', 'held', 'all'):
        rs = [r for r in rows if part == 'all' or split(r) == part]
        ok = wrong = abst = 0; per = collections.defaultdict(lambda: [0, 0, 0]); conf = collections.Counter()
        for r in rs:
            p = pred(r); t = r['label']
            if p == 'UNKNOWN' and t == 'OTHER': p = 'OTHER'   # not Belowland: staying idle is the right answer
            if p == 'UNKNOWN': abst += 1; per[t][2] += 1
            elif p == t: ok += 1; per[t][0] += 1
            else: wrong += 1; per[t][1] += 1; conf[(t, p)] += 1
        out[part] = {'n': len(rs), 'correct': ok, 'wrong': wrong, 'abstain': abst, 'acc': round(ok / max(1, len(rs)), 3),
                     'perClass': {k: dict(zip(('ok', 'wrong', 'abstain'), v)) for k, v in sorted(per.items())},
                     'confusions': [[a, b, n] for (a, b), n in conf.most_common(20)]}
    return {name: out}
if __name__ == '__main__':
    rows = load(); res = {}
    res.update(score(v1, rows, 'v1_flow_state')); res.update(score(runner_rules, rows, 'runner_rules'))
    if '--model' in sys.argv:
        from screen_model_eval import predict_all
        res.update(predict_all(rows, score))
    (HERE / 'screens_eval_result.json').write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
    for k, v in res.items():
        for part in ('dev', 'held', 'all'):
            x = v[part]; print(f"{k:16s} {part:4s} n={x['n']:3d} correct={x['correct']:3d} wrong={x['wrong']:3d} abstain={x['abstain']:3d} acc={x['acc']}")
        print('   confusions(all):', v['all']['confusions'][:12])
