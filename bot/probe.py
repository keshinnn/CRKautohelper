"""Read-only probe: connect to MuMu via ADB, save one screenshot + device facts. Sends NO input."""
import json, sys, time, traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
out = Path(__file__).parent / 'probe-out'; out.mkdir(exist_ok=True)
report = {'time': time.strftime('%Y-%m-%d %H:%M:%S')}
try:
    from adb_bridge import Device, find_adb, mumu_ports
    report['adb'] = find_adb(); report['mumuPorts'] = mumu_ports()
    d = Device(); report['serial'] = d.serial; report['size'] = d.size
    report['focus'] = d.foreground_package()
    times = []
    for i in range(3):
        t = time.perf_counter(); img, at = d.capture(); png=None; times.append(round((time.perf_counter() - t) * 1000))
        img.save(out / f"probe-{i}.png"); time.sleep(0.5)
    report['captureMs'] = times; report['imageSize'] = img.size; report['ok'] = True
except Exception as e:
    report['ok'] = False; report['error'] = repr(e); report['trace'] = traceback.format_exc()
(out / 'probe.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
