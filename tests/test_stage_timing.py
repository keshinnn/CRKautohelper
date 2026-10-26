import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ml'))

class StageTimingTests(unittest.TestCase):
    def test_module_durations_partition_real_monotonic_intervals(self):
        from stage_timing import StageTiming
        values=iter([1,1.125,1.375]);timer=StageTiming(clock=lambda:next(values))
        timer.mark('decode');timer.mark('vision')
        self.assertEqual(timer.module_ms,{'decode':125,'vision':250})

    def test_duplicate_stage_names_cannot_hide_previous_elapsed_time(self):
        from stage_timing import StageTiming
        timer=StageTiming();timer.mark('vision')
        with self.assertRaises(ValueError):timer.mark('vision')

if __name__=='__main__':unittest.main()
