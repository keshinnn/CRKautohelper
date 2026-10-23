"""Render diagnostic geometry on saved pixels; never operates a window."""
import json, math, sys
from pathlib import Path
from PIL import Image, ImageDraw
source, destination, geometry = map(Path, sys.argv[1:4])
with Image.open(source) as loaded: image = loaded.convert('RGB')
draw = ImageDraw.Draw(image)
for row in json.loads(geometry.read_text(encoding='utf-8')):
    if 'box' in row:
        box = row['box']
        if len(box)!=4 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in box): raise ValueError('invalid overlay box')
        x,y,w,h=box
        if not (0<=x<x+w<=image.width and 0<=y<y+h<=image.height): raise ValueError('overlay outside client')
        draw.rectangle((x,y,x+w-1,y+h-1), outline=(255,40,60), width=3)
    if 'point' in row:
        x,y=row['point']
        if not (math.isfinite(x) and math.isfinite(y) and 0<=x<image.width and 0<=y<image.height): raise ValueError('invalid overlay point')
        draw.line((x-6,y,x+6,y),fill='yellow',width=2);draw.line((x,y-6,x,y+6),fill='yellow',width=2)
image.save(destination, format='PNG')
