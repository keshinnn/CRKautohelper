"""CRK Belowland runner (MuMu/ADB). observe -> decide -> act -> re-observe.
Map taps are reversible (they only open a preview); the irreversible 進入 is gated by an
OCR-verified preview floor. Unknown screens wait briefly, then pause with the frame saved.
usage: runner.py <strategy.json> [--steps N] [--dry] [--reset]"""
import json, re, sys, time
from pathlib import Path
HERE = Path(__file__).parent; sys.path.insert(0, str(HERE))
from adb_bridge import Device
from observe import observe_image
from navigator import plan_map_tap, verify_preview, header_progress
from screen_model import predict as screen_predict, PASSIVE

STATE_FILE = HERE / 'run-state.json'
STATUS_FILE = HERE / 'status.json'


def write_status(d):
    """Shared with webui.py: what the runner is doing right now."""
    d = {**d, 'at': time.time(), 'pid': __import__('os').getpid()}
    tmp = STATUS_FILE.with_suffix('.tmp'); tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8'); tmp.replace(STATUS_FILE)


def norm(t):
    return re.sub(r'\s+', '', t or '').translate(str.maketrans({'战': '戰', '斗': '鬥', '门': '鬥', '进': '進', '确': '確', '认': '認', '继': '繼', '续': '續', '区': '區', '层': '層', '试': '試', '胜': '勝', '败': '敗'}))


def texts(p, min_score=.8):
    return [(norm(r['text']), r) for r in p['evidence'] if r['score'] >= min_score]


def find_text(p, pattern, min_score=.85):
    rows = [r for t, r in texts(p, min_score) if re.fullmatch(pattern, t)]
    return rows


def center_of(row):
    xs = [q[0] for q in row['box']]; ys = [q[1] for q in row['box']]
    return ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)


def green_button(img, region):
    import cv2, numpy as np
    x0, y0, x1, y1 = region
    a = cv2.cvtColor(np.asarray(img.convert('RGB'))[y0:y1, x0:x1], cv2.COLOR_RGB2HSV)
    m = ((a[..., 0] >= 30) & (a[..., 0] <= 72) & (a[..., 1] >= 125) & (a[..., 2] >= 135)).astype('uint8')
    n, lab, stats, cent = cv2.connectedComponentsWithStats(m)
    best = max(range(1, n), key=lambda i: stats[i, 4], default=None)
    if best is None or stats[best, 4] < 15000: return None
    return (x0 + cent[best][0], y0 + cent[best][1])


def patch_changed(a, b, pt, r=110, limit=12.0):
    """Freshness guard: compare the analysed frame and a fresh capture around the tap point."""
    import numpy as np
    x, y = pt
    pa = np.asarray(a.convert('L').crop((x - r, y - r, x + r, y + r)).resize((44, 44))).astype(float)
    pb = np.asarray(b.convert('L').crop((x - r, y - r, x + r, y + r)).resize((44, 44))).astype(float)
    return float(np.abs(pa - pb).mean()) > limit


def box_center(b):
    return (b[0] + b[2] / 2, b[1] + b[3] / 2)


def result_state(T):
    """Result banner '區域Z第F層' + 勝利/失敗 (replaces V1's template fallback, which only ever contributed FAILURE)."""
    header = any(re.search(r'區域\d+第\d+[層唇]', t) for t in T)
    timer = any(re.fullmatch(r'\d{2}:\d{2}\.\d{2}', t) for t in T)   # result-screen clear time, e.g. 00:51.82
    if not (header or timer): return None
    if any(t in ('失敗', '失败') for t in T): return 'FAILURE'
    if any(t == '勝利' for t in T): return 'VICTORY'
    return None


def preview_panel(T):
    """Right-hand node panel open over the map (held-out S4 video: V1 called all of these MAP).
    Any panel shows 危險度; the map alone never does. Subtype from its own labels."""
    j = '\n'.join(T)
    if not ('危險度' in j or '危险度' in j or '危度' in j): return None
    if '可能發生的事件' in j or '冥界裂' in j: return 'RIFT'
    if '恢復方式' in j or '恢復所有' in j or '所選餅乾' in j: return 'HEAL'
    if any(t == '進入' for t in T) or '套用效果' in j:
        if 'BOSS' in j.upper(): return 'BOSS'
        if any(t.startswith('激') for t in T): return 'ELITE'
        return 'BATTLE'
    return 'UNKNOWN_PANEL'


def recruit_popup(T):
    j = '\n'.join(T)
    return ('發現新' in j or '加入了' in j) and any(t == '加入' for t in T)


def classify(p):
    """Canonical screen class used by the runner (same rules/order as Runner.decide), for offline evaluation."""
    f = p['flow']; state = f['state']; T = [t for t, _ in texts(p)]; joined = '\n'.join(T)
    if '確定要開始' in joined and find_text(p, '開始'): return 'UNDERFILLED_CONFIRM'
    if state == 'EXPEDITION_ROSTER': return 'ROSTER'
    if '最高分數' in joined and '最高過關區域' in joined and find_text(p, '進入'): return 'LOBBY'
    if any(re.fullmatch(r'第(\d+)[層唇]冥界裂[縫缝]', t) for t in T): return 'RIFT_RESOLVING' if '確認結果' in joined else 'PREVIEW_RIFT'
    if state in ('NODE_BATTLE', 'NODE_BOSS'): return 'PREVIEW_' + state[5:]
    if state == 'UNKNOWN' and result_state(T): return result_state(T)
    if any('結束探' in t or '前往大廳' in t for t in T): return 'EXPEDITION_MENU'
    if recruit_popup(T): return 'RECRUIT'
    pv = preview_panel(T) if state in ('MAP', 'UNKNOWN') else None
    if pv: return 'PREVIEW_' + pv
    if any('讀取中' in t for t in T): return 'LOADING'
    if state == 'UNKNOWN' and any(t in ('隊伍設定', '隧伍設定') for t in T) and ('登場' in joined or 'BOSS' in joined or '前排' in joined): return 'BATTLE_READY'
    if state in ('MAP', 'NODE_ENTRY_CONFIRM', 'BATTLE_READY', 'TEAM_SELECT', 'TREASURE_SELECT', 'MISSING_EQUIPMENT', 'BATTLE', 'VICTORY', 'FAILURE', 'AREA_REWARD'): return state
    return 'UNKNOWN'


class Runner:
    def __init__(self, strategy, dry=False):
        self.s = strategy; self.dry = dry; self.d = Device()
        self.state = json.loads(STATE_FILE.read_text(encoding='utf-8')) if STATE_FILE.exists() else {'zone': None, 'step': 0, 'pending': None}
        self.log_dir = HERE / 'runs' / time.strftime('%Y%m%d-%H%M%S'); self.log_dir.mkdir(parents=True)
        self.unknown_since = None; self.n = 0

    def save(self):
        STATE_FILE.write_text(json.dumps(self.state, ensure_ascii=False, indent=1), encoding='utf-8')

    def zone_steps(self, zone):
        z = next((z for z in self.s['zones'] if z['zone'] == zone), None)
        return z['steps'] if z else None

    def current_step(self):
        steps = self.zone_steps(self.state['zone'])
        if steps is None or self.state['step'] >= len(steps):
            return None
        st = dict(steps[self.state['step']]); st['floor'] = self.state['step'] + 1
        if st['type'] == 'boss': st['column'] = None
        return st

    def team_of(self, st):
        t = st.get('team')
        if isinstance(t, str): t = self.s.get('teams', {}).get(t)
        return list(t) if t else None

    # ---------- manual hand-over ----------
    @staticmethod
    def manual_msg(m):
        return f"手動關卡：區域{m['zone']} 第{m['floor']}層 — 請玩家接手遊玩；打出勝利畫面後程式自動接手" + (f"（{m['note']}）" if m.get('note') else '')

    def manual_done(self, m, why):
        self.state.pop('manual', None); self.state.pop('mapTaps', None)
        self.state.update(step=m['step'] + 1, pending=None, previewSeen=None, mapCandidate=None)
        return ('wait', f'手動關卡 區域{m["zone"]} 第{m["floor"]}層 完成（{why}）-> 恢復自動')

    def manual_watch(self, T, m):
        """Player is playing this node. Never tap; only watch for proof that the node was cleared."""
        resume = HERE / 'jobs' / 'RESUME'
        if resume.exists() and resume.stat().st_mtime > m['since']:
            return self.manual_done(m, '玩家在網頁按下「已完成，繼續」')
        if '勝利' in T:
            hdr = next((re.search(r'區域(\d+)第(\d+)[層唇]', t) for t in T if re.search(r'區域(\d+)第(\d+)[層唇]', t)), None)
            if hdr and int(hdr.group(1)) == m['zone'] and int(hdr.group(2)) == m['floor']:
                return self.manual_done(m, '偵測到勝利畫面')
        if any(re.fullmatch(rf"{m['zone']}區域完成", t) for t in T):
            return self.manual_done(m, '偵測到區域完成')
        return ('manual', self.manual_msg(m))

    # ---------- decisions ----------
    def decide(self, p):
        f = p['flow']; state = f['state']; T = [t for t, _ in texts(p)]
        if self.state.get('halt') and state not in ('BATTLE', 'VICTORY', 'FAILURE'):
            return ('pause', self.state['halt'] + '（請調整後清除 halt 再繼續）')
        joined = '\n'.join(T)
        # independent screen model (OCR cues + appearance kNN, bot/screen_model.py); conflicts never act
        sm = p.get('screen')
        if sm is None and getattr(self, 'last_img', None) is not None:
            sm = p['screen'] = screen_predict(self.last_img, [t for t, _ in texts(p)], state)
        sm = sm or {'cls': 'UNKNOWN', 'how': 'no image'}
        man = self.state.get('manual')
        if man:
            return self.manual_watch(T, man)
        st0 = self.current_step()
        if st0 and st0.get('manual') and (state in ('MAP', 'NODE_BATTLE', 'NODE_BOSS', 'NODE_ENTRY_CONFIRM', 'BATTLE_READY', 'TEAM_SELECT') or preview_panel(T)):
            self.state['manual'] = {'zone': self.state['zone'], 'step': self.state['step'], 'floor': st0['floor'], 'since': time.time(), 'note': st0.get('note')}
            self.state.update(pending=None, previewSeen=None, mapCandidate=None)
            return ('manual', self.manual_msg(self.state['manual']))
        rres = next((re.fullmatch(r'第(\d+)[層唇](加入[餅饼]乾|.*獎勵|.*奬勵)', t) for t in T if re.fullmatch(r'第(\d+)[層唇](加入[餅饼]乾|.*獎勵|.*奬勵)', t)), None)
        if rres and not re.search(r'危[險险]?度', joined):   # rift outcome panel without a fight: the floor is finished
            pend = self.state.get('pending') or {}
            if pend.get('type') == 'random' and pend.get('floor') == int(rres.group(1)):
                self.state.update(step=pend['step'] + 1, pending=None, previewSeen=None); self.state.pop('mapTaps', None)
                return ('tap', (2490, 290), f'rift result floor {rres.group(1)} ({rres.group(2)}) -> floor done, close panel')
            return ('pause', f'rift result panel floor {rres.group(1)} without a matching pending rift step')
        if sm['cls'] == 'RIFT_RESOLVING':
            return ('wait', 'rift result resolving (purple panel button)')
        if state == 'MAP' and sm['cls'] == 'UNKNOWN' and sm['how'].startswith('conflict'):
            return ('wait', 'screen model conflict on a map frame: ' + sm['how'])
        if '確定要開始' in joined and find_text(p, '開始'):
            return ('tap', center_of(find_text(p, '開始')[-1]), 'underfilled team confirm -> start (strategy uses fewer than 5)')
        if state == 'EXPEDITION_ROSTER':
            return ('pause', '遠征隊名單畫面：請手動選好 15 隻')
        # entry screen (season lobby)
        if '最高分數' in joined and '最高過關區域' in joined and find_text(p, '進入'):
            roster = next((t for t in T if re.fullmatch(r'\+?\d+/15.*', t)), None)
            if not roster or not roster.lstrip('+').startswith('15/15'):
                return ('pause', f'遠征隊尚未選滿 15 隻（{roster}）')
            return ('tap', center_of(find_text(p, '進入')[0]), 'enter expedition')
        rift = next((re.fullmatch(r'第(\d+)[層唇]冥界裂[縫缝]', t) for t in T if re.fullmatch(r'第(\d+)[層唇]冥界裂[縫缝]', t)), None)
        if rift and '確認結果' in joined:
            return ('wait', 'rift resolving (確認結果中)')
        if rift:
            st = self.current_step()
            if not st or int(rift.group(1)) != st['floor']:
                return ('pause', f'rift preview floor {rift.group(1)} != strategy floor {st and st["floor"]}')
            seen = self.state.get('previewSeen')
            self.state['previewSeen'] = {'floor': int(rift.group(1)), 'state': 'RIFT', 'at': time.time()}
            if not (seen and seen['floor'] == int(rift.group(1)) and seen['state'] == 'RIFT' and time.time() - seen['at'] <= 8):
                return ('wait', f'rift preview floor {rift.group(1)} seen once; need a second consistent preview')
            rows = sorted(find_text(p, '確(認|定)?'), key=lambda r: center_of(r)[1])
            if rows: self.state['previewSeen'] = None; self.state.pop('mapTaps', None)
            if rows: return ('tap', center_of(rows[-1]), f'rift floor {rift.group(1)} verified twice -> 確認')
            g = green_button(self.last_img, (1800, 1150, 2560, 1440))
            return ('tap', g, 'rift -> confirm (green)') if g else ('wait', 'rift: confirm not visible yet')
        if any('結束探' in t or '前往大廳' in t for t in T):
            return ('pause', 'expedition menu (繼續/前往大廳/結束探險) is open; never act behind it')
        if recruit_popup(T):
            rows = find_text(p, '加入')
            return ('tap', center_of(rows[-1]), 'recruit popup -> 加入 (no choice offered)')
        pv = preview_panel(T) if state in ('MAP', 'UNKNOWN') else None   # dialogs over the panel keep their own state
        if pv == 'HEAL' and '已恢復' in T:   # heal already applied; the panel stays open -> close it (reversible)
            return ('tap', (2490, 290), 'heal done (已恢復) -> close panel')
        if pv == 'HEAL':
            st = self.current_step(); pend = self.state.get('pending') or {}
            fl = next((int(m.group(1)) for t in T for m in [re.search(r'第(\d+)[層唇]', t)] if m), None)
            if not st or st['type'] not in ('heal', 'random') or pend.get('type') != st['type'] or pend.get('floor') != st['floor'] or (fl is not None and fl != st['floor']):
                return ('pause', f'heal panel open but strategy step is {st and st["type"]} (pending {pend.get("type")}); not acting')
            seen = self.state.get('previewSeen')
            self.state['previewSeen'] = {'floor': st['floor'], 'state': 'HEAL', 'at': time.time()}
            if not (seen and seen['state'] == 'HEAL' and seen['floor'] == st['floor'] and time.time() - seen['at'] <= 8):
                return ('wait', 'heal panel seen once; need a second consistent observation')
            # default option is 恢復所有餅乾 (all +20); the action button at the panel bottom reads '…恢復'
            btn = sorted([r for t, r in texts(p, .85) if t.endswith('恢復') and t not in ('恢復',) or t == '恢復'], key=lambda r: center_of(r)[1])
            if not btn: return ('pause', 'heal confirm button not found')
            self.state.update(previewSeen=None, pending=None, step=self.state['step'] + 1); self.state.pop('mapTaps', None)
            return ('tap', center_of(btn[-1]), f'heal floor {st["floor"]}: default 恢復所有餅乾 -> 恢復')
        if pv == 'UNKNOWN_PANEL':
            return ('pause', 'unknown node panel open (never plan map taps behind a panel)')
        if pv == 'RIFT' and not rift:
            return ('pause', 'rift panel open but its floor is unreadable; cannot verify against strategy')
        if pv and pv != 'RIFT':
            state = 'NODE_BOSS' if pv == 'BOSS' else 'NODE_BATTLE'   # never plan map taps behind an open preview
            if not [t for t in f.get('targets', []) if t.get('target') == 'enter']:
                rows = find_text(p, '進入')
                if rows:
                    xs = [q[0] for q in rows[-1]['box']]; ys = [q[1] for q in rows[-1]['box']]
                    f = {**f, 'targets': [{'target': 'enter', 'box': [min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)]}]}; p = {**p, 'flow': f}
        if state in ('NODE_BATTLE', 'NODE_BOSS') and preview_panel(T) and not [t for t in f.get('targets', []) if t.get('target') == 'enter']:
            rows = find_text(p, '進入')   # V1 may miss the button on a panel it classified itself; accept a unique OCR 進入
            if len(rows) == 1:
                xs = [q[0] for q in rows[0]['box']]; ys = [q[1] for q in rows[0]['box']]
                f = {**f, 'targets': [{'target': 'enter', 'box': [min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)]}]}; p = {**p, 'flow': f}
        if state == 'UNKNOWN' and result_state(T):
            state = result_state(T)
        if any('讀取中' in t for t in T):
            return ('wait', 'loading screen')
        if state == 'UNKNOWN' and any(t in ('隊伍設定', '隧伍設定') for t in T) and ('登場' in joined or 'BOSS' in joined or '前排' in joined):
            state = 'BATTLE_READY'
        tap_on = [r for r in texts(p, .8) if re.fullmatch(r'輕觸?以繼?續', r[0])] if state in ('MAP', 'UNKNOWN') else []
        if tap_on:   # reward toast over the map ('節點突破獎勵 … 輕觸以繼續'): dismiss it, never plan on it
            return ('tap', center_of(tap_on[-1][1]), 'reward toast -> tap to continue')
        if state == 'MAP' and self.state.get('halt'):
            return ('pause', self.state['halt'] + '（請調整隊伍／配料後清除 halt 再繼續）')
        if state == 'MAP':
            hp = header_progress(p['evidence'])
            done = next((re.fullmatch(r'(\d+)區域完成', t) for t in T if re.fullmatch(r'(\d+)區域完成', t)), None)
            zone = hp[0] if hp else (self.state['zone'] if done and int(done.group(1)) == self.state['zone'] - 1 else p['progress'].get('displayedZone'))
            if not hp and done and int(done.group(1)) == self.state['zone'] and self.state['step'] >= len(self.zone_steps(self.state['zone']) or []):
                self.state.update(zone=self.state['zone'] + 1, step=0, pending=None, scrolls=0); self.state.pop('mapTaps', None)
                return ('wait', f'區域{done.group(1)}完成 -> next zone {self.state["zone"]}')
            if zone is None:
                return ('wait', 'map zone unknown')
            if self.state['zone'] != zone:
                self.state.update(zone=zone, step=(hp[1] - 1) if hp else 0, pending=None)
            st = self.current_step()
            if st is None:
                return ('pause', f'區域 {zone} 第 {self.state["step"]+1} 步沒有攻略資料')
            # deepest completed floor = header floor only when two sources agree: the header '第F層進行中'
            # and our own victory record (step == F), and no node carries the '進行中' label.
            labels = [t for t in T if t == '進行中']
            if hp and hp[1] == self.state['step'] and not labels:
                p['_lastCompletedFloor'] = hp[1]
            plan = plan_map_tap(p, st)
            if plan['point'] is None:
                if plan.get('scroll') and self.state.get('scrolls', 0) < 4:
                    self.state['scrolls'] = self.state.get('scrolls', 0) + 1
                    W, H = self.d.size[1], self.d.size[0]  # landscape
                    return ('swipe', (W*0.5, H*0.7, W*0.5, H*0.35) if plan['scroll'] == 'down' else (W*0.5, H*0.35, W*0.5, H*0.7), plan['reason'])
                return ('pause', 'map: ' + plan['reason'])
            self.state['scrolls'] = 0
            cand = {'floor': st['floor'], 'column': st['column'], 'point': [round(v, 1) for v in plan['point']], 'at': time.time()}
            prev = self.state.get('mapCandidate')
            stable = prev and prev['floor'] == cand['floor'] and prev['column'] == cand['column'] and \
                abs(prev['point'][0] - cand['point'][0]) <= 6 and abs(prev['point'][1] - cand['point'][1]) <= 6 and cand['at'] - prev['at'] <= 8
            self.state['mapCandidate'] = cand
            if not stable:
                return ('wait', f'map target f{st["floor"]} c{st["column"]} seen once; need a second consistent observation')
            taps = self.state.setdefault('mapTaps', {}); key = f"{zone}-{st['floor']}"
            if taps.get(key, 0) >= 2:
                return ('pause', f'map tap for floor {st["floor"]} sent twice without a preview; stop (no blind re-tapping)')
            taps[key] = taps.get(key, 0) + 1; self.state['mapCandidate'] = None
            self.state['pending'] = {'zone': zone, 'step': self.state['step'], 'floor': st['floor'], 'type': st['type'], 'column': st['column'], 'nodeId': plan.get('nodeId')}
            return ('tap', plan['point'], f'map node z{zone} f{st["floor"]} c{st["column"]} ({plan["reason"]}, 2 consistent observations)')
        if state in ('NODE_BATTLE', 'NODE_BOSS'):
            st = self.current_step()
            if st is None: return ('pause', 'preview without strategy step')
            v = verify_preview(p, st)
            if not v['ok']:
                return ('pause', 'preview mismatch: ' + v['reason'])
            want = {'battle': 'NODE_BATTLE', 'boss': 'NODE_BOSS', 'random': None}.get(st['type'], 'NODE_BATTLE')
            if want and state != want:
                return ('pause', f'preview type {state} does not match strategy step type {st["type"]}')
            seen = self.state.get('previewSeen')
            self.state['previewSeen'] = {'floor': v['floor'], 'state': state, 'at': time.time()}
            if not (seen and seen['floor'] == v['floor'] and seen['state'] == state and time.time() - seen['at'] <= 8):
                return ('wait', f'preview floor {v["floor"]} seen once; need a second consistent preview before 進入')
            self.state['previewSeen'] = None; self.state.pop('mapTaps', None)
            return ('tap', box_center(v['enter']['box']), f'enter floor {v["floor"]} (2 consistent previews)')
        if state == 'NODE_ENTRY_CONFIRM':
            rows = find_text(p, '(繼?續|確認|確定)')
            return ('tap', center_of(rows[-1]), 'confirm node entry') if rows else ('pause', 'entry confirm button not found')
        if state == 'BATTLE_READY':
            st = self.current_step(); key = [self.state['zone'], self.state['step']]
            if st and self.team_of(st) and self.state.get('teamSetFor') != key:
                ts = [t for t in f.get('targets', []) if t['target'] == 'teamSettings']
                pt = box_center(ts[0]['box']) if ts else (center_of(find_text(p, '隊伍設定|隧伍設定')[0]) if find_text(p, '隊伍設定|隧伍設定') else None)
                return ('tap', pt, 'open team settings') if pt else ('pause', 'team settings button not found')
            start = [t for t in f.get('targets', []) if t['target'] == 'battleStart']
            if len(start) == 1: return ('tap', box_center(start[0]['box']), 'battle start')
            rows = find_text(p, '(戰鬥|鬥)?開始')
            if rows: return ('tap', center_of(rows[-1]), 'battle start (text)')
            g = green_button(self.last_img, (1800, 1150, 2560, 1440))
            return ('tap', g, 'battle start (green button)') if g else ('pause', 'battle start button not found')
        if state == 'TEAM_SELECT':
            st = self.current_step(); team = self.team_of(st) if st else None
            if not team: return ('pause', 'team select without strategy team')
            clear = [t for t in f.get('targets', []) if t['target'] == 'clearAll']
            if not clear: return ('pause', 'clear-all button not verified')
            treasures = st.get('treasures') or self.s.get('treasures', {}).get('default', [])
            return ('team', {'team': team, 'treasures': treasures, 'clear': box_center(clear[0]['box'])}, 'set team ' + ','.join(team) + ' + treasures')
        if state == 'BATTLE':
            auto = f.get('autoSkills') or {}
            if auto.get('verified') and auto.get('enabled') is False:
                return ('tap', box_center(auto['box']), 'enable auto skills')
            return ('wait', 'battle in progress')
        if state == 'VICTORY':
            hdr = next((re.search(r'區域(\d+)第(\d+)[層唇]', t) for t in T if re.search(r'區域(\d+)第(\d+)[層唇]', t)), None)
            if hdr:
                self.state.update(zone=int(hdr.group(1)), step=int(hdr.group(2)), pending=None)   # idempotent: floor F done -> next step index F
            rows = find_text(p, '離開')
            if rows:
                self.state.pop('victoryWaits', None)
                return ('tap', center_of(rows[-1]), f'victory {hdr.group(0) if hdr else ""} -> 離開')
            w = self.state['victoryWaits'] = self.state.get('victoryWaits', 0) + 1
            if w % 3 == 0:   # like the failure screen, 離開 stays hidden until the result screen is tapped
                return ('tap', (1280, 1340), 'victory: reveal buttons (tap empty area below rewards)')
            return ('wait', 'victory: waiting for 離開 button')
        if state == 'FAILURE':
            st = self.current_step() or {}; key = f"{self.state['zone']}-{self.state['step']}"
            fails = self.state.setdefault('failures', {}); limit = st.get('attempts') or self.s.get('options', {}).get('retryLimit', 2)
            retry, leave = find_text(p, '再一次'), find_text(p, '離開')
            if not retry and not leave:
                return ('tap', (1280, 1100), 'failure: reveal buttons')
            if self.state.get('lastFailureFrame') == p['flow'].get('frameId'):
                return ('wait', 'failure: same frame')
            fails[key] = fails.get(key, 0) + 1
            if fails[key] <= limit and retry:
                self.state['teamSetFor'] = [self.state['zone'], self.state['step']]   # retry keeps the same team
                return ('tap', center_of(retry[-1]), f'failure #{fails[key]} -> 再一次 (limit {limit})')
            self.state['halt'] = f'區域{self.state["zone"]} 第{self.state["step"]+1}步 已失敗 {fails[key]} 次'
            return ('tap', center_of(leave[-1]), 'failure: retry limit reached -> 離開') if leave else ('pause', self.state['halt'])
        if state == 'AREA_REWARD':
            r = f.get('rewardContinuation') or {}
            pt = box_center(r['box']) if r.get('verified') else (self.d.size[1]*0.5, self.d.size[0]*0.9)
            self.state.update(zone=(self.state['zone'] or 0) + 1, step=0, pending=None)
            return ('tap', pt, 'area reward -> continue')
        if state == 'MISSING_EQUIPMENT' and self.s.get('options', {}).get('ignoreMissingEquipment', True):
            rows = sorted(find_text(p, '確(認|定)?'), key=lambda r: center_of(r)[1])
            return ('tap', center_of(rows[-1]), 'missing toppings/biscuit popup -> confirm (user: ignore during testing)') if rows else ('pause', 'missing-equipment confirm not found')
        if state in ('TREASURE_SELECT', 'MISSING_EQUIPMENT', 'EXPEDITION_ROSTER'):
            return ('pause', f'{state} 需要處理（尚未自動化）')
        if sm['cls'] in PASSIVE:   # V1 had no state, but the screen model sees a screen where we only wait
            self.passive_since = getattr(self, 'passive_since', None) or time.time()
            cap = {'LOADING': 60, 'BOSS_INTRO': 30}.get(sm['cls'], 240)   # unseen non-Belowland screens can look like loading art
            if time.time() - self.passive_since > cap:
                return ('pause', f'{sm["cls"]}（只有影像判斷）超過 {cap} 秒沒有變化，請確認畫面')
            return ('wait', f'{sm["cls"]} (screen model {sm["how"]}, {sm.get("imageConf")})')
        return ('unknown', state)

    # ---------- loop ----------
    def step(self):
        self.n += 1
        img, at = self.d.capture(); self.last_img = img; t0 = time.perf_counter(); p = observe_image(img)
        obs_ms = round((time.perf_counter() - t0) * 1000)
        action = self.decide(p); kind = action[0]
        if not str(action[-1]).startswith(('BATTLE (screen', 'LOADING (screen', 'BOSS_INTRO (screen')): self.passive_since = None
        if kind == 'unknown':
            self.unknown_since = self.unknown_since or time.time()
            kind = 'pause' if time.time() - self.unknown_since > 20 else 'wait'
            action = (kind, f'unrecognized screen ({action[1]})')
        else:
            self.unknown_since = None
        rec = {'n': self.n, 'at': at, 'state': p['flow']['state'], 'obsMs': obs_ms, 'action': [str(a) if not isinstance(a, (int, float, str, list, tuple)) else a for a in action],
               'run': dict(self.state), 'texts': [t for t, _ in texts(p, .85)][:40], 'screen': p.get('screen')}
        img.convert('RGB').resize((1280, 720)).save(self.log_dir / f'{self.n:04d}.jpg', quality=80)
        if kind in ('pause', 'wait') or kind == 'unknown': img.save(self.log_dir / f'{self.n:04d}-full.png', compress_level=1)
        (self.log_dir / f'{self.n:04d}.json').write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding='utf-8')
        print(json.dumps({k: rec[k] for k in ('n', 'state', 'obsMs', 'action', 'run')}, ensure_ascii=False), flush=True)
        write_status({'mode': 'manual' if kind == 'manual' else ('paused' if kind == 'pause' else 'auto'), 'message': str(action[-1]),
                      'n': self.n, 'state': rec['state'], 'action': kind, 'run': rec['run'], 'frame': str(self.log_dir / f'{self.n:04d}.jpg')})
        if kind == 'manual':
            self.save(); time.sleep(3.0); return kind
        if not self.dry:
            if kind == 'tap':
                fresh, _ = self.d.capture()
                if patch_changed(img, fresh, action[1]):
                    print(json.dumps({'n': self.n, 'skipped': 'screen changed at tap point since analysis; re-observe'}, ensure_ascii=False), flush=True)
                    self.save(); return 'wait'
                self.d.tap(*action[1]); time.sleep(1.5)
            elif kind == 'swipe': self.d.swipe(*action[1], ms=600); time.sleep(1.2)
            elif kind == 'wait': time.sleep(2.0)
            elif kind == 'team':
                fresh, _ = self.d.capture()
                if patch_changed(img, fresh, action[1]['clear']):
                    print(json.dumps({'n': self.n, 'skipped': 'team screen changed since analysis; re-observe'}, ensure_ascii=False), flush=True)
                    self.save(); return 'wait'
                from team import set_team
                r = set_team(self.d, action[1]['team'], action[1]['clear'], log=lambda m: print(m, flush=True))
                print(json.dumps(r, ensure_ascii=False), flush=True)
                if not r['ok']: self.save(); return 'pause'
                wanted_t = action[1].get('treasures') or []
                if wanted_t:
                    from treasure import equip
                    self.d.tap(141, 380); time.sleep(1.5)        # first treasure slot -> 裝備寶物 modal
                    tr = equip(self.d, wanted_t, log=lambda m: print(m, flush=True))
                    print(json.dumps(tr, ensure_ascii=False), flush=True)
                    self.d.tap(2300, 105); time.sleep(1.2)       # close modal
                    if not tr['ok']: self.save(); return 'pause'
                self.d.tap(2480, 75); time.sleep(1.5)   # close team screen (top-right X)
                self.state['teamSetFor'] = [self.state['zone'], self.state['step']]
        self.save()
        return kind


if __name__ == '__main__':
    args = sys.argv[1:]; strategy = json.loads(Path(args[0]).read_text(encoding='utf-8'))
    steps = int(args[args.index('--steps') + 1]) if '--steps' in args else 1
    if '--reset' in args and STATE_FILE.exists(): STATE_FILE.write_text('{"zone": null, "step": 0, "pending": null}', encoding='utf-8')
    try:
        r = Runner(strategy, dry='--dry' in args); print('log', r.log_dir, flush=True)
    except Exception as e:
        write_status({'mode': 'error', 'message': f'無法連上模擬器（ADB）：{e!r}'[:300]}); raise
    stop = HERE / 'jobs' / 'STOP_RUN'; t_start = time.time()
    end = {'mode': 'stopped', 'message': f'已執行 {steps} 步上限'}
    for _ in range(steps):
        if stop.exists() and stop.stat().st_mtime > t_start:
            print('stopped by STOP_RUN'); end = {'mode': 'stopped', 'message': '已由使用者停止'}; break
        try:
            k = r.step()
        except Exception as e:
            import traceback; traceback.print_exc(); end = {'mode': 'error', 'message': f'程式錯誤：{e!r}'}; break
        if k == 'pause':
            last = json.loads(STATUS_FILE.read_text(encoding='utf-8')) if STATUS_FILE.exists() else {}
            end = {'mode': 'paused', 'message': last.get('message', '暫停')}; break
    last = json.loads(STATUS_FILE.read_text(encoding='utf-8')) if STATUS_FILE.exists() else {}
    r.save(); write_status({**last, **end, 'run': r.state, 'n': r.n})
