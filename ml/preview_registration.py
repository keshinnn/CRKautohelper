"""Direct fresh pixel correspondence for preview identity, never new clicks."""
import copy,hashlib,io,math,os,sys
from pathlib import Path
from PIL import Image

def _decode(frame):
    raw=frame['png'];p=frame['packet'];b=p['binding']
    if hashlib.sha256(raw).hexdigest()!=b['imageSha256']:raise ValueError('PNG binding mismatch')
    with Image.open(io.BytesIO(raw)) as im:
        if im.format!='PNG' or list(im.size)!=[b['width'],b['height']]:raise ValueError('PNG geometry mismatch')
        image=im.convert('RGB')
    digest=hashlib.sha256(image.tobytes()).hexdigest()
    if digest!=b['pixelSha256'] or p.get('mapReview',{}).get('frameId')!=digest[:20]:raise ValueError('pixel binding mismatch')
    return image

def recover_preview_anchor(before,after):
    rejected={'verified':False,'previewOnly':True,'actionsExecuted':False,'reason':'PREVIEW_REGISTRATION_UNPROVEN'}
    try:
        for key in ['atMs','sourcePtsMs']:
            a,b=before.get(key),after.get(key)
            if not all(isinstance(x,(int,float)) and math.isfinite(x) for x in [a,b]) or not 0<b-a<=2500:return rejected
        if abs((after['atMs']-before['atMs'])-(after['sourcePtsMs']-before['sourcePtsMs']))>.001:return rejected
        if not before.get('windowKey') or before['windowKey']!=after.get('windowKey') or not before.get('geometryVersion') or before['geometryVersion']!=after.get('geometryVersion'):return rejected
        a,b=_decode(before),_decode(after)
        if a.size!=b.size:return rejected
        pa,pb=before['packet'],after['packet'];ga,gb=pa['mapReview'],pb['mapReview']
        if pa.get('actionsExecuted') is not False or pb.get('actionsExecuted') is not False:return rejected
        zones=[]
        for p in [pa,pb]:
            z=p.get('progress',{})
            if type(z.get('displayedZone')) is not int or not 1<=z['displayedZone']<=9 or z.get('conflictingEvidence') is not False or not .9<=z.get('score',0)<=1:return rejected
            zones.append(z['displayedZone'])
        if zones[0]!=zones[1] or ga.get('absoluteFloorKnown') is not True or ga.get('floorAnchorSource')!='visible_top_gate' or len([n for n in ga['nodes'] if n.get('type')=='exit'])!=1:return rejected
        for g in [ga,gb]:
            ids=[n.get('id') for n in g.get('nodes',[])]
            if not ids or any(not isinstance(n,str) or not n for n in ids) or len(set(ids))!=len(ids):return rejected
        module_path=str(Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper'))/'ml')
        if module_path not in sys.path:sys.path.insert(0,module_path)
        from map_registration import register_map_images
        registration=register_map_images(a,b,ga,gb)
        if registration.get('verified') is not True:return {**rejected,'registration':registration}
        previous={n['id']:n for n in ga['nodes']};current={n['id']:n for n in gb['nodes']};offsets=set()
        pairs=registration['pairs']
        if len(pairs)<5 or len({p['beforeRow'] for p in pairs})<2:return rejected
        for pair in pairs:
            old,new=previous[pair['beforeNode']],current[pair['afterNode']]
            if type(old.get('floor')) is not int or type(new.get('visibleRow')) is not int:return rejected
            offsets.add(old['floor']-new['visibleRow'])
        if len(offsets)!=1:return rejected
        offset=next(iter(offsets));restored=copy.deepcopy(gb)
        for n in restored['nodes']:
            if n.get('type')=='exit':continue
            floor=n['visibleRow']+offset
            if not 1<=floor<=31 or n.get('floor') not in [None,floor]:return rejected
            n['floor']=floor
        proof={'verified':True,'method':'fresh_same_zone_direct_map_pixel_registration','previewOnly':True,'actionsExecuted':False,
          'sourceImageSha256':pa['binding']['imageSha256'],'sourceFrameId':pa['binding']['frameId'],
          'sourcePixelSha256':pa['binding']['pixelSha256'],'pixelSha256':pb['binding']['pixelSha256'],
          'sourceAtMs':before['atMs'],'atMs':after['atMs'],'zone':zones[0],'windowKey':before['windowKey'],
          'geometryVersion':before['geometryVersion'],'registration':registration}
        restored.update(absoluteFloorKnown=True,floorAnchorSource='verified_preview_pixel_registration',registrationEvidence=copy.deepcopy(proof))
        return {**proof,'mapReview':restored}
    except (KeyError,TypeError,ValueError,AttributeError):return rejected

class PreviewAnchorTracker:
    """One direct, short-lived anchor per observation stream; no intent input."""
    def __init__(self):self.anchor=None

    def observe(self,frame):
        unknown={'verified':False,'previewOnly':True,'actionsExecuted':False}
        packet=frame.get('packet') or {};m=packet.get('mapReview') or {};time=frame.get('atMs')
        if not isinstance(time,(int,float)) or not math.isfinite(time):self.anchor=None;return unknown
        if self.anchor:
            previous=self.anchor;zone=(packet.get('progress') or {}).get('displayedZone');old_zone=(previous['packet'].get('progress') or {}).get('displayedZone')
            if (not 0<time-previous['atMs']<=2500 or frame.get('windowKey')!=previous.get('windowKey')
                or frame.get('geometryVersion')!=previous.get('geometryVersion') or zone!=old_zone):self.anchor=None
        visible=(packet.get('flow') or {}).get('state')=='MAP' and m.get('absoluteFloorKnown') is True and m.get('floorAnchorSource')=='visible_top_gate'
        if visible:
            if self.anchor is None:self.anchor=copy.deepcopy(frame)
            return unknown
        if self.anchor is None:return unknown
        return recover_preview_anchor(self.anchor,frame)
