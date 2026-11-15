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


def load_templates():
    labels = json.loads((CARDS / 'labels.json').read_text(encoding='utf-8'))
    out = {}
    for name, files in labels.items():
        ts = []
        for f in ([files] if isinstance(files, str) else files):
            t = cv2.imread(str(CARDS / f))[BADGE:, :]; h, w = t.shape[:2]
            m = np.ones_like(t); m[int(h * .15):int(h * .75), int(w * .05):int(w * .8)] = 0   # ignore the selection check-mark area
            ts.append((t, m))
        out[name] = ts
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
    found = {n: (s, x) for n, (s, x) in locate(strip, templates).items() if s >= MATCH_MIN}
    return {n: {'score': round(s, 3), 'x': x, 'checked': is_checked(strip, x)} for n, (s, x) in found.items()}


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
    missing = [n for n in wanted if n not in templates]
    if missing: return {'ok': False, 'reason': f'no card template for {missing}'}
    dev.tap(*clear_point); time.sleep(1.0)
    y_mid = (STRIP[0] + STRIP[1]) / 2; done = []
    for name in wanted:
        info, _ = find_card(dev, name, templates, max_swipes)
        if info is None: return {'ok': False, 'reason': f'card {name} not found', 'selected': done}
        if not info['checked']:
            dev.tap(info['x'] + CARD_W / 2, y_mid); time.sleep(1.0)
            info, _ = find_card(dev, name, templates, max_swipes)
            log(f'  tap {name} -> checked={bool(info and info["checked"])}')
            if not info or not info['checked']: return {'ok': False, 'reason': f'could not verify {name} selected', 'selected': done}
        done.append(name)
    return {'ok': True, 'selected': done}
