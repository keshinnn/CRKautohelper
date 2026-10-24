"""Opt-in V2 OCR preprocessing. Existing assets, refiners and scores unchanged."""
import re
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
        self.side=side;self.reader=None;self.records=[];self.recognition_crops=[];self.enabled=False
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
        rows=normalize_evidence(self.previous_read(image))
        header=text_reader.map_header_from_evidence(rows)
        if header['displayedZone'] is not None or header['conflictingEvidence']:return rows
        remaining=[r for r in rows if '剩餘時間' in r.get('text','') and r.get('score',0)>=.85]
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
        matches=[r for r in local if r.get('score',0)>=.9 and re.fullmatch(r'[區区]域(?:10|[1-9])[進进]行中',re.sub(r'\s+','',r.get('text','')))]
        if len(matches)!=1:return rows
        row=matches[0]
        return [*rows,{**row,'box':[[round(px/3+left,2),round(py/3+top,2)] for px,py in row['box']],
            'source':'remaining_time_adjacent_progress_original_crop','cropBox':[left,top,endx-left,endy-top],'analysisSize':list(size)}]

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
