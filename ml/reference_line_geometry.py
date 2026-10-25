"""Measure borderline lines at the original 58-pixel node reference size."""
import copy
import functools
import hashlib
import re
import numpy as np
from PIL import Image


def reference_line(image,a,b,original):
    raw=original(image,a,b)
    pitch=float(np.median([min(a['box'][2:]),min(b['box'][2:])]))
    if not .5<=raw<.85 or pitch<=58:return raw,None
    factor=58/pitch;size=[round(image.width*factor),round(image.height*factor)]
    if min(size)<1:return raw,None
    sx,sy=size[0]/image.width,size[1]/image.height
    nodes=[{'box':[v*(sx if i%2==0 else sy) for i,v in enumerate(n['box'])],
            'center':[n['center'][0]*sx,n['center'][1]*sy]} for n in [a,b]]
    reference=image.resize(tuple(size),Image.Resampling.LANCZOS)
    score=original(reference,*nodes)
    if score<.85:return raw,None
    return score,{'method':'original_line_kernel_at_node58_reference','referenceNodeSize':58,
        'originalSupport':raw,'pixelSupport':score,'analysisSize':list(image.size),
        'analysisPixelSha256':hashlib.sha256(image.convert('RGB').tobytes()).hexdigest(),
        'sourceNodeBoxes':[list(a['box']),list(b['box'])],
        'sourceNodeCenters':[list(a['center']),list(b['center'])],
        'medianNodeShortSide':pitch,'referenceSize':size,
        'referencePixelSha256':hashlib.sha256(reference.convert('RGB').tobytes()).hexdigest(),
        'referenceNodeBoxes':[n['box'] for n in nodes],
        'referenceNodeCenters':[n['center'] for n in nodes],'actionsExecuted':False}


def reference_geometry(fn):
    @functools.wraps(fn)
    def wrapped(image,packet):
        binding=packet.get('binding',{})
        if re.fullmatch(r'[a-f0-9]{32}',binding.get('frameId','')) is None:return fn(image,packet)
        import map_vision
        original=map_vision.line_evidence;records={}
        def measure(current,a,b):
            score,proof=reference_line(current,a,b,original)
            records[(a.get('id'),b.get('id'))]=(score,proof)
            return score
        map_vision.line_evidence=measure
        try:result=fn(image,packet)
        finally:map_vision.line_evidence=original
        if not isinstance(result,dict) or result is packet.get('mapReview'):return result
        rect=result.get('aspectRectification') or {}
        for edge in result.get('edges',[]):
            score,proof=records.get((edge['from'],edge['to']),(None,None))
            if proof is None or score!=edge['pixel_support']:continue
            edge['lineScoreMethod']='reference_node58_original_kernel'
            edge['lineReference']={**copy.deepcopy(proof),'sourceImageSha256':binding['imageSha256'],
                'pixelSha256':binding['pixelSha256'],'sourceCaptureFrameId':binding['frameId'],
                'sourceSize':list(image.size),'sourceNodeIds':[edge['from'],edge['to']],
                'rectifiedInputSize':rect.get('rectifiedInputSize',list(image.size)),
                'rectifiedPixelSha256':rect.get('rectifiedPixelSha256',binding['pixelSha256'])}
        return result
    return wrapped
