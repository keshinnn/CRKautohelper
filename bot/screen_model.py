"""Screen-state model for MuMu Belowland frames (2560x1440 or any 16:9 size).

Two independent recognizers, fused conservatively:
  1. text_class(): OCR evidence -> class, from on-screen words (variants the OCR produces are listed).
  2. ImageKNN: a small appearance model (layout thumbnails + regional colour statistics, k-nearest
     neighbours, numpy only) trained on eyeballed MuMu frames (selfcheck/screens).
Fusion (predict): text decides when it has a cue; if the image model is confident about a *different*
class the result is UNKNOWN (conflict -> wait, never act). Without a text cue the image class is used
only above IMAGE_MIN confidence. The runner still needs OCR boxes to tap; this model only names the screen.
"""
import re
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
MODEL_FILE = HERE / 'models' / 'screen_knn.npz'
CLASSES = ['MAP', 'MAP_TOAST', 'PREVIEW_BATTLE', 'PREVIEW_BOSS', 'PREVIEW_HEAL', 'PREVIEW_RIFT', 'RIFT_RESOLVING', 'RIFT_RESULT',
           'NODE_ENTRY_CONFIRM', 'BATTLE_READY', 'TEAM_SELECT', 'UNDERFILLED_CONFIRM', 'MISSING_EQUIPMENT', 'LOADING',
           'BATTLE', 'BOSS_INTRO', 'VICTORY', 'FAILURE', 'RECRUIT', 'LOBBY', 'ROSTER', 'OTHER']
IMAGE_MIN = 0.75
# image-only decisions are allowed only for screens where the runner just waits (no tap follows)
PASSIVE = {'BATTLE', 'BOSS_INTRO', 'LOADING'}          # image-only decisions need this kNN vote share (measured on the dev split)
V1MAP = {'NODE_BATTLE': 'PREVIEW_BATTLE', 'NODE_BOSS': 'PREVIEW_BOSS', 'EXPEDITION_ROSTER': 'ROSTER'}

_TR = str.maketrans({'隧': '隊', '险': '險', '级': '級', '战': '戰', '斗': '鬥', '门': '鬥', '进': '進', '确': '確', '认': '認',
                     '继': '繼', '续': '續', '区': '區', '层': '層', '试': '試', '胜': '勝', '败': '敗', '还': '還', '装': '裝',
                     '载': '載', '饼': '餅', '唇': '層', '缝': '縫'})


def norm(t):
    return re.sub(r'\s+', '', t or '').translate(_TR)


def text_class(texts, v1_state='UNKNOWN'):
    """texts: OCR strings (score already filtered). Returns (class or None, cue)."""
    T = [norm(t) for t in texts]; j = '\n'.join(T)
    has = lambda *ws: any(w in j for w in ws)
    if has('未裝載', '配料塔或脆餅'): return 'MISSING_EQUIPMENT', '未裝載配料'
    if has('還能配置', '確定要開始？'): return 'UNDERFILLED_CONFIRM', '隊伍還能配置'
    if has('在通關前無法前往', '進入冥界試煉節點'): return 'NODE_ENTRY_CONFIRM', '無法前往其他節點'
    if has('發現新', '加入了！', '加入了!'): return 'RECRUIT', '加入了'
    if re.search(r'輕觸?以繼?續', j) and has('冥界', '節點突破', '過關獎勵', '下次挑', '區域'): return 'MAP_TOAST', '輕觸以繼續'
    if has('讀取中'): return 'LOADING', '讀取中'
    if has('BOSS登場'): return 'BOSS_INTRO', 'BOSS登場'
    if '勝利' in T: return 'VICTORY', '勝利'
    if '失敗' in T or (has('失敗') and has('再一次')): return 'FAILURE', '失敗'
    if has('全部解除'): return 'TEAM_SELECT', '全部解除'
    if has('最高分數') and has('最高過關區域'):
        return ('ROSTER', '請選…加入') if has('請選', '加入限制') else ('LOBBY', '最高分數')
    if re.search(r'第\d+層(加入餅乾|.*獎勵)', j) and not re.search(r'危[險]?度', j): return 'RIFT_RESULT', '裂縫結果面板'
    if re.search(r'危[險]?度', j):            # an open node panel: never the bare map
        if has('確認結果'): return 'RIFT_RESOLVING', '確認結果中'
        if has('可能發生的事件', '冥界裂'): return 'PREVIEW_RIFT', '可能發生的事件'
        if has('恢復方式', '恢復所有', '已恢復'): return 'PREVIEW_HEAL', '恢復方式'
        if re.search(r'第\d+層.*BOSS', j) or (has('BOSS') and has('鬥限制時間')): return 'PREVIEW_BOSS', 'BOSS'
        if has('進入', '套用效果'): return 'PREVIEW_BATTLE', '進入'
        return None, 'unknown panel'
    if has('隊伍設定') and has('前排', '後排', '中排'): return 'BATTLE_READY', '隊伍設定'
    if '自動' in T and any(re.fullmatch(r'\d{2}:\d{2}', t) for t in T): return 'BATTLE', '自動+時間'
    if has('（下次挑', '(下次挑') or re.search(r'區域第\d+層進行中|區域\d*進行中', j): return 'MAP', '地圖標頭'
    v = V1MAP.get(v1_state, v1_state)
    if v in CLASSES: return v, 'v1:' + v1_state
    return None, ''


# ---------------- appearance model ----------------
def features(img):
    """img: PIL.Image (any size, 16:9). -> 1-D float32 feature vector."""
    import cv2
    a = np.asarray(img.convert('RGB').resize((320, 180)), dtype=np.uint8)
    g = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY)
    tiny_g = cv2.resize(g, (32, 18), interpolation=cv2.INTER_AREA).astype(np.float32).ravel() / 255
    tiny_c = cv2.resize(a, (16, 9), interpolation=cv2.INTER_AREA).astype(np.float32).ravel() / 255
    hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV).astype(np.float32)
    reg = []
    for r in range(4):
        for c in range(4):
            p = hsv[r * 45:(r + 1) * 45, c * 80:(c + 1) * 80].reshape(-1, 3)
            reg += list(p.mean(0) / 255) + list(p.std(0) / 128)
    edges = cv2.Canny(g, 60, 160)
    ed = [edges[r * 45:(r + 1) * 45, c * 80:(c + 1) * 80].mean() / 255 for r in range(4) for c in range(4)]
    return np.concatenate([tiny_g, tiny_c, np.array(reg, np.float32) * 2, np.array(ed, np.float32) * 4]).astype(np.float32)


class ImageKNN:
    def __init__(self, X=None, y=None, k=5):
        self.k = k
        if X is not None: self.fit(X, y)

    def fit(self, X, y):
        X = np.asarray(X, np.float32); self.mu = X.mean(0); self.sd = X.std(0) + 1e-3
        Z = (X - self.mu) / self.sd; self.Z = Z / np.linalg.norm(Z, axis=1, keepdims=True); self.y = np.asarray(y)
        return self

    def predict(self, x):
        z = (np.asarray(x, np.float32) - self.mu) / self.sd; z /= np.linalg.norm(z)
        s = self.Z @ z; idx = np.argsort(-s)[:self.k]
        votes = {}
        for i in idx: votes[self.y[i]] = votes.get(self.y[i], 0) + max(s[i], 0)
        best = max(votes, key=votes.get); tot = sum(votes.values()) or 1
        return best, float(votes[best] / tot), float(s[idx[0]])

    def save(self, path=MODEL_FILE):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(path, Z=self.Z, y=self.y, mu=self.mu, sd=self.sd, k=self.k)

    @classmethod
    def load(cls, path=MODEL_FILE):
        d = np.load(path, allow_pickle=False); m = cls(k=int(d['k']))
        m.Z, m.y, m.mu, m.sd = d['Z'], d['y'], d['mu'], d['sd']; return m


_MODEL = None
def image_model():
    global _MODEL
    if _MODEL is None and MODEL_FILE.exists(): _MODEL = ImageKNN.load()
    return _MODEL


def fuse(text_cls, img_cls, img_conf, image_min=IMAGE_MIN):
    if text_cls:
        if img_cls and img_cls != text_cls and img_conf >= 0.9 and not _compatible(text_cls, img_cls):
            return 'UNKNOWN', f'conflict text={text_cls} image={img_cls}'
        return text_cls, 'text'
    if img_cls in PASSIVE and img_conf >= image_min: return img_cls, 'image'
    return 'UNKNOWN', 'no cue'


def _compatible(a, b):
    """Overlays share their background with the screen beneath; the image model may name the background."""
    groups = [{'MAP', 'MAP_TOAST', 'RECRUIT', 'RIFT_RESULT', 'PREVIEW_BATTLE', 'PREVIEW_BOSS', 'PREVIEW_HEAL', 'PREVIEW_RIFT', 'RIFT_RESOLVING', 'NODE_ENTRY_CONFIRM'},
              {'BATTLE_READY', 'UNDERFILLED_CONFIRM', 'MISSING_EQUIPMENT', 'TEAM_SELECT'}, {'BATTLE', 'BOSS_INTRO'}, {'LOBBY', 'ROSTER'}]
    return any(a in g and b in g for g in groups)


def panel_button(img):
    """Colour of the node-panel action button (2560x1440 frame, scaled): 'green' = actionable,
    'purple' = rift result resolving, 'gray' = done/disabled. Measured on MuMu S8 panels."""
    import cv2
    a = np.asarray(img.convert('RGB').resize((1280, 720)))[612:640, 1060:1220]
    h, s_, v = np.median(cv2.cvtColor(a, cv2.COLOR_RGB2HSV).reshape(-1, 3), 0)
    if s_ < 60: return 'gray'
    if 30 <= h <= 60: return 'green'
    if 110 <= h <= 150: return 'purple'
    return None


def predict(img, texts, v1_state='UNKNOWN'):
    t, cue = text_class(texts, v1_state)
    btn = panel_button(img) if img is not None and t and t.startswith('PREVIEW_') else None
    if t == 'PREVIEW_RIFT' and btn == 'purple': t, cue = 'RIFT_RESOLVING', 'purple panel button'
    m = image_model(); ic, conf = (None, 0.0)
    if m is not None and img is not None:
        ic, conf, _ = m.predict(features(img))
    cls, how = fuse(t, ic, conf)
    return {'cls': cls, 'how': how, 'text': t, 'cue': cue, 'image': ic, 'imageConf': round(conf, 3), 'panelButton': btn}
