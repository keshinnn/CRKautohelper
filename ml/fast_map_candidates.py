"""Original V1 search with incremental nominal quantization supplements.

Default M1 scans nominal floor/ceil sizes only below four base candidates.
Explicit V2 coverage then scans the bounded one-pixel band, retaining the
entire M1 result. Both reuse one Canny image; supplements never rescan an
earlier stage's (template,size) pair.
The hook is local to an offline V2 process; no V1 files are edited.
"""
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from pathlib import Path
import copy,json,math
import cv2
import numpy as np

@lru_cache(maxsize=8)
def _groups(folder,height,width):
    from map_vision import map_templates
    folder=Path(folder);meta=folder/'template-metadata.json'
    metadata=json.loads(meta.read_text(encoding='utf-8')) if meta.exists() else {}
    groups={};order=0
    for name,t,ring,_,_ in map_templates(folder):
        h,w=t.shape;path=Path(name+'.png');reference_height=metadata.get(path.name,{}).get('frame_height',720 if path.stem.startswith('node-b-') else 540);base=height/reference_height
        for scale in sorted({round(base*f,4) for f in [.8,.9,1.,1.1,1.2]}|{.75,.9,1.,1.1,1.25,1.3333,1.5}):
            tw,th=round(w*scale),round(h*scale)
            if tw>=width or th>=height:continue
            temp=cv2.resize(t,(tw,th),interpolation=cv2.INTER_NEAREST);mask=cv2.resize(ring,(tw,th),interpolation=cv2.INTER_NEAREST)
            key=(mask.shape,mask.tobytes())
            if key not in groups:groups[key]=[mask,[]]
            temp.flags.writeable=False
            norm=float(np.sqrt(np.square(temp.astype('float32')).sum()))
            groups[key][1].append((order,path.name,temp,norm));order+=1
    return tuple(groups.values())

def _supplement_groups(folder,height,width,padding,omit_nominal=False):
    from map_vision import map_templates
    folder=Path(folder);meta=folder/'template-metadata.json'
    metadata=json.loads(meta.read_text(encoding='utf-8')) if meta.exists() else {}
    base=[k for _,kernels in _groups(str(folder),height,width) for k in kernels]
    seen={(name,tuple(temp.shape[::-1])) for _,name,temp,_ in base}
    groups={};order=max((k[0] for k in base),default=-1)+1
    if omit_nominal:
        nominal=_nominal_groups(str(folder),height,width)
        seen.update((name,tuple(temp.shape[::-1])) for _,kernels in nominal for _,name,temp,_ in kernels)
        order+=sum(len(kernels) for _,kernels in nominal)
    for name,t,ring,_,_ in map_templates(folder):
        h,w=t.shape;path=Path(name+'.png')
        reference_height=metadata.get(path.name,{}).get('frame_height',720 if path.stem.startswith('node-b-') else 540)
        scale=round(height/reference_height,4)
        for tw in range(max(1,math.floor(w*scale)-padding),math.ceil(w*scale)+padding+1):
            for th in range(max(1,math.floor(h*scale)-padding),math.ceil(h*scale)+padding+1):
                key=(path.name,(tw,th))
                if key in seen or min(tw,th)<=0 or tw>=width or th>=height:continue
                seen.add(key)
                temp=cv2.resize(t,(tw,th),interpolation=cv2.INTER_NEAREST)
                mask=cv2.resize(ring,(tw,th),interpolation=cv2.INTER_NEAREST)
                mask_key=(mask.shape,mask.tobytes())
                if mask_key not in groups:groups[mask_key]=[mask,[]]
                temp.flags.writeable=False
                norm=float(np.sqrt(np.square(temp.astype('float32')).sum()))
                groups[mask_key][1].append((order,path.name,temp,norm));order+=1
    return tuple(groups.values())


@lru_cache(maxsize=8)
def _nominal_groups(folder,height,width):
    return _supplement_groups(folder,height,width,0)


@lru_cache(maxsize=8)
def _coverage_groups(folder,height,width,omit_nominal=False):
    return _supplement_groups(folder,height,width,1,omit_nominal)

def _match_group(edges,group):
    mask,kernels=group
    energy=cv2.matchTemplate(edges,(mask>0).astype('uint8'),cv2.TM_CCORR)*255
    inverse=np.zeros_like(energy);np.sqrt(np.maximum(energy,0),out=inverse)
    np.divide(1,inverse,out=inverse,where=energy>255**2/2);inverse[energy<=255**2/2]=0
    matches=[]
    for order,name,temp,norm in kernels:
        numerator=cv2.matchTemplate(edges,temp,cv2.TM_CCORR)
        res=numerator*inverse/norm if norm>0 else np.zeros_like(numerator)
        th,tw=temp.shape
        for peak in range(50):
            _,score,_,(x,y)=cv2.minMaxLoc(res)
            if score<.48:break
            matches.append((order,peak,{'box':[x,y,tw,th],'center':[x+tw/2,y+th/2],'score':float(score),'template':name}))
            res[max(0,y-th//2):y+th//2+1,max(0,x-tw//2):x+tw//2+1]=0
    return matches

class _CandidateScan:
    """One exact model raster; lazy raw stages return independent copies."""
    def __init__(self,image,templates,workers=4):
        if workers not in [1,2,4]:raise ValueError('bounded worker count required')
        if cv2.getNumThreads()!=1:cv2.setNumThreads(1)
        self.workers=workers
        a=np.array(image.convert('RGB'));gray=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY)
        self.edges=cv2.Canny(gray,70,150)
        self.folder=str(Path(templates).resolve());self.height,self.width=gray.shape
        self.kept=[]
        self._append(self._scan(_groups(self.folder,self.height,self.width)))
        self.low_count=len(self.kept)<4
        self._m1=None;self._coverage=None

    def _scan(self,groups):
        if self.workers==1:parts=[_match_group(self.edges,g) for g in groups]
        else:
            with ThreadPoolExecutor(max_workers=self.workers) as pool:
                parts=list(pool.map(lambda g:_match_group(self.edges,g),groups))
        return [item for part in parts for item in part]

    def _append(self,matches):
        matches.sort(key=lambda item:(-item[2]['score'],item[0],item[1]))
        for _,_,m in matches:
            r=min(m['box'][2:])/2
            if any(math.dist(m['center'],k['center'])<max(r,min(k['box'][2:])/2) for k in self.kept):continue
            self.kept.append(m)

    def candidates(self,coverage=False):
        if type(coverage) is not bool:raise ValueError('boolean coverage mode required')
        if self._m1 is None:
            if self.low_count:self._append(self._scan(_nominal_groups(self.folder,self.height,self.width)))
            self._m1=copy.deepcopy(self.kept)
        if not coverage:return copy.deepcopy(self._m1)
        if self._coverage is None:
            self._append(self._scan(_coverage_groups(self.folder,self.height,self.width,omit_nominal=self.low_count)))
            self._coverage=copy.deepcopy(self.kept)
        return copy.deepcopy(self._coverage)


def node_candidates(image,templates,workers=4,*,coverage=False):
    if type(coverage) is not bool:raise ValueError('boolean coverage mode required')
    return _CandidateScan(image,templates,workers).candidates(coverage)

def coverage_node_candidates(image,templates,workers=4):
    """Bounded V2 coverage; candidates still carry no selection authority."""
    return node_candidates(image,templates,workers,coverage=True)
