"""Team setup on the 冥界試煉隊伍設定 screen using the user's own card captures as templates.
Each template is the card crop below the stamina badge; matching is done on the card strip at
native MuMu resolution (2560x1440). Present cards score ~1.0, absent ones <0.7."""
import json, time
from pathlib import Path
import cv2, numpy as np
HERE = Path(__file__).parent; CARDS = HERE / 'cards'
STRIP = (1105, 1409)          # y-range of the card row (2560x1440)
CARD_W, BADGE = 254, 60
MATCH_MIN = 0.90


PITCH = 280                   # card spacing on the strip (measured: constant 280 px at 2560x1440)
MARGIN = 0.10                 # best card must beat every other card at the same spot by this much
BANK = CARDS / 'bank.json'
INBOX = CARDS / 'inbox'


def _template(path):
    t = cv2.imread(str(path))[BADGE:, :]; h, w = t.shape[:2]
    m = np.ones_like(t); m[int(h * .15):int(h * .75), int(w * .05):int(w * .8)] = 0   # ignore the selection check-mark area
    return t, m


def load_templates():
    """Card templates by key. Keys: catalog ids from the confirmed card bank (cards/bank.json) and, for older
    strategies, the short names of cards/labels.json (aliases point at the same pixels)."""
    out = {}
    if BANK.exists():
        bank = json.loads(BANK.read_text(encoding='utf-8'))['cards']
        for cid, row in bank.items():
            ts = [_template(CARDS / f['file']) for f in row['files']]
            out[cid] = ts
            for a in row.get('aliases', []): out[a] = ts
    labels = json.loads((CARDS / 'labels.json').read_text(encoding='utf-8')) if (CARDS / 'labels.json').exists() else {}
    for name, files in labels.items():
        if name not in out: out[name] = [_template(CARDS / f) for f in ([files] if isinstance(files, str) else files)]
    return out


def to_bgr(img):
    return cv2.cvtColor(np.asarray(img.convert('RGB')), cv2.COLOR_RGB2BGR)


def strip_of(img):
    return to_bgr(img)[STRIP[0]:STRIP[1]]


def locate(strip, templates):
    """-> {name: (score, x_left)} for every template (best location)."""
    res = {}
    for name, ts in templates.items():
        best = (-1, None)
        for t, m in ts:
            r = cv2.matchTemplate(strip, t, cv2.TM_CCOEFF_NORMED, mask=m); r[~np.isfinite(r)] = -1; _, mx, _, loc = cv2.minMaxLoc(r)
            if mx > best[0]: best = (mx, loc[0])
        res[name] = best
    return res


def is_checked(strip, x):
    c = strip[:, x:x + CARD_W]; h, w = c.shape[:2]
    hsv = cv2.cvtColor(c[int(h * .3):int(h * .8), int(w * .15):int(w * .75)], cv2.COLOR_BGR2HSV)
    return float(((hsv[..., 0] >= 35) & (hsv[..., 0] <= 80) & (hsv[..., 1] > 150) & (hsv[..., 2] > 150)).mean()) > .04


def visible_cards(strip, templates):
    """Cards on the strip that are identified without doubt: score >= MATCH_MIN and at least MARGIN above any
    *different* card scoring at the same position. Aliases of one card are not competitors."""
    loc = locate(strip, templates)
    same = {}
    for n, ts in templates.items(): same.setdefault(id(ts[0][0]), set()).add(n)
    out = {}
    for n, (s, x) in loc.items():
        if s < MATCH_MIN: continue
        group = same[id(templates[n][0][0])]
        rival = max((s2 for m, (s2, x2) in loc.items() if m not in group and x2 is not None and abs(x2 - x) < CARD_W / 2), default=-1)
        if s - rival < MARGIN: continue          # two cards look alike here: leave it unknown
        out[n] = {'score': round(s, 3), 'x': x, 'checked': is_checked(strip, x)}
    return out


def harvest_unknown(strip, templates, log=print):
    """Save card slots that no confirmed card explains into cards/inbox/ for the user to label (web console).
    A slot counts as a card when its stamina badge (bright yellow bolt pill) is present."""
    vis = visible_cards(strip, templates)
    xs = sorted(v['x'] for v in vis.values())
    if not xs: return []
    base = xs[0] % PITCH; saved = []
    INBOX.mkdir(parents=True, exist_ok=True)
    for x in range(base, strip.shape[1] - CARD_W + 1, PITCH):
        if any(abs(x - k) < CARD_W / 2 for k in xs): continue
        c = strip[:, x:x + CARD_W]
        if c.shape[1] < CARD_W: continue
        top = cv2.cvtColor(c[:BADGE], cv2.COLOR_BGR2HSV)
        bolt = float(((top[..., 0] >= 18) & (top[..., 0] <= 40) & (top[..., 1] > 120) & (top[..., 2] > 150)).mean())
        pill = float(((top[..., 1] < 40) & (top[..., 2] > 220)).mean())
        if bolt < .006 or pill < .3: continue   # measured on cards: bolt ~.012, white pill ~.35
        import hashlib
        key = hashlib.sha1(cv2.resize(c, (32, 38)).tobytes()).hexdigest()[:16]
        f = INBOX / f'{key}.png'
        if not f.exists():
            cv2.imwrite(str(f), c); saved.append(f.name); log(f'  unknown card saved for review: {f.name}')
    return saved


def slots(strip):
    """x positions of card slots: each card carries a white stamina pill (145x54 px) whose left edge is card x + 54."""
    band = cv2.cvtColor(strip[:BADGE], cv2.COLOR_BGR2HSV)
    w = ((band[..., 1] < 40) & (band[..., 2] > 220)).astype(np.uint8)
    n, _, st, _ = cv2.connectedComponentsWithStats(w)
    xs = [int(st[i, 0]) - 54 for i in range(1, n) if 120 <= st[i, 2] <= 170 and st[i, 3] >= 40]
    return sorted(x for x in xs if 0 <= x <= strip.shape[1] - CARD_W)


_REC = None
def recognizer():
    global _REC
    if _REC is None:
        from card_model2 import CardRecognizer
        _REC = CardRecognizer()
    return _REC


def resolve_id(name):
    """strategy key -> catalog id (bank id itself, or a bank alias)."""
    if BANK.exists():
        bank = json.loads(BANK.read_text(encoding='utf-8'))['cards']
        if name in bank: return name
        for cid, row in bank.items():
            if name in row.get('aliases', []): return cid
    return name if str(name).startswith('cookie-') else None


def model_find(strip, cid, candidates=None):
    """Card-model fallback for a character without a confirmed bank card. Returns {'x','checked','by'} or None."""
    rec = recognizer()
    for x in slots(strip):
        o = rec.identify(strip[:, x:x + CARD_W], candidates)
        if o['status'] == 'ok' and o['id'] == cid:
            return {'x': x, 'checked': False, 'score': o['score'], 'by': 'model', 'art': strip[:, x:x + CARD_W].copy()}
    return None


def same_card_checked(strip, art):
    """After tapping a model-found card: find a ticked slot whose art (tick masked) correlates with the pre-tap crop."""
    import card_align as A
    ref = A.mumu_art(art).astype(np.float32)[None]
    for x in slots(strip):
        if not is_checked(strip, x): continue
        if float(A.ncc_scores(A.mumu_art(strip[:, x:x + CARD_W]), ref, A.mask())[0]) >= .8: return x
    return None


def find_card(dev, name, templates, max_swipes=3):
    """Scan the strip (start -> end) for a card. Returns (info, strip) or (None, None). Leaves strip where found."""
    y_mid = (STRIP[0] + STRIP[1]) / 2
    for attempt in range(2 * max_swipes + 2):
        img, _ = dev.capture(); strip = strip_of(img); vis = visible_cards(strip, templates)
        if name in vis and 230 < vis[name]['x'] + CARD_W / 2 < 2500:
            return vis[name], strip
        if attempt == max_swipes:   # reached the end side: go back to the start once
            for _ in range(max_swipes): dev.swipe(700, y_mid, 2300, y_mid, 700); time.sleep(0.8)
        elif attempt < max_swipes: dev.swipe(2300, y_mid, 700, y_mid, 900)
        else: dev.swipe(2300, y_mid, 700, y_mid, 900)
        time.sleep(1.2)
    return None, None


def set_team(dev, wanted, clear_point, log=print, max_swipes=3):
    """On TEAM_SELECT: clear all, then tap each wanted card and re-find it to verify the check mark."""
    templates = load_templates()
    missing = [n for n in wanted if n not in templates and not resolve_id(n)]
    if missing:
        try:
            img, _ = dev.capture(); harvest_unknown(strip_of(img), templates, log)
        except Exception: pass
        return {'ok': False, 'reason': f'這些角色還沒有確認過的遊戲內卡片：{missing}（請到網頁「角色卡片」確認）'}
    dev.tap(*clear_point); time.sleep(1.0)
    y_mid = (STRIP[0] + STRIP[1]) / 2; done = []
    roster = {resolve_id(n) for n in wanted} - {None}
    for name in wanted:
        if name not in templates:            # no confirmed in-game card: the card model may identify it (never guesses)
            r = model_select(dev, resolve_id(name), roster, max_swipes, log)
            if not r: return {'ok': False, 'reason': f'card {name} not identified without doubt', 'selected': done}
            done.append(name); continue
        info, _ = find_card(dev, name, templates, max_swipes)
        if info is None:
            try:
                img, _ = dev.capture(); harvest_unknown(strip_of(img), templates, log)
            except Exception: pass
            return {'ok': False, 'reason': f'card {name} not found (or not identifiable without doubt)', 'selected': done}
        if not info['checked']:
            dev.tap(info['x'] + CARD_W / 2, y_mid); time.sleep(1.0)
            info, _ = find_card(dev, name, templates, max_swipes)
            log(f'  tap {name} -> checked={bool(info and info["checked"])}')
            if not info or not info['checked']: return {'ok': False, 'reason': f'could not verify {name} selected', 'selected': done}
        done.append(name)
    return {'ok': True, 'selected': done}


def model_select(dev, cid, roster, max_swipes, log):
    y_mid = (STRIP[0] + STRIP[1]) / 2
    for attempt in range(2 * max_swipes + 2):
        img, _ = dev.capture(); strip = strip_of(img); hit = model_find(strip, cid)
        if hit:
            dev.tap(hit['x'] + CARD_W / 2, y_mid); time.sleep(1.0)
            for _ in range(2 * max_swipes + 2):     # the strip may jump back after a tap: look for the ticked twin
                img, _ = dev.capture(); x = same_card_checked(strip_of(img), hit['art'])
                if x is not None:
                    log(f'  tap {cid} (card model, score {hit["score"]}) -> checked=True'); return True
                dev.swipe(2300, y_mid, 700, y_mid, 900); time.sleep(1.2)
            log(f'  tap {cid} (card model) -> could not verify the tick'); return False
        if attempt == max_swipes:
            for _ in range(max_swipes): dev.swipe(700, y_mid, 2300, y_mid, 700); time.sleep(0.8)
        else: dev.swipe(2300, y_mid, 700, y_mid, 900)
        time.sleep(1.2)
    return False
