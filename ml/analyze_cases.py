"""Read-only batch observer. Test truth and intent never reach the recognizer."""
import argparse,atexit,base64,hashlib,json,os,socket,sys,time
from pathlib import Path
from PIL import Image
sys.dont_write_bytecode=True

def main():
    parser=argparse.ArgumentParser();parser.add_argument('source_manifest');parser.add_argument('output');parser.add_argument('--cache');parser.add_argument('--fast-map',action='store_true');parser.add_argument('--bounded-ocr',type=int,choices=[736,960,1280]);args=parser.parse_args()
    root=Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper'));sys.path.insert(0,str(root/'ml'))
    socket.socket.connect=lambda *a,**k: (_ for _ in ()).throw(RuntimeError('network disabled in offline observer'))
    from observation import inspect_capture
    from preview_identity import inspect_preview_identity
    from map_action_evidence import inspect_map_actions
    from preview_registration import PreviewAnchorTracker
    if args.fast_map:
        import map_vision
        from fast_map_candidates import node_candidates
        map_vision.node_candidates=node_candidates
    bounded=None;ocr_mode='original_v1';ocr_code=None
    if args.bounded_ocr is not None:
        from bounded_ocr import BoundedOCRRuntime
        bounded=BoundedOCRRuntime(args.bounded_ocr);bounded.__enter__();atexit.register(bounded.close)
        ocr_mode=bounded.mode;ocr_code=hashlib.sha256((Path(__file__).parent/'bounded_ocr.py').read_bytes()).hexdigest()
    from runtime_evidence import capture_runtime_evidence
    runtime_evidence=capture_runtime_evidence()
    source_path=Path(args.source_manifest);m=json.loads(source_path.read_text(encoding='utf-8'));out=Path(args.output);out.mkdir()
    cached={};cache_ignored=None
    if args.cache:
        old=json.loads(Path(args.cache).read_text(encoding='utf-8'))
        old_ocr=(old.get('analysis') or {}).get('ocrPreprocessing') or {'mode':'original_v1','codeSha256':None}
        if old_ocr.get('mode')!=ocr_mode or old_ocr.get('codeSha256')!=ocr_code:cache_ignored='OCR_PREPROCESSING_CHANGED'
        elif (old.get('analysis') or {}).get('runtimeEvidence',{}).get('fingerprint')!=runtime_evidence['fingerprint']:cache_ignored='OCR_RUNTIME_CHANGED_OR_UNBOUND'
        else:
            for c in old['cases']:
                for f in c['frames']:
                    if f.get('packet'):cached[(f['frameIndex'],f['sha256'])]=f['packet']
    m['analysis']={'sourceManifestSha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),
      'runtimeEvidence':runtime_evidence,
      'identityCodeSha256':hashlib.sha256((Path(__file__).parent/'preview_identity.py').read_bytes()).hexdigest(),
      'mapActionCodeSha256':hashlib.sha256((Path(__file__).parent/'map_action_evidence.py').read_bytes()).hexdigest(),
      'previewRegistrationCodeSha256':hashlib.sha256((Path(__file__).parent/'preview_registration.py').read_bytes()).hexdigest(),
      'ocrPreprocessing':{'mode':ocr_mode,'codeSha256':ocr_code,'maximumTensorSide':args.bounded_ocr,'thresholdsChanged':False},'cacheIgnoredReason':cache_ignored,
      'cacheManifestSha256':hashlib.sha256(Path(args.cache).read_bytes()).hexdigest() if args.cache else None,
      'nativeActions':0,'allFramesAnalyzed':False,'mapBackend':'exact_grouped_masks_parallel4' if args.fast_map else 'v1_original',
      'mapBackendSha256':hashlib.sha256((Path(__file__).parent/'fast_map_candidates.py').read_bytes()).hexdigest() if args.fast_map else None}
    for c in m['cases']:
        folder=out/c['id'];folder.mkdir();count=0;tracker=PreviewAnchorTracker()
        for f in c['frames']:
            started=time.perf_counter();image_path=Path(f['image']);raw=image_path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
            if digest!=f['sha256']:raise ValueError('frozen image bytes changed')
            with Image.open(image_path) as im:
                if im.format!='PNG' or list(im.size)!=f['size']:raise ValueError('source PNG dimensions changed')
                rgb=im.convert('RGB')
            key=(f['frameIndex'],digest);cache=cached.get(key)
            if cache:
                p=json.loads(Path(cache).read_text(encoding='utf-8'))
                if p['binding']['imageSha256']!=digest or p['binding']['pixelSha256']!=hashlib.sha256(rgb.tobytes()).hexdigest():raise ValueError('cache does not bind original bytes')
                p['analysisTiming']={'mode':'cached_v1_packet_current_v2_identity','freshFullPipeline':False,'cachedPacketSha256':hashlib.sha256(Path(cache).read_bytes()).hexdigest()}
            else:
                frame_id=hashlib.sha256((m['videoSha256']+str(f['frameIndex'])+digest).encode()).hexdigest()[:32]
                p=inspect_capture('data:image/png;base64,'+base64.b64encode(raw).decode(),
                  {'frameId':frame_id,'imageSha256':digest,'width':rgb.width,'height':rgb.height},root/'data/flow')
                p['analysisTiming']={'mode':'fresh_full_pipeline','freshFullPipeline':True}
            p.pop('v2TrackedMap',None)
            p['v2TrackedMap']=tracker.observe({'png':raw,'packet':p,'atMs':f.get('atMs'),'sourcePtsMs':f.get('sourcePtsMs'),'windowKey':'offline:original-video','geometryVersion':f.get('geometryVersion','original')})
            p['v2Preview']=inspect_preview_identity(rgb,p)
            p['v2MapActions']=inspect_map_actions(rgb,p)
            p['ocrAnalysis']=bounded.take_metadata() if bounded else {'mode':'original_v1'}
            p['ocrAnalysis']['freshFullPipeline']=not bool(cache)
            p['analysisTiming']['elapsedMs']=(time.perf_counter()-started)*1000
            target=folder/f"{f['frameIndex']:07}.packet.json";target.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8');f['packet']=str(target.resolve());count+=1
            (out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
            if p['flow']['state']=='UNKNOWN' and not p['v2Preview']['verified']:
                raise ValueError('UNKNOWN; failure packet preserved: '+str(target))
        print(json.dumps({'case':c['id'],'frames':count,'complete':True}),flush=True)
    m['analysis']['allFramesAnalyzed']=True
    (out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
