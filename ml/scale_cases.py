"""P4-B fixed virtual client sizes. Truth is transformed for the evaluator only."""
import argparse,copy,hashlib,json
from pathlib import Path
from PIL import Image

def scale_png(source,scale,output):
    if scale not in [.75,1,1.25]:raise ValueError('P4-B permits only fixed 75/100/125 percent')
    source=Path(source);output=Path(output);raw=source.read_bytes()
    with Image.open(source) as image:
        size=[round(image.width*scale),round(image.height*scale)]
        sx,sy=size[0]/image.width,size[1]/image.height
        with output.open('xb') as target:
            if scale==1:target.write(raw)
            else:image.resize(tuple(size),Image.Resampling.LANCZOS).save(target,format='PNG')
    return {'image':str(output.resolve()),'size':size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
      'transform':{'kind':'fixed_scale','requestedScale':scale,'sx':sx,'sy':sy,'inputSha256':hashlib.sha256(raw).hexdigest()}}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('native_manifest');parser.add_argument('output');args=parser.parse_args()
    original=Path(args.native_manifest);m=json.loads(original.read_text(encoding='utf-8'))
    if m['stage']!='P4-A' or m['transform']!='none' or len(m['cases'])!=5:raise ValueError('five frozen originals required')
    root=Path(args.output);root.mkdir();cases=[]
    for c in m['cases']:
        for scale in [.75,1,1.25]:
            case=copy.deepcopy(c);case['originalId']=c['id'];case['id']=c['id']+'-scale-'+str(scale);case['scale']=scale
            folder=root/case['id'];folder.mkdir();frames=[]
            for f in c['frames']:
                transformed=scale_png(f['image'],scale,folder/Path(f['image']).name)
                frames.append({**f,**transformed,'geometryVersion':'fixed-'+str(scale)})
            case['frames']=frames;case['clientSize']=frames[0]['size']
            sx,sy=frames[0]['transform']['sx'],frames[0]['transform']['sy']
            for name in ['expectedBox','clientBox']:case[name]=[value*(sx if i%2==0 else sy) for i,value in enumerate(c[name])]
            cases.append(case)
    result={**m,'stage':'P4-B','transform':'fixed_scale','parentManifestSha256':hashlib.sha256(original.read_bytes()).hexdigest(),'cases':cases,'g4Complete':False}
    (root/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'stage':'P4-B','cases':len(cases),'frames':sum(len(c['frames']) for c in cases),'g4Complete':False}))

if __name__=='__main__':main()
