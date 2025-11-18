@echo off
echo ================================================
echo   UTILITY SERVER - QUICK START
echo ================================================
echo.
echo Starting Backend and Frontend servers...
echo.

REM Start Backend in new window
start "Backend Server (Port 8000)" cmd /k "%~dp0start-backend.bat"
timeout /t 3 /nobreak > nul

REM Start Frontend in new window  
start "Frontend Server (Port 5173)" cmd /k "%~dp0start-frontend.bat"

echo.
echo ================================================
echo   Servers are starting...
echo ================================================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo ================================================
echo.
echo Close this window when done.
pause
