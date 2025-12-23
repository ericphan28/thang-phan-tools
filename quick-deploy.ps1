# Quick Deploy to Production via GitHub CI/CD
# PowerShell script for Windows

param(
    [string]$Message = ""
)

Write-Host "`n🚀 QUICK DEPLOY TO PRODUCTION" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# Check if git repo
if (!(Test-Path .git)) {
    Write-Host "❌ Not a git repository" -ForegroundColor Red
    exit 1
}

# Check for uncommitted changes
$status = git status --porcelain
if ($status) {
    Write-Host "📝 You have uncommitted changes" -ForegroundColor Yellow
    
    if ([string]::IsNullOrWhiteSpace($Message)) {
        $Message = Read-Host "Commit message"
    }
    
    if ([string]::IsNullOrWhiteSpace($Message)) {
        Write-Host "❌ Commit message required" -ForegroundColor Red
        exit 1
    }
    
    # Stage all changes
    git add .
    
    # Commit
    git commit -m $Message
    Write-Host "✅ Changes committed" -ForegroundColor Green
} else {
    Write-Host "✅ No uncommitted changes" -ForegroundColor Green
}

# Get current branch
$branch = git branch --show-current
Write-Host "📍 Current branch: $branch" -ForegroundColor Yellow

# Push to GitHub
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Yellow
git push origin $branch

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Code pushed successfully!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Check GitHub Actions: https://github.com/ericphan28/thang-phan-tools/actions"
    Write-Host "2. Wait ~5-10 minutes for build"
    Write-Host "3. Watchtower will auto-deploy to VPS"
    Write-Host "`n🎉 Deployment in progress!" -ForegroundColor Green
} else {
    Write-Host "❌ Push failed" -ForegroundColor Red
    exit 1
}
