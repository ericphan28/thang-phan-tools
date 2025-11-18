@echo off
echo ========================================
echo    CHECKING SERVERS STATUS
echo ========================================
echo.

echo [1/4] Checking Backend (Port 8000)...
curl -s http://localhost:8000/health > nul 2>&1
if %ERRORLEVEL% == 0 (
    echo   Backend: OK - Running
) else (
    echo   Backend: FAILED - Not responding
)

echo.
echo [2/4] Checking Frontend (Port 5173)...
curl -s http://localhost:5173 > nul 2>&1
if %ERRORLEVEL% == 0 (
    echo   Frontend: OK - Running
) else (
    echo   Frontend: FAILED - Not responding
)

echo.
echo [3/4] Process Status:
powershell -Command "Get-Process python,node -ErrorAction SilentlyContinue | Select-Object ProcessName,Id,StartTime | Format-Table"

echo.
echo [4/4] Port Status:
echo   Port 8000:
netstat -ano | findstr ":8000" | findstr "LISTENING"
echo   Port 5173:
netstat -ano | findstr ":5173" | findstr "LISTENING"

echo.
echo ========================================
echo   Press any key to exit...
echo ========================================
pause > nul
