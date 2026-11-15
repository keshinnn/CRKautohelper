"""Pixel-only independent research OCR pass. No intent or previous labels."""
import hashlib,json,sys
from pathlib import Path
from PIL import Image
sys.dont_write_bytecode=True
sys.path.insert(0,'F:/CRK helper/ml')
from text_reader import read_text
from flow_vision import semantic_state
rows=[]
for name in sys.argv[2:]:
    file=Path(name);raw=file.read_bytes()
    with Image.open(file) as im:
        rgb=im.convert('RGB')
    evidence=read_text(rgb)
    if hashlib.sha256(file.read_bytes()).hexdigest()!=hashlib.sha256(raw).hexdigest():
        raise ValueError('IMAGE_CHANGED')
    rows.append(dict(image=str(file.resolve()),imageSha256=hashlib.sha256(raw).hexdigest(),
        pixelSha256=hashlib.sha256(rgb.tobytes()).hexdigest(),size=list(rgb.size),evidence=evidence,
        originalSemantic=semantic_state(evidence)))
Path(sys.argv[1]).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
