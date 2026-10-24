"""Losslessly decode native video frames; never rescale or sample away transitions."""
import argparse,hashlib,json
from pathlib import Path
import cv2

def extract_case(video,case,output):
    pre=case['preFrames'];last=case['lastFrame']
    if len(pre)!=2 or any(type(n) is not int or n<0 for n in [*pre,last]) or pre[1]-pre[0]<6 or last<=pre[1]:raise ValueError('invalid source interval')
    output=Path(output);output.mkdir()
    cap=cv2.VideoCapture(str(video))
    if not cap.isOpened() or abs(cap.get(cv2.CAP_PROP_FPS)-30)>.0001:raise ValueError('expected reviewed 30fps source')
    cap.set(cv2.CAP_PROP_POS_FRAMES,pre[0]);frames=[]
    try:
        for index in range(pre[0],last+1):
            ok,bgr=cap.read()
            if not ok:raise ValueError(f'missing original frame {index}')
            if index<pre[1] and index!=pre[0]:continue
            if bgr.shape[:2]!=(1080,1440):raise ValueError('native dimensions changed')
            pts=cap.get(cv2.CAP_PROP_POS_MSEC)
            if abs(pts-index/30*1000)>.1:raise ValueError('decoder PTS not aligned to reviewed source')
            p=output/f'{index:07}.png'
            if not cv2.imwrite(str(p),bgr):raise ValueError('PNG write failed')
            frames.append({'image':str(p.resolve()),'frameIndex':index,'sourcePtsMs':round(pts,6),'atMs':round(pts,6),
              'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':[1440,1080],'geometryVersion':'original'})
    finally:cap.release()
    return frames

def main():
    parser=argparse.ArgumentParser();parser.add_argument('annotations');parser.add_argument('output');args=parser.parse_args()
    annotation_path=Path(args.annotations);annotations=json.loads(annotation_path.read_text(encoding='utf-8'));video=Path(annotations['video'])
    digest=hashlib.file_digest(video.open('rb'),'sha256').hexdigest()
    if digest!=annotations['videoSha256']:raise ValueError('source video changed')
    output=Path(args.output);output.mkdir();cases=[]
    for c in annotations['cases']:
        frames=extract_case(video,c,output/c['id'])
        cases.append({**c,'frames':frames,'source':{'videoSha256':digest,'startPtsMs':frames[0]['sourcePtsMs'],'endPtsMs':frames[-1]['sourcePtsMs']},'scale':1,'passed':False})
    result={'stage':'P4-A','video':str(video),'videoSha256':digest,'annotationSha256':hashlib.sha256(annotation_path.read_bytes()).hexdigest(),
      'sourceFps':30,'sourceSize':[1440,1080],'transform':'none','cases':cases,'g4Complete':False}
    (output/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'cases':len(cases),'frames':sum(len(c['frames']) for c in cases),'g4Complete':False}))

if __name__=='__main__':main()
