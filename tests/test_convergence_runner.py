import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def module():
    spec=importlib.util.spec_from_file_location('convergence_regression',ROOT/'scripts/convergence-regression.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class ConvergenceRunnerTests(unittest.TestCase):
    def test_fixed_milestone_keeps_original_ids_and_uses_frozen_scale_grader(self):
        m=module();manifest=ROOT/'artifacts/convergence-20261026/fixed15-final-02/manifest.json'
        source=json.loads(manifest.read_text(encoding='utf-8'));before=json.dumps(source,sort_keys=True)
        command=m.replay_command(manifest,Path('out'),source)
        self.assertEqual(command,['node','scripts/accept-replay.cjs',str(manifest),'data/p4a/cases.json','out'])
        self.assertEqual(json.dumps(source,sort_keys=True),before)
        self.assertIn('zone-1-first-battle-scale-0.75',[c['id'] for c in source['cases']])
        self.assertEqual(m.replay_command(Path('development.json'),Path('out'),{'cases':[]}),['node','scripts/replay-development.cjs','development.json','out'])
        with self.assertRaises(ValueError):m.replay_command(manifest,Path('out'),{**source,'transform':'unknown'})

    def test_external_producers_templates_and_ocr_assets_cannot_change_undetected(self):
        m=module()
        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts') as tmp:
            root=Path(tmp);v1=root/'v1';ocr=root/'ocr'
            for p in [v1/'ml',v1/'data/map',v1/'data/flow',ocr/'models']:p.mkdir(parents=True)
            files=[v1/'ml/map_vision.py',v1/'data/map/node.png',ocr/'models/model.onnx']
            for p in files:p.write_bytes(b'before')
            runtime={'packageRoot':str(ocr),'ocrAssets':[{'path':'models/model.onnx'}]}
            before=m.dependency_snapshot(v1,runtime)
            for p in files:
                p.write_bytes(b'after');self.assertNotEqual(m.dependency_snapshot(v1,runtime),before);p.write_bytes(b'before')

    def test_source_hash_snapshot_detects_changed_and_new_runner_files(self):
        m=module()
        with tempfile.TemporaryDirectory(dir=ROOT/'artifacts') as tmp:
            root=Path(tmp);(root/'scripts').mkdir();p=root/'scripts/driver.py';p.write_text('before')
            old=m.code_snapshot(root);m.check_snapshot(root,old)
            p.write_text('after')
            with self.assertRaises(ValueError):m.check_snapshot(root,old)
            p.write_text('before');(root/'scripts/other.py').write_text('new')
            with self.assertRaises(ValueError):m.check_snapshot(root,old)

    def test_merging_cannot_relabel_or_drop_source_frames(self):
        m=module();source={'cases':[{'id':'one','intent':{'zone':1},'frames':[{'sha256':'a','atMs':1}]}]}
        good={'cases':[{'id':'one','intent':{'zone':1},'frames':[{'sha256':'a','atMs':1,'packet':'out'}]}]}
        self.assertEqual(m.merge_cases(source,[good])[0]['id'],'one')
        for mutate in [lambda c:c.update(intent={'zone':2}),lambda c:c.update(frames=[]),lambda c:c['frames'][0].update(sha256='b')]:
            bad=json.loads(json.dumps(good));mutate(bad['cases'][0])
            with self.assertRaises(ValueError):m.merge_cases(source,[bad])

if __name__=='__main__':unittest.main()
