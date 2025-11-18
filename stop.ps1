# Stop All Servers Script
# Sử dụng: .\stop.ps1

Write-Host "🛑 Đang dừng tất cả servers..." -ForegroundColor Yellow

# Dừng Python
Get-Process python -ErrorAction SilentlyContinue | Where-Object { 
    $_.Path -like "*utility-server*" -or $_.CommandLine -like "*uvicorn*" 
} | Stop-Process -Force -ErrorAction SilentlyContinue

# Dừng Node
Get-Process node -ErrorAction SilentlyContinue | Where-Object { 
    $_.CommandLine -like "*vite*" 
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "✅ Đã dừng tất cả servers!" -ForegroundColor Green

# Kiểm tra ports
$port8000 = netstat -ano | findstr ":8000" | findstr "LISTENING"
$port5173 = netstat -ano | findstr ":5173" | findstr "LISTENING"

if ($port8000) {
    Write-Host "⚠️  Port 8000 vẫn đang được sử dụng!" -ForegroundColor Yellow
}
if ($port5173) {
    Write-Host "⚠️  Port 5173 vẫn đang được sử dụng!" -ForegroundColor Yellow
}

if (-not $port8000 -and -not $port5173) {
    Write-Host "🎉 Tất cả ports đã được giải phóng!" -ForegroundColor Green
}
