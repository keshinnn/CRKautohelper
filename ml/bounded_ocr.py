"""Opt-in V2 OCR preprocessing. Existing assets, refiners and scores unchanged."""
import re,math,hashlib
import numpy as np
from PIL import Image
import text_reader
from rapidocr_onnxruntime import RapidOCR
from rapidocr_onnxruntime.ch_ppocr_det.utils import DetPreProcess

def normalize_evidence(rows):
    result=[]
    for row in rows:
        text=row.get('text');normalized=re.sub(r'剩[余餘][時时][間间]','剩餘時間',text) if isinstance(text,str) else text
        result.append({**row,'text':normalized,'recognizerText':text,'orthographicNormalization':'remaining_time_traditional_glyphs'} if normalized!=text else dict(row))
    return result

def _remaining_timer_locators(rows):
    timers=[r for r in rows if .85<=r.get('score',0)<=1 and
        ('剩餘時間' in r.get('text','') or re.fullmatch(r'剩時間\d+天\d{2}:\d{2}:\d{2}',re.sub(r'\s+','',r.get('text',''))))]
    if any(re.fullmatch(r'(?:剩餘時間|剩時間)\d+天\d{2}:\d{2}:\d{2}',re.sub(r'\s+','',r.get('text',''))) for r in timers):return timers
    labels=[r for r in rows if .65<=r.get('score',0)<=1 and re.fullmatch(r'剩餘時間(?:\d+天)?',re.sub(r'\s+','',r.get('text','')))]
    if len(labels)!=1:return timers
    days_with_label=re.search(r'\d+天$',re.sub(r'\s+','',labels[0]['text'])) is not None
    pattern=r'\d{2}:\d{2}:\d{2}' if days_with_label else r'\d+天\d{2}:\d{2}:\d{2}'
    clocks=[r for r in rows if .9<=r.get('score',0)<=1 and re.fullmatch(pattern,re.sub(r'\s+','',r.get('text','')))]
    if len(clocks)!=1:return timers
    bounds=[]
    for row in [labels[0],clocks[0]]:
        points=np.asarray(row.get('box'),dtype=float)
        if points.shape!=(4,2) or not np.isfinite(points).all():return []
        lo,hi=points.min(0),points.max(0)
        if (hi<=lo).any():return []
        bounds.append((*lo,*hi))
    (x,y,right,bottom),(cx,cy,cr,cb)=bounds;h=bottom-y;ch=cb-cy
    if not (cx>(x+right)/2 and cr>right and -.5*max(h,ch)<=cx-right<=max(h,ch)
            and abs((cy+cb-y-bottom)/2)<=max(h,ch)*.3):return []
    left,top,endx,endy=min(x,cx),min(y,cy),max(right,cr),max(bottom,cb)
    # Both original rows locate one crop only. Neither weak label nor the
    # adjacent clock grants context until that full crop is independently read.
    return [{**labels[0],'box':[[left,top],[endx,top],[endx,endy],[left,endy]],
        'remainingLabelLocator':labels[0],'adjacentClockLocator':clocks[0]}]

def _context_reading_key(kind,text):
    text=re.sub(r'\s+','',text)
    if kind=='season':
        match=re.fullmatch(r'冥界[試试](?:[煉炼])?季([1-9]\d?)',text)
        return ('season',int(match[1])) if match else None
    match=re.fullmatch(r'剩餘時間(\d+)天(\d{2}):(\d{2}):(\d{2})',text)
    return ('timer',*map(int,match.groups())) if match else None

def _context_claim_agrees(kind,locator,reading):
    if not .9<=reading.get('score',0)<=1:return False
    original=re.sub(r'\s+','',locator['text']+locator.get('adjacentClockLocator',{}).get('text',''))
    actual=re.sub(r'\s+','',reading['text'])
    if kind=='season':
        old=re.search(r'季([1-9]\d?)$',original);new=re.search(r'季([1-9]\d?)$',actual)
        return old is not None and new is not None and old[1]==new[1]
    # Label spelling does not erase an observed complete clock claim. Colon
    # presentation is normalized for contradiction checking only, never to
    # make an otherwise unqualified fresh reading satisfy its label gate.
    old=re.findall(r'(?<!\d)(\d+)天(\d{2}):(\d{2}):(\d{2})(?!\d)',original.replace('：',':'))
    if not old:return True
    new=re.fullmatch(r'剩餘時間(\d+)天(\d{2}):(\d{2}):(\d{2})',actual)
    return len(old)==1 and new is not None and tuple(map(int,old[0]))==tuple(map(int,new.groups()))

class _MeasuredPreprocess(DetPreProcess):
    def __init__(self,side,mean,std,records):
        super().__init__(side,'max',mean,std);self.records=records

    def __call__(self,image):
        tensor=super().__call__(image)
        if tensor is not None:
            h,w=image.shape[:2];th,tw=tensor.shape[-2:]
            self.records.append({'inputSize':[w,h],'tensorSize':[tw,th],'sx':tw/w,'sy':th/h,'maximumTensorSide':self.limit_side_len,'inputFormat':'BGR8'})
        return tensor

class BoundedOCRRuntime:
    def __init__(self,side):
        if type(side) is not int or side not in [736,960,1280]:raise ValueError('explicit tested OCR bound required')
        self.side=side;self.reader=None;self.records=[];self.recognition_crops=[];self.enabled=False;self.context_refining=False
        self.mode=f'bounded_detector_{side}_orthographic_v1'

    def __enter__(self):
        if self.enabled:raise RuntimeError('OCR runtime already active')
        self.previous_reader,self.previous_read=text_reader._reader,text_reader.read_text
        self.had_previous_runtime=hasattr(text_reader,'_v2_bounded_ocr_runtime');self.previous_runtime=getattr(text_reader,'_v2_bounded_ocr_runtime',None)
        reader=RapidOCR(intra_op_num_threads=4,inter_op_num_threads=2)
        reader.text_det.get_preprocess=lambda max_wh:_MeasuredPreprocess(self.side,reader.text_det.mean,reader.text_det.std,self.records)
        self.reader=reader;self.wrapper=self._read_with_progress
        text_reader._reader=reader;text_reader.read_text=self.wrapper;text_reader._v2_bounded_ocr_runtime=self;self.enabled=True
        return self

    def _read_with_progress(self,image):
        rows=self._reread_map_title(image,normalize_evidence(self.previous_read(image)))
        rows=self._reread_map_context(image,rows)
        from english_context_evidence import reread_english_context
        rows=reread_english_context(self,image,rows)
        header=text_reader.map_header_from_evidence(rows)
        if header['displayedZone'] is not None or header['conflictingEvidence']:return rows
        remaining=[r for r in rows if ('剩餘時間' in r.get('text','') or re.fullmatch(r'Ends\s+in:\s*\d+D\s+\d{2}:\d{2}:\d{2}',r.get('text','').strip(),re.I)) and r.get('score',0)>=.85]
        if len(remaining)!=1:return rows
        points=np.asarray(remaining[0].get('box'),dtype=float)
        if points.shape!=(4,2) or not np.isfinite(points).all():return rows
        x,y=points.min(0);right,bottom=points.max(0);h=bottom-y
        if not 0<h<image.height*.1 or x<0 or right>image.width*.5 or y>image.height*.35:return rows
        left,top=max(0,int(x-h)),int(bottom+h*.5)
        endx,endy=min(image.width,int(right+h)),min(image.height,int(bottom+h*3))
        if endx<=left or endy<=top:return rows
        crop=image.crop((left,top,endx,endy));size=(crop.width*3,crop.height*3)
        local=normalize_evidence(self.previous_read(crop.resize(size,Image.Resampling.LANCZOS)))
        matches=[r for r in local if r.get('score',0)>=.9 and re.fullmatch(r'(?:[區区]域(?:10|[1-9])[進进]行中|Zone(?:10|[1-9])inProgress)',re.sub(r'\s+','',r.get('text','')),re.I)]
        if len(matches)!=1:return rows
        row=matches[0]
        augmented=[*rows,{**row,'box':[[round(px/3+left,2),round(py/3+top,2)] for px,py in row['box']],
            'source':'remaining_time_adjacent_progress_original_crop','cropBox':[left,top,endx-left,endy-top],'analysisSize':list(size)}]
        return self._reread_map_context(image,self._reread_map_title(image,augmented))

    def _reread_map_title(self,image,rows):
        # A partial OCR result only locates pixels; it never grants MAP state.
        partial=[r for r in rows if r.get('text','').strip() in ('冥界','冥界試') and .9<=r.get('score',0)<=1]
        full=[r for r in rows if r.get('text','').strip()=='冥界試煉' and r.get('score',0)>=.9]
        timer=[r for r in rows if '剩餘時間' in r.get('text','') and .9<=r.get('score',0)<=1]
        header=text_reader.map_header_from_evidence(rows)
        if full or len(partial)!=1 or len(timer)!=1 or header['displayedZone'] is None or header['conflictingEvidence']:return rows
        points=np.asarray(partial[0].get('box'),dtype=float);times=np.asarray(timer[0].get('box'),dtype=float)
        if points.shape!=(4,2) or times.shape!=(4,2) or not np.isfinite(points).all() or not np.isfinite(times).all():return rows
        x,y=points.min(0);right,bottom=points.max(0);h=bottom-y;tx,ty=times.min(0)
        if not 0<h<image.height*.1 or x<0 or right>image.width*.35 or y>image.height*.15 or not bottom<ty<image.height*.3 or not x-h<=tx<image.width*.35:return rows
        left,top=max(0,int(x-h*.1)),max(0,int(y-h*.1))
        endx,endy=min(image.width,int(right+h*.1)),min(image.height,int(bottom+h*.1))
        readings=self.read_line_variants(image.crop((left,top,endx,endy)),4)
        matches=[r for r in readings if r['text'] in ('冥界試','冥界試煉') and r['score']>=.9]
        matches=sorted(matches,key=lambda r:r['score'],reverse=True)[:1]
        if len(matches)!=1:return rows
        return [*rows,{**matches[0],'box':[[left,top],[endx,top],[endx,endy],[left,endy]],'source':'map_title_original_crop','cropBox':[left,top,endx-left,endy-top],'originalText':partial[0]['text'],'originalScore':partial[0]['score']}]

    def _reread_map_context(self,image,rows):
        if self.context_refining:return rows
        import flow_vision
        scene=flow_vision.semantic_state(rows)
        if scene['state'] not in ('MAP','UNKNOWN') or scene['state']=='MAP' and scene['confidence']>=.9:return rows
        season_candidates=[r for r in rows if re.fullmatch(r'冥界[試试](?:[煉炼])?季[1-9]\d?',r.get('text','').strip()) and .75<=r.get('score',0)<=1]
        # Original global boxes locate crops. A known V1 reread of that same
        # line is preserved as evidence, not counted as a second location.
        global_seasons=[r for r in season_candidates if not r.get('source')]
        seasons=global_seasons or season_candidates
        if len(global_seasons)==1:
            base=global_seasons[0];base_points=np.asarray(base.get('box'),dtype=float)
            if base_points.shape!=(4,2) or not np.isfinite(base_points).all():return rows
            low,high=base_points.min(0),base_points.max(0)
            number=re.search(r'季([1-9]\d?)$',base['text'].strip()).group(1)
            precise=[]
            for candidate in season_candidates:
                if candidate.get('source')!='bounded_map_title_crop_ocr' or candidate['score']<.9:continue
                points=np.asarray(candidate.get('box'),dtype=float)
                if points.shape!=(4,2) or not np.isfinite(points).all():continue
                if (points.min(0)<low).any() or (points.max(0)>high).any():continue
                if re.search(r'季([1-9]\d?)$',candidate['text'].strip()).group(1)!=number:return rows
                precise.append(candidate)
            if len(precise)==1:seasons=precise
            elif len(precise)>1:return rows
        # A missing global glyph is only a crop locator. The fresh crop below
        # must still read the complete original label and clock at >=.90.
        timers=_remaining_timer_locators(rows)
        header=text_reader.map_header_from_evidence(rows)
        if len(seasons)!=1 or len(timers)!=1 or header['displayedZone'] is None or header['score']<.9 or header['conflictingEvidence']:return rows
        geometry=self._map_context_geometry(image,[seasons[0],timers[0]])
        if geometry is None:
            if not any(r.get('source')=='bounded_map_title_crop_ocr' for r in season_candidates):
                context=[r for r in rows if r is seasons[0] or not re.search(r'冥界[試试]',r.get('text',''))]
                self.context_refining=True
                try:refined=text_reader.refine_map_title(image,context)
                finally:self.context_refining=False
                actual=[r for r in refined if r.get('source')=='bounded_map_title_crop_ocr']
                if len(actual)==1:return self._reread_map_context(image,[*rows,*actual])
            return self._remeasure_map_context(image,rows,[seasons[0],timers[0]])
        bounds,position_evidence=geometry
        fresh=[]
        for kind,row,(x,y,right,bottom,h) in zip(['season','timer'],[seasons[0],timers[0]],bounds):
            trim=(0 if row.get('source')=='bounded_map_title_crop_ocr' else .12*h) if kind=='season' else -.1*h
            left,top=max(0,int(x+trim)),max(0,int(y+trim))
            endx,endy=min(image.width,int(right-trim)),min(image.height,int(bottom-trim))
            if endx<=left or endy<=top:return rows
            pattern=r'冥界[試试](?:[煉炼])?季[1-9]\d?' if kind=='season' else r'剩餘時間\d+天\d{2}:\d{2}:\d{2}'
            crops=[(left,top,endx,endy)]
            if kind=='season':
                crops.append((left,max(0,int(y+h*.08)),min(image.width,int(right-h*.30)),min(image.height,int(bottom-h*.18))))
                crops.append((left,top,endx,min(image.height,int(bottom-h*.25))))
            matches=[]
            for crop_box in crops:
                if crop_box[2]<=crop_box[0] or crop_box[3]<=crop_box[1]:continue
                glyph_text=row['text']+row.get('adjacentClockLocator',{}).get('text','')
                readings=normalize_evidence(self.read_line_variants(image.crop(crop_box),len(re.sub(r'\s+','',glyph_text))))
                matches=[{**r,'actualCropBox':crop_box} for r in readings if r['score']>=.9 and re.fullmatch(pattern,re.sub(r'\s+','',r['text']))]
                if matches:break
            keys={_context_reading_key(kind,r['text']) for r in matches}
            if len(keys)>1:return rows
            if not keys:return self._remeasure_map_context(image,rows,[seasons[0],timers[0]],fresh)
            best=max(matches,key=lambda r:r['score']);left,top,endx,endy=best.pop('actualCropBox')
            if not _context_claim_agrees(kind,row,best):return rows
            fresh.append({**best,'box':[[left,top],[endx,top],[endx,endy],[left,endy]],'source':'map_context_original_crop','contextKind':kind,'cropBox':[left,top,endx-left,endy-top],'originalText':row['text'],'originalScore':row['score']})
            if 'adjacentClockLocator' in row:
                fresh[-1].update({key:row[key] for key in ['remainingLabelLocator','adjacentClockLocator']})
            if position_evidence:fresh[-1]['positionEvidence']=position_evidence
        return [*rows,*fresh]

    def _map_context_geometry(self,image,lines):
        bounds=[]
        for row in lines:
            points=np.asarray(row.get('box'),dtype=float)
            if points.shape!=(4,2) or not np.isfinite(points).all():return None
            x,y=points.min(0);right,bottom=points.max(0);h=bottom-y
            if not 0<h<image.height*.1 or x<0 or right>image.width*.5 or y>image.height*.3:return None
            bounds.append((x,y,right,bottom,h))
        a,b=bounds
        # Detector quadrilateral padding may touch or slightly overlap even
        # though the two original text baselines are clearly separate.
        minimum_height=min(a[4],b[4])
        separation=(b[1]+b[3]-a[1]-a[3])/2
        horizontal_limit=max(a[4],b[4]);position_evidence=None
        if abs(a[0]-b[0])>horizontal_limit:
            from map_aspect import estimate_pixel_aspect
            calibration=estimate_pixel_aspect(image)
            if calibration is not None and calibration['ratio']>1:
                horizontal_limit*=calibration['ratio']
                position_evidence={'method':'same_frame_pixel_aspect_horizontal_indent',
                    'pixelAspect':calibration['ratio'],'pixelSha256':calibration['pixelSha256'],
                    'sourceSize':calibration['sourceSize'],'calibrationMethod':calibration['method']}
        if separation<minimum_height*.75 or a[3]-b[1]>minimum_height*.15 or abs(a[0]-b[0])>horizontal_limit:
            return None
        return bounds,position_evidence

    def _remeasure_map_context(self,image,rows,locators,fresh_prefix=()):
        # Old rows locate pixels only. Remeasure each line independently with
        # the existing detector, then read that original crop at unchanged .90.
        measured=[];proofs=[]
        for kind,locator in zip(['season','timer'],locators):
            prior=next((r for r in fresh_prefix if r['contextKind']==kind),None)
            if prior is not None:
                measured.append(prior);proofs.append(None);continue
            points=np.asarray(locator.get('box'),dtype=float)
            if points.shape!=(4,2) or not np.isfinite(points).all():return rows
            lo,hi=points.min(0),points.max(0);h=hi[1]-lo[1]
            if not (0<h<image.height*.1 and 0<=lo[0]<hi[0]<=image.width*.5 and 0<=lo[1]<hi[1]<=image.height and lo[1]<=image.height*.3):return rows
            pad=h/2
            outer=(max(0,int(lo[0]-pad)),max(0,int(lo[1]-pad)),min(image.width,int(hi[0]+pad)),min(image.height,int(hi[1]+pad)))
            local=normalize_evidence(self.previous_read(image.crop(outer)));contained=[]
            for candidate in local:
                q=np.asarray(candidate.get('box'),dtype=float)
                if q.shape!=(4,2) or not np.isfinite(q).all():continue
                q=q+np.array(outer[:2]);a,b=q.min(0),q.max(0)
                if (b<=a).any() or (a<lo).any() or (b>hi).any():continue
                crop=(math.ceil(a[0]),math.ceil(a[1]),math.floor(b[0]),math.floor(b[1]))
                if crop[2]>crop[0] and crop[3]>crop[1]:contained.append((candidate,q,crop))
            if len(contained)!=1:return rows
            candidate,q,crop=contained[0];left,top,endx,endy=crop
            measured.append({**locator,'box':[[left,top],[endx,top],[endx,endy],[left,endy]]})
            proofs.append({'method':'same_frame_contained_detector_line_and_fresh_recognition','locator':locator,
                'detectorCropBox':[outer[0],outer[1],outer[2]-outer[0],outer[3]-outer[1]],
                'detectorReading':candidate,'sourceDetectorQuad':q.tolist(),'recognitionCropBox':[left,top,endx-left,endy-top]})
        # Line envelopes establish context alignment; contained detector boxes
        # establish the pixels read. Preserve already-valid envelopes rather
        # than replacing both with narrower glyph bounds unnecessarily.
        envelopes=locators
        geometry=self._map_context_geometry(image,envelopes)
        if geometry is None:
            for candidate_pair in [[measured[0],locators[1]],[locators[0],measured[1]],measured]:
                geometry=self._map_context_geometry(image,candidate_pair)
                if geometry is not None:
                    envelopes=candidate_pair;break
        if geometry is None:return rows
        _,position_evidence=geometry
        pixel_sha=hashlib.sha256(image.tobytes()).hexdigest()
        fresh=[]
        for kind,locator,row,envelope,proof in zip(['season','timer'],locators,measured,envelopes,proofs):
            if proof is None:
                if not _context_claim_agrees(kind,locator,row):return rows
                fresh.append(row);continue
            left,top=row['box'][0];endx,endy=row['box'][2]
            pattern=r'冥界[試试](?:[煉炼])?季[1-9]\d?' if kind=='season' else r'剩餘時間\d+天\d{2}:\d{2}:\d{2}'
            glyph_text=locator['text']+locator.get('adjacentClockLocator',{}).get('text','')
            count=len(re.sub(r'\s+','',glyph_text))
            if not 1<=count<=20:return rows
            readings=normalize_evidence(self.read_line_variants(image.crop((left,top,endx,endy)),count))
            matches=[r for r in readings if r['score']>=.9 and re.fullmatch(pattern,re.sub(r'\s+','',r['text']))]
            if len({_context_reading_key(kind,r['text']) for r in matches})!=1:return rows
            best=max(matches,key=lambda r:r['score'])
            if not _context_claim_agrees(kind,locator,best):return rows
            fresh.append({**best,'box':row['box'],'source':'map_context_original_crop','contextKind':kind,
                'cropBox':[left,top,endx-left,endy-top],'originalText':locator['text'],'originalScore':locator['score'],
                'originalPixelRefinement':{**proof,'sourcePixelSha256':pixel_sha,'refinedReading':best,
                    'contextGeometryEnvelopes':[e['box'] for e in envelopes],'geometryEnvelopeBox':envelope['box']}})
            if 'adjacentClockLocator' in locator:fresh[-1].update({key:locator[key] for key in ['remainingLabelLocator','adjacentClockLocator']})
            if position_evidence:fresh[-1]['positionEvidence']=position_evidence
        return [*rows,*fresh]

    def take_metadata(self):
        records,self.records=self.records,[]
        crops,self.recognition_crops=self.recognition_crops,[]
        return {'mode':self.mode,'maximumTensorSide':self.side,'thresholdsChanged':False,'detectorCalls':records,'recognitionCrops':crops}

    def read_line_variants(self,crop,glyph_count):
        if not self.enabled or type(glyph_count) is not int or not 1<=glyph_count<=20:raise ValueError('active runtime and observed glyph count required')
        sizes=[(max(24,round(glyph_count*40*ratio)),40) for ratio in [.8,.95,1.1]]
        images=[np.asarray(crop.convert('RGB').resize(size,Image.Resampling.LANCZOS))[:,:,::-1].copy() for size in sizes]
        readings,elapsed=self.reader.text_rec(images);best={};variants=[]
        for size,(text,score) in zip(sizes,readings):
            score=float(score);variants.append({'analysisSize':list(size),'text':text,'score':score})
            if text not in best or score>best[text]['score']:best[text]={'text':text,'score':score,'analysisSize':list(size)}
        self.recognition_crops.append({'inputSize':list(crop.size),'observedGlyphCount':glyph_count,'variants':variants,'elapsedMs':float(elapsed)*1000})
        return list(best.values())

    def close(self):
        if self.enabled:
            if text_reader._reader is self.reader:text_reader._reader=self.previous_reader
            if text_reader.read_text is self.wrapper:text_reader.read_text=self.previous_read
            if getattr(text_reader,'_v2_bounded_ocr_runtime',None) is self:
                if self.had_previous_runtime:text_reader._v2_bounded_ocr_runtime=self.previous_runtime
                else:delattr(text_reader,'_v2_bounded_ocr_runtime')
            self.enabled=False

    def __exit__(self,*args):self.close()
