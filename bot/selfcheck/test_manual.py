"""Offline contract test: manual hand-over never taps, and resumes only on proof."""
import sys, time, json, os
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE))
import runner as R

S = {'zones': [{'zone': 4, 'steps': [{'type': 'battle', 'column': 2, 'team': ['金桂']},
                                     {'type': 'battle', 'column': 1, 'manual': True, 'note': '需手動'},
                                     {'type': 'boss', 'column': None, 'team': ['莫札']}]}]}
def mk(state='MAP', texts=()):
    ev = [{'text': t, 'score': .99, 'box': [[0, 0], [10, 0], [10, 10], [0, 10]]} for t in texts]
    return {'flow': {'state': state, 'targets': []}, 'evidence': ev, 'progress': {}, 'mapReview': {}}
def runner(step):
    r = R.Runner.__new__(R.Runner); r.s = S; r.dry = True; r.n = 0; r.unknown_since = None
    r.state = {'zone': 4, 'step': step, 'pending': None}; return r
ok = 0; fails = []
def check(name, cond):
    global ok
    if cond: ok += 1
    else: fails.append(name)

r = runner(1)
a = r.decide(mk('MAP', ['4區域第1層進行中']))
check('handover on map', a[0] == 'manual' and r.state.get('manual', {}).get('floor') == 2)
for scr in [mk('BATTLE'), mk('FAILURE', ['失敗', '再一次', '離開']), mk('UNKNOWN', ['確定要開始', '開始']), mk('MISSING_EQUIPMENT', ['確認']),
            mk('UNKNOWN', ['勝利', '區域4第1層'])]:
    a = r.decide(scr); check(f'no action while manual {scr["flow"]["state"]} {a}', a[0] == 'manual')
a = r.decide(mk('UNKNOWN', ['勝利', '區域4第2層']))
check('victory of manual floor resumes', a[0] == 'wait' and 'manual' not in r.state and r.state['step'] == 2)
r = runner(1); r.decide(mk('MAP')); r.state['manual']['since'] = time.time() - 5
res = HERE / 'jobs' / 'RESUME'; res.write_text('x')
a = r.decide(mk('MAP')); check('web resume', a[0] == 'wait' and r.state['step'] == 2 and 'manual' not in r.state)
r = runner(1); r.decide(mk('MAP')); time.sleep(0.05); r.state['manual']['since'] = time.time() + 5   # stale RESUME must not count
a = r.decide(mk('MAP')); check('stale resume ignored', a[0] == 'manual')
r = runner(1); r.decide(mk('MAP')); a = r.decide(mk('MAP', ['4區域完成'])); check('zone complete resumes', a[0] == 'wait' and r.state['step'] == 2)
r = runner(0); a = r.decide(mk('BATTLE')); check('auto step not handed over', a[0] != 'manual')
print(json.dumps({'passed': ok, 'failed': fails}, ensure_ascii=False))
sys.exit(1 if fails else 0)
