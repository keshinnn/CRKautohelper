"""Map navigation: act-then-verify.
A map tap only opens a preview (reversible); commitment happens at 進入, which is gated by
an OCR-verified preview floor. So the map planner only needs: anchor row + strategy column."""
import re

def _center(box):
    return (box[0] + box[2] / 2, box[1] + box[3] / 2)


def header_progress(evidence):
    """'1區域第3層進行中' -> (zone, floor, 'in_progress'); also handles '區域1第3層'."""
    for r in evidence:
        t = re.sub(r'\s+', '', r.get('text', ''))
        m = re.search(r'(\d+)區域第(\d+)[層唇]進行中', t) or re.search(r'區域(\d+)第(\d+)[層唇]進行中', t)
        if m and r.get('score', 0) >= .8:
            return int(m.group(1)), int(m.group(2))
    return None


def plan_map_tap(packet, step):
    """step = {'floor': absolute floor to enter, 'column': 1-4 or None for zone boss}.
    Returns {'point','nodeId','reason'} or {'point':None,'reason','scroll': 'up'|'down'|None}."""
    m = packet.get('mapReview') or {}
    nodes = [dict(n, id=n.get('id') or f'unanchored-{i}') for i, n in enumerate(m.get('nodes') or [])]
    cur = m.get('currentPosition') or {}
    by_id = {n['id']: n for n in nodes}
    target_floor = step['floor']
    # 1) resume: the in-progress node IS the requested floor -> tap it again.
    if cur.get('verified') and cur.get('floor') == target_floor:
        n = by_id.get(cur.get('nodeId'))
        if n and (step['column'] is None or n.get('column') == step['column']):
            return {'point': _center(n['box']), 'nodeId': n['id'], 'reason': 'resume_in_progress_node'}
        return {'point': None, 'reason': f'in-progress node is column {cur.get("column")}, strategy says {step["column"]}'}
    # 1b) gate off-screen and V1 current-position proof absent: the in-progress node is the one directly
    #     above the unique '進行中' label; its floor comes from the header '…第N層進行中'.
    if not cur.get('verified') and not any(n.get('floor') is not None for n in nodes):
        labels = [r for r in packet.get('evidence', []) if re.sub(r'\s+', '', r.get('text', '')) == '進行中' and r.get('score', 0) >= .9]
        hp = header_progress(packet.get('evidence', []))
        if len(labels) == 1 and hp:
            lx = sum(q[0] for q in labels[0]['box']) / 4; ly = min(q[1] for q in labels[0]['box'])
            above = [n for n in nodes if n['box'][0] <= lx <= n['box'][0] + n['box'][2] and n['box'][1] + n['box'][3] * .5 <= ly <= n['box'][1] + n['box'][3] * 1.6]
            if len(above) == 1:
                cur = {'verified': True, 'nodeId': above[0]['id'], 'floor': hp[1], 'column': above[0].get('column'), 'method': 'progress_label'}
                if hp[1] == target_floor:
                    n = above[0]
                    if step['column'] is None or n.get('column') == step['column']:
                        return {'point': _center(n['box']), 'nodeId': n['id'], 'reason': 'resume_in_progress_node(label)'}
                    return {'point': None, 'reason': f'in-progress node is column {n.get("column")}, strategy says {step["column"]}'}
    # 2) anchor row: absolute floors if the recognizer anchored them, else relative to current/completed node.
    def floor_of(n):
        if n.get('floor') is not None:
            return n['floor']
        return None
    candidates = []
    if any(floor_of(n) is not None for n in nodes):
        row_nodes = [n for n in nodes if floor_of(n) == target_floor]
    else:
        anchor = by_id.get(cur.get('nodeId')) if cur.get('verified') else None
        done = [n for n in nodes if n.get('completed') and n.get('visibleRow')]
        if anchor is None and done:
            anchor = max(done, key=lambda n: n['visibleRow'])  # deepest completed node on screen
        if anchor is None:
            return {'point': None, 'reason': 'no floor anchor on screen (gate/current/completed)', 'scroll': 'up'}
        anchor_floor = cur.get('floor') if cur.get('verified') else packet.get('_lastCompletedFloor')
        if anchor_floor is None:
            return {'point': None, 'reason': 'anchor floor unknown'}
        row = anchor['visibleRow'] + (target_floor - anchor_floor)
        row_nodes = [n for n in nodes if n.get('visibleRow') == row]
    if step['column'] is None:
        candidates = [n for n in nodes if n['type'] == 'boss']
    else:
        candidates = [n for n in row_nodes if n.get('column') == step['column'] and n['type'] not in ('exit', 'boss')]
    candidates = [n for n in candidates if not n.get('completed')]
    if len(candidates) == 1:
        return {'point': _center(candidates[0]['box']), 'nodeId': candidates[0]['id'], 'type': candidates[0]['type'], 'reason': 'strategy_column'}
    if not candidates:
        return {'point': None, 'reason': f'floor {target_floor} column {step["column"]} not visible', 'scroll': 'down'}
    return {'point': None, 'reason': f'{len(candidates)} candidates for floor {target_floor} column {step["column"]}'}


def verify_preview(packet, step):
    """Gate before the irreversible 進入: floor title must match, enter button must be unique."""
    f = packet['flow']
    h = packet.get('nodeHeader') or {}
    enter = [t for t in f.get('targets', []) if t.get('target') == 'enter']
    floor = h.get('floor') if h.get('verified') else None
    if floor is None:
        for r in packet.get('evidence', []):
            m = re.fullmatch(r'第(\d+)層.*', re.sub(r'\s+', '', r.get('text', '')))
            if m and r.get('score', 0) >= .88:
                floor = int(m.group(1)); break
    ok = floor == step['floor'] and len(enter) == 1
    return {'ok': ok, 'floor': floor, 'enter': enter[0] if len(enter) == 1 else None,
            'reason': None if ok else f'preview floor={floor} expected={step["floor"]}, enter buttons={len(enter)}'}
