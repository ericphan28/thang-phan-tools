Write-Host "Testing Backend Health..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri 'http://localhost:8000/health' -Method Get -TimeoutSec 5
    Write-Host "✅ Backend is healthy!" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "❌ Backend health check failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
