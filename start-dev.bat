@echo off
chcp 65001 > nul
title Utility Server - Development

echo.
echo ╔════════════════════════════════════════════╗
echo ║   🚀 Utility Server Development Mode      ║
echo ╚════════════════════════════════════════════╝
echo.

echo [1/2] Khởi động Backend (Port 8000)...
start "Backend Server" /D "D:\thang\utility-server\backend" cmd /k "set PYTHONPATH=D:\thang\utility-server\backend && python -m uvicorn app.main_simple:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak > nul

echo [2/2] Khởi động Frontend (Port 5173)...
start "Frontend Server" /D "D:\thang\utility-server\frontend" cmd /k "npm run dev"

timeout /t 2 /nobreak > nul

echo.
echo ✅ Đã khởi động cả hai servers!
echo.
echo 📍 Truy cập:
echo    Frontend: http://localhost:5173
echo    Backend:  http://127.0.0.1:8000
echo    API Docs: http://127.0.0.1:8000/docs
echo.
echo 🔐 Đăng nhập: admin / admin123
echo.
echo ⚠️  Đóng cửa sổ terminal để dừng servers
echo.
pause
