"""Auto-suggest ground-truth classes, then apply manual corrections (screens/labels_fix.json).
Suggestion for run frames = the runner's own decision (validated by the next frame in the live run);
recording frames + undecided frames = NEEDS_REVIEW (labelled by eye from contact sheets)."""
import json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; S = HERE / 'screens'
CLASSES = ['MAP', 'MAP_TOAST', 'PREVIEW_BATTLE', 'PREVIEW_BOSS', 'PREVIEW_HEAL', 'PREVIEW_RIFT', 'RIFT_RESOLVING', 'NODE_ENTRY_CONFIRM',
           'BATTLE_READY', 'TEAM_SELECT', 'TREASURE_MODAL', 'UNDERFILLED_CONFIRM', 'MISSING_EQUIPMENT', 'LOADING', 'BATTLE', 'BOSS_INTRO',
           'VICTORY', 'FAILURE', 'RECRUIT', 'LOBBY', 'ROSTER', 'EXPEDITION_MENU', 'OTHER']
RULES = [(r'battle in progress|enable auto skills', 'BATTLE'), (r'^victory', 'VICTORY'), (r'loading screen', 'LOADING'),
         (r'underfilled', 'UNDERFILLED_CONFIRM'), (r'missing toppings|missing-equipment', 'MISSING_EQUIPMENT'),
         (r'battle start \(|open team settings', 'BATTLE_READY'), (r'confirm node entry', 'NODE_ENTRY_CONFIRM'),
         (r'reward toast', 'MAP_TOAST'), (r'heal ', 'PREVIEW_HEAL'), (r'rift', 'PREVIEW_RIFT'), (r'^set team', 'TEAM_SELECT'),
         (r'recruit', 'RECRUIT'), (r'enter expedition', 'LOBBY'),
         (r'map target|map node|no floor anchor|anchor floor|沒有攻略資料|手動關卡|已失敗', 'MAP'),
         (r'preview floor|enter floor|preview mismatch', None), (r'failure|戰鬥失敗', 'FAILURE')]
def suggest(r):
    a = r.get('action')
    if not a: return 'NEEDS_REVIEW'
    reason = str(a[-1])
    for pat, cls in RULES:
        if re.search(pat, reason):
            if cls is None: return 'PREVIEW_BOSS' if r['v1'] == 'NODE_BOSS' else 'PREVIEW_BATTLE'
            return cls
    return 'NEEDS_REVIEW'
def text_guess(r):
    T = r.get('texts') or []; j = '\n'.join(T); v = r['v1']
    if '勝利' in T: return 'VICTORY'
    if any('失敗' in t or '失败' in t for t in T): return 'FAILURE'
    if '讀取中' in j: return 'LOADING'
    if '確定要開始' in j: return 'UNDERFILLED_CONFIRM'
    if re.search(r'輕觸?以繼?續', j): return 'MAP_TOAST'
    if '裝備寶物' in j: return 'TREASURE_MODAL'
    if '全部解除' in j: return 'TEAM_SELECT'
    if re.search(r'危[險险]?度', j):
        if '恢復' in j: return 'PREVIEW_HEAL'
        if '裂' in j: return 'PREVIEW_RIFT'
        if 'BOSS' in j: return 'PREVIEW_BOSS'
        return 'PREVIEW_BATTLE'
    if '發現新' in j or '加入了' in j: return 'RECRUIT'
    if '最高分數' in j: return 'LOBBY'
    if v.startswith('NODE_'): return 'PREVIEW_' + v[5:]
    if v == 'EXPEDITION_ROSTER': return 'ROSTER'
    return v if v != 'UNKNOWN' else 'OTHER'
def load():
    rows = [json.loads(l) for l in (S / 'index.jsonl').read_text(encoding='utf-8').splitlines()]
    fix = json.loads((S / 'labels_fix.json').read_text(encoding='utf-8')) if (S / 'labels_fix.json').exists() else {}
    for r in rows:
        r['suggested'] = suggest(r)
        if r['suggested'] == 'NEEDS_REVIEW': r['suggested'] = 'REVIEW_' + text_guess(r)
        r['label'] = fix.get(r['id'], r['suggested'])
    return rows
if __name__ == '__main__':
    import collections
    rows = load(); print(collections.Counter(r['label'] for r in rows).most_common())
    (S / 'labels.json').write_text(json.dumps({r['id']: r['label'] for r in rows}, ensure_ascii=False, indent=0), encoding='utf-8')
