"""MuMu Player 12 ADB bridge: discover, capture, tap, swipe. No game logic."""
import json, os, subprocess, time
from pathlib import Path

MUMU_ROOTS = [Path(r'C:\Program Files\Netease\MuMuPlayer'), Path(r'C:\Program Files\Netease\MuMuPlayer-12.0'),
              Path(r'D:\Program Files\Netease\MuMuPlayer'), Path(r'C:\Program Files\MuMuPlayer')]
FALLBACK_PORTS = [16384, 16416, 16448, 7555, 5555]
NO_WINDOW = 0x08000000 if os.name == 'nt' else 0


def _run(args, timeout=15, binary=False):
    r = subprocess.run(args, capture_output=True, timeout=timeout, creationflags=NO_WINDOW)
    if r.returncode != 0:
        raise RuntimeError(f'{args[1:4]} failed: {r.stderr.decode(errors="ignore").strip()}')
    return r.stdout if binary else r.stdout.decode('utf-8', errors='ignore')


def find_adb():
    env = os.environ.get('CRK_ADB')
    if env and Path(env).exists():
        return str(env)
    for root in MUMU_ROOTS:
        for sub in ('nx_main', 'shell', 'nx_device/12.0/shell'):
            p = root / sub / 'adb.exe'
            if p.exists():
                return str(p)
    return 'adb'


def mumu_ports():
    """Ask MuMuManager for running instances' adb ports (MuMu 12)."""
    ports = []
    for root in MUMU_ROOTS:
        mgr = root / 'nx_main' / 'MuMuManager.exe'
        if not mgr.exists():
            continue
        try:
            info = json.loads(_run([str(mgr), 'info', '-v', 'all']))
        except Exception:
            continue
        rows = info.values() if isinstance(info, dict) and 'index' not in info else [info]
        for row in rows:
            if isinstance(row, dict) and row.get('adb_port') and row.get('is_android_started', True):
                ports.append((row.get('adb_host_ip', '127.0.0.1'), int(row['adb_port'])))
    return ports


class Device:
    def __init__(self, serial=None, adb=None):
        self.adb = adb or find_adb()
        self.serial = serial or os.environ.get('CRK_SERIAL') or self._discover()
        self.size = self.screen_size()

    def _discover(self):
        candidates = [f'{h}:{p}' for h, p in mumu_ports()] + [f'127.0.0.1:{p}' for p in FALLBACK_PORTS]
        for s in dict.fromkeys(candidates):
            try:
                out = _run([self.adb, 'connect', s], timeout=6)
            except Exception:
                continue
            if 'connected' in out and 'cannot' not in out:
                try:
                    if _run([self.adb, '-s', s, 'get-state'], timeout=6).strip() == 'device':
                        return s
                except Exception:
                    pass
        raise RuntimeError('找不到 MuMu 的 ADB 連線；請確認模擬器已啟動且 ADB 已開啟')

    def sh(self, *cmd, timeout=15):
        return _run([self.adb, '-s', self.serial, 'shell', *map(str, cmd)], timeout=timeout)

    def screen_size(self):
        out = self.sh('wm', 'size')
        line = [l for l in out.splitlines() if 'size' in l.lower()][-1]
        w, h = map(int, line.split(':')[-1].strip().split('x'))
        return w, h

    def capture_png(self):
        data = _run([self.adb, '-s', self.serial, 'exec-out', 'screencap', '-p'], timeout=15, binary=True)
        if not data.startswith(b'\x89PNG'):
            raise RuntimeError('screencap 未回傳 PNG')
        return data

    def capture_raw(self):
        """Uncompressed screencap (much faster than -p). Returns PIL RGB image."""
        from PIL import Image
        data = _run([self.adb, '-s', self.serial, 'exec-out', 'screencap'], timeout=15, binary=True)
        w, h = int.from_bytes(data[0:4], 'little'), int.from_bytes(data[4:8], 'little')
        n = w * h * 4
        if w <= 0 or h <= 0 or len(data) < n + 12:
            raise RuntimeError('raw screencap 格式不符')
        body = data[-n:]
        return Image.frombuffer('RGBA', (w, h), body, 'raw', 'RGBA', 0, 1).convert('RGB')

    def capture(self):
        """Returns (PIL.Image RGB, capturedAt epoch seconds)."""
        t = time.time()
        try:
            img = self.capture_raw()
        except Exception:
            import io
            from PIL import Image
            img = Image.open(io.BytesIO(self.capture_png())).convert('RGB')
        return img, t

    def tap(self, x, y):
        self.sh('input', 'tap', int(round(x)), int(round(y)))

    def swipe(self, x1, y1, x2, y2, ms=400):
        self.sh('input', 'swipe', int(x1), int(y1), int(x2), int(y2), int(ms))

    def key(self, code):
        self.sh('input', 'keyevent', code)

    def foreground_package(self):
        out = self.sh('dumpsys', 'window')
        for l in out.splitlines():
            if 'mCurrentFocus' in l or 'mFocusedApp' in l:
                return l.strip()
        return ''
