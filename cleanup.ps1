# Cleanup Script - Xoa code thua thi
# Chay script nay de don dep backend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   CLEANUP CODE THUA THI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$cleaned = 0

# 1. Xoa duplicate endpoint files
Write-Host "[1/4] Xoa duplicate endpoint files..." -ForegroundColor Yellow
$filesToDelete = @(
    "backend\app\api\v1\endpoints\users_temp.py",
    "backend\app\api\v1\endpoints\users_fixed.py",
    "backend\app\main.py"
)

foreach ($file in $filesToDelete) {
    $fullPath = Join-Path $PSScriptRoot $file
    if (Test-Path $fullPath) {
        Remove-Item $fullPath -Force
        Write-Host "  Deleted: $file" -ForegroundColor Green
        $cleaned++
    }
}

# 2. Xoa init scripts da chay
Write-Host "[2/4] Xoa init scripts da chay..." -ForegroundColor Yellow
$scriptFiles = @(
    "backend\app\scripts\init_auth.py",
    "backend\app\scripts\init_auth_sqlite.py"
)

foreach ($file in $scriptFiles) {
    $fullPath = Join-Path $PSScriptRoot $file
    if (Test-Path $fullPath) {
        Remove-Item $fullPath -Force
        Write-Host "  Deleted: $file" -ForegroundColor Green
        $cleaned++
    }
}

# 3. Clear Python cache
Write-Host "[3/4] Clear Python cache..." -ForegroundColor Yellow
$cacheCount = 0
Get-ChildItem -Path "backend" -Directory -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force
    $cacheCount++
}
Get-ChildItem -Path "backend" -File -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Force
    $cacheCount++
}
Write-Host "  Cleared $cacheCount cache items" -ForegroundColor Green

# 4. Fix auth.py - Xoa duplicate UserUpdate
Write-Host "[4/4] Fix duplicate schema..." -ForegroundColor Yellow
$authFile = Join-Path $PSScriptRoot "backend\app\schemas\auth.py"
if (Test-Path $authFile) {
    $content = Get-Content $authFile -Raw
    # Check if UserUpdate exists
    if ($content -match "class UserUpdate") {
        Write-Host "  Found UserUpdate in auth.py" -ForegroundColor Yellow
        Write-Host "  Keep: user.py (full featured)" -ForegroundColor Green
        Write-Host "  Note: Can dua UserUpdate ra khoi auth.py" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   CLEANUP HOAN TAT!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Files deleted: $cleaned" -ForegroundColor White
Write-Host "  Cache cleared: $cacheCount items" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Restart backend server" -ForegroundColor White
Write-Host "  2. Test all features" -ForegroundColor White
Write-Host ""
