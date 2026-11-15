"""Contact sheets for eyeball labelling: screens/sheets/<label>-<k>.jpg, 8x6 thumbnails with index numbers."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
HERE = Path(__file__).resolve().parent; BOT = HERE.parent; sys.path.insert(0, str(HERE))
from screens_label import load
out = HERE / 'screens' / 'sheets3'; out.mkdir(exist_ok=True)
W, H, C, R = 240, 135, 6, 6
want = sys.argv[1:] or None
rows = load(); groups = {}
for i, r in enumerate(rows): r['i'] = i; groups.setdefault(r['label'], []).append(r)
try: font = ImageFont.truetype('DejaVuSans-Bold.ttf', 20)
except Exception: font = ImageFont.load_default()
for lab, rs in groups.items():
    if want and lab not in want: continue
    for k in range(0, len(rs), C * R):
        sheet = Image.new('RGB', (C * W, R * H), 'black'); d = ImageDraw.Draw(sheet)
        for j, r in enumerate(rs[k:k + C * R]):
            im = Image.open(BOT / r['thumb']).convert('RGB').resize((W - 4, H - 4))
            x, y = (j % C) * W, (j // C) * H; sheet.paste(im, (x + 2, y + 2))
            d.rectangle([x + 2, y + 2, x + 70, y + 26], fill='yellow'); d.text((x + 5, y + 3), str(r['i']), fill='black', font=font)
        sheet.save(out / f'{lab}-{k // (C * R)}.jpg', quality=82)
print({k: len(v) for k, v in groups.items()})
