# SSH to VPS and fix backend container
# Run this script to restart backend on production

$vpsIP = "165.99.59.47"
$vpsUser = "root"

Write-Host "`n=== FIXING BACKEND ON VPS ===`n" -ForegroundColor Cyan

Write-Host "Server: $vpsIP" -ForegroundColor Yellow
Write-Host "Commands to run:`n" -ForegroundColor Gray

$commands = @"
cd /root/thang-phan-tools

echo "=== Checking Docker containers ==="
docker-compose -f docker-compose.prod.yml ps

echo "`n=== Backend logs (last 30 lines) ==="
docker-compose -f docker-compose.prod.yml logs backend --tail=30

echo "`n=== Restarting backend ==="
docker-compose -f docker-compose.prod.yml restart backend

echo "`n=== Waiting 5 seconds ==="
sleep 5

echo "`n=== Checking status again ==="
docker-compose -f docker-compose.prod.yml ps

echo "`n=== Testing backend health ==="
curl -s http://localhost:8000/docs | head -n 5
"@

Write-Host $commands -ForegroundColor White

Write-Host "`n=== OPTION 1: Manual SSH ===" -ForegroundColor Cyan
Write-Host "ssh $vpsUser@$vpsIP" -ForegroundColor Yellow
Write-Host "Then paste the commands above`n" -ForegroundColor Gray

Write-Host "=== OPTION 2: Auto-run (if you have SSH key) ===" -ForegroundColor Cyan
Write-Host "ssh $vpsUser@$vpsIP '$($commands -replace "`n", " && ")'" -ForegroundColor Yellow
Write-Host ""

# Ask if user wants to try auto-run
$answer = Read-Host "Do you have SSH key configured? Try auto-run? (y/n)"
if($answer -eq 'y') {
    Write-Host "`nConnecting to VPS..." -ForegroundColor Cyan
    ssh "$vpsUser@$vpsIP" $commands
}
