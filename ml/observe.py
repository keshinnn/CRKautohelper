"""Read one saved PNG using V1's local image recognizers. No native I/O."""
import base64, hashlib, json, socket, sys
from pathlib import Path
from PIL import Image
sys.dont_write_bytecode = True
root, filename, frame_id = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), sys.argv[3]
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(RuntimeError('network disabled in offline observer'))
sys.path.insert(0, str(root/'ml'))
from observation import inspect_capture
raw = filename.read_bytes()
with Image.open(filename) as image:
    if image.format != 'PNG': raise ValueError('original PNG required; no implicit resize or re-encode')
    width, height = image.size
packet = inspect_capture('data:image/png;base64,'+base64.b64encode(raw).decode(),
    {'frameId':frame_id,'imageSha256':hashlib.sha256(raw).hexdigest(),'width':width,'height':height}, root/'data/flow')
sys.stdout.reconfigure(encoding='utf-8')
print(json.dumps(packet, ensure_ascii=False))
