# Force Deploy with API logging
param(
    [Parameter(Mandatory=$false)]
    [string]$Version = ""
)

$ErrorActionPreference = "Continue"

Write-Host "`n⚡ FORCE DEPLOY - Skip Watchtower wait`n" -ForegroundColor Cyan

# Get version
if ($Version -eq "") {
    $versionLine = Select-String -Path "backend\app\main_simple.py" -Pattern 'version="([^"]+)"' | Select-Object -First 1
    if ($versionLine) {
        $Version = $versionLine.Matches.Groups[1].Value
    }
}

Write-Host "Target version: $Version" -ForegroundColor Yellow

# Start deployment log
$deploymentLog = @{
    version = $Version
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
    method = "force"
    status = "in-progress"
    phases = @()
}

# Phase 1: Git operations (already done)
Write-Host "`n📦 Phase 1: Git push - completed`n" -ForegroundColor Gray

# Phase 2: Wait for GitHub Actions
Write-Host "⏳ Phase 2: Waiting for GitHub Actions build (5 min)...`n" -ForegroundColor Cyan
$buildStart = Get-Date
Start-Sleep 300
$buildTime = [math]::Round(((Get-Date) - $buildStart).TotalSeconds, 1)
$deploymentLog.phases += @{
    name = "GitHub Actions Build"
    duration_seconds = $buildTime
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
}
Write-Host "✓ Build: $buildTime s`n" -ForegroundColor Green

# Phase 3: VPS Pull
Write-Host "📥 Phase 3: Pulling image on VPS..." -ForegroundColor Cyan
$pullStart = Get-Date
ssh root@165.99.59.47 "cd /opt/utility-server && docker-compose -f docker-compose.prod.yml pull backend" | Out-Null
$pullTime = [math]::Round(((Get-Date) - $pullStart).TotalSeconds, 1)
$deploymentLog.phases += @{
    name = "VPS Image Pull"
    duration_seconds = $pullTime
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
}
Write-Host "✓ Pull: $pullTime s`n" -ForegroundColor Green

# Phase 4: Container Restart
Write-Host "🔄 Phase 4: Restarting container..." -ForegroundColor Cyan
$restartStart = Get-Date
ssh root@165.99.59.47 "cd /opt/utility-server && docker-compose -f docker-compose.prod.yml up -d backend" | Out-Null
$restartTime = [math]::Round(((Get-Date) - $restartStart).TotalSeconds, 1)
$deploymentLog.phases += @{
    name = "Container Restart"
    duration_seconds = $restartTime
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
}
Write-Host "✓ Restart: $restartTime s`n" -ForegroundColor Green

# Phase 5: Verify
Write-Host "✅ Phase 5: Verifying deployment..." -ForegroundColor Cyan
Start-Sleep 15
$verifyStart = Get-Date
$response = ssh root@165.99.59.47 "curl -s http://localhost:8000/health"
$verifyTime = [math]::Round(((Get-Date) - $verifyStart).TotalSeconds, 1)
$deploymentLog.phases += @{
    name = "Verify + Startup Wait"
    duration_seconds = $verifyTime + 15
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
}

# Calculate total
$totalTime = $buildTime + $pullTime + $restartTime + $verifyTime + 15
$deploymentLog.total_duration_seconds = $totalTime

# Check success
if ($response -match '"version":"([^"]+)"') {
    $deployed = $matches[1]
    if ($deployed -eq $Version) {
        Write-Host "🎉 Successfully deployed v$Version!" -ForegroundColor Green
        $deploymentLog.status = "completed"
    } else {
        Write-Host "⚠️  Version mismatch: expected $Version, got $deployed" -ForegroundColor Yellow
        $deploymentLog.status = "failed"
        $deploymentLog.error_message = "Version mismatch: expected $Version, got $deployed"
    }
} else {
    Write-Host "❌ Failed to verify deployment" -ForegroundColor Red
    $deploymentLog.status = "failed"
    $deploymentLog.error_message = "Health check failed"
}

# Summary
Write-Host "`n================================================" -ForegroundColor Yellow
Write-Host "  DEPLOYMENT SUMMARY - v$Version" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Yellow
foreach ($phase in $deploymentLog.phases) {
    $name = $phase.name.PadRight(25)
    Write-Host "  $name $($phase.duration_seconds) s" -ForegroundColor White
}
Write-Host "  ------------------------------------------------" -ForegroundColor Yellow
Write-Host "  Total".PadRight(27) + "$totalTime s  (~$([math]::Round($totalTime / 60, 1)) min)" -ForegroundColor Green
Write-Host "================================================`n" -ForegroundColor Yellow

# Log to API
Write-Host "📝 Logging to API..." -ForegroundColor Gray
try {
    $jsonLog = $deploymentLog | ConvertTo-Json -Depth 10
    $response = Invoke-RestMethod -Uri "http://165.99.59.47:8000/api/v1/deployment/log" `
        -Method Post `
        -Body $jsonLog `
        -ContentType "application/json" `
        -TimeoutSec 5
    Write-Host "✓ Logged successfully`n" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Failed to log to API: $_`n" -ForegroundColor Yellow
}
