"""Score Codex's 180-class card model (models/cards: ResNet18 + templates + SIFT gate) on MuMu team-select cards.
Truth = the per-season card templates (bot/cards), which were confirmed live by the game's own check marks.
Writes selfcheck/cards_codex_eval.json. Runs on Windows (needs torch from the V1 venv)."""
import json, sys, time, glob
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from observe import ROOT as V1
sys.path.insert(0, str(V1 / 'ml'))
from PIL import Image
import team
from card_model import CardModel

def frames():
    out = []
    for f in ['grab-row0.png', 'grab-row1.png', 'grab-row2.png', 'grab-t1.png', 'grab-t2.png', 'grab-t3.png', 'grab-c1.png', 'grab-e2.png', '020439.png', '032003.png']:
        p = HERE / 'shots' / f
        if p.exists(): out.append((str(p.relative_to(HERE)), Image.open(p).convert('RGB')))
    lab = json.loads((HERE / 'selfcheck' / 'screens' / 'labels.json').read_text(encoding='utf-8'))
    for fid, cls in lab.items():
        if cls != 'TEAM_SELECT' or not fid.startswith('run/'): continue
        _, sess, n = fid.split('/'); p = HERE / 'runs' / sess / f'{n}.jpg'
        if p.exists(): out.append((str(p.relative_to(HERE)), Image.open(p).convert('RGB').resize((2560, 1440), Image.LANCZOS)))
    return out

def main():
    t0 = time.time(); model = CardModel(V1 / 'models' / 'cards'); T = team.load_templates(); rows = []
    for name, img in frames():
        strip = team.strip_of(img); vis = team.visible_cards(strip, T)
        for label, v in vis.items():
            x = v['x']
            if x < 0 or x + team.CARD_W > 2560: continue
            crop = img.crop((x, team.STRIP[0], x + team.CARD_W, team.STRIP[1]))
            p = model.predict(crop)
            rows.append({'frame': name, 'truth': label, 'x': x, 'checked': v['checked'], 'status': p['status'], 'support': p['geometric_support'],
                         'margin': p['margin'], 'top': [(m['name'], m['similarity'], m['geometric_inliers']) for m in p['matches'][:5]]})
        print(name, len(vis), flush=True)
    (HERE / 'selfcheck' / 'cards_codex_eval.json').write_text(json.dumps({'seconds': round(time.time() - t0), 'rows': rows}, ensure_ascii=False, indent=1), encoding='utf-8')
    print('done', len(rows), round(time.time() - t0))

if __name__ == '__main__': main()
