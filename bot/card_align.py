"""MuMu team-select card -> wiki card-art alignment (measured 2026-11-16 on 14 S8 cards):
the 254x304 MuMu card shows the wiki card art at scale ~1.01 shifted down 47 px; the top 47 px is the
stamina pill. UI overlays (level text, role icon, stars, check mark) are masked on both sides."""
import cv2, numpy as np
S = 128                       # working size of the aligned art square
def mumu_art(card_bgr):
    """254x304 BGR card crop -> SxS aligned art (BGR)."""
    a = card_bgr[47:47 + 257, 0:254]
    a = cv2.copyMakeBorder(a, 0, max(0, 257 - a.shape[0]), 0, 3, cv2.BORDER_REPLICATE)[:257, :257]
    return cv2.resize(a, (S, S), interpolation=cv2.INTER_AREA)
def ref_art(ref_bgr):
    """Wiki art is the square card itself. User-supplied in-game card screenshots (~277x290, newest cookies)
    show the same art offset; their art square is ref[8:270, 13:272] (measured on 阿福花 / 小花茉莉)."""
    h, w = ref_bgr.shape[:2]
    if h > w * 1.02 and w > 250: ref_bgr = ref_bgr[8:270, 13:272]
    return cv2.resize(ref_bgr, (S, S), interpolation=cv2.INTER_AREA)
def mask():
    m = np.ones((S, S), np.uint8); k = S / 257
    m[:int(90 * k), :int(118 * k)] = 0          # 等級 100 block
    m[:int(70 * k), int(185 * k):] = 0          # role icon
    m[int(190 * k):, :] = 0                     # stars + bottom frame
    m[:, :int(6 * k)] = 0; m[:, int(250 * k):] = 0
    return m


def check_mask(art_bgr):
    """Mask the green selection tick (and the dimmed centre it sits on) of a selected card; 1 = keep."""
    hsv = cv2.cvtColor(art_bgr, cv2.COLOR_BGR2HSV)
    g = ((hsv[..., 0] >= 35) & (hsv[..., 0] <= 85) & (hsv[..., 1] > 140) & (hsv[..., 2] > 120)).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(g)
    h, w = g.shape; tick = np.zeros_like(g)
    for i in range(1, n):   # the tick is one large green stroke near the centre; green artwork is scattered
        if st[i, 4] >= .03 * h * w and .2 * w < cen[i][0] < .8 * w and .2 * h < cen[i][1] < .8 * h: tick[lab == i] = 1
    if not tick.any(): return np.ones(g.shape, np.uint8)
    return (cv2.dilate(tick, np.ones((15, 15), np.uint8)) == 0).astype(np.uint8)


_CACHE = {}
def _norm_rows(X):
    """X: (N, P, 3) -> per-channel mean/scale normalised, flattened. A selected card is the art under a uniform
    dark overlay (I' = a*I + b per channel), which per-channel normalisation cancels."""
    X = X - X.mean(1, keepdims=True); X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-6)
    return X.reshape(len(X), -1) / np.sqrt(3)


def ncc_scores(query_art, refs, base_mask, tick=True):
    """Masked per-channel correlation of one aligned query (BGR) against stacked refs (N,S,S,3 float RGB/BGR)."""
    m = (base_mask & (check_mask(query_art) if tick else np.ones_like(base_mask))).astype(bool)
    key = (id(refs), m.tobytes() if not m.all() else None, base_mask.tobytes())
    if key not in _CACHE:
        if len(_CACHE) > 8: _CACHE.clear()
        _CACHE[key] = _norm_rows(refs[:, m].astype(np.float32))
    q = _norm_rows(query_art.astype(np.float32)[m][None])[0]
    return _CACHE[key] @ q


def list_art(card_bgr):
    """Kingdom cookie-list card (392x436 crop from its '等級' label) -> SxS aligned art.
    Measured on 20 cards: the art is the wiki card at 385 px, starting 8 px below the crop top."""
    a = card_bgr[8:8 + 385, 0:385]
    a = cv2.copyMakeBorder(a, 0, max(0, 385 - a.shape[0]), 0, max(0, 385 - a.shape[1]), cv2.BORDER_REPLICATE)[:385, :385]
    return cv2.resize(a, (S, S), interpolation=cv2.INTER_AREA)
