"""Run the bot's own safety/unit checks with the Windows venv (the interpreter the runner really uses)."""
import json, subprocess, sys, time
from pathlib import Path
here = Path(__file__).resolve().parent
for t in ('test_contracts.py', 'test_manual.py', 'test_treasure_equip.py', 'card_owned_eval.py'):
    t0 = time.time(); r = subprocess.run([sys.executable, '-B', str(here / 'selfcheck' / t)], cwd=here.parent, capture_output=True, text=True, timeout=600, encoding='utf-8', errors='replace')
    print(json.dumps({'test': t, 'code': r.returncode, 'sec': round(time.time() - t0, 1), 'tail': ((r.stderr or '') + (r.stdout or '')).strip().splitlines()[-2:]}, ensure_ascii=False), flush=True)
r = subprocess.run([sys.executable, '-B', '-c', 'import sys; sys.path.insert(0, "bot"); import runner, team, navigator, treasure, card_model2, screen_model; from PIL import Image; print(runner.boss_icon(Image.open("bot/runs/20261116-162345/0035-full.png").convert("RGB")))'], cwd=here.parent, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(json.dumps({'test': 'imports+boss_icon', 'code': r.returncode, 'out': (r.stdout + r.stderr).strip()[-300:]}, ensure_ascii=False))
