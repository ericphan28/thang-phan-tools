@echo off
cd /d "%~dp0backend"
set PYTHONPATH=%~dp0backend
python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000
pause
