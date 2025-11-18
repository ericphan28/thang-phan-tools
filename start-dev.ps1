# Script khởi động Backend và Frontend cho môi trường development
# Sử dụng: .\start-dev.ps1

Write-Host "🚀 Đang khởi động Utility Server..." -ForegroundColor Green
Write-Host ""

# Kiểm tra Python
Write-Host "✓ Kiểm tra Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  $pythonVersion" -ForegroundColor Gray
} catch {
    Write-Host "✗ Lỗi: Python không được cài đặt hoặc không có trong PATH" -ForegroundColor Red
    exit 1
}

# Kiểm tra Node.js
Write-Host "✓ Kiểm tra Node.js..." -ForegroundColor Cyan
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  Node.js $nodeVersion" -ForegroundColor Gray
} catch {
    Write-Host "✗ Lỗi: Node.js không được cài đặt hoặc không có trong PATH" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

# Khởi động Backend
Write-Host ""
Write-Host "🔧 Khởi động Backend Server..." -ForegroundColor Yellow
Write-Host "   URL: http://127.0.0.1:8000" -ForegroundColor Gray
Write-Host "   Docs: http://127.0.0.1:8000/docs" -ForegroundColor Gray
Write-Host ""

$backendJob = Start-Job -ScriptBlock {
    Set-Location "D:\thang\utility-server\backend"
    $env:PYTHONPATH = "D:\thang\utility-server\backend"
    python -m uvicorn app.main_simple:app --host 127.0.0.1 --port 8000 --reload
}

Start-Sleep -Seconds 3

# Khởi động Frontend
Write-Host "🎨 Khởi động Frontend Server..." -ForegroundColor Yellow
Write-Host "   URL: http://localhost:5173" -ForegroundColor Gray
Write-Host ""

$frontendJob = Start-Job -ScriptBlock {
    Set-Location "D:\thang\utility-server\frontend"
    npm run dev
}

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""
Write-Host "✅ Cả hai server đã được khởi động!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Truy cập ứng dụng tại:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "   Backend:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "   API Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Đăng nhập mặc định:" -ForegroundColor Cyan
Write-Host "   Username: admin" -ForegroundColor White
Write-Host "   Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""
Write-Host "⚠️  Nhấn Ctrl+C để dừng cả hai servers" -ForegroundColor Yellow
Write-Host ""

# Chờ người dùng nhấn Ctrl+C
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host ""
    Write-Host "🛑 Đang dừng servers..." -ForegroundColor Red
    Stop-Job -Job $backendJob
    Stop-Job -Job $frontendJob
    Remove-Job -Job $backendJob
    Remove-Job -Job $frontendJob
    Write-Host "✓ Đã dừng tất cả servers" -ForegroundColor Green
}
