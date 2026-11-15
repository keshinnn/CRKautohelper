import json,sys,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'ml'),'F:/CRK helper/ml']
from bounded_ocr import BoundedOCRRuntime
from preview_context import inspect_preview_context


class PreviewTimerConflictTests(unittest.TestCase):
    def test_conflicting_qualified_fresh_clocks_cannot_be_filtered_to_expected_value(self):
        a=json.loads((ROOT/'artifacts/exploration-20261102-01/audit-summary.json').read_text(encoding='utf-8'))
        r=next(r for r in a['rows'] if r['number']==53)
        image=Image.open(r['criticalImage']).convert('RGB');p=json.loads(Path(r['criticalPacket']).read_text(encoding='utf-8'))
        readings=[{'text':text,'score':.99,'box':[[1,1],[70,1],[70,20],[1,20]]} for text in ['03:00','02:00']]
        with BoundedOCRRuntime(960) as runtime,patch.object(runtime,'previous_read',return_value=readings):
            self.assertFalse(inspect_preview_context(image,p)['verified'])


if __name__=='__main__':unittest.main()
