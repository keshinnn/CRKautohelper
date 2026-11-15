"""Offline test of treasure.equip control flow with a fake device (no ADB): model miss -> title scan finds it."""
import sys, types
from pathlib import Path
BOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(BOT))
import treasure as T
from PIL import Image
class Dev:
    def __init__(s): s.taps = []; s.swipes = 0
    def capture(s): return Image.new('RGB', (2560, 1440)), 0
    def tap(s, x, y): s.taps.append((round(x), round(y)))
    def swipe(s, *a): s.swipes += 1
T.time.sleep = lambda *_: None
filled = {'n': 0}
T.slot_filled = lambda img, i: filled['n'] > i
T.grid_items = lambda img: []                       # icon model proposes nothing
titles = iter(['別的寶物', '老朝聖者的致勝秘笈', '老朝聖者的致勝秘笈'])
T.read_title = lambda img: next(titles, '')
sys.modules['treasure_model'] = types.SimpleNamespace(detect_icons=lambda g: [(10, 10, 100, 100), (200, 10, 100, 100)])
orig_tap = Dev.tap
def tap(s, x, y):
    orig_tap(s, x, y)
    if (round(x), round(y)) == T.SLOTS[0]: filled['n'] = 1
Dev.tap = tap
T.LEARNED = BOT / 'tmp' / 'learned-test'
d = Dev(); r = T.equip(d, ['老朝聖者的致勝秘笈'], log=print, pages=2)
print(r, 'swipes', d.swipes, 'taps', d.taps)
ok = r['ok'] and d.taps[-1] == T.SLOTS[0] and d.swipes >= 4   # first sweep (model only) must finish before scanning
print('PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
