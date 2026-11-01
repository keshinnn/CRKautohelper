"""Exact raw candidate reuse inside one frame; never caches authority or OCR.

Classification, lattice assignment, connecting pixels and proof verification
still run normally. Template changes fail closed instead of using stale kernels.
"""
from contextlib import contextmanager
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
    def __init__(self,source_id,source_sha256,source_size,owner=None,enabled=True):
        if (re.fullmatch(r'[a-f0-9]{32}',source_id or '') is None
                or re.fullmatch(r'[a-f0-9]{64}',source_sha256 or '') is None
                or len(source_size)!=2 or any(type(x) is not int or x<=0 for x in source_size)):
            raise ValueError('FRAME_CONTEXT_SOURCE_INVALID')
        if type(enabled) is not bool:raise ValueError('FRAME_CONTEXT_POLICY_INVALID')
        self.enabled=enabled
        self.source_id=source_id;self.source_sha256=source_sha256;self.source_size=list(source_size)
        self.owner=owner;self._cache={};self._scans={};self._assets={};self._calls=[];self._active=False

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
            self._active=True
            if self.enabled:self.owner.node_candidates=self._candidates
        except BaseException:
            _scope_thread=None;_scope_lock.release();raise
        return self

    def __exit__(self,*exc):
        global _scope_thread
        if self.enabled:self.owner.node_candidates=self.original
        self._active=False
        self._cache.clear();self._scans.clear();self._assets.clear()
        _scope_thread=None;_scope_lock.release()

    @contextmanager
    def backend(self,backend):
        """Select a raw backend only inside this owned frame, then restore it."""
        if not self._active or _scope_thread!=threading.get_ident():
            raise RuntimeError('FRAME_CONTEXT_NOT_ACTIVE')
        if not callable(backend):raise ValueError('FRAME_BACKEND_INVALID')
        previous=self.original
        self.original=backend
        if not self.enabled:self.owner.node_candidates=backend
        try:
            yield
        finally:
            self.original=previous
            if not self.enabled:self.owner.node_candidates=previous

    def _identity(self,image,folder,args,kwargs,*,scan=False):
        from pathlib import Path
        import cv2
        root=Path(folder).resolve();files=sorted(root.glob('node-*.png'))
        metadata=root/'template-metadata.json'
        if metadata.exists():files.append(metadata)
        assets=tuple((p.name,hashlib.sha256(p.read_bytes()).hexdigest()) for p in files)
        if root in _process_assets and _process_assets[root]!=assets:raise ValueError('FRAME_ASSETS_CHANGED')
        _process_assets[root]=assets;self._assets[root]=assets
        fast=sys.modules.get('fast_map_candidates')
        backend=(id(getattr(fast,'_CandidateScan',None)) if scan else id(self.original),
            id(getattr(fast,'_CandidateScan',None)),id(getattr(fast,'_match_group',None)),id(getattr(fast,'_groups',None)),
            id(getattr(fast,'_nominal_groups',None)),id(getattr(fast,'_coverage_groups',None)),
            id(getattr(fast,'_supplement_groups',None)),
            id(cv2.matchTemplate),id(cv2.Canny),id(cv2.resize),cv2.__version__,
            cv2.useOptimized(),cv2.getNumThreads(),
            id(getattr(self.owner,'map_templates',None)),id(getattr(self.owner,'binary_ring_correlation',None)))
        # Unsupported mutable parameters are computed, never cached.
        try:parameters=json.dumps([args,kwargs],sort_keys=True,allow_nan=False)
        except (TypeError,ValueError):return None
        return (self.source_id,self.source_sha256,tuple(self.source_size),tuple(image.size),image.mode,
            hashlib.sha256(image.convert('RGB').tobytes()).hexdigest(),str(root),assets,backend,parameters)

    def _candidates(self,image,folder,*args,**kwargs):
        started=time.perf_counter()
        fast=sys.modules.get('fast_map_candidates')
        shared=fast is not None and not args and not kwargs and self.original in (
            getattr(fast,'node_candidates',None),getattr(fast,'coverage_node_candidates',None))
        if shared:
            import cv2
            if cv2.getNumThreads()!=1:cv2.setNumThreads(1)
        key=self._identity(image,folder,args,kwargs)
        identity_ms=(time.perf_counter()-started)*1000
        hit=key is not None and key in self._cache;backend_ms=0;copy_started=time.perf_counter()
        scan_reused=False
        if hit:result=copy.deepcopy(self._cache[key])
        else:
            compute_started=time.perf_counter()
            if shared:
                scan_key=self._identity(image,folder,args,kwargs,scan=True)
                scan=self._scans.get(scan_key) if scan_key is not None else None
                scan_reused=scan is not None
                if scan is None:
                    scan=fast._CandidateScan(image,folder)
                    if scan_key is not None and len(self._scans)<8:self._scans[scan_key]=scan
                result=scan.candidates(coverage=self.original is fast.coverage_node_candidates)
            else:
                result=self.original(image,folder,*args,**kwargs)
            backend_ms=(time.perf_counter()-compute_started)*1000
            key=self._identity(image,folder,args,kwargs) if key is not None else None
            identity_ms+=(time.perf_counter()-compute_started)*1000-backend_ms
            copy_started=time.perf_counter()
            if key is not None and len(self._cache)<8:self._cache[key]=copy.deepcopy(result)
        self._calls.append({'hit':hit,'identityMs':identity_ms,'backendMs':backend_ms,
            'copyMs':(time.perf_counter()-copy_started)*1000,'elapsedMs':(time.perf_counter()-started)*1000,
            'inputSize':list(image.size),'rawScanReused':scan_reused})
        return result

    def summary(self):
        return {'enabled':self.enabled,'method':'same_frame_exact_raw_candidate_inputs','sourceCaptureFrameId':self.source_id,
            'sourceImageSha256':self.source_sha256,'sourceSize':self.source_size,'crossFrameReuse':False,
            'authorityCached':False,'hits':sum(c['hit'] for c in self._calls),
            'misses':sum(not c['hit'] for c in self._calls),'calls':copy.deepcopy(self._calls)}
