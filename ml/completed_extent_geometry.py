"""Refine an existing completed hypothesis only from original done/check pixels."""
import copy
import functools
import hashlib
import os
import re
from pathlib import Path
import numpy as np
from PIL import Image


def recover_completed_extents(image,m,binding):
    from completed_node_candidates import completed_node_candidates
    from map_action_evidence import inspect_map_actions
    rgb=image.convert('RGB');digest=hashlib.sha256(rgb.tobytes()).hexdigest()
    if (not isinstance(m,dict) or m.get('absoluteFloorKnown') is not True
            or binding.get('pixelSha256')!=digest or m.get('frameId')!=digest[:20]
            or [binding.get('width'),binding.get('height')]!=list(rgb.size)
            or re.fullmatch(r'[a-f0-9]{64}',binding.get('imageSha256','')) is None
            or re.fullmatch(r'[a-f0-9]{32}',binding.get('frameId','')) is None):return m
    candidates=[n for n in m.get('nodes',[]) if n.get('completed') is True and n.get('type') not in ('exit','boss')
                and not n.get('checkProposal') and not n.get('completedRefinement') and .48<=n.get('score',0)<=1]
    if not candidates:return m
    subset={**m,'nodes':candidates,'absoluteFloorKnown':False}
    actions=inspect_map_actions(rgb,{'binding':binding,'mapReview':subset})
    bad=[n for n in candidates if actions.get('nodes',{}).get(n['id'],{}).get('checkMaskIoU',1)<.8]
    if not bad:return m
    rect=m.get('aspectRectification') or {};normal_size=rect.get('rectifiedInputSize',list(rgb.size))
    if (not isinstance(normal_size,list) or len(normal_size)!=2 or any(type(v) is not int or v<=0 for v in normal_size)
            or normal_size[1]!=rgb.height):return m
    inverse=rgb.width/normal_size[0];normalized=rgb.resize(tuple(normal_size),Image.Resampling.LANCZOS)
    normal_pixel=hashlib.sha256(normalized.tobytes()).hexdigest()
    if normal_pixel!=rect.get('rectifiedPixelSha256',digest):return m
    analysis_size=[960,round(normal_size[1]*960/normal_size[0])]
    analysis=normalized.resize(tuple(analysis_size),Image.Resampling.LANCZOS)
    analysis_pixel=hashlib.sha256(analysis.tobytes()).hexdigest();initial=copy.deepcopy(m)
    for n in initial['nodes']:
        n['box']=list(n.get('analysisBox',n['box']));n['center']=list(n.get('analysisCenter',n['center']))
    result=copy.deepcopy(m);changed=set();root=Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper'))
    for old in bad:
        view={**initial,'nodes':[n for n in initial['nodes'] if n['id']!=old['id']]}
        proposals=completed_node_candidates(rgb,view,inverse,root,binding,normal_size,normal_pixel,analysis_size,analysis_pixel)
        matches=[]
        for proposal in proposals:
            proof=proposal['checkProposal'];x,y,w,h=proof['sourceBox'];ox,oy,ow,oh=old['box']
            if (.85*ow<=w<=1.15*ow and .85*oh<=h<=1.15*oh
                    and np.linalg.norm(np.array([x+w/2,y+h/2])-old['center'])<=min(ow,oh)*.05):matches.append(proof)
        if len(matches)!=1:continue
        proof=matches[0];n=next(n for n in result['nodes'] if n['id']==old['id'])
        n['completedRefinement']={**proof,'originalNodeId':old['id'],'originalModelCompleted':True,
            'originalModelType':old['type'],'originalModelScore':old['score'],'originalModelTemplate':old.get('template'),
            'previousSourceBox':list(old['box']),'previousSourceCenter':list(old['center']),
            'previousAnalysisBox':list(old.get('analysisBox',old['box'])),'previousAnalysisCenter':list(old.get('analysisCenter',old['center'])),
            'previousCheckMaskIoU':actions['nodes'][old['id']]['checkMaskIoU']}
        n['geometryMethod']='original_source_done_template_extent'
        x,y,w,h=proof['sourceBox'];n['box']=[round(x,2),y,round(w,2),h];n['center']=[round(x+w/2,2),y+h/2]
        n['analysisBox']=list(proof['originalAnalysisBox']);n['analysisCenter']=list(proof['originalAnalysisCenter']);changed.add(n['id'])
    if not changed:return m
    # Re-read actual connecting pixels after changing endpoint geometry.
    import map_vision
    columns=rect.get('rectifiedColumns',m['columns']);spacing=float(np.mean(np.diff(columns)))
    result['edges']=[e for e in result['edges'] if not changed.intersection([e['from'],e['to']])]
    result['uncertainConnections']=[e for e in result.get('uncertainConnections',[]) if not changed.intersection([e['from'],e['to']])]
    def node_geometry(n):
        box=n.get('analysisBox',n['box']);center=n.get('analysisCenter',n['center']);sx,sy=analysis_size[0]/normal_size[0],analysis_size[1]/normal_size[1]
        return {'id':n['id'],'box':[v*(sx if i%2==0 else sy) for i,v in enumerate(box)],
                'center':[center[0]*sx,center[1]*sy],'lineGeometryStage':'final_verified_boxes'}
    for a in result['nodes']:
        for b in result['nodes']:
            if not changed.intersection([a['id'],b['id']]) or b.get('type')=='exit' or b.get('visibleRow')!=a.get('visibleRow',-10)+1:continue
            if a['type'] not in ('exit','boss') and b['type']!='boss' and abs(a['column']-b['column'])>1:continue
            if abs(b.get('analysisCenter',b['center'])[1]-a.get('analysisCenter',a['center'])[1]-spacing)>spacing*.25:continue
            score=map_vision.line_evidence(analysis,node_geometry(a),node_geometry(b))
            edge={'from':a['id'],'to':b['id'],'pixel_support':score}
            if score>=.85:result['edges'].append({**edge,'completedPath':a.get('completed',False) and b.get('completed',False),'review_required':True})
            else:result['uncertainConnections'].append({**edge,'reason':'Refined endpoint still lacks original-kernel line support'})
    return result


def completed_geometry(fn):
    @functools.wraps(fn)
    def wrapped(image,packet):return recover_completed_extents(image,fn(image,packet),packet.get('binding',{}))
    return wrapped
