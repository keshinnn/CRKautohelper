"""Opt-in process-local diagnostics, including calls made by OpenCV workers.

Elapsed operation totals are inclusive and may overlap across threads. They are
not additive wall time and must never be used as the acceptance benchmark.
"""
import functools
import threading
import time


class OperationProfile:
    def __init__(self):
        self._lock=threading.Lock();self._restore=[];self._pending=[];self._rows=[]
        self.frame=0;self.main_thread=threading.get_ident()

    def __enter__(self):return self

    def __exit__(self,*exc):
        self.finish_stage('unattributed')
        for owner,name,original in reversed(self._restore):setattr(owner,name,original)
        self._restore.clear()

    def begin_frame(self):
        self.finish_stage('startup' if self.frame==0 else 'unattributed')
        self.frame+=1

    @staticmethod
    def _shapes(args):
        shapes=[]
        for arg in args[:3]:
            shape=getattr(arg,'shape',None)
            if shape is None:shape=getattr(arg,'size',None)
            if isinstance(shape,(tuple,list)) and all(isinstance(x,int) for x in shape):shapes.append(list(shape))
        return shapes

    def hook(self,owner,name,label=None):
        original=getattr(owner,name);label=label or name
        @functools.wraps(original)
        def measured(*args,**kwargs):
            shapes=self._shapes(args);frame=self.frame;thread=threading.get_ident()
            failed=False;started=time.perf_counter()
            try:return original(*args,**kwargs)
            except BaseException:
                failed=True;raise
            finally:
                elapsed=(time.perf_counter()-started)*1000
                with self._lock:self._pending.append((frame,label,shapes,thread,elapsed,failed))
        self._restore.append((owner,name,original));setattr(owner,name,measured)
        return measured

    def finish_stage(self,name):
        with self._lock:
            pending,self._pending=self._pending,[]
        for frame,label,shapes,thread,elapsed,failed in pending:
            self._rows.append({'frame':frame,'stage':name,'operation':label,'inputShapes':shapes,
                'thread':thread,'elapsedMs':elapsed,'failed':failed})

    def summary(self):
        groups={}
        for row in self._rows:
            key=(row['frame'],row['stage'],row['operation'],str(row['inputShapes']))
            if key not in groups:groups[key]={k:row[k] for k in ['frame','stage','operation','inputShapes']}
            g=groups[key];g['calls']=g.get('calls',0)+1;g['elapsedMs']=g.get('elapsedMs',0)+row['elapsedMs']
            g['maxMs']=max(g.get('maxMs',0),row['elapsedMs']);g['failures']=g.get('failures',0)+int(row['failed'])
            g['mainThreadCalls']=g.get('mainThreadCalls',0)+int(row['thread']==self.main_thread)
            g.setdefault('threads',set()).add(row['thread'])
        rows=[]
        for g in groups.values():g['threadCount']=len(g.pop('threads'));rows.append(g)
        return {'diagnosticOnly':True,'acceptanceTiming':False,'frames':self.frame,
            'method':'inclusive per-operation durations, overlapping worker calls are not additive wall time',
            'operations':rows}
