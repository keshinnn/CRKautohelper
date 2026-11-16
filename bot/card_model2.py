"""MuMu character-card recogniser (no torch). Built on Codex's 180-character / 550-reference card library.

Pipeline (measured 2026-11-16, bot/selfcheck/REPORT.md §16):
  1. align the 254x304 MuMu team card to the wiki card art (card_align: +47 px, scale 1.01) and mask UI overlays;
  2. per-channel masked colour correlation against every reference (+ confirmed MuMu bank cards), small shift search;
  3. SIFT + RANSAC geometric check against the winner's best reference.
Decision gate (abstain unless all hold): score >= 0.40, margin to the next character >= 0.06, inliers >= 4,
card not showing the selection tick. Real MuMu crops: 189/189 right among accepted, 0 wrong; open-set stress over all
550 references with the exact costume removed: 0 wrong accepts; out-of-catalog card: rejected."""
import json
from pathlib import Path
import cv2, numpy as np
import card_align as A
HERE = Path(__file__).resolve().parent
V1 = HERE.parent if (HERE.parent / 'models' / 'cards').exists() else Path('F:/CRK helper')
SCORE, MARGIN, INLIERS = .40, .06, 4
SIFT = cv2.SIFT_create(nfeatures=350, contrastThreshold=.015)


def _sift(art):
    a = cv2.resize(art, (256, 256)); g = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
    m = cv2.resize(A.mask(), (256, 256), interpolation=cv2.INTER_NEAREST) * 255
    m[cv2.resize(A.check_mask(art), (256, 256), interpolation=cv2.INTER_NEAREST) == 0] = 0   # only a real tick, not green artwork
    return SIFT.detectAndCompute(g, m)


def _inliers(q, r):
    (kp, des), (tk, td) = q, r
    if des is None or td is None or len(des) < 4 or len(td) < 4: return 0
    pairs = cv2.BFMatcher().knnMatch(des, td, k=2); good = [a for p in pairs if len(p) == 2 for a, b in [p] if a.distance < .72 * b.distance]
    if len(good) < 4: return 0
    p = np.float32([kp[g.queryIdx].pt for g in good]); t = np.float32([tk[g.trainIdx].pt for g in good])
    M, mask = cv2.findHomography(p, t, cv2.RANSAC, 4)
    if M is None or mask is None: return 0
    pts = p[mask.ravel() > 0]
    if len(pts) < 4 or cv2.contourArea(cv2.convexHull(pts)) < 250: return 0
    area = abs(cv2.contourArea(cv2.perspectiveTransform(np.float32([[[0, 0], [256, 0], [256, 256], [0, 256]]]), M)[0]))
    return int(mask.sum()) if 12000 < area < 180000 else 0


class CardRecognizer:
    def __init__(self, v1=V1, bank=HERE / 'cards' / 'bank.json'):
        info = json.loads((v1 / 'models/cards/model.json').read_text(encoding='utf-8'))
        self.names = {c['id']: c['name'] for c in info['classes']}
        ov = v1 / 'data' / 'name-overrides-tw.json'   # Taiwan in-game names (model.json itself is integrity-hashed)
        if ov.exists():
            o = json.loads(ov.read_text(encoding='utf-8'))
            self.names.update({k: v.removesuffix('餅乾') for k, v in o.get('names', {}).items()})
            self.names.update({k: v['name'].removesuffix('餅乾') for k, v in o.get('added', {}).items()})
        self.ids, arts, self.variants = [], [], []
        for t in info['templates']:
            self.ids.append(t['character_id']); self.variants.append(t['variant']); arts.append(A.ref_art(cv2.imread(str(v1 / 'models/cards' / t['reference_file']))))
        if bank and Path(bank).exists():   # confirmed in-game cards are references too (same domain as the queries)
            for cid, row in json.loads(Path(bank).read_text(encoding='utf-8'))['cards'].items():
                for f in row['files']:
                    self.ids.append(cid); self.variants.append('MuMu bank: ' + f['file']); arts.append(A.mumu_art(cv2.imread(str(Path(bank).parent / f['file']))))
                self.names.setdefault(cid, row.get('name', cid))
        self.ids = np.array(self.ids); self.arts = arts; self.R = np.stack(arts).astype(np.float32); self.base = A.mask(); self._sf = {}

    def sift_of(self, j):
        if j not in self._sf: self._sf[j] = _sift(self.arts[j])
        return self._sf[j]

    def identify(self, card_bgr, candidates=None, shifts=((0, 0), (-3, 0), (3, 0), (0, -4), (0, 4), (-6, 0), (6, 0)), layout='team', exclude=None):
        """card_bgr: 254 wide strip slice (304 tall) for layout='team', or a 392x436 cookie-list card for layout='list'.
        candidates: optional set of character ids (e.g. the roster). exclude: reference indices to ignore (evaluation)."""
        to_art = A.mumu_art if layout == 'team' else A.list_art
        if layout == 'list': shifts = tuple((int(dy * 1.5), int(dx * 1.5)) for dy, dx in shifts)
        art0 = to_art(card_bgr)
        if layout == 'team' and not A.check_mask(art0).all(): return {'status': 'abstain', 'reason': 'selected card (tick hides the art)'}
        allow = np.ones(len(self.ids), bool) if not candidates else np.isin(self.ids, list(candidates))
        best = np.full(len(self.ids), -9.0)
        for dy, dx in shifts:
            c = np.roll(card_bgr, (-dy, -dx), axis=(0, 1))
            best = np.maximum(best, A.ncc_scores(to_art(c), self.R, self.base, tick=layout == 'team'))
        best[~allow] = -9
        if exclude is not None: best[list(exclude)] = -9
        per = {}
        for j in np.argsort(-best)[:60]:
            if best[j] > per.get(self.ids[j], (-9, 0))[0]: per[self.ids[j]] = (float(best[j]), int(j))
        ranked = sorted(per.items(), key=lambda x: -x[1][0])
        if not ranked: return {'status': 'abstain', 'reason': 'no candidates'}
        (cid, (s1, j1)) = ranked[0]; s2 = ranked[1][1][0] if len(ranked) > 1 else -1
        inl = _inliers(_sift(art0), self.sift_of(j1))
        top = [{'id': c, 'name': self.names.get(c, c), 'score': round(v, 3)} for c, (v, _) in ranked[:3]]
        why = [w for w, bad in (('low score', s1 < SCORE), ('ambiguous', s1 - s2 < MARGIN), ('no geometric support', inl < INLIERS)) if bad]
        return {'status': 'abstain' if why else 'ok', 'id': cid, 'name': self.names.get(cid, cid), 'variant': self.variants[j1], 'score': round(s1, 3),
                'margin': round(s1 - s2, 3), 'inliers': inl, 'top': top, 'reason': ', '.join(why)}
