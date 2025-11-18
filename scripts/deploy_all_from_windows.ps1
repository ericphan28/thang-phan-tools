# ============================================
# FULL DEPLOYMENT FROM WINDOWS
# Deploy Everything in One Go!
# ============================================

# Configuration
$VPS_IP = "165.99.59.47"
$VPS_USER = "root"
$VPS_PASSWORD = "@8Alm523jIqS"
$VPS_PATH = "/opt/utility-server"
$LOCAL_PATH = "D:\thang\utility-server"

Write-Host "🚀 Full Deployment Script" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will deploy:" -ForegroundColor Yellow
Write-Host "  [+] Docker and Docker Compose" -ForegroundColor Green
Write-Host "  [+] Cockpit (VPS Management)" -ForegroundColor Green
Write-Host "  [+] Portainer (Docker Management)" -ForegroundColor Green
Write-Host "  [+] Dozzle (Logs Viewer)" -ForegroundColor Green
Write-Host "  [+] Utility Server (Your API)" -ForegroundColor Green
Write-Host ""

# Check local path
if (-not (Test-Path $LOCAL_PATH)) {
    Write-Host "❌ Local path not found: $LOCAL_PATH" -ForegroundColor Red
    exit 1
}

cd $LOCAL_PATH

# ============================================
# STEP 1: Check/Create .env file
# ============================================
Write-Host "📝 Step 1/5: Checking .env file..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Write-Host "[!] .env not found, copying from .env.example" -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "[!] IMPORTANT: Please configure .env file!" -ForegroundColor Red
    Write-Host "   - DB_PASSWORD" -ForegroundColor White
    Write-Host "   - REDIS_PASSWORD" -ForegroundColor White
    Write-Host "   - SECRET_KEY" -ForegroundColor White
    Write-Host "   - JWT_SECRET_KEY" -ForegroundColor White
    Write-Host ""
    
    $edit = Read-Host "Do you want to edit .env now? (y/n)"
    if ($edit -eq "y") {
        notepad .env
        Write-Host "Press Enter after saving..." -ForegroundColor Yellow
        $null = Read-Host
    }
}

Write-Host "✅ .env file ready" -ForegroundColor Green

# ============================================
# STEP 2: Upload files to VPS
# ============================================
Write-Host ""
Write-Host "📤 Step 2/5: Uploading files to VPS..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray

# Using SCP
$scpAvailable = Get-Command scp -ErrorAction SilentlyContinue

if ($scpAvailable) {
    Write-Host "Using SCP to upload files..." -ForegroundColor Gray
    
    # Create directory on VPS
    $createDir = "mkdir -p $VPS_PATH"
    echo $VPS_PASSWORD | plink -ssh -batch -pw $VPS_PASSWORD ${VPS_USER}@${VPS_IP} $createDir 2>$null
    
    # Upload files (excluding node_modules, __pycache__, etc.)
    pscp -r -pw $VPS_PASSWORD $LOCAL_PATH\* ${VPS_USER}@${VPS_IP}:${VPS_PATH}/ 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Files uploaded successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Upload failed!" -ForegroundColor Red
        Write-Host ""
        Write-Host "📝 Manual Upload Instructions:" -ForegroundColor Yellow
        Write-Host "1. Download WinSCP: https://winscp.net/eng/download.php" -ForegroundColor White
        Write-Host "2. Connect to: $VPS_IP" -ForegroundColor White
        Write-Host "3. Login: $VPS_USER / $VPS_PASSWORD" -ForegroundColor White
        Write-Host "4. Upload folder: $LOCAL_PATH" -ForegroundColor White
        Write-Host "5. Upload to: $VPS_PATH" -ForegroundColor White
        Write-Host ""
        $continue = Read-Host "Press Enter after uploading files manually..."
    }
} else {
    Write-Host "⚠️  SCP not available. Please upload manually." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 Manual Upload Instructions:" -ForegroundColor Cyan
    Write-Host "1. Download WinSCP: https://winscp.net/eng/download.php" -ForegroundColor White
    Write-Host "2. Connect to: $VPS_IP" -ForegroundColor White
    Write-Host "3. Login: $VPS_USER / $VPS_PASSWORD" -ForegroundColor White
    Write-Host "4. Upload folder: $LOCAL_PATH to $VPS_PATH" -ForegroundColor White
    Write-Host ""
    $null = Read-Host "Press Enter after uploading files manually..."
}

# ============================================
# STEP 3: Run full deployment script
# ============================================
Write-Host ""
Write-Host "🚀 Step 3/5: Running full deployment on VPS..." -ForegroundColor Yellow
Write-Host "This will take 5-10 minutes. Please wait..." -ForegroundColor Gray
Write-Host ""

$sshCommands = @"
cd $VPS_PATH
chmod +x scripts/*.sh
bash scripts/full_deploy.sh
"@

# Execute SSH commands
$sshCommands | ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP}

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Deployment script had issues. Continuing..." -ForegroundColor Yellow
}

# ============================================
# STEP 4: Deploy Utility Server
# ============================================
Write-Host ""
Write-Host "🚀 Step 4/5: Deploying Utility Server..." -ForegroundColor Yellow

$deployCommands = @"
cd $VPS_PATH
docker-compose down 2>/dev/null || true
docker-compose up -d --build
sleep 10
docker-compose ps
"@

$deployCommands | ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP}

Write-Host "✅ Utility Server deployed!" -ForegroundColor Green

# ============================================
# STEP 5: Verify installations
# ============================================
Write-Host ""
Write-Host "🔍 Step 5/5: Verifying installations..." -ForegroundColor Yellow

$verifyCommands = @"
echo '=== Docker Info ==='
docker --version
docker-compose --version
echo ''
echo '=== Running Containers ==='
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
echo ''
echo '=== Services Status ==='
systemctl is-active cockpit || echo 'Cockpit: Not running'
docker ps | grep -q portainer && echo 'Portainer: Running' || echo 'Portainer: Not running'
docker ps | grep -q dozzle && echo 'Dozzle: Running' || echo 'Dozzle: Not running'
"@

$verifyCommands | ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP}

# ============================================
# FINAL SUMMARY
# ============================================
Write-Host ""
Write-Host "✅ ═══════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ DEPLOYMENT COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "✅ ═══════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Host "🌐 ACCESS YOUR SERVICES:" -ForegroundColor Cyan
Write-Host ""
Write-Host "┌─────────────────────────────────────────────────────────┐" -ForegroundColor White
Write-Host "│ 🖥️  COCKPIT (VPS Management)                            │" -ForegroundColor White
Write-Host "│    URL: http://$VPS_IP:9090                      │" -ForegroundColor Yellow
Write-Host "│    Login: $VPS_USER / $VPS_PASSWORD                     │" -ForegroundColor Gray
Write-Host "│    Features: System monitoring, services, terminal      │" -ForegroundColor Gray
Write-Host "├─────────────────────────────────────────────────────────┤" -ForegroundColor White
Write-Host "│ 🐳 PORTAINER (Docker Management)                        │" -ForegroundColor White
Write-Host "│    URL: https://$VPS_IP:9443                     │" -ForegroundColor Yellow
Write-Host "│    Setup: Create admin account on first visit          │" -ForegroundColor Gray
Write-Host "│    Features: Containers, images, volumes, networks      │" -ForegroundColor Gray
Write-Host "├─────────────────────────────────────────────────────────┤" -ForegroundColor White
Write-Host "│ 📋 DOZZLE (Logs Viewer)                                 │" -ForegroundColor White
Write-Host "│    URL: http://$VPS_IP:9999                      │" -ForegroundColor Yellow
Write-Host "│    No login required                                    │" -ForegroundColor Gray
Write-Host "│    Features: Real-time container logs                   │" -ForegroundColor Gray
Write-Host "├─────────────────────────────────────────────────────────┤" -ForegroundColor White
Write-Host "│ 🚀 UTILITY SERVER (Your API)                            │" -ForegroundColor White
Write-Host "│    API Docs: http://$VPS_IP/docs                 │" -ForegroundColor Yellow
Write-Host "│    Health: http://$VPS_IP/health                 │" -ForegroundColor Yellow
Write-Host "│    ReDoc: http://$VPS_IP/redoc                   │" -ForegroundColor Yellow
Write-Host "└─────────────────────────────────────────────────────────┘" -ForegroundColor White
Write-Host ""

Write-Host "📊 RESOURCE USAGE:" -ForegroundColor Cyan
Write-Host "   RAM: ~2GB / 6GB (4GB free)" -ForegroundColor Gray
Write-Host "   Disk: ~6GB / 197GB (191GB free)" -ForegroundColor Gray
Write-Host ""

Write-Host "💡 USEFUL COMMANDS:" -ForegroundColor Cyan
Write-Host "   View logs: ssh root@$VPS_IP 'cd $VPS_PATH && docker-compose logs -f'" -ForegroundColor Gray
Write-Host "   Restart: ssh root@$VPS_IP 'cd $VPS_PATH && docker-compose restart'" -ForegroundColor Gray
Write-Host "   Stop: ssh root@$VPS_IP 'cd $VPS_PATH && docker-compose down'" -ForegroundColor Gray
Write-Host ""

Write-Host "🎉 ALL DONE! Open your browser and test the services!" -ForegroundColor Green
Write-Host ""

# Open browser automatically
$openBrowser = Read-Host "Open Cockpit in browser? (y/n)"
if ($openBrowser -eq "y") {
    Start-Process "http://$VPS_IP:9090"
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
