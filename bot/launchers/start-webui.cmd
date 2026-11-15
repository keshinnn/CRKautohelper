@echo off
title CRK Belowland control panel
cd /d "%~dp0"
".venv\Scripts\python.exe" -B bot\webui.py
pause
