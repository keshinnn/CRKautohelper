"""Approved small RESEARCH model: separate from formal A1 and all action authority."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from annotation_audit import box_iou
from train_export import verify_pixels, yolo_label, sha, APPROVED_WEIGHTS_SHA256, validate_loaded_model, supervised_parent

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/candidate-research-pilot-20261112-01'
WEIGHTS=ROOT/'artifacts/candidate-training-20261112-01/assets/yolo26n.pt'
PROTECTED={'buAwy1zf2LI','L0ktY5qUppI','0QxozULx_SQ','LX46_2XTfJg'}


def check_split(train,val):
    if any(r['sourceId'] in PROTECTED for r in train): raise ValueError('PROTECTED_TRAINING_SOURCE')
    if {r['sourceId'] for r in train}&{r['sourceId'] for r in val}: raise ValueError('SOURCE_OVERLAP')
    if {r['pixelSha256'] for r in train}&{r['pixelSha256'] for r in val}: raise ValueError('PIXEL_OVERLAP')
    if not train or not val: raise ValueError('EMPTY_SPLIT')


def score(predictions,truth,threshold):
    edges=[]
    for t in truth:
        choices=[(box_iou(t['box'],p['box']),j) for j,p in enumerate(predictions) if t['className']==p['className']]
        edges.append([j for iou,j in sorted(choices,reverse=True) if iou>=threshold])
    matched={}
    def augment(i,seen):
        for j in edges[i]:
            if j in seen: continue
            seen.add(j)
            if j not in matched or augment(matched[j],seen): matched[j]=i; return True
        return False
    for i in range(len(truth)): augment(i,set())
    pairs=[dict(prediction=j,truth=i,iou=box_iou(predictions[j]['box'],truth[i]['box'])) for j,i in matched.items()]
    tp=len(pairs); fp=len(predictions)-tp; fn=len(truth)-tp
    result=dict(tp=tp,fp=fp,fn=fn,threshold=threshold,pairs=pairs,
                precision=tp/(tp+fp) if tp+fp else None,recall=tp/(tp+fn) if tp+fn else None)
    for visibility in ('complete','partial'):
        total=sum(t.get('visibility','complete')==visibility for t in truth)
        hit=sum(truth[x['truth']].get('visibility','complete')==visibility for x in pairs)
        result[visibility]=dict(tp=hit,fn=total-hit,total=total)
    return result


def prepare_dataset(train,val):
    check_split(train,val)
    if len(train)!=52 or len(val)!=12: raise ValueError('RESEARCH_SUBSET_CHANGED')
    if sha(WEIGHTS)!=APPROVED_WEIGHTS_SHA256: raise ValueError('WEIGHTS_CHANGED')
    for r in train+val:
        verify_pixels(r)
        if r.get('reviewed') is not True or r.get('independentReviews')!=2 or not isinstance(r.get('boxes'),list):
            raise ValueError('UNREVIEWED_RESEARCH_LABEL')
        if not r['boxes'] and not r.get('hardNegativeReviewed'): raise ValueError('UNREVIEWED_NEGATIVE')
        for box in r['boxes']: yolo_label(box,r['sourceSize'])
    dataset=OUT/'dataset'; dataset.mkdir(exist_ok=False)
    for split,records in [('train',train),('val',val)]:
        images=dataset/'images'/split; labels=dataset/'labels'/split
        images.mkdir(parents=True); labels.mkdir(parents=True)
        for r in records:
            name=r['imageSha256']; shutil.copyfile(r['image'],images/(name+'.png'))
            (labels/(name+'.txt')).write_text('\n'.join(yolo_label(x,r['sourceSize']) for x in r['boxes'])+'\n',encoding='utf-8')
    data=dataset/'data.yaml'
    data.write_text('path: '+json.dumps(str(dataset))+'\ntrain: images/train\nval: images/val\nnames:\n  0: map_node\n  1: entry_gate\n',encoding='utf-8')
    seal=dict(scope='small_research_only_not_formal_A1',seed=20261112,maxEpochs=50,maxWallSeconds=1800,
              train=train,val=val,sourceDisjoint=True,layoutIndependenceCertified=False,
              pretrainedSha256=sha(WEIGHTS),confidence=.25,nmsIoU=.7,
              files={str(p.relative_to(dataset)):sha(p) for p in dataset.rglob('*') if p.is_file()})
    (OUT/'dataset-seal.json').write_text(json.dumps(seal,indent=2),encoding='utf-8')
    return seal


def require_supervisor():
    try:
        pid=int(os.environ.get('CRK_RESEARCH_PILOT_PARENT_PID',''))
    except ValueError:
        raise ValueError('SUPERVISED_RESEARCH_LAUNCH_REQUIRED') from None
    if not supervised_parent(pid): raise ValueError('SUPERVISED_RESEARCH_LAUNCH_REQUIRED')


def fit():
    require_supervisor()
    # Never invoke the formal A1 admission/budget entry. This is a separate approval.
    seal=json.loads((OUT/'dataset-seal.json').read_text(encoding='utf-8'))
    check_split(seal['train'],seal['val'])
    if sha(WEIGHTS)!=APPROVED_WEIGHTS_SHA256: raise ValueError('WEIGHTS_CHANGED')
    actual={str(p.relative_to(OUT/'dataset')):sha(p) for p in (OUT/'dataset').rglob('*') if p.is_file()}
    if actual!=seal['files']: raise ValueError('RESEARCH_DATASET_CHANGED')
    with (OUT/'research-training-attempt.json').open('x',encoding='utf-8') as stream:
        json.dump(dict(researchOnly=True,formalA1Consumed=False,datasetSealSha256=sha(OUT/'dataset-seal.json'),maxEpochs=50,maxWallSeconds=1800),stream,indent=2)
    import torch
    from ultralytics import YOLO
    torch.set_num_threads(6)
    model=YOLO(str(WEIGHTS)); validate_loaded_model(model)
    start=time.perf_counter()
    model.train(data=str(OUT/'dataset/data.yaml'),project=str(OUT/'fit'),name='research-model',
                epochs=50,time=None,imgsz=640,batch=4,device='cpu',workers=0,
                seed=20261112,deterministic=True,amp=False,cache=False,resume=False,
                pretrained=True,val=True,split='val',plots=False,save=True,save_period=10,
                patience=50,optimizer='AdamW',lr0=.001,lrf=.01,nbs=4,
                mosaic=0.0,close_mosaic=0,scale=.3,translate=.1,fliplr=.5)
    elapsed=time.perf_counter()-start
    best=OUT/'fit/research-model/weights/best.pt'
    final=YOLO(str(best)); exported=Path(final.export(format='onnx',imgsz=640,batch=1,half=False,dynamic=False,simplify=False,opset=17,device='cpu'))
    (OUT/'fit-result.json').write_text(json.dumps(dict(researchOnly=True,formalA1Consumed=False,
        trainingSeconds=elapsed,best=str(best),bestSha256=sha(best),onnx=str(exported),onnxSha256=sha(exported)),indent=2))


def supervise():
    start=time.perf_counter()
    child_env=dict(os.environ,CRK_RESEARCH_PILOT_PARENT_PID=str(os.getpid()))
    try:
        with (OUT/'training.log').open('x',encoding='utf-8') as stream:
            result=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'fit'],stdout=stream,stderr=subprocess.STDOUT,timeout=1800,env=child_env)
        status='FINISHED' if result.returncode==0 else 'FAILED'; code=result.returncode
    except subprocess.TimeoutExpired:
        status='CPU_COST_LIMIT'; code=1
    (OUT/'supervision.json').write_text(json.dumps(dict(status=status,returncode=code,wallSeconds=time.perf_counter()-start,researchOnly=True,formalA1Consumed=False),indent=2))
    if code: raise SystemExit(code)


def predict_images(model_path,inputs,output):
    # Pixel-only generator: no truth, intent, observer packet, previous/future frame arguments.
    import torch
    from ultralytics import YOLO
    torch.set_num_threads(6); model=YOLO(str(model_path))
    records=[]
    for source in inputs:
        if sha(source['image'])!=source['imageSha256']: raise ValueError('SOURCE_CHANGED')
        start=time.perf_counter()
        r=model.predict(source=source['image'],imgsz=640,rect=False,conf=.25,iou=.7,device='cpu',verbose=False,save=False)[0]
        elapsed=(time.perf_counter()-start)*1000
        boxes=[]
        for xyxy,confidence,cls in zip(r.boxes.xyxy.cpu().tolist(),r.boxes.conf.cpu().tolist(),r.boxes.cls.cpu().tolist()):
            x0,y0,x1,y1=xyxy
            boxes.append(dict(className=model.names[int(cls)],confidence=confidence,box=[x0,y0,x1-x0,y1-y0]))
        records.append(dict(image=source['image'],imageSha256=source['imageSha256'],sourceSize=list(reversed(r.orig_shape)),
                            boxes=boxes,elapsedMs=elapsed,modelSha256=sha(model_path),researchOnly=True))
    Path(output).write_text(json.dumps(dict(records=records,confidence=.25,nmsIoU=.7,truthReadByGenerator=False,actionAuthority=False),indent=2))
    return records


def main():
    os.environ.setdefault('YOLO_CONFIG_DIR',str(OUT/'ultralytics-settings'))
    os.environ['YOLO_AUTOINSTALL']='false'
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=['train','fit']); args=parser.parse_args()
    if args.action=='train': supervise()
    else: fit()

if __name__=='__main__': main()
