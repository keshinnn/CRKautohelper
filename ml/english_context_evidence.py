"""Original-pixel English header repair. Old tokens locate, never authorize."""
import hashlib
import math
import re
import numpy as np
from PIL import Image

PATTERNS={
    'zone':re.compile(r'Zone\s*(10|[1-9])\s*in\s*Progress',re.I),
    'timer':re.compile(r'Ends\s+in:\s*(\d+)D\s+(\d{2}):(\d{2}):(\d{2})',re.I),
}


def _key(kind,text):
    m=PATTERNS[kind].fullmatch(text.strip())
    if not m:return None
    values=tuple(map(int,m.groups()))
    if kind=='timer' and not (values[1]<24 and values[2]<60 and values[3]<60):return None
    return values


def _bounds(row,image):
    try:q=np.asarray(row.get('box'),dtype=float)
    except (ValueError,TypeError):return None
    if q.shape!=(4,2) or not np.isfinite(q).all():return None
    lo,hi=q.min(0),q.max(0);h=hi[1]-lo[1]
    if not (0<h<image.height*.1 and 0<=lo[0]<hi[0]<=image.width*.5 and 0<=lo[1]<hi[1]<=image.height*.35):return None
    return [*lo,*hi]


def reread_english_context(runtime,image,rows):
    title=[r for r in rows if r.get('text','').strip().casefold()=='trials of the nether realm' and .9<=r.get('score',0)<=1]
    if len(title)!=1:return rows
    tb=_bounds(title[0],image)
    if tb is None or tb[1]>image.height*.15:return rows
    locators={kind:[] for kind in PATTERNS}
    for r in rows:
        if not .65<=r.get('score',0)<=1:continue
        bounds=_bounds(r,image)
        if bounds is None:continue
        text=r.get('text','').strip()
        if re.match(r'\)?Ends\s+in:',text,re.I):locators['timer'].append((r,bounds))
        elif re.match(r'Zone\s*(?:10|[1-9])(?!\d)',text,re.I):locators['zone'].append((r,bounds))
    if any(len(v)!=1 for v in locators.values()):return rows
    timer,timerbox=locators['timer'][0];zone,zonebox=locators['zone'][0]
    if not (tb[3]<timerbox[1] and timerbox[3]<zonebox[1]):return rows
    fresh=[]
    for kind,items in locators.items():
        locator,box=items[0]
        qualified=[r for r in rows if .9<=r.get('score',0)<=1 and _key(kind,r.get('text','')) is not None]
        if qualified:continue
        hints=[locator]
        if kind=='zone':
            # Merge only same-baseline adjacent detector envelopes. Their text
            # never becomes a semantic claim: reread the entire original crop.
            h=box[3]-box[1]
            for r in rows:
                if r is locator or not .65<=r.get('score',0)<=1:continue
                q=_bounds(r,image)
                if q is None or not re.fullmatch(r'(?:in\s*)?Progress\.?',r.get('text','').strip(),re.I):continue
                if abs((q[1]+q[3]-box[1]-box[3])/2)>h*.3 or not -h<=q[0]-box[2]<=h*1.5:continue
                hints.append(r);box=[min(box[0],q[0]),min(box[1],q[1]),max(box[2],q[2]),max(box[3],q[3])]
            hint=re.match(r'Zone\s*(10|[1-9])(?!\d)',locator['text'],re.I)
            expected=(int(hint[1]),)
            # A detector may omit the entire suffix. The independently
            # observed title/timer bound the same header column; scan the
            # full current text line rather than inventing missing tokens.
            box=[box[0],box[1],max(box[2],tb[2],timerbox[2]),box[3]]
        else:
            clocks=re.findall(r'(\d+)D\s+(\d{2}):(\d{2}):(\d{2})',locator['text'],re.I)
            if len(clocks)!=1:return rows
            expected=tuple(map(int,clocks[0]))
        h=box[3]-box[1];readings=[];accepted=[]
        for pad in [0,.1,.25]:
            crop=(max(0,math.floor(box[0]-h*pad)),max(0,math.floor(box[1]-h*pad)),
                  min(image.width,math.ceil(box[2]+h*pad)),min(image.height,math.ceil(box[3]+h*pad)))
            pixels=image.crop(crop)
            local=runtime.previous_read(pixels.resize((pixels.width*3,pixels.height*3),Image.Resampling.LANCZOS))
            count=len(re.sub(r'\s+','', ''.join(r['text'] for r in hints)))
            if 1<=count<=20:local=[*local,*runtime.read_line_variants(pixels,count)]
            for r in local:
                reading={'text':r.get('text',''),'score':r.get('score',0),'cropBox':[crop[0],crop[1],crop[2]-crop[0],crop[3]-crop[1]]}
                readings.append(reading)
                key=_key(kind,reading['text'])
                if key is not None and .9<=reading['score']<=1:
                    if key!=expected:return rows
                    accepted.append(reading)
            if accepted:break
        if not accepted:return rows
        best=max(accepted,key=lambda r:r['score']);x,y,w,h=best['cropBox']
        fresh.append({**best,'text':best['text'].strip(),'box':[[x,y],[x+w,y],[x+w,y+h],[x,y+h]],
            'source':'english_header_original_crop','contextKind':kind,
            'sourcePixelSha256':hashlib.sha256(image.convert('RGB').tobytes()).hexdigest(),
            'sourceSize':list(image.size),'originalLocators':hints,'recognitionReadings':readings})
    return [*rows,*fresh] if fresh else rows
