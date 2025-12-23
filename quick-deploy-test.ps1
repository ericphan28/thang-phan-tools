# Quick deploy test with automatic monitoring
# Usage: .\quick-deploy-test.ps1

Write-Host "`n🚀 QUICK DEPLOY & MONITOR`n" -ForegroundColor Cyan

# Step 1: Bump version
$versionFile = "backend\app\main_simple.py"
$content = Get-Content $versionFile -Raw

if ($content -match 'version="(\d+)\.(\d+)\.(\d+)"') {
    $major = [int]$matches[1]
    $minor = [int]$matches[2]
    $patch = [int]$matches[3]
    
    $newPatch = $patch + 1
    $newVersion = "$major.$minor.$newPatch"
    
    $content = $content -replace 'version="\d+\.\d+\.\d+"', "version=`"$newVersion`""
    $content | Set-Content $versionFile
    
    Write-Host "✓ Bumped version to: $newVersion`n" -ForegroundColor Green
} else {
    Write-Host "❌ Could not parse version`n" -ForegroundColor Red
    exit 1
}

# Step 2: Git commit & push
$commitStart = Get-Date
git add backend/app/main_simple.py
git commit -m "test: auto-deploy v$newVersion"
git push
$commitTime = [math]::Round(((Get-Date) - $commitStart).TotalSeconds, 1)

Write-Host "✓ Pushed to GitHub in $commitTime s`n" -ForegroundColor Green

# Step 3: Monitor deployment
Write-Host "Starting deployment monitor...`n" -ForegroundColor Yellow
& ".\monitor-deploy.ps1" -ExpectedVersion $newVersion
