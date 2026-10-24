"""Scoped extension for the real tenth area; retain existing claim conflicts."""
import re
import text_reader

_original_parser=text_reader.map_header_from_evidence


def parse_progress(evidence):
    original=_original_parser(evidence)
    if original['conflictingEvidence']:return original
    claims=[]
    for row in evidence:
        if row.get('score',0)<.78:continue
        text=re.sub(r'\s+','',row.get('text','')).replace('区','區').replace('层','層')
        floor=re.search(r'(?<!\d)10區域第(\d{1,2})(?:層|\D{0,2}[進进]行中)',text)
        if floor and 1<=int(floor[1])<=31:claims.append((10,int(floor[1]),False,float(row['score'])))
        elif re.search(r'(?<!\d)10區域完成',text):claims.append((10,None,True,float(row['score'])))
        elif re.search(r'區域10[進进]行中',text):claims.append((10,None,False,float(row['score'])))
    if not claims:return original
    if original['displayedZone'] is not None:
        claims.append((original['displayedZone'],original['lastEnteredFloor'],original['displayedAreaComplete'],original['score']))
    if len({c[:3] for c in claims})!=1:
        return {**original,'displayedZone':None,'lastEnteredFloor':None,'displayedAreaComplete':False,'score':0,'conflictingEvidence':True}
    zone,floor,completed,score=max(claims,key=lambda c:c[3])
    return {**original,'displayedZone':zone,'lastEnteredFloor':floor,'displayedAreaComplete':completed,'score':round(score,4),'progressParser':'v2_zone10_full_phrase_extension'}


class ProgressRuntime:
    def __init__(self):self.enabled=False
    def __enter__(self):
        if self.enabled:raise RuntimeError('progress runtime already active')
        self.previous=text_reader.map_header_from_evidence
        text_reader.map_header_from_evidence=parse_progress;self.enabled=True
        return self
    def close(self):
        if self.enabled:
            if text_reader.map_header_from_evidence is parse_progress:text_reader.map_header_from_evidence=self.previous
            self.enabled=False
    def __exit__(self,*args):self.close()
