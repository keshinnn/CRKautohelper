"""CRK 冥界試煉 控制台（本機網頁）。
啟動：start-webui.cmd 或  .venv\\Scripts\\python.exe bot\\webui.py   然後開 http://127.0.0.1:8765
- 攻略編輯：人工輸入 → 存成 bot/strategies/<名稱>.json（程式只讀 JSON，不讀 PDF）
- 控制：開始/繼續、從頭開始、停止、清除失敗鎖定、手動關卡交還程式
- 狀態：runner 寫的 bot/status.json + 最新畫面 + 輸出紀錄
只綁 127.0.0.1，不對外開放。"""
import json, os, re, subprocess, sys, time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

BOT = Path(__file__).resolve().parent
ROOT = BOT.parent
STRATS = BOT / 'strategies'; STRATS.mkdir(exist_ok=True)
JOBS = BOT / 'jobs'; JOBS.mkdir(exist_ok=True)
STATUS = BOT / 'status.json'
STATE = BOT / 'run-state.json'
LOGS = BOT / 'runs'; LOGS.mkdir(exist_ok=True)
TREASURE_DIR = ROOT / 'data' / 'treasures'
PORT = int(os.environ.get('CRK_WEB_PORT', '8765'))
STEP_TYPES = ('battle', 'random', 'heal', 'boss')

proc = None          # runner started from this page
proc_log = None

# first start: offer the draft as an editable strategy
if not any(STRATS.glob('*.json')) and (BOT / 'strategy-s8-draft.json').exists():
    (STRATS / 'S8-困難-草稿.json').write_text((BOT / 'strategy-s8-draft.json').read_text(encoding='utf-8'), encoding='utf-8')


def safe_name(name):
    name = (name or '').strip()
    if not re.fullmatch(r'[\w\-㐀-鿿 ]{1,60}', name):
        raise ValueError('名稱只能用中英文、數字、空白、- 和 _（最多 60 字）')
    return name


def read_json(p, default=None):
    try:
        return json.loads(Path(p).read_text(encoding='utf-8'))
    except Exception:
        return default


def cards():
    return list((read_json(BOT / 'cards' / 'labels.json', {}) or {}).keys())


def treasures():
    m = read_json(TREASURE_DIR / 'manifest.json', {}) or {}
    return [{'name': t['name'], 'icon': t.get('image')} for t in m.get('treasures', [])]


def validate(s):
    """Returns (errors, warnings). Errors block saving; warnings are shown."""
    errs, warns = [], []
    known_c = set(cards()); known_t = {t['name'] for t in treasures()}
    if not isinstance(s, dict) or not isinstance(s.get('zones'), list) or not s['zones']:
        return ['攻略必須有至少一個區域'], []
    for t in (s.get('treasures') or {}).get('default') or []:
        if t not in known_t: warns.append(f'預設寶物「{t}」不在寶物清單')
    seen = set()
    for z in s['zones']:
        zn = z.get('zone')
        if not isinstance(zn, int) or zn < 1: errs.append(f'區域編號不正確：{zn}'); continue
        if zn in seen: errs.append(f'區域 {zn} 重複')
        seen.add(zn)
        steps = z.get('steps') or []
        if not steps: errs.append(f'區域 {zn} 沒有任何一層')
        for i, st in enumerate(steps, 1):
            where = f'區域{zn} 第{i}層'
            ty = st.get('type')
            if ty not in STEP_TYPES: errs.append(f'{where}：類型不正確（{ty}）'); continue
            col = st.get('column')
            if ty == 'boss':
                if i != len(steps): warns.append(f'{where}：BOSS 不是最後一層')
            elif col not in (1, 2, 3, 4):
                errs.append(f'{where}：要選路線欄 1–4')
            team = st.get('team')
            if isinstance(team, str): team = (s.get('teams') or {}).get(team)
            if ty in ('battle', 'boss', 'random') and not st.get('manual') and not team:
                errs.append(f'{where}：自動關卡需要隊伍（或勾選「手動」）')
            for c in team or []:
                if c not in known_c: warns.append(f'{where}：餅乾「{c}」沒有卡片圖可辨識')
            for t in st.get('treasures') or []:
                if t not in known_t: warns.append(f'{where}：寶物「{t}」不在寶物清單')
            if len(st.get('treasures') or []) > 3: errs.append(f'{where}：寶物最多 3 個')
    return errs, warns


def runner_status():
    st = read_json(STATUS, {}) or {}
    mine = proc is not None and proc.poll() is None
    fresh = st.get('mode') in ('auto', 'manual') and time.time() - st.get('at', 0) < 45
    st['running'] = bool(mine or fresh)
    st['startedHere'] = mine
    st['age'] = round(time.time() - st['at'], 1) if st.get('at') else None
    st['runState'] = read_json(STATE, {}) or {}
    return st


def start_runner(name, reset):
    global proc, proc_log
    if runner_status()['running']:
        raise ValueError('程式已經在執行中')
    path = STRATS / f'{safe_name(name)}.json'
    s = read_json(path)
    if s is None: raise ValueError('找不到攻略')
    errs, _ = validate(s)
    if errs: raise ValueError('攻略有錯誤，請先修正：' + '；'.join(errs[:3]))
    if reset:
        STATE.write_text('{"zone": null, "step": 0, "pending": null}', encoding='utf-8')
    args = [sys.executable, '-B', str(BOT / 'runner.py'), str(path), '--steps', '100000']
    proc_log = LOGS / f'webui-{time.strftime("%Y%m%d-%H%M%S")}.log'
    f = open(proc_log, 'w', encoding='utf-8')
    env = {**os.environ, 'PYTHONUTF8': '1', 'PYTHONIOENCODING': 'utf-8'}
    proc = subprocess.Popen(args, cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT, env=env)
    STATUS.write_text(json.dumps({'mode': 'auto', 'message': f'啟動中：{name}', 'at': time.time()}, ensure_ascii=False), encoding='utf-8')


def touch(p):
    Path(p).write_text(str(time.time()), encoding='utf-8')


def log_tail(n=60):
    if proc_log and proc_log.exists():
        lines = proc_log.read_text(encoding='utf-8', errors='replace').splitlines()
    else:
        outs = sorted(JOBS.glob('*-run.out'), key=lambda p: p.stat().st_mtime)
        lines = outs[-1].read_text(encoding='utf-8', errors='replace').splitlines() if outs else []
    res = []
    for l in lines[-n:]:
        try:
            j = json.loads(l)
            if 'n' in j and 'action' in j:
                a = j['action']; l = f"#{j['n']} {j.get('state', '')} → {a[0]}：{a[-1] if len(a) > 1 else ''}"
        except Exception:
            pass
        res.append(l)
    return res


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype='application/json; charset=utf-8'):
        if isinstance(body, (dict, list)): body = json.dumps(body, ensure_ascii=False).encode('utf-8')
        elif isinstance(body, str): body = body.encode('utf-8')
        self.send_response(code); self.send_header('Content-Type', ctype); self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)

    def file(self, p, ctype):
        p = Path(p)
        if not p.is_file(): return self.send(404, {'error': 'not found'})
        self.send(200, p.read_bytes(), ctype)

    def do_GET(self):
        u = urlparse(self.path); q = parse_qs(u.query)
        try:
            if u.path == '/':
                return self.file(BOT / 'webui.html', 'text/html; charset=utf-8')
            if u.path == '/api/status':
                return self.send(200, runner_status())
            if u.path == '/api/log':
                return self.send(200, log_tail())
            if u.path == '/api/frame':
                f = Path((read_json(STATUS, {}) or {}).get('frame') or '')
                if f.is_file() and LOGS.resolve() in f.resolve().parents:
                    return self.file(f, 'image/jpeg')
                return self.send(404, {'error': 'no frame'})
            if u.path == '/api/catalog':
                return self.send(200, {'cards': cards(), 'treasures': treasures(), 'types': STEP_TYPES})
            if u.path == '/api/strategies':
                return self.send(200, sorted(p.stem for p in STRATS.glob('*.json')))
            if u.path == '/api/strategy':
                s = read_json(STRATS / f"{safe_name(q.get('name', [''])[0])}.json")
                return self.send(200, s) if s is not None else self.send(404, {'error': '找不到攻略'})
            if u.path.startswith('/img/card/'):
                fn = (read_json(BOT / 'cards' / 'labels.json', {}) or {}).get(unquote(u.path[10:]))
                return self.file(BOT / 'cards' / fn, 'image/png') if fn else self.send(404, {})
            if u.path.startswith('/img/treasure/'):
                name = unquote(u.path[14:])
                t = next((t for t in treasures() if t['name'] == name), None)
                return self.file(TREASURE_DIR / t['icon'], 'image/png') if t and t.get('icon') else self.send(404, {})
            return self.send(404, {'error': 'not found'})
        except ValueError as e:
            return self.send(400, {'error': str(e)})

    def do_POST(self):
        u = urlparse(self.path)
        try:
            body = json.loads(self.rfile.read(int(self.headers.get('Content-Length') or 0)) or b'{}')
            if u.path == '/api/validate':
                e, w = validate(body); return self.send(200, {'errors': e, 'warnings': w})
            if u.path == '/api/strategy':
                name = safe_name(body.get('name')); s = body.get('strategy')
                e, w = validate(s)
                if e: return self.send(400, {'error': '；'.join(e), 'errors': e, 'warnings': w})
                s.setdefault('format', 'crk-belowland-strategy'); s.setdefault('version', 1)
                (STRATS / f'{name}.json').write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding='utf-8')
                return self.send(200, {'ok': True, 'warnings': w})
            if u.path == '/api/start':
                start_runner(body.get('name'), bool(body.get('reset'))); return self.send(200, {'ok': True})
            if u.path == '/api/stop':
                touch(JOBS / 'STOP_RUN'); return self.send(200, {'ok': True})
            if u.path == '/api/resume':          # manual node finished by the player
                touch(JOBS / 'RESUME'); return self.send(200, {'ok': True})
            if u.path == '/api/clearhalt':
                st = read_json(STATE, {}) or {}
                st.pop('halt', None); st.pop('failures', None)
                STATE.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding='utf-8')
                return self.send(200, {'ok': True})
            return self.send(404, {'error': 'not found'})
        except (ValueError, json.JSONDecodeError) as e:
            return self.send(400, {'error': str(e)})


if __name__ == '__main__':
    srv = ThreadingHTTPServer(('127.0.0.1', PORT), H)
    print(f'CRK 控制台：http://127.0.0.1:{PORT}', flush=True)
    try:
        import webbrowser; webbrowser.open(f'http://127.0.0.1:{PORT}')
    except Exception:
        pass
    srv.serve_forever()
