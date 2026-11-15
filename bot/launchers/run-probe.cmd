@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" -B bot\probe.py
echo.
echo Done. See bot\probe-out\probe.json
timeout /t 8
