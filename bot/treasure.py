"""Treasure modal (裝備寶物) at 2560x1440.
Tap a grid icon -> detail panel shows its exact title (OCR-verified) -> tap the arrowed empty slot to equip.
Icons are located with V1's TreasureModel (data/treasures references)."""
import json, re, sys, time
from pathlib import Path
import cv2, numpy as np
HERE = Path(__file__).parent; TDIR = HERE / 'treasures'
from observe import ROOT as V1
sys.path.insert(0, str(V1 / 'ml'))
GRID = (1200, 240, 2300, 1240)            # x0,y0,x1,y1 of the scrollable grid
TITLE = (520, 670, 1130, 750)             # detail-panel title
SLOTS = [(420, 410), (696, 410), (970, 410)]


def bgr(img): return cv2.cvtColor(np.asarray(img.convert('RGB')), cv2.COLOR_RGB2BGR)


def read_title(img):
    from text_reader import read_text
    rows = read_text(img.crop(TITLE))
    rows = [r for r in rows if r['score'] >= .8]
    return re.sub(r'\s+', '', ''.join(r['text'] for r in rows)) if rows else ''


_MODEL = None
def model():
    """Reuse V1's treasure retrieval (data/treasures references, SIFT + colour + correlation)."""
    global _MODEL
    if _MODEL is None:
        from treasure_model import TreasureModel
        _MODEL = TreasureModel(V1 / 'data' / 'treasures')
    return _MODEL


def grid_items(img):
    from treasure_model import detect_icons
    from treasure_modal import predict_known, supported
    x0, y0, x1, y1 = GRID; g = img.crop(GRID); out = []
    for x, y, w, h in detect_icons(g):
        p = predict_known(model(), g.crop((x, y, x + w, y + h)))
        if supported(p):
            out.append({'name': p['matches'][0]['name'], 'center': (x0 + x + w / 2, y0 + y + h / 2), 'inliers': p['matches'][0]['inliers']})
    return out


def _norm(t):
    t = re.sub(r'\s+', '', t)
    return t.translate(str.maketrans({'赐': '賜', '蕴': '蘊', '钟': '鐘', '鹅': '鵝', '盗': '盜', '圆': '圓', '实': '實', '装': '裝', '凈': '淨', '愈': '癒'}))


def title_matches(title, want):
    from difflib import SequenceMatcher
    return SequenceMatcher(None, _norm(title), _norm(want)).ratio() >= .8


def slot_filled(img, i):
    """Empty slot = grey hex with a bright green '+'; filled slot = pink treasure tile, no green plus."""
    x, y = SLOTS[i]
    c = cv2.cvtColor(np.asarray(img.convert('RGB'))[y - 60:y + 60, x - 60:x + 60], cv2.COLOR_RGB2HSV)
    green = ((c[..., 0] >= 30) & (c[..., 0] <= 75) & (c[..., 1] > 150) & (c[..., 2] > 150)).mean()
    pink = (((c[..., 0] >= 140) | (c[..., 0] <= 10)) & (c[..., 1] > 80)).mean()
    return green < .03 and pink > .2


LEARNED = HERE / 'treasures' / 'learned'


def title_scan(dev, img, want, log=print, limit=16):
    """Fallback: tap each detected icon on the current grid page and read the detail title (game text = truth).
    Tapping an icon only shows its details; nothing is equipped until a slot is tapped. Every read title is kept
    as a labelled crop (treasures/learned/) so the icon model can be extended from real MuMu frames."""
    from treasure_model import detect_icons
    x0, y0, _, _ = GRID; g = img.crop(GRID); LEARNED.mkdir(parents=True, exist_ok=True)
    for x, y, w, h in list(detect_icons(g))[:limit]:
        c = (x0 + x + w / 2, y0 + y + h / 2); dev.tap(*c); time.sleep(0.7)
        im2, _ = dev.capture(); title = read_title(im2)
        if title:
            g.crop((x, y, x + w, y + h)).save(LEARNED / f"{_norm(title)[:40]}.png")
        if title_matches(title, want):
            log(f'  {want}: found by title scan at {tuple(round(v) for v in c)}')
            return [{'name': want, 'center': c, 'byTitle': True}]
    return []


def equip(dev, wanted, log=print, pages=6):
    """Treasure modal open with empty slots. wanted: exact treasure names (as in data/treasures)."""
    img0, _ = dev.capture()
    start = sum(slot_filled(img0, k) for k in range(3))
    for i, want in enumerate(wanted):
        if i < start: continue   # already equipped in an earlier attempt (slots fill left to right)
        done = False
        for page in range(pages * 4):
            scan = page >= pages * 2   # 2nd sweep: the icon model never proposed it -> read detail titles instead
            img, _ = dev.capture(); hit = [t for t in grid_items(img) if t['name'] == want]
            if not hit and scan:
                hit = title_scan(dev, img, want, log)
            if hit:
                dev.tap(*hit[0]['center']); time.sleep(0.8)
                im2, _ = dev.capture(); title = read_title(im2)
                if not title_matches(title, want):
                    return {'ok': False, 'reason': f'detail title {title!r} != {want!r}'}
                dev.tap(*SLOTS[i]); time.sleep(0.9)
                im3, _ = dev.capture(); ok = slot_filled(im3, i)
                log(f'  {want}: grid -> title ok -> slot {i+1} verified={ok}')
                if not ok: return {'ok': False, 'reason': f'slot {i+1} does not show {want}'}
                done = True; break
            if page % (pages * 2) < pages: dev.swipe(1750, 1150, 1750, 480, 1200)
            else: dev.swipe(1750, 480, 1750, 1150, 1200)
            time.sleep(1.3)
        if not done: return {'ok': False, 'reason': f'{want} not found in treasure grid'}
        for _ in range(pages): dev.swipe(1750, 480, 1750, 1150, 500); time.sleep(0.4)
    return {'ok': True}


if __name__ == '__main__':
    sys.path.insert(0, str(HERE)); from adb_bridge import Device
    d = Device()
    if sys.argv[1] == 'equip': print(json.dumps(equip(d, sys.argv[2:]), ensure_ascii=False))
