# Restart All Servers Script
# Sử dụng: .\restart.ps1

Write-Host "🔄 Đang restart servers..." -ForegroundColor Cyan

# Stop trước
& "$PSScriptRoot\stop.ps1"

# Đợi 2 giây
Start-Sleep -Seconds 2

# Start lại
& "$PSScriptRoot\start.ps1"
