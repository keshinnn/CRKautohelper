"""Independent ordinary-preview controls: waiting authority, never node identity."""
import hashlib, re, os, sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

def _box(row):
    points=np.asarray(row.get('box',[]),dtype=float)
    if points.shape!=(4,2) or not np.isfinite(points).all():return None
    lo=points.min(axis=0);hi=points.max(axis=0)
    return [float(lo[0]),float(lo[1]),float(hi[0]-lo[0]),float(hi[1]-lo[1])]

def _english_ordinary_crop(image,evidence):
    labels=[r for r in evidence if r.get('text','').strip().casefold()=='difficulty' and r.get('score',0)>=.95 and _box(r) and _box(r)[0]>image.width*.5]
    if len(labels)!=1:return []
    x,y,w,h=_box(labels[0])
    if h<=0 or h>image.height*.1 or x+w>=image.width:return []
    left,top=int(x+w),max(0,int(y-h*.15))
    right,bottom=max(left,int(image.width-h)),min(image.height,int(y+h*1.15))
    if min(right-left,bottom-top)<=0:return []
    crop=image.crop((left,top,right,bottom))
    import text_reader
    runtime=getattr(text_reader,'_v2_bounded_ocr_runtime',None)
    if not runtime or not runtime.enabled:return []
    sizes=[(max(24,round(crop.width/crop.height*40*ratio)),40) for ratio in [.65,.8,.95]]
    pixels=[np.asarray(crop.convert('RGB').resize(size,Image.Resampling.LANCZOS))[:,:,::-1].copy() for size in sizes]
    readings,elapsed=runtime.reader.text_rec(pixels)
    runtime.recognition_crops.append({'inputSize':list(crop.size),'source':'difficulty_adjacent_english_line','variants':[{'text':text,'score':float(score),'analysisSize':list(size)} for size,(text,score) in zip(sizes,readings)],'elapsedMs':float(elapsed)*1000})
    # Difficulty stars are part of the actual observed line. Keep them and
    # the original recognizer score; reject every other prefix/suffix.
    matches=[(text,float(score),size) for size,(text,score) in zip(sizes,readings) if re.fullmatch(r'\*{0,2}Normal',text.strip(),re.I) and float(score)>=.95]
    if not matches:return []
    text,score,analysis_size=max(matches,key=lambda row:row[1])
    return [{'text':text,'score':score,'box':[[left,top],[right,top],[right,bottom],[left,bottom]],
        'boxSource':'original_line_crop_extent','source':'difficulty_adjacent_english_normal_original_crop','cropBox':[left,top,right-left,bottom-top],'analysisSize':list(analysis_size)}]


def _timer_original_crop(image,evidence):
    # A clock icon sometimes becomes '@' in the same OCR row as the digits.
    # That weak token locates pixels only; it is never accepted as a timer.
    rows=[r for r in evidence if r.get('score',0)>=.75 and _box(r) and _box(r)[0]>image.width*.5
        and re.fullmatch(r'[@◎○〇]?\d{2}:\d{2}',r.get('text','').strip())]
    if len(rows)!=1 or not re.fullmatch(r'[@◎○〇]03:00',rows[0]['text'].strip()):return []
    import text_reader
    runtime=getattr(text_reader,'_v2_bounded_ocr_runtime',None)
    if not runtime or not runtime.enabled:return []
    row=rows[0];x,y,w,h=_box(row)
    if not 0<h<image.height*.1 or x+w>image.width or y<0 or y+h>image.height:return []
    labels=[]
    for label in evidence:
        text=re.sub(r'\s+','',label.get('text',''));bounds=_box(label)
        if not bounds:continue
        if not (re.fullmatch(r'.{0,3}限制時[間间]',text) or text.casefold() in ('timelimit','battletimelimit')):continue
        lx,ly,lw,lh=bounds
        if (lx>image.width*.5 and lx+lw<=x+h*.25 and x-lx-lw<=image.width*.25
                and abs(ly+lh/2-y-h/2)<=max(lh,h)*.6):
            if .65<=label.get('score',0)<.75:
                # Weak text locates a bounded original crop only. A new OCR
                # reading must clear the unchanged .75 label threshold; the
                # timer digits still independently require .95 below.
                left,top=int(lx),int(ly);right,bottom=int(lx+lw),int(ly+lh)
                if min(left,top)<0 or right>image.width or bottom>image.height:continue
                readings=runtime.read_line_variants(image.crop((left,top,right,bottom)),len(text))
                labels_read=[r for r in readings if r.get('score',0)>=.75 and
                    re.fullmatch(r'.{0,3}限制時[間间]',re.sub(r'\s+','',r.get('text','')))]
                if not labels_read:continue
                label={**max(labels_read,key=lambda r:r['score']),'box':label['box'],
                       'source':'time_limit_original_crop','cropBox':[left,top,right-left,bottom-top],
                       'originalText':label['text'],'originalScore':label['score']}
            if label.get('score',0)>=.75:labels.append(label)
    if len(labels)!=1:return []
    for fraction in [0,.2,.4,.6,.8,1.0]:
        left,top=max(0,int(x+h*fraction)),max(0,int(y-2))
        right,bottom=min(image.width,int(x+w+2)),min(image.height,int(y+h+2))
        if right<=left or bottom<=top:continue
        readings=runtime.read_line_variants(image.crop((left,top,right,bottom)),5)
        timed=[r for r in readings if r.get('score',0)>=.95 and re.fullmatch(r'\d{2}:\d{2}',r.get('text','').strip())]
        if {r['text'].strip() for r in timed}!={'03:00'}:continue
        best=max(timed,key=lambda r:r['score'])
        return [{**best,'box':[[left,top],[right,top],[right,bottom],[left,bottom]],
            'source':'timer_digits_original_crop','cropBox':[left,top,right-left,bottom-top],
            'originalText':row['text'],'originalScore':row['score'],'timeLimitEvidence':labels[0]}]
    return []


def _ordinary_crop_scale(packet,binding,digest,width,height):
    e=(packet.get('mapReview') or {}).get('aspectRectification')
    if e is None:return 1,None
    # Unversioned captures predate the geometry certificate. Preserve their
    # legacy scale-one OCR recipe without using any unverified aspect data.
    # A current V2 packet may never fall back when its certificate is missing.
    if packet.get('observerContractVersion') is None and e.get('coordinateContract') is None:return 1,None
    from geometry_contract import geometry_certificate,analysis_raster
    size=[width,height];r=e.get('rectifiedInputSize')
    if (e.get('verified') is not True or e.get('method')!='same_frame_circle_aspect_map_rectification'
        or e.get('actionsExecuted') is not False or e.get('sourceCaptureFrameId')!=binding['frameId']
        or e.get('sourceImageSha256')!=binding['imageSha256'] or e.get('pixelSha256')!=digest or e.get('sourceSize')!=size
        or not isinstance(r,list) or len(r)!=2 or any(type(v) is not int or v<=0 for v in r) or r[1]!=height):return None
    scale=width/r[0]
    if (e.get('modelAnalysisSize')!=analysis_raster(r)
        or e.get('coordinateContract')!=geometry_certificate(binding,r,analysis_raster(r))
        or e.get('forwardMatrix')!=[[1/scale,0,0],[0,1,0],[0,0,1]]
        or e.get('inverseMatrix')!=[[scale,0,0],[0,1,0],[0,0,1]]
        or (e.get('calibration') or {}).get('pixelSha256')!=digest
        or (e.get('calibration') or {}).get('sourceSize')!=size):return None
    return scale,{'method':'same_frame_rectified_horizontal_glyph_crop','horizontalScale':scale,
        'sourceCaptureFrameId':binding['frameId'],'sourceImageSha256':binding['imageSha256'],
        'pixelSha256':digest,'sourceSize':size,'rectifiedInputSize':r}

def inspect_preview_context(image,packet):
    unknown={'verified':False,'reason':'PREVIEW_CONTEXT_UNPROVEN'}
    a=np.asarray(image.convert('RGB'));height,width=a.shape[:2]
    digest=hashlib.sha256(a.tobytes()).hexdigest();binding=packet.get('binding') or {};progress=packet.get('progress') or {}
    if (binding.get('pixelSha256')!=digest or [binding.get('width'),binding.get('height')]!=[width,height]
            or re.fullmatch(r'[a-f0-9]{32}',binding.get('frameId','')) is None
            or re.fullmatch(r'[a-f0-9]{64}',binding.get('imageSha256','')) is None):return unknown
    if progress.get('conflictingEvidence') is not False or not .9<=progress.get('score',0)<=1 or type(progress.get('displayedZone')) is not int:return unknown
    if not 1<=progress['displayedZone']<=10:return unknown
    evidence=packet.get('evidence',[])
    enters=[r for r in evidence if re.sub(r'\s+','',r.get('text','')).casefold() in ('進入','enter') and r.get('score',0)>=.95 and _box(r) and _box(r)[0]>width*.5]
    timers=[r for r in evidence if r.get('text')=='03:00' and r.get('score',0)>=.95 and _box(r) and _box(r)[0]>width*.5]
    ordinary=[r for r in evidence if '普通' in r.get('text','') and r.get('score',0)>=.65 and _box(r) and _box(r)[0]>width*.5]
    english_difficulty=[r for r in evidence if r.get('text','').strip().casefold()=='difficulty' and r.get('score',0)>=.95 and _box(r) and _box(r)[0]>width*.5]
    if not timers and len(enters)==1 and (len(ordinary)==1 or len(english_difficulty)==1):
        timers=_timer_original_crop(image,evidence)
    if not ordinary and len(enters)==1 and len(timers)==1 and enters[0].get('text','').strip().casefold()=='enter':
        ordinary=_english_ordinary_crop(image,evidence)
    if len(enters)!=1 or len(timers)!=1 or len(ordinary)!=1:return unknown
    ordinary_evidence={'kind':'original_ocr','originalScore':ordinary[0]['score']}
    if ordinary[0].get('source')=='difficulty_adjacent_english_normal_original_crop':
        ordinary_evidence={**ordinary_evidence,'kind':ordinary[0]['source'],'originalPixelReading':ordinary[0]}
    if ordinary[0]['score']<.8:
        # Re-read a bounded original-pixel crop; do not promote the old score
        # or substitute an expected word into OCR output.
        geometry=_ordinary_crop_scale(packet,binding,digest,width,height)
        if geometry is None:return unknown
        horizontal_scale,position_evidence=geometry
        ox,oy,ow,oh=_box(ordinary[0]);left=max(0,int(ox+ow-oh*2*horizontal_scale));top=max(0,int(oy-3));right=min(width,int(ox+ow+3));bottom=min(height,int(oy+oh+3))
        crop=image.crop((left,top,right,bottom))
        root=Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper'));module_path=str(root/'ml')
        if module_path not in sys.path:sys.path.insert(0,module_path)
        import text_reader
        runtime=getattr(text_reader,'_v2_bounded_ocr_runtime',None)
        if runtime:
            readings=runtime.read_line_variants(crop,sum('\u3400'<=c<='\u9fff' for c in ordinary[0]['text']));kind='bounded_original_pixel_line_recognition';crop_scale=1
        else:
            crop=crop.resize((crop.width*3,crop.height*3));readings=text_reader.read_text(crop);kind='bounded_original_pixel_crop_ocr';crop_scale=3
        refined=sorted([r for r in readings if re.sub(r'\s+','',r.get('text',''))=='普通' and r.get('score',0)>=.95],key=lambda r:r['score'],reverse=True)[:1]
        if runtime and not refined:
            # Adjacent difficulty stars can share the detected text box. Trim
            # only a small, bounded left margin and require a new high-score
            # reading from actual pixels; never strip punctuation from text.
            for fraction in [.1,.2,.3]:
                local_left=left+round(oh*fraction*horizontal_scale)
                readings=runtime.read_line_variants(image.crop((local_left,top,right,bottom)),sum('\u3400'<=c<='\u9fff' for c in ordinary[0]['text']))
                refined=sorted([r for r in readings if re.sub(r'\s+','',r.get('text',''))=='普通' and r.get('score',0)>=.95],key=lambda r:r['score'],reverse=True)[:1]
                if len(refined)==1:
                    left=local_left
                    break
        if len(refined)!=1:return unknown
        ordinary_evidence={'kind':kind,'originalScore':ordinary[0]['score'],'refinedScore':refined[0]['score'],'refinedReading':dict(refined[0]),'cropBox':[left,top,right-left,bottom-top],'cropScale':crop_scale}
        if position_evidence:ordinary_evidence['positionEvidence']=position_evidence
    eb,tb,ob=map(_box,[enters[0],timers[0],ordinary[0]])
    if not ob[1]<tb[1]<eb[1] or eb[1]-tb[1]<height*.15:return unknown
    hsv=cv2.cvtColor(a,cv2.COLOR_RGB2HSV)
    green=(hsv[:,:,0]>30)&(hsv[:,:,0]<85)&(hsv[:,:,1]>100)&(hsv[:,:,2]>150)
    x,y,w,h=eb
    left,top=max(0,int(x-w*2)),max(0,int(y-h));right,bottom=min(width,int(x+w*3)),min(height,int(y+h*2))
    mask=green[top:bottom,left:right].astype('uint8')
    count,labels,stats,centers=cv2.connectedComponentsWithStats(mask)
    buttons=[]
    for bx,by,bw,bh,area in stats[1:]:
        if bw>w*2 and bh>h*1.3 and area/(bw*bh)>.45 and left+bx<x and left+bx+bw>x+w and top+by<y and top+by+bh>y+h:
            buttons.append([int(left+bx),int(top+by),int(bw),int(bh)])
    if len(buttons)!=1:return unknown
    return {'verified':True,'waitOnly':True,'method':'same_frame_ordinary_preview_controls',
        'sourceCaptureFrameId':binding['frameId'],'sourceImageSha256':binding['imageSha256'],
        'pixelSha256':digest,'sourceSize':[width,height],'zone':progress['displayedZone'],
        'enterBox':buttons[0],'enterEvidence':enters[0],'timerBox':tb,'timerEvidence':timers[0],
        'ordinaryBox':ob,'ordinaryReading':ordinary[0],'ordinaryEvidence':ordinary_evidence,'actionsExecuted':False}
