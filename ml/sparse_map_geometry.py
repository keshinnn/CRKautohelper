"""Recover one absent map column from a unique same-frame visible-gate lattice."""
import copy,hashlib,os
from itertools import combinations
from pathlib import Path
import numpy as np


def recover_map_geometry(image,packet):
    original=packet.get('mapReview')
    if not original or original.get('absoluteFloorKnown') is True or original.get('columns'):return original
    digest=hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()
    if packet.get('binding',{}).get('pixelSha256')!=digest or original.get('frameId')!=digest[:20]:return original
    nodes=original.get('nodes',[]);gates=[n for n in nodes if n.get('type')=='exit']
    normal=[n for n in nodes if n.get('type') not in ('exit','boss')]
    if len(gates)!=1 or len(normal)<5:return original
    if any(len(n.get('box',[]))!=4 or len(n.get('center',[]))!=2 or not np.isfinite([*n['box'],*n['center']]).all() or n.get('score',0)<.48 for n in nodes):return original
    radius=float(np.median([min(n['box'][2:]) for n in normal]));clusters=[]
    if radius<=0:return original
    for x in sorted(n['center'][0] for n in normal):
        if not clusters or x-np.mean(clusters[-1])>radius*.5:clusters.append([x])
        else:clusters[-1].append(x)
    if len(clusters)!=3:return original
    centers=np.array([np.mean(c) for c in clusters]);gx,gy=gates[0]['center'];solutions=[]
    for slots in combinations(range(1,5),3):
        offsets=np.array(slots,dtype=float)-2.5
        spacing=float(np.dot(offsets,centers-gx)/np.dot(offsets,offsets))
        if not radius*.85<spacing<radius*2.2:continue
        columns=[gx+(i-2.5)*spacing for i in range(1,5)]
        if columns[0]<0 or columns[-1]>=image.width or max(abs(centers-(gx+offsets*spacing)))>spacing*.04:continue
        # Measure vertical pitch independently: residual aspect-calibration
        # error must not accumulate once per visible row. Require three
        # adjacent, equally spaced observed rows and agreement with x pitch.
        rows=[]
        for y in sorted(n['center'][1] for n in normal):
            if not rows or y-np.mean(rows[-1])>radius*.5:rows.append([y])
            else:rows[-1].append(y)
        vertical=spacing
        if len(rows)>=3:
            gaps=np.diff([np.mean(row) for row in rows]);measured=float(np.median(gaps))
            if abs(measured/spacing-1)>.04 or max(abs(gaps/measured-1))>.04:continue
            vertical=measured
        floors=[(n['center'][1]-gy)/vertical for n in normal]
        if any(not 1<=round(f)<=31 or abs(f-round(f))>.08 for f in floors):continue
        if min(round(f) for f in floors)!=1 or len(set(round(f) for f in floors))<2:continue
        solutions.append(columns)
    if len(solutions)!=1:return original
    # Rerun the original detector and actual connecting-line pixels. Geometry
    # comes solely from this image's measured candidates, never an annotation.
    from map_vision import inspect_map
    repaired=inspect_map(image,Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper'))/'data/map',geometry={'columns':solutions[0]},read_header=False)
    if repaired.get('absoluteFloorKnown') is not True or repaired.get('floorAnchorSource')!='visible_top_gate' or repaired.get('frameId')!=digest[:20]:return original
    repaired['header']=copy.deepcopy(original.get('header'))
    repaired['latticeEvidence']={'method':'same_frame_visible_gate_unique_three_column_lattice','pixelSha256':digest,'sourceImageSha256':packet['binding'].get('imageSha256'),'observedColumns':centers.tolist(),'inferredColumns':solutions[0],'observedNodeCount':len(normal),'gateBox':list(gates[0]['box']),'actionsExecuted':False}
    return repaired
