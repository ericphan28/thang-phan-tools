# Check Deployment Status
# VPS: 165.99.59.47

Write-Host "`n=== CHECKING 4 TOOLS DEPLOYMENT STATUS ===`n" -ForegroundColor Cyan

# Tool 1: Cockpit
Write-Host "1. Cockpit (System Management)" -ForegroundColor Yellow
$cockpit = ssh root@165.99.59.47 "systemctl is-active cockpit.socket 2>&1"
if ($cockpit -eq "active") {
    Write-Host "   [OK] Running on http://165.99.59.47:9090" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] Not running: $cockpit" -ForegroundColor Red
}

# Tool 2: Portainer
Write-Host "`n2. Portainer (Docker Management)" -ForegroundColor Yellow
$portainer = ssh root@165.99.59.47 "docker ps --filter 'name=portainer' --format '{{.Status}}' 2>&1"
if ($portainer -match "Up") {
    Write-Host "   [OK] Running on https://165.99.59.47:9443" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] Not running: $portainer" -ForegroundColor Red
}

# Tool 3: Dozzle
Write-Host "`n3. Dozzle (Logs Viewer)" -ForegroundColor Yellow
$dozzle = ssh root@165.99.59.47 "docker ps --filter 'name=dozzle' --format '{{.Status}}' 2>&1"
if ($dozzle -match "Up") {
    Write-Host "   [OK] Running on http://165.99.59.47:9999" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] Not running: $dozzle" -ForegroundColor Red
}

# Tool 4: Utility Server
Write-Host "`n4. Utility Server (Your API)" -ForegroundColor Yellow
$backend = ssh root@165.99.59.47 "docker ps --filter 'name=backend' --format '{{.Status}}' 2>&1"
if ($backend -match "Up") {
    Write-Host "   [OK] Running on http://165.99.59.47/docs" -ForegroundColor Green
    
    # Check health endpoint
    $health = ssh root@165.99.59.47 "curl -s http://localhost/health 2>&1"
    if ($health -match "ok") {
        Write-Host "   [OK] Health check passed" -ForegroundColor Green
    } else {
        Write-Host "   [WARNING] Health check pending: $health" -ForegroundColor Yellow
    }
} else {
    Write-Host "   [BUILDING] Backend is still building..." -ForegroundColor Yellow
    Write-Host "   Status: $backend" -ForegroundColor Gray
    
    # Check build progress
    Write-Host "`n   Checking build logs (last 5 lines):" -ForegroundColor Gray
    ssh root@165.99.59.47 "cd /opt/utility-server && docker-compose logs --tail=5 backend 2>&1 || echo 'Build in progress...'"
}

Write-Host "`n=== RESOURCES ===`n" -ForegroundColor Cyan
ssh root@165.99.59.47 "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'"

Write-Host "`n=== SUMMARY ===`n" -ForegroundColor Cyan
Write-Host "Cockpit:        http://165.99.59.47:9090"
Write-Host "Portainer:      https://165.99.59.47:9443"
Write-Host "Dozzle:         http://165.99.59.47:9999"
Write-Host "Utility Server: http://165.99.59.47/docs (building...)"
Write-Host ""
