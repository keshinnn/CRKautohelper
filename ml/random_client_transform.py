"""Reproducible virtual-client pixels; metadata belongs only to the evaluator.

This utility does not run recognition or claim P4-C acceptance. A dataset
generator must freeze its sequences and anchors before invoking it.
"""
import hashlib,io,math,random
from pathlib import Path
from PIL import Image

def sample_layout(size,required_boxes,seed):
    if len(size)!=2 or any(type(n) is not int or n<1 for n in size) or type(seed) is not int or not required_boxes:raise ValueError('reviewed size, anchors and integer seed required')
    w,h=size
    for b in required_boxes:
        if len(b)!=4 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in b) or b[0]<0 or b[1]<0 or min(b[2:])<=0 or b[0]+b[2]>w or b[1]+b[3]>h:raise ValueError('anchor outside source')
    limits=[min(b[0] for b in required_boxes),min(b[1] for b in required_boxes),w-max(b[0]+b[2] for b in required_boxes),h-max(b[1]+b[3] for b in required_boxes)]
    rng=random.Random(seed);margins=[]
    for limit,extent in zip(limits,[w,h,w,h]):
        maximum=min(math.floor(limit),max(0,math.floor(extent*.08)))
        margins.append(rng.randint(1,maximum) if maximum>0 else 0)
    if not sum(margins):raise ValueError('required anchors leave no positive crop possible')
    left,top,right,bottom=margins;cw,ch=w-left-right,h-top-bottom
    # Sample absolute client dimensions inside the declared design test range.
    # Native source dimensions do not silently shrink this range for 960px videos.
    oh=rng.randint(540,1440)
    ow=rng.randint(max(960,math.ceil(oh*1.25)),min(2560,math.floor(oh*2.5)))
    sx,sy=ow/cw,oh/ch
    return {'kind':'virtual_client_random','seed':seed,'inputSize':list(size),'cropMargins':margins,'cropBox':[left,top,cw,ch],'outputSize':[ow,oh],'sx':sx,'sy':sy,
      'matrix':[[sx,0,-left*sx],[0,sy,-top*sy],[0,0,1]],'inverseMatrix':[[1/sx,0,left],[0,1/sy,top],[0,0,1]]}

def transform_box(box,layout):
    left,top,_,_=layout['cropBox'];sx,sy=layout['sx'],layout['sy']
    return [(box[0]-left)*sx,(box[1]-top)*sy,box[2]*sx,box[3]*sy]

def inverse_point(point,layout):
    return [point[0]/layout['sx']+layout['cropBox'][0],point[1]/layout['sy']+layout['cropBox'][1]]

def transform_png(source,layout,output):
    source=Path(source);output=Path(output);raw=source.read_bytes()
    with Image.open(io.BytesIO(raw)) as image:
        if image.format!='PNG' or list(image.size)!=layout['inputSize']:raise ValueError('original PNG size does not match frozen layout')
        left,top,w,h=layout['cropBox']
        if min(left,top)<0 or min(w,h)<=0 or left+w>image.width or top+h>image.height:raise ValueError('crop outside source')
        cropped=image.crop((left,top,left+w,top+h));transformed=cropped.resize(tuple(layout['outputSize']),Image.Resampling.LANCZOS)
        with output.open('xb') as target:transformed.save(target,format='PNG')
    return {'image':str(output.resolve()),'size':list(layout['outputSize']),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'transform':{**layout,'inputSha256':hashlib.sha256(raw).hexdigest()}}
