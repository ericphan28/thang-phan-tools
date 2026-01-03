# Diagnose 502 Bad Gateway Error
# Quick script to check production server status

$server = "tienich.giakiemso.com"
$serverIP = "165.99.59.47"

Write-Host "`n╔══════════════════════════════════════════════╗" -ForegroundColor Red
Write-Host "║      502 BAD GATEWAY DIAGNOSTICS            ║" -ForegroundColor Red
Write-Host "╚══════════════════════════════════════════════╝`n" -ForegroundColor Red

# Test 1: Server connectivity
Write-Host "[1] Server Connectivity" -ForegroundColor Cyan
Write-Host "    Testing $server ($serverIP)..."
$ping = Test-Connection -ComputerName $serverIP -Count 2 -Quiet
if($ping) {
    Write-Host "    ✓ Server is online`n" -ForegroundColor Green
} else {
    Write-Host "    ✗ Server is offline!`n" -ForegroundColor Red
    exit 1
}

# Test 2: Nginx (port 80)
Write-Host "[2] Nginx Web Server" -ForegroundColor Cyan
try {
    $nginx = Invoke-WebRequest "http://$server" -TimeoutSec 5 -UseBasicParsing
    Write-Host "    ✓ Nginx responding (HTTP $($nginx.StatusCode))`n" -ForegroundColor Green
} catch {
    Write-Host "    ✗ Nginx not responding`n" -ForegroundColor Red
}

# Test 3: Backend (port 8000 direct)
Write-Host "[3] Backend Server (Port 8000)" -ForegroundColor Cyan
try {
    $backend = Invoke-WebRequest "http://$serverIP:8000/docs" -TimeoutSec 5 -UseBasicParsing
    Write-Host "    ✓ Backend responding directly (HTTP $($backend.StatusCode))`n" -ForegroundColor Green
} catch {
    Write-Host "    ✗ Backend NOT responding on port 8000!" -ForegroundColor Red
    Write-Host "    → This is the problem! Backend container is DOWN`n" -ForegroundColor Yellow
}

# Test 4: API via Nginx
Write-Host "[4] API via Nginx Proxy" -ForegroundColor Cyan
try {
    $api = Invoke-RestMethod "http://$server/api/v1/health" -TimeoutSec 5
    Write-Host "    ✓ API routing works (Status: $($api.status))`n" -ForegroundColor Green
} catch {
    $statusCode = 0
    if($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
    }
    Write-Host "    ✗ API not accessible (HTTP $statusCode)" -ForegroundColor Red
    if($statusCode -eq 502) {
        Write-Host "    → 502 = Nginx can't reach backend`n" -ForegroundColor Yellow
    }
}

# Test 5: Login endpoint (the failing one)
Write-Host "[5] Login Endpoint Test" -ForegroundColor Cyan
try {
    $loginBody = '{"username":"test","password":"test"}'
    $headers = @{"Content-Type"="application/json"}
    $login = Invoke-WebRequest -Uri "http://$server/api/v1/auth/login" -Method Post -Body $loginBody -Headers $headers -TimeoutSec 5 -UseBasicParsing
    Write-Host "    ✓ Login endpoint works (HTTP $($login.StatusCode))`n" -ForegroundColor Green
} catch {
    $statusCode = 0
    if($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
    }
    Write-Host "    ✗ Login endpoint failed (HTTP $statusCode)" -ForegroundColor Red
    if($statusCode -eq 502) {
        Write-Host "    → Backend container is STOPPED or CRASHED!`n" -ForegroundColor Yellow
    }
}

# Summary & Fix
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║              DIAGNOSIS SUMMARY               ║" -ForegroundColor Yellow
Write-Host "╚══════════════════════════════════════════════╝`n" -ForegroundColor Yellow

Write-Host "PROBLEM:" -ForegroundColor Red
Write-Host "  Backend container on VPS is not running`n" -ForegroundColor White

Write-Host "POSSIBLE CAUSES:" -ForegroundColor Yellow
Write-Host "  1. Container crashed after new deployment" -ForegroundColor Gray
Write-Host "  2. Docker daemon restarted" -ForegroundColor Gray
Write-Host "  3. Out of memory (OOM killed)" -ForegroundColor Gray
Write-Host "  4. Database connection failed`n" -ForegroundColor Gray

Write-Host "FIX (SSH to VPS and run):" -ForegroundColor Cyan
Write-Host @"
  ssh root@$serverIP
  cd /root/thang-phan-tools
  
  # Check container status
  docker-compose -f docker-compose.prod.yml ps
  
  # View backend logs
  docker-compose -f docker-compose.prod.yml logs backend --tail=50
  
  # Restart backend
  docker-compose -f docker-compose.prod.yml restart backend
  
  # Or pull new image and restart all
  docker-compose -f docker-compose.prod.yml pull
  docker-compose -f docker-compose.prod.yml up -d
"@ -ForegroundColor White

Write-Host "`n💡 TIP:" -ForegroundColor Cyan
Write-Host "   Localhost works because your local backend is running." -ForegroundColor Gray
Write-Host "   Production fails because VPS backend container is down.`n" -ForegroundColor Gray
