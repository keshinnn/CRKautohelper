"""Read one saved PNG using V1's local image recognizers. No native I/O."""
import atexit, base64, hashlib, json, socket, sys
from pathlib import Path
from PIL import Image
sys.dont_write_bytecode = True
root, filename, frame_id = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), sys.argv[3]
socket.socket.connect = lambda *a, **k: (_ for _ in ()).throw(RuntimeError('network disabled in offline observer'))
sys.path.insert(0, str(root/'ml'))
from observation import inspect_capture
from frame_intermediates import FrameIntermediates
from progress_evidence import ProgressRuntime
progress_runtime=ProgressRuntime();progress_runtime.__enter__();atexit.register(progress_runtime.close)
from english_scene import EnglishSceneRuntime
english_runtime=EnglishSceneRuntime();english_runtime.__enter__();atexit.register(english_runtime.close)
raw = filename.read_bytes()
with Image.open(filename) as image:
    if image.format != 'PNG': raise ValueError('original PNG required; no implicit resize or re-encode')
    width, height = image.size
with FrameIntermediates(frame_id,hashlib.sha256(raw).hexdigest(),[width,height]) as intermediates:
    packet = inspect_capture('data:image/png;base64,'+base64.b64encode(raw).decode(),
        {'frameId':frame_id,'imageSha256':hashlib.sha256(raw).hexdigest(),'width':width,'height':height}, root/'data/flow')
    packet['observerContractVersion']=1
    from preview_identity import inspect_preview_identity
    from preview_context import inspect_preview_context
    from map_action_evidence import inspect_map_actions
    from sparse_map_geometry import recover_map_geometry
    from map_aspect import recover_map_aspect
    with Image.open(filename) as image:
        repaired_map=recover_map_geometry(image,packet)
        if repaired_map is not packet.get('mapReview'):
            packet['v2OriginalMapReview']=packet.get('mapReview');packet['mapReview']=repaired_map
        aspect_map=recover_map_aspect(image,packet)
        if aspect_map is not packet.get('mapReview'):
            if 'v2OriginalMapReview' not in packet:packet['v2OriginalMapReview']=packet.get('mapReview')
            packet['mapReview']=aspect_map
        packet['v2PreviewContext'] = inspect_preview_context(image, packet)
        packet['v2Preview'] = inspect_preview_identity(image, packet,context=packet['v2PreviewContext'])
        packet['v2MapActions'] = inspect_map_actions(image, packet)
packet['frameIntermediates']=intermediates.summary()
sys.stdout.reconfigure(encoding='utf-8')
print(json.dumps(packet, ensure_ascii=False))
