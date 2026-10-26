"""V1 geometry contract: actual raster sizes, half-open boxes, no implicit rounding.

Source is the capture PNG; client has identical pixels in the offline observer.
Rectified is the aspect-corrected raster; analysis is the actual model raster.
Box coordinates remain float64 through projections. Only raster creation and
the eventual input boundary quantize; OCR/crop policies are separate consumers.
"""
import math


def raster_round(value):
    if not math.isfinite(value) or value < 0:
        raise ValueError('invalid raster extent')
    return math.floor(value + .5)


def analysis_raster(source):
    """Actual legacy map_vision raster: preserve its operation order/ties-even.

    V2-owned rectification/calibration rasters use raster_round; the preserved
    V1 producer owns this model raster and uses round(height * (960/width)).
    """
    _size(source)
    return [960,round(source[1]*(960/source[0]))]


def _size(size):
    if len(size) != 2 or any(type(v) is not int or v <= 0 for v in size):
        raise ValueError('actual positive raster dimensions required')


def resize_point(point, source, target):
    _size(source); _size(target)
    if len(point) != 2 or any(not math.isfinite(v) or not 0 <= v <= source[i] for i,v in enumerate(point)):
        raise ValueError('point outside source raster')
    return [point[i] * target[i] / source[i] for i in range(2)]


def resize_box(box, source, target):
    if len(box) != 4 or any(not math.isfinite(v) for v in box) or min(box[2:]) <= 0:
        raise ValueError('invalid half-open box')
    x,y,w,h=box
    left,top=resize_point([x,y],source,target)
    right,bottom=resize_point([x+w,y+h],source,target)
    return [left,top,right-left,bottom-top]


def geometry_certificate(binding, rectified, analysis):
    source=[binding['width'],binding['height']]
    for size in [source,rectified,analysis]: _size(size)
    if rectified[1] != source[1]: raise ValueError('aspect rectification preserves source Y')
    if list(analysis)!=analysis_raster(rectified): raise ValueError('analysis raster differs from actual legacy producer')
    return {'version':1,'spaces':{'source':source,'client':list(source),'rectified':list(rectified),'analysis':list(analysis)},
            'sourceCaptureFrameId':binding.get('frameId'),'sourceImageSha256':binding['imageSha256'],
            'pixelSha256':binding['pixelSha256'],'rounding':'endpoints_float64_raster_half_up',
            'analysisRounding':'legacy_model_ties_even'}
