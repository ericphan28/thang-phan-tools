@echo off
echo.
echo ================================================
echo   UTILITY SERVER - QUICK START
echo ================================================
echo.
echo Cleaning old processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul
echo.

echo Starting Backend...
start "Backend (Port 8000)" "%~dp0RUN-BACKEND.bat"
timeout /t 3 /nobreak >nul

echo Starting Frontend...
start "Frontend (Port 5173)" "%~dp0RUN-FRONTEND.bat"

echo.
echo ================================================
echo   SERVERS STARTED!
echo ================================================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo ================================================
echo.
echo   Login: admin / admin123
echo.
echo   Close CMD windows to stop servers
echo ================================================
echo.
pause
