"""V2-scoped English map context from actual independent full OCR labels."""
import re
import flow_vision
from progress_evidence import parse_progress

_original_semantic=flow_vision.semantic_state


def semantic_state(evidence):
    original=_original_semantic(evidence)
    if original['state'] not in ('UNKNOWN','MAP') or original['state']=='MAP' and original['confidence']>=.9:return original
    fresh=[r for r in evidence if r.get('source')=='map_context_original_crop' and .9<=r.get('score',0)<=1]
    season=[r for r in fresh if r.get('contextKind')=='season' and re.fullmatch(r'冥界[試试](?:[煉炼])?季[1-9]\d?',r.get('text','').strip())]
    remaining=[r for r in fresh if r.get('contextKind')=='timer' and re.fullmatch(r'剩餘時間\d+天\d{2}:\d{2}:\d{2}',re.sub(r'\s+','',r.get('text','')))]
    progress=parse_progress(evidence)
    if len(season)==1 and len(remaining)==1 and progress['displayedZone'] is not None and progress['score']>=.9 and not progress['conflictingEvidence']:
        return {**original,'state':'MAP','confidence':min(season[0]['score'],remaining[0]['score'],progress['score']),'method':'v2_original_season_time_zone_context','evidence':evidence}
    if original['state']!='UNKNOWN':return original
    rows=[r for r in evidence if .9<=r.get('score',0)<=1]
    title=[r for r in rows if r.get('text','').strip().casefold()=='trials of the nether realm']
    timer=[r for r in rows if re.fullmatch(r'Ends\s+in:\s*\d+D\s+\d{2}:\d{2}:\d{2}',r.get('text','').strip(),re.I)]
    zone=[r for r in rows if re.fullmatch(r'Zone\s*(?:10|[1-9])\s*in\s*Progress',r.get('text','').strip(),re.I)]
    progress=parse_progress(evidence)
    if len(title)!=1 or len(timer)!=1 or len(zone)!=1 or progress['conflictingEvidence'] or progress['displayedZone'] is None:return original
    return {**original,'state':'MAP','confidence':min(r['score'] for r in [title[0],timer[0],zone[0]]),'method':'v2_english_full_label_context','evidence':evidence}


class EnglishSceneRuntime:
    def __init__(self):self.enabled=False
    def __enter__(self):
        if self.enabled:raise RuntimeError('English scene runtime already active')
        self.previous=flow_vision.semantic_state
        flow_vision.semantic_state=semantic_state;self.enabled=True
        return self
    def close(self):
        if self.enabled:
            if flow_vision.semantic_state is semantic_state:flow_vision.semantic_state=self.previous
            self.enabled=False
    def __exit__(self,*args):self.close()
