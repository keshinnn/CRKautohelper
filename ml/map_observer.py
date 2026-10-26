"""V2 boundary around the unchanged V1 detector/lattice/line algorithms.

Observe their actual 960 raster directly and project once. Calling the V1
large-image convenience path would independently round boxes and centres to
.01 before rectification, losing the measurement needed by later proofs.
"""
import hashlib
import numpy as np
from PIL import Image
from geometry_contract import analysis_raster,resize_box,resize_point


def inspect_map(image,folder,geometry=None,read_header=True):
    from map_vision import inspect_map as legacy_inspect
    source=list(image.size);size=analysis_raster(source)
    model=image if source==size else image.resize(tuple(size),Image.Resampling.LANCZOS)
    calibration=dict(geometry) if geometry else None
    if calibration and 'columns' in calibration:
        calibration['columns']=[resize_point([x,0],source,size)[0] for x in calibration['columns']]
    result=legacy_inspect(model,folder,calibration,read_header=False)
    for n in result['nodes']:
        n['detectorGeometry']={'box':list(n['box']),'center':list(n['center'])}
        n['box']=resize_box(n['box'],size,source)
        n['center']=resize_point(n['center'],size,source)
    if result.get('columns'):
        result['columns']=[resize_point([x,0],size,source)[0] for x in result['columns']]
    digest=hashlib.sha256(np.asarray(image.convert('RGB')).tobytes()).hexdigest()
    result.update(frameId=digest[:20],analysisScale=size[0]/source[0],analysisScaleY=size[1]/source[1],
        modelGeometryEvidence={'sourceSize':source,'sourcePixelSha256':digest,'size':size,
          'pixelSha256':hashlib.sha256(np.asarray(model.convert('RGB')).tobytes()).hexdigest()})
    if read_header and result['nodes']:
        from text_reader import read_map_header
        result['header']=read_map_header(image)
    return result
