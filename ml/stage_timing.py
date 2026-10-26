"""Actual monotonic module intervals; no changes to replay clocks or TTLs."""
import time


class StageTiming:
    def __init__(self,clock=time.perf_counter):
        self.clock=clock;self.last=clock();self.module_ms={}

    def mark(self,name):
        if name in self.module_ms:raise ValueError('duplicate timing stage')
        now=self.clock();self.module_ms[name]=(now-self.last)*1000;self.last=now
