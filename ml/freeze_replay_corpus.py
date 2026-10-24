"""Freeze reviewed multi-video source intervals; never execute game input."""
import argparse,hashlib,json,math,re
from pathlib import Path
from freeze_video_cases import extract_case


def _box(box,size):
    return isinstance(box,list) and len(box)==4 and all(type(x) in (int,float) and math.isfinite(x) for x in box) and min(box[:2])>=0 and min(box[2:])>0 and box[0]+box[2]<=size[0] and box[1]+box[3]<=size[1]


def validate_corpus(data):
    cases=data.get('cases',[])
    if len(cases)!=30 or sum(c.get('split')=='development' for c in cases)!=20 or sum(c.get('split')=='holdout' for c in cases)!=10:raise ValueError('requires thirty cases and twenty/ten split')
    seen=set();intervals={};source_specs={}
    for c in cases:
        name=c.get('id');sha=c.get('videoSha256');fps=c.get('sourceFps');size=c.get('sourceSize');pre=c.get('preFrames');last=c.get('lastFrame');intent=c.get('intent',{})
        if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,127}',name) or name in seen:raise ValueError('invalid or duplicate case id')
        seen.add(name)
        if not isinstance(c.get('video'),str) or not c['video'] or not isinstance(sha,str) or not re.fullmatch(r'[a-f0-9]{64}',sha):raise ValueError('source identity missing')
        if fps not in [30,60] or not isinstance(size,list) or len(size)!=2 or any(type(x) is not int or x<=0 for x in size):raise ValueError('source size or fps invalid')
        if sha in source_specs and source_specs[sha]!=(fps,size):raise ValueError('conflicting source specification')
        source_specs[sha]=(fps,size)
        if not isinstance(pre,list) or len(pre)!=2 or any(type(x) is not int or x<0 for x in [*pre,last]) or pre[1]-pre[0]<fps*.2 or last<=pre[1]:raise ValueError('source interval invalid')
        if c.get('reviewed') is not True or c.get('split')=='holdout' and c.get('modelInferenceRun') is not False:raise ValueError('unreviewed or already evaluated holdout')
        if any(type(intent.get(k)) is not int or not 1<=intent[k]<=limit for k,limit in [('zone',10),('floor',31),('column',4)]) or intent.get('event')!='battle' or intent.get('mode') not in ['select','resume']:raise ValueError('ordinary interaction identity invalid')
        box,safe=c.get('expectedBox'),c.get('clientBox')
        if not _box(box,size) or not _box(safe,size) or not (box[0]<=safe[0] and box[1]<=safe[1] and safe[0]+safe[2]<=box[0]+box[2] and safe[1]+safe[3]<=box[1]+box[3]):raise ValueError('independent target and safe geometry invalid')
        gate=c.get('gateWindowMs')
        if not isinstance(gate,list) or len(gate)!=2 or any(type(t) not in (int,float) or not math.isfinite(t) or abs(t-round(pre[1]/fps*1000,6))>.001 for t in gate):raise ValueError('dispatch gate is not the second reviewed native frame')
        for a,b in intervals.setdefault(sha,[]):
            if max(a,pre[0])<=min(b,last):raise ValueError('overlapping source interactions')
        intervals[sha].append((pre[0],last))
    if len({c['intent']['zone'] for c in cases})<3 or len({c['intent']['floor'] for c in cases})<2 or len({c['intent']['column'] for c in cases})<2:raise ValueError('source coverage insufficient')
    return cases


def freeze_corpus(annotation_path,output):
    annotation_path=Path(annotation_path);raw=annotation_path.read_bytes();annotations=json.loads(raw);cases=validate_corpus(annotations)
    videos={}
    for c in cases:
        path=Path(c['video']).resolve()
        if path not in videos:
            with path.open('rb') as stream:videos[path]=hashlib.file_digest(stream,'sha256').hexdigest()
        if videos[path]!=c['videoSha256']:raise ValueError('source video changed')
    for entry in annotations.get('inputAnnotationSnapshots',[]):
        if hashlib.sha256(Path(entry['path']).read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('reviewed annotation changed')
    output=Path(output);output.mkdir();(output/'annotations.snapshot.json').write_bytes(raw)
    result={'stage':'P4-C-source','sourceFreezeVerified':False,'annotationSha256':hashlib.sha256(raw).hexdigest(),'freezerCodeSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'splitUnit':annotations.get('splitUnit'),'cases':[],'g4Complete':False,'nativeActions':0,'transform':'none'}
    try:
        for c in cases:
            frames=extract_case(c['video'],c,output/c['id'],source_spec={'fps':c['sourceFps'],'size':c['sourceSize']})
            result['cases'].append({**c,'frames':frames,'source':{'videoSha256':c['videoSha256'],'startPtsMs':frames[0]['sourcePtsMs'],'endPtsMs':frames[-1]['sourcePtsMs']},'scale':1,'passed':False,'formal30Frozen':True})
            (output/'manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
            print(json.dumps({'case':c['id'],'frames':len(frames),'split':c['split']}),flush=True)
    except Exception as error:
        (output/'failure.json').write_text(json.dumps({'sourceFreezeVerified':False,'error':str(error),'g4Complete':False}),encoding='utf-8')
        raise
    result['sourceFreezeVerified']=True
    (output/'manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('annotations');parser.add_argument('output');args=parser.parse_args()
    result=freeze_corpus(args.annotations,args.output)
    print(json.dumps({'cases':len(result['cases']),'frames':sum(len(c['frames']) for c in result['cases']),'sourceFreezeVerified':True,'g4Complete':False}))

if __name__=='__main__':main()
