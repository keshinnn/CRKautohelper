"""Run the existing Codex self-check suites on Windows and the handoff's replay reproduction. Writes logs to bot/selfcheck/suites/."""
import os, subprocess, sys, time, json
from pathlib import Path
V1 = Path(r'F:\CRK helper'); V2 = Path(r'C:\Users\User\Documents\Codex\CRK-Helper-V2')
out = V1 / 'bot' / 'selfcheck' / 'suites'; out.mkdir(parents=True, exist_ok=True)
py = str(V1 / '.venv' / 'Scripts' / 'python.exe')
stamp = time.strftime('%Y%m%d-%H%M%S')
tmp = V2 / 'artifacts' / 'rift-episode-20261113-01' / 'tmp'
env = {**os.environ, 'PYTHONUTF8': '1', 'TEMP': str(tmp), 'TMP': str(tmp)}
jobs = {
 'v2-node-tests': (['node', '--test', *[str(p) for p in sorted((V2 / 'tests').glob('*.test.cjs'))]], V2),
 'v2-research-node-tests': (['node', '--test', *[str(p) for p in sorted((V2 / 'experiments' / 'candidate_poc').glob('*.test.cjs'))]], V2),
 'v1-node-tests': (['node', '--test', *[str(p) for p in sorted((V1 / 'tests').glob('*.test.cjs'))]], V1),
 'v1-python-tests': ([py, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py'], V1),
 'v2-rift-replay-repro': (['node', 'experiments/candidate_poc/episode-replay.cjs', 'artifacts/rift-episode-20261113-01/episode',
                           f'artifacts/rift-episode-20261113-01/run-claude-{stamp}', 'artifacts/result-repair-20261113-01', 'artifacts/rift-episode-20261113-01'], V2),
}
only = sys.argv[1:] or list(jobs)
summary = {}
for name in only:
    cmd, cwd = jobs[name]; t = time.time()
    with open(out / f'{name}-{stamp}.log', 'w', encoding='utf-8') as fh:
        r = subprocess.run(cmd, cwd=str(cwd), stdout=fh, stderr=subprocess.STDOUT, env=env, timeout=3000, shell=False)
    summary[name] = {'exit': r.returncode, 'seconds': round(time.time() - t), 'log': f'{name}-{stamp}.log'}
    print(name, summary[name], flush=True)
(out / f'summary-{stamp}.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
