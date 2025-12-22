# Test Deploy Speed Measurement Script
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " DEPLOY VERSION 2.0.3 - MEASUREMENT" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

$deployStart = Get-Date

# Step 1: Pull image
Write-Host "Step 1: Pull image sha-3452f9d..." -ForegroundColor Yellow
$s1 = Get-Date
ssh root@165.99.59.47 "docker pull ghcr.io/ericphan28/thang-phan-tools-backend:sha-3452f9d" | Out-Null
$e1 = Get-Date
$t1 = [math]::Round(($e1 - $s1).TotalSeconds, 1)
Write-Host "  -> Pull completed: $t1 seconds`n" -ForegroundColor Green

# Step 2: Tag as latest
Write-Host "Step 2: Tag as latest..." -ForegroundColor Yellow
$s2 = Get-Date
ssh root@165.99.59.47 "docker tag ghcr.io/ericphan28/thang-phan-tools-backend:sha-3452f9d ghcr.io/ericphan28/thang-phan-tools-backend:latest" | Out-Null
$e2 = Get-Date
$t2 = [math]::Round(($e2 - $s2).TotalSeconds, 1)
Write-Host "  -> Tag completed: $t2 seconds`n" -ForegroundColor Green

# Step 3: Stop container
Write-Host "Step 3: Stop container..." -ForegroundColor Yellow
$s3 = Get-Date
ssh root@165.99.59.47 "cd /opt/utility-server && docker compose -f docker-compose.prod.yml stop backend" | Out-Null
$e3 = Get-Date
$t3 = [math]::Round(($e3 - $s3).TotalSeconds, 1)
Write-Host "  -> Stop completed: $t3 seconds`n" -ForegroundColor Green

# Step 4: Remove container
Write-Host "Step 4: Remove container..." -ForegroundColor Yellow
$s4 = Get-Date
ssh root@165.99.59.47 "cd /opt/utility-server && docker compose -f docker-compose.prod.yml rm -f backend" | Out-Null
$e4 = Get-Date
$t4 = [math]::Round(($e4 - $s4).TotalSeconds, 1)
Write-Host "  -> Remove completed: $t4 seconds`n" -ForegroundColor Green

# Step 5: Start container
Write-Host "Step 5: Start new container..." -ForegroundColor Yellow
$s5 = Get-Date
ssh root@165.99.59.47 "cd /opt/utility-server && docker compose -f docker-compose.prod.yml up -d backend" | Out-Null
$e5 = Get-Date
$t5 = [math]::Round(($e5 - $s5).TotalSeconds, 1)
Write-Host "  -> Start completed: $t5 seconds`n" -ForegroundColor Green

# Step 6: Wait for backend
Write-Host "Step 6: Wait for backend to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 12

# Step 7: Verify version
Write-Host "Step 7: Verify version..." -ForegroundColor Yellow
$s7 = Get-Date
$health = ssh root@165.99.59.47 "curl -s http://localhost:8000/health"
$e7 = Get-Date
$t7 = [math]::Round(($e7 - $s7).TotalSeconds, 1)

if ($health -match '"version":"([^"]+)"') {
    $version = $matches[1]
    Write-Host "  -> Version: $version" -ForegroundColor $(if($version -eq "2.0.3"){"Green"}else{"Red"})
    Write-Host "  -> Verify completed: $t7 seconds`n" -ForegroundColor Green
}

$deployEnd = Get-Date
$total = [math]::Round(($deployEnd - $deployStart).TotalSeconds, 1)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " SUMMARY" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pull image:      $t1 s" -ForegroundColor White
Write-Host "Tag latest:      $t2 s" -ForegroundColor White
Write-Host "Stop container:  $t3 s" -ForegroundColor White
Write-Host "Remove container:$t4 s" -ForegroundColor White
Write-Host "Start container: $t5 s" -ForegroundColor White
Write-Host "Wait (12s):      12.0 s" -ForegroundColor White
Write-Host "Verify version:  $t7 s" -ForegroundColor White
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "TOTAL DEPLOY:    $total s" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host "========================================`n" -ForegroundColor Cyan
