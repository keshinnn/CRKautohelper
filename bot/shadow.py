import runpy, sys
from pathlib import Path
sys.argv = [sys.argv[0]] + sys.argv[1:]
runpy.run_path(str(Path(__file__).parent / "selfcheck" / "video_shadow.py"), run_name="__main__")
