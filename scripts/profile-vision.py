"""Run the unchanged observer under opt-in native/Python operation diagnostics."""
import argparse,cProfile,hashlib,json,os,pstats,runpy,subprocess,sys
from pathlib import Path


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    root=Path(__file__).resolve().parents[1];source=Path(args.source).resolve();out=Path(args.output).resolve();out.mkdir()
    sys.path.insert(0,str(root/'ml'));sys.path.insert(1,str(Path(os.environ.get('CRK_V1_ROOT','F:/CRK helper'))/'ml'))
    import cv2,numpy as np,map_vision,observation,fast_map_candidates,map_aspect,map_observer,stage_timing
    import flow_vision,text_reader,map_current
    from bounded_ocr import BoundedOCRRuntime
    from rapidocr_onnxruntime import RapidOCR
    from PIL import Image
    from operation_profile import OperationProfile
    original_init=stage_timing.StageTiming.__init__;original_mark=stage_timing.StageTiming.mark
    profiler=cProfile.Profile();profile=OperationProfile();error=None
    try:
        with profile:
            for name in ['matchTemplate','minMaxLoc','cvtColor','Canny','resize','findContours','inRange','threshold','connectedComponentsWithStats']:
                profile.hook(cv2,name,'cv2.'+name)
            for name in ['array','asarray']:profile.hook(np,name,'numpy.'+name)
            for name in ['convert','resize','crop','tobytes']:profile.hook(Image.Image,name,'PIL.'+name)
            for owner,names,prefix in [(map_vision,['inspect_map','classify_node','line_evidence'],'v1.map.'),
                (observation,['inspect_capture'],'v1.'),(fast_map_candidates,['node_candidates','_match_group'],'fast.'),
                (map_aspect,['estimate_pixel_aspect','_supplement_orange_candidates','_orange_node_pixel_geometry'],'aspect.'),
                (map_observer,['inspect_map'],'v2.map.'),
                (flow_vision,['inspect_frame'],'v1.flow.'),(text_reader,['read_text','refine_map_title','refine_map_progress'],'v1.text.'),
                (map_current,['inspect_current_node'],'v1.current.'),
                (BoundedOCRRuntime,['_read_with_progress','_reread_map_title','_reread_map_context','read_line_variants'],'ocr.bounded.'),
                (RapidOCR,['__call__','auto_text_det'],'ocr.engine.'),
                (RapidOCR.__init__.__globals__['TextRecognizer'],['__call__'],'ocr.recognizer.'),
                (RapidOCR.__init__.__globals__['TextClassifier'],['__call__'],'ocr.classifier.')]:
                for name in names:profile.hook(owner,name,prefix+name)
            def begin(self,*a,**kw):profile.begin_frame();original_init(self,*a,**kw)
            def mark(self,name):original_mark(self,name);profile.finish_stage(name)
            stage_timing.StageTiming.__init__=begin;stage_timing.StageTiming.mark=mark
            sys.argv=['ml/analyze_cases.py',str(source),str(out/'analysis'),'--fast-map','--bounded-ocr','960']
            profiler.enable()
            try:runpy.run_path(str(root/'ml/analyze_cases.py'),run_name='__main__')
            finally:profiler.disable()
    except BaseException as e:error=repr(e)
    finally:
        stage_timing.StageTiming.__init__=original_init;stage_timing.StageTiming.mark=original_mark
        profiler.dump_stats(str(out/'python.prof'))
        report=profile.summary();report.update(error=error,sourceManifestSha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            runnerSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip(),
            nativeActions=0,crossFrameCache=False)
        (out/'operations.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        rows=[]
        try:stats=pstats.Stats(profiler).stats
        except TypeError:stats={}
        for (file,line,name),(primitive,calls,self_s,cumulative_s,callers) in stats.items():
            rows.append({'file':file,'line':line,'name':name,'primitiveCalls':primitive,'calls':calls,'selfMs':self_s*1000,'cumulativeMs':cumulative_s*1000})
        (out/'python-functions.json').write_text(json.dumps(sorted(rows,key=lambda r:-r['cumulativeMs']),indent=2),encoding='utf-8')
    if error:raise RuntimeError(error)
    print(json.dumps({'frames':report['frames'],'diagnosticOnly':True,'operationGroups':len(report['operations'])}),flush=True)


if __name__=='__main__':main()
