"""Offline component checks.
Cards: template matcher on team-select strips. Truth = the game's fixed roster order (sorted by rarity, never
changes within an expedition): visible cards must form a contiguous run of that order at a ~280px pitch.
Strips cut for templates (grab-row0/row1) are reported separately as 'template-source' (not evidence).
Treasures: V1 TreasureModel vs the in-game detail title read by OCR when each icon was tapped (game text = truth)."""
import json, sys, re
from pathlib import Path
from difflib import SequenceMatcher
BOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(BOT))
from observe import ROOT as V1  # adds V1 ml/ to sys.path
from PIL import Image
import team

ORDER = ['百合', '芒果', '船長', '水母', '莫札', '風鈴草', '金桂', '薄荷醇', '煙燻', '木乃伊', '奶油蘇打', '氣泡', '巴斯克', '阿福花', '茉莉']
TEMPLATE_SRC = {'grab-row0.png', 'grab-row1.png'}

def card_check():
    T = team.load_templates(); rows = []
    for f in ['grab-row0.png', 'grab-row1.png', 'grab-row2.png', 'grab-t1.png', 'grab-t2.png', 'grab-t3.png', 'grab-c1.png', 'grab-e2.png', '020439.png', '032003.png']:
        img = Image.open(BOT / 'shots' / f).convert('RGB'); vis = team.visible_cards(team.strip_of(img), T)
        seq = sorted(vis.items(), key=lambda kv: kv[1]['x']); names = [n for n, _ in seq]; xs = [v['x'] for _, v in seq]
        start = ORDER.index(names[0]) if names else -1
        contiguous = names == ORDER[start:start + len(names)]
        pitch_ok = all(abs((b - a) - 280) <= 6 for a, b in zip(xs, xs[1:]))
        # every card position fully inside the strip (x 230..2306) must be detected
        expected = [x for x in range(xs[0] % 280, 2560, 280) if 230 <= x and x + 254 <= 2560] if xs else []
        full = len([x for x in expected]) == len(names)
        rows.append({'file': f, 'templateSource': f in TEMPLATE_SRC, 'detected': names, 'checked': [n for n, v in seq if v['checked']],
                     'contiguousOrder': contiguous, 'pitchOk': pitch_ok, 'allVisibleDetected': full,
                     'minScore': min((v['score'] for _, v in seq), default=None)})
    return rows

def norm(t):
    t = re.sub(r'\s+', '', t)
    return t.translate(str.maketrans({'赐': '賜', '蕴': '蘊', '钟': '鐘', '鹅': '鵝', '盗': '盜', '圆': '圓', '实': '實', '装': '裝', '凈': '淨', '愈': '癒', '镰': '鐮'}))

def treasure_check():
    from treasure_model import TreasureModel
    from treasure_modal import predict_known, supported
    import treasure
    model = TreasureModel(V1 / 'data' / 'treasures'); names = [t['name'] for t in model.info['treasures']]
    labels = json.loads((BOT / 'treasures' / 'labels.json').read_text(encoding='utf-8')); rows = []
    for ocr_title, f in labels.items():
        # resolve the (possibly mis-read) OCR title to the closest reference name; record the similarity
        ref, sim = max(((n, SequenceMatcher(None, norm(ocr_title), n).ratio()) for n in names), key=lambda x: x[1])
        crop = Image.open(BOT / 'treasures' / f).convert('RGB')
        p = predict_known(model, crop); pred = p['matches'][0]['name']
        rows.append({'ocrTitle': ocr_title, 'truth': ref if sim >= .7 else None, 'titleSimilarity': round(sim, 2), 'predicted': pred,
                     'supported': supported(p), 'correct': pred == ref and sim >= .7})
    grid = []
    for f in ['grab-c2.png', 'grab-c3.png', 'grab-e1.png']:
        items = treasure.grid_items(Image.open(BOT / 'shots' / f).convert('RGB'))
        grid.append({'file': f, 'supportedIcons': len(items), 'names': [i['name'] for i in items]})
    return rows, grid

if __name__ == '__main__':
    cards = card_check(); trs, grid = treasure_check()
    for r in cards: print('CARD', r)
    for r in trs: print('TREASURE', r)
    for g in grid: print('GRID', g)
    held = [r for r in cards if not r['templateSource']]
    summary = {'cardStrips_heldout': len(held), 'cardStrips_ok': sum(r['contiguousOrder'] and r['pitchOk'] and r['allVisibleDetected'] for r in held),
               'treasure_titled': sum(r['truth'] is not None for r in trs), 'treasure_correct': sum(r['correct'] for r in trs),
               'treasure_supported': sum(r['supported'] for r in trs)}
    print(json.dumps(summary, ensure_ascii=False))
    (Path(__file__).parent / 'cards_treasures_result.json').write_text(json.dumps({'summary': summary, 'cards': cards, 'treasures': trs, 'grid': grid}, ensure_ascii=False, indent=1), encoding='utf-8')
