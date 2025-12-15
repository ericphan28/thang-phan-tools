@echo off
echo ================================
echo Starting Utility Server Stack
echo ================================
echo.

REM Kill existing processes
echo [1/4] Stopping existing servers...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start Backend
echo [2/4] Starting Backend Server (Port 8000)...
cd /d "%~dp0backend"
start "Backend Server" cmd /k "set PYTHONPATH=%CD% && python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul

REM Start Frontend
echo [3/4] Starting Frontend Dev Server (Port 5173)...
cd /d "%~dp0frontend"
start "Frontend Dev Server" cmd /k "npm run dev"
timeout /t 2 /nobreak >nul

REM Open browser
echo [4/4] Opening browser...
timeout /t 5 /nobreak >nul
start http://localhost:5173

echo.
echo ================================
echo ✅ All servers started!
echo ================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to close this window...
pause >nul
