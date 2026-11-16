"""Evaluate card_model2 on every owned cookie in its currently equipped costume (kingdom cookie list,
names read from each cookie's own detail page). Truth: OCR name -> catalog id (normalised, fuzzy) +
manual overrides in list_truth_fix.json. Usage: list_eval.py <recording dir> [--table]"""
import json, sys, re, difflib, collections
from pathlib import Path
import cv2, numpy as np
BOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(BOT))
D = Path(sys.argv[1]); rows = json.loads((D / 'labels.json').read_text(encoding='utf-8'))
V1 = BOT.parent; m = json.loads((V1 / 'models/cards/model.json').read_text(encoding='utf-8'))
T2S = str.maketrans('饼纯黄恒鹅鲜蓝凤龙团面银梦乐兰红绿紫叶灵觉华岛东乌鸟鱼马丽锦钢铁风云电雾冰圣恶魔猎术战斗将军应龟妖狮虫汤','餅純黃恆鵝鮮藍鳳龍團麵銀夢樂蘭紅綠紫葉靈覺華島東烏鳥魚馬麗錦鋼鐵風雲電霧冰聖惡魔獵術戰鬥將軍應龜妖獅蟲湯')
def norm(t): return re.sub(r'(餅乾|乾|餅|鲜乾|餠乾)$', '', re.sub(r'\s+', '', t).translate(T2S).replace('餠', '餅')).strip()
cat = {}
for c in m['classes']: cat[norm(c['name'])] = c['id']
fix = json.loads((BOT / 'selfcheck' / 'list_truth_fix.json').read_text(encoding='utf-8')) if (BOT / 'selfcheck' / 'list_truth_fix.json').exists() else {}
names = {c['id']: c['name'] for c in m['classes']}
def truth(name):
    if name in fix: return fix[name]
    n = norm(name)
    if n in cat: return cat[n]
    best = difflib.get_close_matches(n, list(cat), 1, .75)
    return cat[best[0]] if best else None
if '--table' in sys.argv:
    for r in rows: t = truth(r['name']); print(r['file'], r['name'], '->', names.get(t, t))
    sys.exit()
import card_model2 as CM
rec = CM.CardRecognizer(bank=None, owned=None)   # the list cards themselves are owned references: keep them out
res = collections.Counter(); wrong = []; abst = []
for r in rows:
    t = truth(r['name']); card = cv2.imread(str(D / r['file']))
    o = rec.identify(card, layout='list')
    if t == 'SKIP' or t is None: res['skipped'] += 1; continue
    key = 'in' if t != 'OUT' else 'out'
    if o['status'] != 'ok': res[key + '-abstain'] += 1; abst.append((r['name'], o.get('name'), o.get('score'), o.get('margin'), o.get('inliers'), o.get('reason')))
    elif key == 'in' and o['id'] == t:
        res['right'] += 1; v = o.get('variant', '')
        res['right: official art' if v.startswith('Official') else 'right: user/in-game card ref' if ('使用者' in v or '遊戲' in v or 'MuMu' in v) else 'right: costume/event art'] += 1
    else: res['WRONG'] += 1; wrong.append((r['name'], names.get(t, t), o['name'], o['score'], o['margin'], o['inliers']))
print(dict(res)); print('WRONG:', wrong); print('abstain sample:', abst[:40])
(BOT / 'selfcheck' / 'list_eval_result.json').write_text(json.dumps({'counts': res, 'wrong': wrong, 'abstain': abst}, ensure_ascii=False, indent=0, default=str), encoding='utf-8')
