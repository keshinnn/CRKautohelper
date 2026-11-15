"""Research-only wait-context admission; never changes production packets."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'ml'))
import analyze_cases
original=analyze_cases.effective_observation_state
def state(packet):
    value=original(packet)
    rows=packet.get('evidence',[])
    import re
    loading=[r for r in rows if r.get('score',0)>=.9 and re.sub(r'[.。…]+$','',r.get('text','').replace(' ','').replace('读','讀'))=='讀取中']
    if value=='UNKNOWN' and len(loading)==1:
        return 'RESEARCH_LOADING_WAIT_ONLY'
    return value
analyze_cases.effective_observation_state=state
analyze_cases.main()
