"""Training admission/budget tests; no model fitting occurs in this suite."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image
try:
    import train_export as subject
except ImportError:
    subject = None

class TrainingEntryTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(subject, 'bounded training entry is missing')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config = dict(modelArchitectureProposal='yolo26n', inputSize=640, precision='FP32', seed=20261108, maxEpochs=50, maxGpuSeconds=14400, maxTrainingRuns=1)

    def test_unreviewed_pool_cannot_consume_the_single_training_run(self):
        with self.assertRaisesRegex(ValueError, 'DATA_NOT_READY'):
            subject.prepare_run({'records': []}, self.config, self.root, self.root/'weights.pt', '0'*64)
        self.assertFalse((self.root/'training-attempt.json').exists())

    def test_unapproved_training_budget_or_model_cannot_start(self):
        for key,value in [('maxEpochs',51),('maxGpuSeconds',14401),('maxTrainingRuns',2),('seed',1),('inputSize',1280),('modelArchitectureProposal','yolo26s'),('precision','FP16')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                subject.validate_config(dict(self.config, **{key:value}))

    def test_exclusive_attempt_survives_failed_or_interrupted_run(self):
        subject.claim_attempt(self.root, {'status':'STARTED'})
        with self.assertRaises(FileExistsError):
            subject.claim_attempt(self.root, {'status':'STARTED'})
        self.assertEqual(json.loads((self.root/'training-attempt.json').read_text())['status'], 'STARTED')

    def test_yolo_box_uses_source_dimensions_without_clamp(self):
        line=subject.yolo_label({'className':'entry_gate','box':[20,10,40,20],'visibility':'partial'}, [100,50])
        parts=line.split(); self.assertEqual(parts[0],'1')
        self.assertEqual([float(x) for x in parts[1:]], [.4,.4,.4,.4])
        for box in ([90,0,20,10],[-1,0,10,10],[0,0,float('nan'),10]):
            with self.assertRaises(ValueError):
                subject.yolo_label({'className':'map_node','box':box,'visibility':'complete'},[100,50])

    def test_actual_pixels_not_self_declared_geometry(self):
        image=self.root/'source.png'; Image.new('RGB',(100,50)).save(image)
        record=dict(image=str(image), imageSha256=hashlib.sha256(image.read_bytes()).hexdigest(), pixelSha256='0'*64, sourceSize=[100,50])
        with self.assertRaisesRegex(ValueError,'PIXEL_HASH'):
            subject.verify_pixels(record)

    def test_epoch_and_wall_caps_independently_stop_training(self):
        self.assertFalse(subject.should_stop(epoch_index=48, elapsed_seconds=1))
        self.assertTrue(subject.should_stop(epoch_index=49, elapsed_seconds=1))
        self.assertTrue(subject.should_stop(epoch_index=0, elapsed_seconds=14400))

    def test_training_options_never_select_test_split_or_automatic_resume(self):
        options=subject.training_options('data.yaml','output')
        self.assertEqual(options['epochs'],50); self.assertEqual(options['seed'],20261108)
        self.assertEqual(options['device'],'cpu'); self.assertFalse(options['resume'])
        self.assertEqual(options['split'],'val'); self.assertIsNone(options['time'])  # Hard parent watchdog; library time mode must not override epochs.
        self.assertEqual(options['workers'],0); self.assertFalse(options['amp'])

class TrainingLaunchReviewTests(unittest.TestCase):
    def test_direct_worker_recipe_does_not_bypass_admission(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); weights=root/'weights.pt'; weights.write_bytes(b'not a model')
            recipe=root/'recipe.json'; recipe.write_text(json.dumps(dict(weights=str(weights),weightSha256=hashlib.sha256(weights.read_bytes()).hexdigest())))
            with self.assertRaisesRegex(ValueError,'UNAUTHORIZED_WORKER'):
                subject.worker(recipe)

    def test_nonapproved_weight_digest_cannot_become_approved_by_caller(self):
        with self.assertRaisesRegex(ValueError,'UNAPPROVED_WEIGHTS'):
            subject.validate_weight_digest('0'*64)

    def test_loaded_architecture_is_verified_in_addition_to_weight_hash(self):
        from types import SimpleNamespace
        wrong=SimpleNamespace(task='detect',model=SimpleNamespace(yaml={'yaml_file':'yolo26s.yaml','scale':'s'}))
        with self.assertRaisesRegex(ValueError,'UNAPPROVED_ARCHITECTURE'):
            subject.validate_loaded_model(wrong)

class OneUseWorkerTests(unittest.TestCase):
    def test_bound_recipe_can_launch_once_but_not_replay_or_be_modified(self):
        import os, subprocess, sys
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve(); recipe=root/'recipe.json'
            recipe.write_text(json.dumps(dict(output=str(root),reservation='test-reservation')),encoding='utf-8')
            (root/'training-attempt.json').write_text(json.dumps(dict(reservation='test-reservation',supervisorPid=os.getpid())),encoding='utf-8')
            (root/'launch-receipt.json').write_text(json.dumps(dict(reservation='test-reservation',supervisorPid=os.getpid(),recipeSha256=hashlib.sha256(recipe.read_bytes()).hexdigest())),encoding='utf-8')
            source=str(Path(subject.__file__).parent)
            script='import sys;sys.path.insert(0,sys.argv[1]);import train_export;train_export.claim_worker(sys.argv[2])'
            command=[sys.executable,'-B','-c',script,source,str(recipe)]
            first=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(first.returncode,0,first.stderr)
            second=subprocess.run(command,capture_output=True,text=True)
            self.assertNotEqual(second.returncode,0)
            self.assertIn('UNAUTHORIZED_WORKER',second.stderr)
            # A content edit is refused before a model can be imported.
            recipe.write_text(json.dumps(dict(output=str(root),reservation='different')),encoding='utf-8')
            third=subprocess.run(command,capture_output=True,text=True)
            self.assertIn('WORKER_BINDING',third.stderr)

class ProjectTrainingBudgetTests(unittest.TestCase):
    def test_changing_output_directory_does_not_reset_the_one_run_budget(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            subject.claim_training_attempt(root/'run-a', {'status':'RESERVED'}, root/'global-budget')
            with self.assertRaises(FileExistsError):
                subject.claim_training_attempt(root/'run-b', {'status':'RESERVED'}, root/'global-budget')
            self.assertFalse((root/'run-b/training-attempt.json').exists())

if __name__ == '__main__': unittest.main()
