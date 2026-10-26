"""Exact raw candidate reuse inside one frame; never caches authority or OCR.

Classification, lattice assignment, connecting pixels and proof verification
still run normally. Template changes fail closed instead of using stale kernels.
"""
import copy
import hashlib
import json
import re
import sys
import threading
import time

_scope_lock=threading.Lock()
_scope_thread=None
_process_assets={}


class FrameIntermediates:
    def __init__(self,source_id,source_sha256,source_size,owner=None):
        if (re.fullmatch(r'[a-f0-9]{32}',source_id or '') is None
                or re.fullmatch(r'[a-f0-9]{64}',source_sha256 or '') is None
                or len(source_size)!=2 or any(type(x) is not int or x<=0 for x in source_size)):
            raise ValueError('FRAME_CONTEXT_SOURCE_INVALID')
        self.source_id=source_id;self.source_sha256=source_sha256;self.source_size=list(source_size)
        self.owner=owner;self._cache={};self._assets={};self._calls=[]

    def __enter__(self):
        global _scope_thread
        if not _scope_lock.acquire(False):
            raise RuntimeError('FRAME_CONTEXT_NESTED' if _scope_thread==threading.get_ident() else 'FRAME_CONTEXT_CONCURRENT')
        _scope_thread=threading.get_ident()
        try:
            if self.owner is None:
                import map_vision
                self.owner=map_vision
            self.original=self.owner.node_candidates
            self.owner.node_candidates=self._candidates
        except BaseException:
            _scope_thread=None;_scope_lock.release();raise
        return self

    def __exit__(self,*exc):
        global _scope_thread
        self.owner.node_candidates=self.original;self._cache.clear();self._assets.clear()
        _scope_thread=None;_scope_lock.release()

    def _identity(self,image,folder,args,kwargs):
        from pathlib import Path
        import cv2
        root=Path(folder).resolve();files=sorted(root.glob('node-*.png'))
        metadata=root/'template-metadata.json'
        if metadata.exists():files.append(metadata)
        assets=tuple((p.name,hashlib.sha256(p.read_bytes()).hexdigest()) for p in files)
        if root in _process_assets and _process_assets[root]!=assets:raise ValueError('FRAME_ASSETS_CHANGED')
        _process_assets[root]=assets;self._assets[root]=assets
        fast=sys.modules.get('fast_map_candidates')
        backend=(id(self.original),id(getattr(fast,'_match_group',None)),id(getattr(fast,'_groups',None)),
            id(cv2.matchTemplate),id(cv2.Canny),id(cv2.resize),cv2.__version__,
            cv2.useOptimized(),cv2.getNumThreads(),
            id(getattr(self.owner,'map_templates',None)),id(getattr(self.owner,'binary_ring_correlation',None)))
        # Unsupported mutable parameters are computed, never cached.
        try:parameters=json.dumps([args,kwargs],sort_keys=True,allow_nan=False)
        except (TypeError,ValueError):return None
        return (self.source_id,self.source_sha256,tuple(self.source_size),tuple(image.size),image.mode,
            hashlib.sha256(image.convert('RGB').tobytes()).hexdigest(),str(root),assets,backend,parameters)

    def _candidates(self,image,folder,*args,**kwargs):
        started=time.perf_counter();key=self._identity(image,folder,args,kwargs)
        identity_ms=(time.perf_counter()-started)*1000
        hit=key is not None and key in self._cache;backend_ms=0;copy_started=time.perf_counter()
        if hit:result=copy.deepcopy(self._cache[key])
        else:
            compute_started=time.perf_counter();result=self.original(image,folder,*args,**kwargs)
            backend_ms=(time.perf_counter()-compute_started)*1000
            # The preserved fast backend sets OpenCV threads to one on entry.
            # Bind storage to the settings actually used, not pre-entry defaults.
            key=self._identity(image,folder,args,kwargs) if key is not None else None
            identity_ms+=(time.perf_counter()-compute_started)*1000-backend_ms
            copy_started=time.perf_counter()
            if key is not None and len(self._cache)<8:self._cache[key]=copy.deepcopy(result)
        self._calls.append({'hit':hit,'identityMs':identity_ms,'backendMs':backend_ms,
            'copyMs':(time.perf_counter()-copy_started)*1000,'elapsedMs':(time.perf_counter()-started)*1000,
            'inputSize':list(image.size)})
        return result

    def summary(self):
        return {'method':'same_frame_exact_raw_candidate_inputs','sourceCaptureFrameId':self.source_id,
            'sourceImageSha256':self.source_sha256,'sourceSize':self.source_size,'crossFrameReuse':False,
            'authorityCached':False,'hits':sum(c['hit'] for c in self._calls),
            'misses':sum(not c['hit'] for c in self._calls),'calls':copy.deepcopy(self._calls)}
