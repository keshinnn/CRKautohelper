"""Research typed availability feeding the unchanged current-position builder."""
import json,hashlib,sys
from pathlib import Path
import cv2,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'ml'))
from current_position_evidence import inspect_in_progress
m=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'));records=[]
for f in m['cases'][0]['frames']:
    raw=Path(f['image']).read_bytes();assert hashlib.sha256(raw).hexdigest()==f['sha256']
    p=json.loads(Path(f['packet']).read_text(encoding='utf-8'))
    with Image.open(f['image']) as im: rgb=np.array(im.convert('RGB'))
    assert hashlib.sha256(rgb.tobytes()).hexdigest()==p['binding']['pixelSha256']
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV);actions={};coverage={}
    for n in p['mapReview']['nodes']:
        x,y,w,h=n['box'];q=hsv[int(np.ceil(y+h*12/58)):int(np.ceil(y+h*46/58)),int(np.ceil(x+w*12/58)):int(np.ceil(x+w*46/58))]
        pink=float(((q[:,:,0]>150)&(q[:,:,0]<180)&(q[:,:,1]>130)&(q[:,:,2]>130)).mean()) if q.size else 0
        coverage[n['id']]=pink
        actions[n['id']]={'available':n['type']=='battle' and pink>=.2 and not n.get('completed'), 'completed':n.get('completed',False)}
    records.append(dict(frameIndex=f['frameIndex'],imageSha256=f['sha256'],pixelSha256=p['binding']['pixelSha256'],
        current=inspect_in_progress(rgb,p,actions),pinkCoverage=coverage,
        method='typed_pink_availability_plus_unchanged_current_position_builder',formalAuthority=False))
Path(sys.argv[2]).write_text(json.dumps(records,indent=2),encoding='utf-8')
