"""Read-only batch observer. Test truth and intent never reach the recognizer."""
import argparse,atexit,base64,hashlib,json,os,re,socket,sys,time
from pathlib import Path
from PIL import Image
sys.dont_write_bytecode=True

def case_source_sha(manifest,case):
    direct=case.get('videoSha256');nested=(case.get('source') or {}).get('videoSha256')
    if direct is not None and nested is not None and direct!=nested:raise ValueError('conflicting case video source')
    value=direct if direct is not None else nested if nested is not None else manifest.get('videoSha256')
    if not isinstance(value,str) or re.fullmatch(r'[a-f0-9]{64}',value) is None:raise ValueError('missing or invalid video source SHA256')
    return value


def source_frame_id(video_sha,index,image_sha):
    if type(index) is not int or index<0:raise ValueError('invalid source frame index')
    return hashlib.sha256((video_sha+str(index)+image_sha).encode()).hexdigest()[:32]


def effective_observation_state(packet):
    # Producer hint only: JS still independently validates context and identity.
    # A fully observed control panel is known waiting evidence even when the
    # legacy title classifier is UNKNOWN. An arbitrary unknown still stops.
    if (packet.get('v2Preview') or {}).get('verified') is True:return 'PREVIEW'
    if (packet.get('v2PreviewContext') or {}).get('verified') is True:return 'PREVIEW_PENDING'
    return (packet.get('flow') or {}).get('state','UNKNOWN')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('source_manifest');parser.add_argument('output');parser.add_argument('--cache');parser.add_argument('--fast-map',action='store_true');parser.add_argument('--bounded-ocr',type=int,choices=[736,960,1280]);args=parser.parse_args()
    root=Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper'));sys.path.insert(0,str(root/'ml'))
    socket.socket.connect=lambda *a,**k: (_ for _ in ()).throw(RuntimeError('network disabled in offline observer'))
    from observation import inspect_capture
    from preview_identity import inspect_preview_identity
    from preview_context import inspect_preview_context
    from map_action_evidence import inspect_map_actions
    from preview_registration import PreviewAnchorTracker
    from stage_timing import StageTiming
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
    from progress_evidence import ProgressRuntime,parse_progress
    progress_runtime=ProgressRuntime();progress_runtime.__enter__();atexit.register(progress_runtime.close)
    from english_scene import EnglishSceneRuntime
    english_runtime=EnglishSceneRuntime();english_runtime.__enter__();atexit.register(english_runtime.close)
    source_path=Path(args.source_manifest);m=json.loads(source_path.read_text(encoding='utf-8'));out=Path(args.output);out.mkdir()
    cached={};cache_ignored=None
    if args.cache:
        old=json.loads(Path(args.cache).read_text(encoding='utf-8'))
        old_ocr=(old.get('analysis') or {}).get('ocrPreprocessing') or {'mode':'original_v1','codeSha256':None}
        if old_ocr.get('mode')!=ocr_mode or old_ocr.get('codeSha256')!=ocr_code:cache_ignored='OCR_PREPROCESSING_CHANGED'
        elif (old.get('analysis') or {}).get('runtimeEvidence',{}).get('fingerprint')!=runtime_evidence['fingerprint']:cache_ignored='OCR_RUNTIME_CHANGED_OR_UNBOUND'
        elif any((old.get('analysis') or {}).get(key)!=hashlib.sha256((Path(__file__).parent/filename).read_bytes()).hexdigest() for key,filename in [('englishSceneCodeSha256','english_scene.py'),('progressCodeSha256','progress_evidence.py')]):cache_ignored='SEMANTIC_RUNTIME_CHANGED_OR_UNBOUND'
        else:
            for c in old['cases']:
                try:video_sha=case_source_sha(old,c)
                except ValueError:continue  # Unbound historical cache is not authoritative.
                for f in c['frames']:
                    if f.get('packet'):cached[(video_sha,f['frameIndex'],f['sha256'])]=f['packet']
    m['analysis']={'observerContractVersion':1,'sourceManifestSha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),
      'runtimeEvidence':runtime_evidence,
      'englishSceneCodeSha256':hashlib.sha256((Path(__file__).parent/'english_scene.py').read_bytes()).hexdigest(),
      'progressCodeSha256':hashlib.sha256((Path(__file__).parent/'progress_evidence.py').read_bytes()).hexdigest(),
      'identityCodeSha256':hashlib.sha256((Path(__file__).parent/'preview_identity.py').read_bytes()).hexdigest(),
      'mapGeometryCodeSha256':hashlib.sha256((Path(__file__).parent/'sparse_map_geometry.py').read_bytes()).hexdigest(),
      'mapAspectCodeSha256':hashlib.sha256((Path(__file__).parent/'map_aspect.py').read_bytes()).hexdigest(),
      'mapActionCodeSha256':hashlib.sha256((Path(__file__).parent/'map_action_evidence.py').read_bytes()).hexdigest(),
      'currentPositionCodeSha256':hashlib.sha256((Path(__file__).parent/'current_position_evidence.py').read_bytes()).hexdigest(),
      'previewRegistrationCodeSha256':hashlib.sha256((Path(__file__).parent/'preview_registration.py').read_bytes()).hexdigest(),
      'ocrPreprocessing':{'mode':ocr_mode,'codeSha256':ocr_code,'maximumTensorSide':args.bounded_ocr,'thresholdsChanged':False},'cacheIgnoredReason':cache_ignored,
      'cacheManifestSha256':hashlib.sha256(Path(args.cache).read_bytes()).hexdigest() if args.cache else None,
      'nativeActions':0,'allFramesAnalyzed':False,'mapBackend':'exact_grouped_masks_parallel4' if args.fast_map else 'v1_original',
      'mapBackendSha256':hashlib.sha256((Path(__file__).parent/'fast_map_candidates.py').read_bytes()).hexdigest() if args.fast_map else None}
    for c in m['cases']:
        video_sha=case_source_sha(m,c)
        folder=out/c['id'];folder.mkdir();count=0;tracker=PreviewAnchorTracker()
        for f in c['frames']:
            started=time.perf_counter();timing=StageTiming();image_path=Path(f['image']);raw=image_path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
            if digest!=f['sha256']:raise ValueError('frozen image bytes changed')
            with Image.open(image_path) as im:
                if im.format!='PNG' or list(im.size)!=f['size']:raise ValueError('source PNG dimensions changed')
                rgb=im.convert('RGB')
            frame_id=source_frame_id(video_sha,f['frameIndex'],digest)
            timing.mark('decode_binding')
            key=(video_sha,f['frameIndex'],digest);cache=cached.get(key);source_cache_rejection=None
            if cache:
                candidate=json.loads(Path(cache).read_text(encoding='utf-8'))
                if candidate.get('binding',{}).get('frameId')!=frame_id:cache=None;source_cache_rejection='SOURCE_FRAME_ID_MISMATCH'
            if cache:
                p=json.loads(Path(cache).read_text(encoding='utf-8'))
                if p['binding']['imageSha256']!=digest or p['binding']['pixelSha256']!=hashlib.sha256(rgb.tobytes()).hexdigest():raise ValueError('cache does not bind original bytes')
                p['analysisTiming']={'mode':'cached_v1_packet_current_v2_identity','freshFullPipeline':False,'cachedPacketSha256':hashlib.sha256(Path(cache).read_bytes()).hexdigest()}
            else:
                p=inspect_capture('data:image/png;base64,'+base64.b64encode(raw).decode(),
                  {'frameId':frame_id,'imageSha256':digest,'width':rgb.width,'height':rgb.height},root/'data/flow')
                p['analysisTiming']={'mode':'fresh_full_pipeline','freshFullPipeline':True}
            p['analysisTiming']['sourceCacheRejection']=source_cache_rejection
            timing.mark('v1_observation')
            p['observerContractVersion']=1
            p['sourceBinding']={'videoSha256':video_sha,'frameIndex':f['frameIndex'],'imageSha256':digest}
            p['progress']=parse_progress(p['evidence'])
            timing.mark('progress')
            from sparse_map_geometry import recover_map_geometry
            original_map=p.pop('v2OriginalMapReview',None)
            if original_map is not None:p['mapReview']=original_map
            repaired_map=recover_map_geometry(rgb,p)
            if repaired_map is not p.get('mapReview'):
                p['v2OriginalMapReview']=p.get('mapReview');p['mapReview']=repaired_map
            timing.mark('sparse_geometry')
            from map_aspect import recover_map_aspect
            aspect_map=recover_map_aspect(rgb,p)
            if aspect_map is not p.get('mapReview'):
                if 'v2OriginalMapReview' not in p:p['v2OriginalMapReview']=p.get('mapReview')
                p['mapReview']=aspect_map
            timing.mark('aspect_geometry')
            p.pop('v2TrackedMap',None)
            p['v2TrackedMap']=tracker.observe({'png':raw,'packet':p,'atMs':f.get('atMs'),'sourcePtsMs':f.get('sourcePtsMs'),'windowKey':'offline:original-video','geometryVersion':f.get('geometryVersion','original')})
            timing.mark('preview_registration')
            p['v2PreviewContext']=inspect_preview_context(rgb,p)
            timing.mark('preview_controls')
            p['v2Preview']=inspect_preview_identity(rgb,p,context=p['v2PreviewContext'])
            timing.mark('preview_identity')
            p['v2MapActions']=inspect_map_actions(rgb,p)
            timing.mark('map_actions')
            p['ocrAnalysis']=bounded.take_metadata() if bounded else {'mode':'original_v1'}
            p['ocrAnalysis']['freshFullPipeline']=not bool(cache)
            p['analysisTiming']['elapsedMs']=(time.perf_counter()-started)*1000
            p['analysisTiming']['moduleMs']=timing.module_ms
            target=folder/f"{f['frameIndex']:07}.packet.json";target.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8');f['packet']=str(target.resolve());count+=1
            (out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
            if effective_observation_state(p)=='UNKNOWN':
                raise ValueError('UNKNOWN; failure packet preserved: '+str(target))
        print(json.dumps({'case':c['id'],'frames':count,'complete':True}),flush=True)
    m['analysis']['allFramesAnalyzed']=True
    (out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
