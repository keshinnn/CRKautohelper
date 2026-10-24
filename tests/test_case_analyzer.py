import hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path

class OfflineAnalyzerTests(unittest.TestCase):
    def test_changed_language_or_progress_code_invalidates_cached_legacy_semantics(self):
        root=Path(__file__).resolve().parents[1]
        original=json.loads((root/'artifacts/p4c-LX46-dev-analysis-02/manifest.json').read_text(encoding='utf-8'))
        entry=original['cases'][0]['frames'][0]
        with tempfile.TemporaryDirectory(prefix='crk-language-cache-',dir=root/'artifacts') as folder:
            folder=Path(folder);source=folder/'source.json'
            source.write_text(json.dumps({'cases':[{'id':'language-cache','videoSha256':original['cases'][0]['videoSha256'],'frames':[{k:v for k,v in entry.items() if k!='packet'}]}]}),encoding='utf-8')
            for key in ['englishSceneCodeSha256','progressCodeSha256']:
                cache=json.loads(json.dumps(original));cache['analysis'][key]='a'*64
                cachefile=folder/(key+'.json');cachefile.write_text(json.dumps(cache),encoding='utf-8');out=folder/key
                r=subprocess.run([sys.executable,'-B',str(root/'ml/analyze_cases.py'),str(source),str(out),'--fast-map','--bounded-ocr','960','--cache',str(cachefile)],capture_output=True,text=True,encoding='utf-8')
                self.assertEqual(r.returncode,0,r.stderr)
                m=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
                packet=json.loads(Path(m['cases'][0]['frames'][0]['packet']).read_text(encoding='utf-8'))
                self.assertTrue(packet['analysisTiming']['freshFullPipeline'])
                self.assertEqual(m['analysis']['cacheIgnoredReason'],'SEMANTIC_RUNTIME_CHANGED_OR_UNBOUND')

    def test_case_source_rejects_missing_malformed_and_conflicting_claims(self):
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
        from analyze_cases import case_source_sha,source_frame_id
        self.assertEqual(case_source_sha({'videoSha256':'a'*64},{}),'a'*64)
        self.assertEqual(case_source_sha({}, {'source':{'videoSha256':'b'*64}}),'b'*64)
        for manifest,case in [({},{}),({}, {'videoSha256':'not-sha'}),({}, {'videoSha256':'a'*64,'source':{'videoSha256':'b'*64}})]:
            with self.assertRaises(ValueError):case_source_sha(manifest,case)
        for index in [-1,1.5,True]:
            with self.assertRaises(ValueError):source_frame_id('a'*64,index,'b'*64)

    def test_multisource_frames_and_cache_are_bound_to_each_video(self):
        root=Path(__file__).resolve().parents[1];image=root/'artifacts/p4a-native/0002550.png';digest=hashlib.sha256(image.read_bytes()).hexdigest()
        entry={'image':str(image),'sha256':digest,'frameIndex':2550,'size':[1440,1080]}
        with tempfile.TemporaryDirectory(prefix='crk-multisource-',dir=root/'artifacts') as folder:
            folder=Path(folder);source=folder/'source.json'
            data={'cases':[{'id':'source-a','videoSha256':'a'*64,'frames':[entry.copy()]},{'id':'source-b','videoSha256':'b'*64,'frames':[entry.copy()]}]}
            source.write_text(json.dumps(data),encoding='utf-8');out=folder/'first'
            args=[sys.executable,'-B',str(root/'ml/analyze_cases.py')]
            r=subprocess.run([*args,str(source),str(out),'--fast-map','--bounded-ocr','960'],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(r.returncode,0,r.stderr)
            m=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
            packets=[json.loads(Path(c['frames'][0]['packet']).read_text(encoding='utf-8')) for c in m['cases']]
            self.assertNotEqual(packets[0]['binding']['frameId'],packets[1]['binding']['frameId'])
            for video,p in zip(['a'*64,'b'*64],packets):
                self.assertEqual(p['binding']['frameId'],hashlib.sha256((video+'2550'+digest).encode()).hexdigest()[:32])
                self.assertEqual(p['sourceBinding'],{'videoSha256':video,'frameIndex':2550,'imageSha256':digest})
            m['cases']=m['cases'][:1];cache=folder/'cache.json';cache.write_text(json.dumps(m),encoding='utf-8')
            second=folder/'second'
            r=subprocess.run([*args,str(source),str(second),'--fast-map','--bounded-ocr','960','--cache',str(cache)],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(r.returncode,0,r.stderr)
            m2=json.loads((second/'manifest.json').read_text(encoding='utf-8'))
            p2=[json.loads(Path(c['frames'][0]['packet']).read_text(encoding='utf-8')) for c in m2['cases']]
            self.assertFalse(p2[0]['analysisTiming']['freshFullPipeline'])
            self.assertTrue(p2[1]['analysisTiming']['freshFullPipeline'])
            self.assertEqual(p2[1]['binding']['frameId'],packets[1]['binding']['frameId'])

    def test_bounded_mode_recomputes_original_ocr_cache_and_records_actual_tensor_sizes(self):
        root=Path(__file__).resolve().parents[1];image=root/'artifacts/p4a-native/0002550.png'
        old=json.loads((root/'artifacts/p4a-first-preview-v2/observation.json').read_text(encoding='utf-8'))['rawPacket']
        self.assertEqual(old['binding']['imageSha256'],hashlib.sha256(image.read_bytes()).hexdigest())
        with tempfile.TemporaryDirectory(prefix='crk-bounded-',dir=root/'artifacts') as folder:
            folder=Path(folder);packet=folder/'old.json';packet.write_text(json.dumps(old),encoding='utf-8')
            entry={'image':str(image),'sha256':old['binding']['imageSha256'],'frameIndex':2550,'size':[1440,1080]}
            data={'videoSha256':'a'*64,'cases':[{'id':'test','frames':[entry]}]};source=folder/'source.json';source.write_text(json.dumps(data),encoding='utf-8')
            cache=folder/'cache.json';cache.write_text(json.dumps({'analysis':{'ocrPreprocessing':{'mode':'original_v1'}},'cases':[{'frames':[{**entry,'packet':str(packet)}]}]}),encoding='utf-8');out=folder/'result'
            r=subprocess.run([sys.executable,'-B',str(root/'ml/analyze_cases.py'),str(source),str(out),'--fast-map','--bounded-ocr','960','--cache',str(cache)],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(r.returncode,0,r.stderr)
            m=json.loads((out/'manifest.json').read_text(encoding='utf-8'));p=json.loads(Path(m['cases'][0]['frames'][0]['packet']).read_text(encoding='utf-8'))
            self.assertTrue(p['analysisTiming']['freshFullPipeline']);self.assertTrue(p['v2Preview']['verified'])
            self.assertEqual(m['analysis']['cacheIgnoredReason'],'OCR_PREPROCESSING_CHANGED')
            self.assertEqual(p['ocrAnalysis']['maximumTensorSide'],960);self.assertGreater(len(p['ocrAnalysis']['detectorCalls']),0)
            for call in p['ocrAnalysis']['detectorCalls']:self.assertLessEqual(max(call['tensorSize']),960)

    def test_matching_ocr_mode_cannot_reuse_unbound_or_changed_runtime_cache(self):
        root=Path(__file__).resolve().parents[1];image=root/'artifacts/p4a-native/0002550.png'
        old=json.loads((root/'artifacts/p4a-first-preview-v2/observation.json').read_text(encoding='utf-8'))['rawPacket']
        with tempfile.TemporaryDirectory(prefix='crk-runtime-',dir=root/'artifacts') as folder:
            folder=Path(folder);packet=folder/'old.json';packet.write_text(json.dumps(old),encoding='utf-8')
            entry={'image':str(image),'sha256':old['binding']['imageSha256'],'frameIndex':2550,'size':[1440,1080]}
            source=folder/'source.json';source.write_text(json.dumps({'videoSha256':'a'*64,'cases':[{'id':'test','frames':[entry]}]}),encoding='utf-8')
            cache=folder/'cache.json';cache.write_text(json.dumps({'analysis':{'runtimeEvidence':{'fingerprint':'0'*64}},'cases':[{'frames':[{**entry,'packet':str(packet)}]}]}),encoding='utf-8')
            out=folder/'result'
            r=subprocess.run([sys.executable,'-B',str(root/'ml/analyze_cases.py'),str(source),str(out),'--fast-map','--cache',str(cache)],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(r.returncode,0,r.stderr)
            m=json.loads((out/'manifest.json').read_text(encoding='utf-8'));p=json.loads(Path(m['cases'][0]['frames'][0]['packet']).read_text(encoding='utf-8'))
            self.assertTrue(p['analysisTiming']['freshFullPipeline'])
            self.assertEqual(m['analysis']['cacheIgnoredReason'],'OCR_RUNTIME_CHANGED_OR_UNBOUND')
            self.assertEqual(len(m['analysis']['runtimeEvidence']['fingerprint']),64)
            runtime=m['analysis']['runtimeEvidence']
            models=[a for a in runtime['ocrAssets'] if a['path'].endswith('.onnx')]
            self.assertEqual(len(models),3)
            for asset in models:
                actual=Path(runtime['packageRoot'])/asset['path']
                self.assertEqual(hashlib.sha256(actual.read_bytes()).hexdigest(),asset['sha256'])
                self.assertEqual(actual.stat().st_size,asset['size'])
            self.assertTrue(all(runtime['versions'].values()))

    def test_batch_stream_recomputes_pixel_registration_without_intent_or_truth(self):
        root=Path(__file__).resolve().parents[1];frames=[]
        for index in [23724,23730,23745]:
            image=root/f'artifacts/p4c-registration-dev-source/{index:07}.png'
            frames.append({'image':str(image),'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'frameIndex':index,'size':[1440,1080],'atMs':round(index/30*1000,6),'sourcePtsMs':round(index/30*1000,6),'geometryVersion':'original'})
        with tempfile.TemporaryDirectory(prefix='crk-track-',dir=root/'artifacts') as folder:
            source=Path(folder)/'source.json';source.write_text(json.dumps({'videoSha256':'a'*64,'cases':[{'id':'test-stream','frames':frames}]}),encoding='utf-8');out=Path(folder)/'result'
            r=subprocess.run([sys.executable,'-B',str(root/'ml/analyze_cases.py'),str(source),str(out),'--fast-map'],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(r.returncode,0,r.stderr)
            m=json.loads((out/'manifest.json').read_text(encoding='utf-8'));p=json.loads(Path(m['cases'][0]['frames'][-1]['packet']).read_text(encoding='utf-8'))
            self.assertTrue(p['v2Preview']['verified'])
            self.assertEqual(p['v2TrackedMap']['sourceImageSha256'],frames[0]['sha256'])

    def test_saved_png_binding_and_independent_identity_survive_batch_entry(self):
        root=Path(__file__).resolve().parents[1];image=root/'artifacts/p4a-native/0002550.png';before=image.read_bytes()
        with tempfile.TemporaryDirectory(prefix='crk-analyzer-',dir=root/'artifacts') as folder:
            manifest=Path(folder)/'source.json';manifest.write_text(json.dumps({'videoSha256':'a'*64,'cases':[{'id':'test','frames':[{'image':str(image),'sha256':hashlib.sha256(before).hexdigest(),'frameIndex':2550,'size':[1440,1080]}]}]}),encoding='utf-8')
            output=Path(folder)/'result'
            result=subprocess.run([sys.executable,'-B',str(root/'ml/analyze_cases.py'),str(manifest),str(output)],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stderr)
            generated=json.loads((output/'manifest.json').read_text(encoding='utf-8'));packet=json.loads(Path(generated['cases'][0]['frames'][0]['packet']).read_text(encoding='utf-8'))
            self.assertEqual(packet['binding']['imageSha256'],hashlib.sha256(before).hexdigest())
            self.assertTrue(packet['v2Preview']['verified'])
            self.assertFalse(packet['actionsExecuted'])
            self.assertTrue(packet['v2MapActions']['verified'])
            self.assertEqual(packet['v2MapActions']['pixelSha256'],packet['binding']['pixelSha256'])
            self.assertEqual(image.read_bytes(),before)
    def test_incomplete_failure_cache_does_not_discard_unprocessed_frames(self):
        root=Path(__file__).resolve().parents[1];image=root/'artifacts/p4a-native/0002550.png'
        with tempfile.TemporaryDirectory(prefix='crk-partial-',dir=root/'artifacts') as folder:
            data={'videoSha256':'a'*64,'cases':[{'id':'test','frames':[{'image':str(image),'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'frameIndex':2550,'size':[1440,1080]}]}]}
            source=Path(folder)/'source.json';source.write_text(json.dumps(data),encoding='utf-8');output=Path(folder)/'result'
            r=subprocess.run([sys.executable,'-B',str(root/'ml/analyze_cases.py'),str(source),str(output),'--cache',str(source)],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(r.returncode,0,r.stderr)
            m=json.loads((output/'manifest.json').read_text(encoding='utf-8'));packet=json.loads(Path(m['cases'][0]['frames'][0]['packet']).read_text(encoding='utf-8'))
            self.assertTrue(packet['analysisTiming']['freshFullPipeline'])
    def test_fast_backend_keeps_original_source_binding_and_identity(self):
        root=Path(__file__).resolve().parents[1];image=root/'artifacts/p4a-native/0002550.png'
        with tempfile.TemporaryDirectory(prefix='crk-fast-',dir=root/'artifacts') as folder:
            data={'videoSha256':'a'*64,'cases':[{'id':'test','frames':[{'image':str(image),'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'frameIndex':2550,'size':[1440,1080]}]}]}
            source=Path(folder)/'source.json';source.write_text(json.dumps(data),encoding='utf-8');output=Path(folder)/'result'
            r=subprocess.run([sys.executable,'-B',str(root/'ml/analyze_cases.py'),str(source),str(output),'--fast-map'],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(r.returncode,0,r.stderr)
            m=json.loads((output/'manifest.json').read_text(encoding='utf-8'));self.assertEqual(m['analysis']['mapBackend'],'exact_grouped_masks_parallel4')
            p=json.loads(Path(m['cases'][0]['frames'][0]['packet']).read_text(encoding='utf-8'));self.assertTrue(p['v2Preview']['verified']);self.assertEqual(p['v2Preview']['selectedNode']['column'],2)

if __name__=='__main__':unittest.main()
