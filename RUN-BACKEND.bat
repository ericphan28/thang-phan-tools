@echo off
title Backend Server (Port 8000)
cd /d "%~dp0backend"
set PYTHONPATH=%~dp0backend
echo ========================================
echo   BACKEND SERVER
echo ========================================
echo   Starting on http://0.0.0.0:8000
echo   Press Ctrl+C to stop
echo ========================================
echo.
python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000
