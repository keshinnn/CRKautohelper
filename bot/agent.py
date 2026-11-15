"""Windows-side job runner. Claude writes bot/jobs/<id>.json = {"script": "name.py", "args": [...]};
this runs ONLY scripts that live directly in bot/ with the project venv, and writes <id>.out / <id>.done.
Stop with Ctrl+C or by creating bot/jobs/STOP."""
import json, subprocess, sys, time
from pathlib import Path
here = Path(__file__).parent; jobs = here / 'jobs'; jobs.mkdir(exist_ok=True)
py = sys.executable
print('CRK bot agent running. Jobs folder:', jobs, flush=True)
while not (jobs / 'STOP').exists():
    for job in sorted(jobs.glob('*.json')):
        done = job.with_suffix('.done')
        if done.exists():
            continue
        try:
            spec = json.loads(job.read_text(encoding='utf-8'))
            script = here / spec['script']
            if script.parent != here or script.suffix != '.py' or not script.exists():
                raise ValueError('script not allowed: ' + spec['script'])
            args = [str(a) for a in spec.get('args', [])]
            print(time.strftime('%H:%M:%S'), 'run', spec['script'], *args, flush=True)
            with open(job.with_suffix('.out'), 'w', encoding='utf-8') as out:
                r = subprocess.run([py, '-B', str(script), *args], cwd=str(here.parent), stdout=out, stderr=subprocess.STDOUT,
                                   timeout=spec.get('timeout', 3600), env={**__import__('os').environ, 'PYTHONUTF8': '1', 'PYTHONIOENCODING': 'utf-8'})
            done.write_text(json.dumps({'code': r.returncode, 'at': time.time()}), encoding='utf-8')
        except Exception as e:
            done.write_text(json.dumps({'code': -1, 'error': repr(e)}), encoding='utf-8')
        print(time.strftime('%H:%M:%S'), 'done', job.name, flush=True)
    time.sleep(1)
print('agent stopped')
