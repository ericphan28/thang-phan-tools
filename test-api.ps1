# Test Backend API
Write-Host "`n=== TESTING BACKEND API ===" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "`n1. Testing Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    Write-Host "OK - Backend is running!" -ForegroundColor Green
    $health | ConvertTo-Json
} catch {
    Write-Host "FAILED - Backend not running!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Test 2: Login with admin
Write-Host "`n2. Testing Login with admin/admin123..." -ForegroundColor Yellow
try {
    $loginData = @{
        username = "admin"
        password = "admin123"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -Body $loginData -ContentType "application/json"
    Write-Host "OK - Login successful!" -ForegroundColor Green
    Write-Host "Access Token: $($response.access_token.Substring(0,50))..." -ForegroundColor White
    Write-Host "User: $($response.user.username)" -ForegroundColor White
} catch {
    Write-Host "FAILED - Login failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Test 3: Login with custom user
Write-Host "`n3. Testing Login with cym_sunset@yahoo.com..." -ForegroundColor Yellow
try {
    $loginData = @{
        username = "cym_sunset@yahoo.com"
        password = "Tnt@9961266"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -Body $loginData -ContentType "application/json"
    Write-Host "OK - Login successful!" -ForegroundColor Green
    Write-Host "Access Token: $($response.access_token.Substring(0,50))..." -ForegroundColor White
    Write-Host "User: $($response.user.email)" -ForegroundColor White
} catch {
    Write-Host "FAILED - Login failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host "`n=== TEST COMPLETE ===" -ForegroundColor Cyan
Write-Host "`nFrontend URL: http://localhost:5173" -ForegroundColor White
Write-Host "Backend URL:  http://localhost:8000/docs" -ForegroundColor White
