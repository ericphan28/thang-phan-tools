# Monitor deploy progress from push to production
param(
    [Parameter(Mandatory=$false)]
    [string]$ExpectedVersion = "",
    [int]$MaxWaitMinutes = 15
)

$VPS_IP = "165.99.59.47"
$startTime = Get-Date

Write-Host "`n🚀 DEPLOY MONITOR - Tracking deployment to production`n" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Step 1: Get current local version
if ($ExpectedVersion -eq "") {
    $versionLine = Select-String -Path "backend\app\main_simple.py" -Pattern 'version="([^"]+)"' | Select-Object -First 1
    if ($versionLine) {
        $ExpectedVersion = $versionLine.Matches.Groups[1].Value
    }
}

Write-Host "Expected version: $ExpectedVersion" -ForegroundColor Yellow
Write-Host "Start time: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
Write-Host "`n================================================`n" -ForegroundColor Cyan

# Step 2: Wait for GitHub Actions to complete
Write-Host "⏳ Phase 1: GitHub Actions Build" -ForegroundColor Yellow
Write-Host "   Waiting for build to complete (typically 5 min)..." -ForegroundColor Gray

$buildStart = Get-Date
$buildCompleted = $false
$buildTime = 0

# Wait minimum 4 minutes (builds typically take 4-5 min)
Start-Sleep 240

# Check every 30s for up to 3 more minutes
for ($i = 0; $i -lt 6; $i++) {
    Start-Sleep 30
    $elapsed = [math]::Round(((Get-Date) - $buildStart).TotalSeconds, 0)
    Write-Host "   Building... ${elapsed}s" -ForegroundColor Gray
    
    # Check if image is available on GHCR (optional - requires gh cli)
    # For now, just wait the typical build time
}

$buildTime = [math]::Round(((Get-Date) - $buildStart).TotalSeconds, 0)
Write-Host "   ✓ Build phase complete (assumed): $buildTime s`n" -ForegroundColor Green

# Step 3: Monitor Watchtower deployment
Write-Host "⏳ Phase 2: Watchtower Auto-Deploy" -ForegroundColor Yellow
Write-Host "   Watchtower checks every 5 minutes (300s)" -ForegroundColor Gray
Write-Host "   Checking VPS for version $ExpectedVersion...`n" -ForegroundColor Gray

$deployStart = Get-Date
$deployed = $false
$checkInterval = 15  # Check every 15 seconds

while (-not $deployed) {
    $elapsed = [math]::Round(((Get-Date) - $deployStart).TotalSeconds, 0)
    $totalElapsed = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 0)
    
    # Check VPS version
    try {
        $response = ssh root@$VPS_IP "curl -s http://localhost:8000/health 2>/dev/null"
        $vpsVersion = ""
        
        if ($response -match '"version":"([^"]+)"') {
            $vpsVersion = $matches[1]
        }
        
        Write-Host "   [${elapsed}s] VPS version: $vpsVersion" -ForegroundColor Gray
        
        if ($vpsVersion -eq $ExpectedVersion) {
            $deployed = $true
            $deployTime = $elapsed
            Write-Host "`n   ✅ DEPLOYED! Version $ExpectedVersion is live`n" -ForegroundColor Green
            break
        }
        
    } catch {
        Write-Host "   [${elapsed}s] VPS check failed (backend may be restarting)" -ForegroundColor DarkGray
    }
    
    # Timeout check
    if ($totalElapsed -gt ($MaxWaitMinutes * 60)) {
        Write-Host "`n   ⚠️  Timeout after $MaxWaitMinutes minutes" -ForegroundColor Red
        Write-Host "   Current VPS version: $vpsVersion" -ForegroundColor Yellow
        Write-Host "   Expected version: $ExpectedVersion" -ForegroundColor Yellow
        break
    }
    
    Start-Sleep $checkInterval
}

# Summary
$totalTime = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 0)
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "DEPLOY SUMMARY" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Expected version:    $ExpectedVersion"
if ($deployed) {
    Write-Host "VPS version:         $vpsVersion" -ForegroundColor Green
    Write-Host "Status:              DEPLOYED ✅" -ForegroundColor Green
} else {
    Write-Host "VPS version:         $vpsVersion" -ForegroundColor Red
    Write-Host "Status:              PENDING ⏳" -ForegroundColor Yellow
}
Write-Host "------------------------------------------------" -ForegroundColor Gray
Write-Host "Build phase:         ~$buildTime s (~$([math]::Round($buildTime/60, 1)) min)"
if ($deployed) {
    Write-Host "Deploy phase:        $deployTime s (~$([math]::Round($deployTime/60, 1)) min)"
}
Write-Host "Total time:          $totalTime s (~$([math]::Round($totalTime/60, 1)) min)"
Write-Host "================================================`n" -ForegroundColor Cyan

# Return status
if ($deployed) {
    Write-Host "🎉 Deployment successful!`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  Deployment not confirmed`n" -ForegroundColor Yellow
    exit 1
}
