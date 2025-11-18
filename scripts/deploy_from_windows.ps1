# ============================================
# Windows PowerShell Deployment Script
# Chạy script này từ Windows để deploy lên VPS
# ============================================

# VPS credentials
$VPS_IP = "165.99.59.47"
$VPS_USER = "root"
$VPS_PASSWORD = "@8Alm523jIqS"
$VPS_PATH = "/opt/utility-server"
$LOCAL_PATH = "D:\thang\utility-server"

Write-Host "🚀 Deploying Utility Server to VPS..." -ForegroundColor Green
Write-Host ""

# Check if local path exists
if (-not (Test-Path $LOCAL_PATH)) {
    Write-Host "❌ Local path not found: $LOCAL_PATH" -ForegroundColor Red
    exit 1
}

Write-Host "📦 Preparing files..." -ForegroundColor Yellow
cd $LOCAL_PATH

# Create .env if not exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env not found, copying from .env.example" -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  Please edit .env file with your configuration!" -ForegroundColor Yellow
    notepad .env
    $continue = Read-Host "Continue with deployment? (y/n)"
    if ($continue -ne "y") {
        Write-Host "Deployment cancelled" -ForegroundColor Red
        exit 0
    }
}

Write-Host ""
Write-Host "📤 Uploading files to VPS..." -ForegroundColor Yellow
Write-Host "This will use SCP to upload files"
Write-Host "You may need to install OpenSSH Client on Windows"
Write-Host ""

# Option 1: Using SCP (if available)
$useScp = Read-Host "Use SCP for upload? (y/n) [If no, you'll need to use WinSCP manually]"

if ($useScp -eq "y") {
    Write-Host "Uploading with SCP..." -ForegroundColor Yellow
    
    # Upload entire directory
    scp -r $LOCAL_PATH ${VPS_USER}@${VPS_IP}:${VPS_PATH}
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Files uploaded successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Upload failed!" -ForegroundColor Red
        Write-Host "Please use WinSCP to upload manually" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "📝 Manual Upload Instructions:" -ForegroundColor Cyan
    Write-Host "1. Download WinSCP: https://winscp.net/eng/download.php" -ForegroundColor White
    Write-Host "2. Connect to:" -ForegroundColor White
    Write-Host "   - Host: $VPS_IP" -ForegroundColor White
    Write-Host "   - User: $VPS_USER" -ForegroundColor White
    Write-Host "   - Password: $VPS_PASSWORD" -ForegroundColor White
    Write-Host "3. Upload folder: $LOCAL_PATH" -ForegroundColor White
    Write-Host "4. Upload to: $VPS_PATH" -ForegroundColor White
    Write-Host ""
    $uploaded = Read-Host "Press Enter after uploading files manually"
}

Write-Host ""
Write-Host "🔧 Running deployment on VPS..." -ForegroundColor Yellow

# Create SSH command script
$sshCommands = @"
cd $VPS_PATH
chmod +x scripts/*.sh
bash scripts/setup_vps.sh
bash scripts/deploy.sh
"@

Write-Host "Connecting to VPS and running deployment..." -ForegroundColor Yellow
Write-Host ""

# Show commands that will be executed
Write-Host "Commands to run:" -ForegroundColor Cyan
Write-Host $sshCommands -ForegroundColor White
Write-Host ""

$runNow = Read-Host "Run these commands now? (y/n)"

if ($runNow -eq "y") {
    # Execute via SSH
    # Note: This requires SSH client to be installed on Windows
    $sshCommands | ssh ${VPS_USER}@${VPS_IP}
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ =========================================" -ForegroundColor Green
        Write-Host "✅ Deployment Complete!" -ForegroundColor Green
        Write-Host "✅ =========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 Access your API:" -ForegroundColor Cyan
        Write-Host "   - API Docs: http://${VPS_IP}/docs" -ForegroundColor White
        Write-Host "   - Health: http://${VPS_IP}/health" -ForegroundColor White
        Write-Host "   - ReDoc: http://${VPS_IP}/redoc" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "❌ Deployment failed!" -ForegroundColor Red
        Write-Host "Please check the errors above" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "📝 Manual Deployment Instructions:" -ForegroundColor Cyan
    Write-Host "1. SSH to VPS: ssh ${VPS_USER}@${VPS_IP}" -ForegroundColor White
    Write-Host "2. Run these commands:" -ForegroundColor White
    Write-Host $sshCommands -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
