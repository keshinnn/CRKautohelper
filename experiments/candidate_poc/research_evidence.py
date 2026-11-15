"""A2 research: bound coordinate and raw-gradient witnesses, never authority.

There is deliberately no learned detector, physical outer-boundary decision,
map anchoring, preview identity, or formal verifier bridge in this module.
"""
import hashlib
import math
from pathlib import Path
from PIL import Image


def make_witness(image, box, context):
    raw = Path(image).read_bytes()
    with Image.open(image) as decoded:
        if decoded.format != 'PNG' or decoded.mode != 'RGB':
            raise ValueError('RGB_PNG_REQUIRED')
        im = decoded.copy()
    width, height = im.size
    if (not isinstance(box, list) or len(box) != 4 or
            any(type(x) not in (int, float) or not math.isfinite(x) for x in box) or
            min(box[:2]) < 0 or min(box[2:]) <= 0 or
            box[0] + box[2] > width or box[1] + box[3] > height):
        raise ValueError('BOX_INVALID')
    ratio = min(640 / width, 640 / height)
    rw, rh = math.floor(width * ratio + .5), math.floor(height * ratio + .5)
    if rw < 1 or rh < 1:
        raise ValueError('GEOMETRY_INVALID')
    left, top = (640 - rw) // 2, (640 - rh) // 2
    sx, sy = rw / width, rh / height
    matrix = [[sx, 0, left], [0, sy, top], [0, 0, 1]]
    x, y, w, h = box
    tensor_box = [x * sx + left, y * sy + top, w * sx, h * sy]
    samples = []
    pixels = im.load()
    # Fixed sample schedule measures evidence at a supplied box; it does NOT
    # infer a unique physical node boundary. Raw samples remain non-authority.
    for side in range(4):
        for i in range(16):
            t = (i + .5) / 16
            px, py = [(x + w * t, y), (x + w * t, y + h),
                      (x, y + h * t), (x + w, y + h * t)][side]
            ix, iy = math.floor(px), math.floor(py)
            if not (1 <= ix < width - 1 and 1 <= iy < height - 1):
                raise ValueError('EDGE_SAMPLE_OUTSIDE_SOURCE')
            axis = 'y' if side < 2 else 'x'
            a, b = ((ix, iy - 1), (ix, iy + 1)) if axis == 'y' else ((ix - 1, iy), (ix + 1, iy))
            gradient = sum(abs(pixels[a][j] - pixels[b][j]) for j in range(3))
            samples.append(dict(x=ix, y=iy, axis=axis, gradient=gradient))
    return dict(schema='candidate-evidence/v2-research-geometry-1',
                sourceImageSha256=hashlib.sha256(raw).hexdigest(),
                sourceRgbSha256=hashlib.sha256(im.tobytes()).hexdigest(),
                sourceSize=[width, height], sourceBox=list(box), tensorBox=tensor_box,
                sourceToTensor=matrix, frameToken=context['frameToken'],
                sourceKey=context['sourceKey'], geometryEpoch=context['geometryEpoch'],
                atMs=context['atMs'], edgeSamples=samples,
                researchOnly=True, outerBoundaryVerified=False)
