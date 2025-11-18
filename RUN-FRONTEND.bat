@echo off
title Frontend Server (Port 5173)
cd /d "%~dp0frontend"
echo ========================================
echo   FRONTEND SERVER
echo ========================================
echo   Starting on http://localhost:5173
echo   Press Ctrl+C to stop
echo ========================================
echo.
call npm run dev
