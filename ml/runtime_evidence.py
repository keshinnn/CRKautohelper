"""Read-only fingerprints of the actual offline OCR assets and dependencies."""
import hashlib
import importlib.metadata
import importlib.util
import json
import platform
from pathlib import Path


def capture_runtime_evidence():
    package=Path(importlib.util.find_spec('rapidocr_onnxruntime').origin).parent
    required=['ch_PP-OCRv4_det_infer.onnx','ch_PP-OCRv4_rec_infer.onnx','ch_ppocr_mobile_v2.0_cls_infer.onnx']
    models=[package/'models'/name for name in required]
    if any(not p.is_file() for p in models):raise ValueError('OCR_MODEL_ASSET_MISSING')
    paths=sorted(set(models+list(package.rglob('*.py'))+list(package.rglob('*.yaml'))))
    assets=[]
    for p in paths:
        raw=p.read_bytes()
        assets.append({'path':p.relative_to(package).as_posix(),'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    versions={name:importlib.metadata.version(name) for name in ['Pillow','numpy','opencv-python','rapidocr-onnxruntime','onnxruntime']}
    payload={'schema':1,'python':platform.python_version(),'platform':platform.platform(),'versions':versions,'ocrAssets':assets}
    fingerprint=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {**payload,'fingerprint':fingerprint,'packageRoot':str(package),'readOnly':True}
