"""Evaluate a completed research model; no training, proof construction or actions."""
import csv
import hashlib
import json
from pathlib import Path
import statistics
import time
from PIL import Image,ImageDraw
from research_pilot import ROOT,OUT,score,predict_images,box_iou,sha


def aggregate(records,threshold):
    counts=dict(tp=0,fp=0,fn=0,complete=dict(tp=0,fn=0,total=0),partial=dict(tp=0,fn=0,total=0))
    for record in records:
        r=score(record['predictions'],record['truth'],threshold)
        for k in ('tp','fp','fn'):counts[k]+=r[k]
        for visibility in ('complete','partial'):
            for k in ('tp','fn','total'):counts[visibility][k]+=r[visibility][k]
    tp,fp,fn=(counts[k] for k in ('tp','fp','fn'))
    counts.update(precision=tp/(tp+fp) if tp+fp else None,recall=tp/(tp+fn) if tp+fn else None,threshold=threshold)
    return counts


def overlay(record,truth,destination):
    im=Image.open(record['image']).convert('RGB');draw=ImageDraw.Draw(im)
    for t in truth:
        x,y,w,h=t['box'];draw.rectangle((x,y,x+w,y+h),outline='#00ff70',width=3)
    for p in record['boxes']:
        x,y,w,h=p['box'];draw.rectangle((x,y,x+w,y+h),outline='#ff3636',width=2)
        draw.text((x,y),f"{p['className']} {p['confidence']:.2f}",fill='white',stroke_width=1,stroke_fill='black')
    im.save(destination)


def benchmark(model_path,images):
    import torch,numpy as np
    from ultralytics import YOLO
    torch.set_num_threads(6); model=YOLO(str(model_path))
    options=dict(imgsz=640,rect=False,conf=.25,iou=.7,device='cpu',verbose=False,save=False)
    for _ in range(3): model.predict(source=images[0]['image'],**options)
    timings=[]
    for repeat in range(5):
        for image in images:
            t=time.perf_counter();model.predict(source=image['image'],**options)
            timings.append(dict(imageSha256=image['imageSha256'],repeat=repeat,ms=(time.perf_counter()-t)*1000))
    samples=[r['ms'] for r in timings]
    return dict(scope='fresh image decode + library preprocess + CPU model + postprocess; model object reused, no prediction cache; not proof/transaction/G4',
                backend='PyTorch CPU FP32',threads=6,batch=1,imgsz=640,warmup=3,
                p50=float(np.percentile(samples,50)),p95=float(np.percentile(samples,95)),maxMs=max(samples),records=timings)


def main():
    import os
    os.environ.setdefault('YOLO_CONFIG_DIR',str(OUT/'ultralytics-settings'))
    os.environ['YOLO_AUTOINSTALL']='false'
    result=json.loads((OUT/'fit-result.json').read_text()); model=Path(result['best'])
    sealed=json.loads((OUT/'dataset-seal.json').read_text())
    # Strip all labels before the generator is called. Predictions are persisted first.
    val_inputs=[{k:r[k] for k in ('image','imageSha256')} for r in sealed['val']]
    challenge=json.loads((OUT/'challenge-inputs.json').read_text())['records']
    challenge_inputs=[{k:r[k] for k in ('image','imageSha256')} for r in challenge]
    vp=predict_images(model,val_inputs,OUT/'validation-predictions.json')
    cp=predict_images(model,challenge_inputs,OUT/'challenge-predictions.json')
    (OUT/'generation-complete.json').write_text(json.dumps(dict(validationPredictionsSha256=sha(OUT/'validation-predictions.json'),challengePredictionsSha256=sha(OUT/'challenge-predictions.json'),modelSha256=sha(model),truthReadByGenerator=False,actionAuthority=False),indent=2))
    overlays=OUT/'overlays';overlays.mkdir(exist_ok=True)
    validation=[]
    for p,t in zip(vp,sealed['val']):
        validation.append(dict(id=t['valIndex'],imageSha256=p['imageSha256'],predictions=p['boxes'],truth=t['boxes'],iou50=score(p['boxes'],t['boxes'],.5),iou90=score(p['boxes'],t['boxes'],.9)))
        overlay(p,t['boxes'],overlays/f"validation-{t['valIndex']:02d}.png")
    # Frozen truth and old observer packets are used only by the scorer, after generation.
    frozen=json.loads((OUT/'challenge-scorer-truth.json').read_text())['records']; truth_by_id={t['id']:t for t in frozen}
    cases=[]
    for p,schedule in zip(cp,challenge):
        label=schedule['id']; truth=truth_by_id.get(label); row=dict(id=label,case=schedule['case'],phase=('map' if schedule['phase']=='map' else 'scheduled-post-click-map'),scheduledPhase=schedule['phase'],candidates=len(p['boxes']))
        boxes=[]
        if truth:
            target=truth['expectedBox']; boxes=[dict(className='map_node',box=target,visibility='complete')]
            nodes=[x for x in p['boxes'] if x['className']=='map_node']
            best=max((box_iou(x['box'],target) for x in nodes),default=0)
            packet=json.loads(Path(truth['baselinePacket']).read_text(encoding='utf-8-sig'))
            old=packet.get('mapReview',{}).get('nodes',[])
            old_iou=max((box_iou(x['box'],target) for x in old),default=0)
            row.update(targetIoU=best,targetFound50=best>=.5,targetBoxPass90=best>=.9,
                       savedTemplateCandidates=len(old),savedTemplateTargetIoU=old_iou,
                       frozenTruth=target,scoreScope='one frozen map target only, not full-map FP/FN or safe click')
        else:row['scoreScope']='scheduled post-click frame still showed MAP; not actual preview evidence'
        overlay(p,boxes,overlays/(label+'.png'));cases.append(row)
    latency=benchmark(model,val_inputs)
    report=dict(researchOnly=True,formalA1Consumed=False,formalVerifierChanges=0,nativeActions=0,g4Complete=False,
                trainImages=52,trainBoxes=sum(len(r['boxes']) for r in sealed['train']),validationImages=len(vp),validationBoxes=sum(len(r['boxes']) for r in sealed['val']),
                validation50=aggregate(validation,.5),validation90=aggregate(validation,.9),
                validationDetails=validation,challenge=cases,latency=latency,
                limits=['small source-separated validation, not certified cross-layout generalization','only3 positive validation frames;9 negatives','challenge has target-only map truth; initial scheduled post-click frames still MAP, actual-preview evidence is in separate supplement','no threshold tuning or second training run'])
    (OUT/'evaluation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ('validationDetails','latency')}))
    print('latency',json.dumps({k:v for k,v in latency.items() if k!='records'}))

if __name__=='__main__':main()
