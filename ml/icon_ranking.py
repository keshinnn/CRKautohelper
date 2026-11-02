"""Exact legacy icon ranking with rejection before unnecessary comparisons."""
import cv2
import numpy as np


def rank_required_icon(q, gray, templates, required_names, incumbent_score=None):
    """Return exact required/other maxima, or reject by the existing .9/.08 gates.

    An uncomputed competing score can only worsen the required family's margin.
    Accepted patches still compare every template. No evidence is reused.
    """
    required_names = frozenset(required_names)
    required = [t for t in templates if t[0] in required_names]
    others = [t for t in templates if t[0] not in required_names]
    if not required_names or {t[0] for t in required} != required_names or not others:
        raise ValueError('Required and competing template families must be present')
    pixels = q.astype(float)

    def score(template):
        name, _, _, ref, refg = template
        value = .7*float(cv2.matchTemplate(gray, refg, cv2.TM_CCOEFF_NORMED)[0, 0])+.3*(1-np.abs(pixels-ref).mean()/255)
        return float(value), name

    winner = max(score(t) for t in required)
    if winner[0] < .9 or incumbent_score is not None and winner[0] <= incumbent_score:
        return None
    competing = []
    for template in others:
        item = score(template)
        if winner[0]-item[0] < .08:
            return None
        competing.append(item)
    return winner, max(competing)
