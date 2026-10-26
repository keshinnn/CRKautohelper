import sys,types,unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))
from operation_profile import OperationProfile

class OperationProfileTests(unittest.TestCase):
    def test_worker_calls_are_counted_and_attributed_to_the_frame_stage(self):
        owner=types.SimpleNamespace(work=lambda x:x*2)
        with OperationProfile() as p:
            p.hook(owner,'work','native_work');p.begin_frame()
            with ThreadPoolExecutor(max_workers=2) as pool:self.assertEqual(list(pool.map(owner.work,[1,2,3])),[2,4,6])
            p.finish_stage('aspect_geometry')
        rows=p.summary()['operations'];self.assertEqual(sum(r['calls'] for r in rows),3)
        self.assertTrue(all(r['stage']=='aspect_geometry' and r['frame']==1 for r in rows));self.assertTrue(all(r['mainThreadCalls']==0 for r in rows))

    def test_exception_restores_original_and_preserves_return_identity(self):
        value=[]
        def work():return value
        owner=types.SimpleNamespace(work=work)
        with self.assertRaisesRegex(RuntimeError,'stop'):
            with OperationProfile() as p:
                p.hook(owner,'work');p.begin_frame();self.assertIs(owner.work(),value);raise RuntimeError('stop')
        self.assertIs(owner.work,work)

    def test_failed_operation_preserves_exception_and_is_measured(self):
        def fail():raise ValueError('original')
        owner=types.SimpleNamespace(fail=fail)
        with OperationProfile() as p:
            p.hook(owner,'fail');p.begin_frame()
            with self.assertRaisesRegex(ValueError,'original'):owner.fail()
            p.finish_stage('v1_observation')
        row=p.summary()['operations'][0];self.assertEqual(row['failures'],1);self.assertGreaterEqual(row['elapsedMs'],0)

    def test_intervals_do_not_relabel_previous_frame_and_include_shape(self):
        class Input:shape=(10,20,3)
        owner=types.SimpleNamespace(work=lambda x:x)
        with OperationProfile() as p:
            p.hook(owner,'work');p.begin_frame();owner.work(Input());p.finish_stage('v1_observation')
            p.begin_frame();owner.work(Input());p.finish_stage('aspect_geometry')
        rows=p.summary()['operations'];self.assertEqual([(r['frame'],r['stage']) for r in rows],[(1,'v1_observation'),(2,'aspect_geometry')]);self.assertIn([10,20,3],rows[0]['inputShapes'])

if __name__=='__main__':unittest.main()
