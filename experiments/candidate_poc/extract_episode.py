"""Extract one continuous native lossless episode and verify every decoded frame."""
import cv2, hashlib, json, sys
from pathlib import Path

video, folder, start, stop = sys.argv[1:]
start, stop = int(start), int(stop)
out = Path(folder); out.mkdir(exist_ok=False)
cap = cv2.VideoCapture(video)
fps = cap.get(cv2.CAP_PROP_FPS)
w,h = int(cap.get(3)),int(cap.get(4))
assert fps == 30 and start < stop
writer = cv2.VideoWriter(str(out/'continuous.avi'),cv2.VideoWriter_fourcc(*'FFV1'),fps,(w,h))
assert writer.isOpened()
cap.set(cv2.CAP_PROP_POS_FRAMES,start)
records=[]
for index in range(start,stop+1):
    ok,bgr=cap.read(); assert ok
    pts=cap.get(cv2.CAP_PROP_POS_MSEC)
    assert abs(pts-index/fps*1000)<.1
    rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
    records.append(dict(frameIndex=index,sourcePtsMs=pts,rgbSha256=hashlib.sha256(rgb.tobytes()).hexdigest()))
    writer.write(bgr)
    if index % 150 == 0: print(index,flush=True)
cap.release();writer.release()
check=cv2.VideoCapture(str(out/'continuous.avi'))
for row in records:
    ok,bgr=check.read(); assert ok
    assert hashlib.sha256(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB).tobytes()).hexdigest()==row['rgbSha256']
assert not check.read()[0];check.release()
with open(video,'rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
with (out/'continuous.avi').open('rb') as f: cliphash=hashlib.file_digest(f,'sha256').hexdigest()
(out/'manifest.json').write_text(json.dumps(dict(video=str(Path(video).resolve()),videoSha256=digest,
    clipSha256=cliphash,fps=fps,size=[w,h],firstFrame=start,lastFrame=stop,frames=records,
    allFramesPreserved=True,allDecodedRgbVerified=True,audioIncluded=False,stitched=False),indent=2),encoding='utf-8')
print('VERIFIED',len(records),flush=True)
