@echo off
title CRK bot agent
cd /d "%~dp0"
".venv\Scripts\python.exe" -B bot\agent.py
pause
