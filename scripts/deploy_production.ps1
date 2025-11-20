# ============================================
# Production Deployment Script for Windows
# ============================================

param(
    [switch]$SkipBuild,
    [switch]$SkipUpload,
    [switch]$SkipDeploy
)

# VPS Configuration
$VPS_IP = "165.99.59.47"
$VPS_USER = "root"
$VPS_PASSWORD = "@8Alm523jIqS"
$VPS_PATH = "/opt/utility-server"
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot

Write-Host ""
Write-Host "🚀 =========================================" -ForegroundColor Cyan
Write-Host "🚀  PRODUCTION DEPLOYMENT" -ForegroundColor Cyan
Write-Host "🚀 =========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Project: $PROJECT_ROOT" -ForegroundColor White
Write-Host "📍 Target: ${VPS_USER}@${VPS_IP}:${VPS_PATH}" -ForegroundColor White
Write-Host ""

# Change to project root
Set-Location $PROJECT_ROOT

# ============================================
# STEP 1: Pre-Flight Checks
# ============================================

Write-Host "🔍 Running pre-flight checks..." -ForegroundColor Yellow

# Check if git is clean
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "⚠️  You have uncommitted changes:" -ForegroundColor Yellow
    Write-Host $gitStatus -ForegroundColor Gray
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        Write-Host "❌ Deployment cancelled" -ForegroundColor Red
        exit 0
    }
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found! Please install Node.js" -ForegroundColor Red
    exit 1
}

# Check if npm is installed
try {
    $npmVersion = npm --version
    Write-Host "✅ npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm not found!" -ForegroundColor Red
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================
# STEP 2: Build Frontend
# ============================================

if (-not $SkipBuild) {
    Write-Host "🏗️  Building frontend for production..." -ForegroundColor Yellow
    Write-Host ""
    
    Set-Location "$PROJECT_ROOT\frontend"
    
    # Check if node_modules exists
    if (-not (Test-Path "node_modules")) {
        Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
        npm install
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ npm install failed!" -ForegroundColor Red
            exit 1
        }
    }
    
    # Build frontend
    Write-Host "🔨 Running npm run build..." -ForegroundColor Yellow
    npm run build
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Frontend build successful!" -ForegroundColor Green
        
        # Check build output
        if (Test-Path "dist\index.html") {
            $distSize = (Get-ChildItem dist -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
            Write-Host "   Build size: $([math]::Round($distSize, 2)) MB" -ForegroundColor Gray
        } else {
            Write-Host "⚠️  Warning: dist/index.html not found!" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Frontend build failed!" -ForegroundColor Red
        Write-Host "Please fix build errors before deploying" -ForegroundColor Yellow
        exit 1
    }
    
    Set-Location $PROJECT_ROOT
    Write-Host ""
} else {
    Write-Host "⏭️  Skipping frontend build" -ForegroundColor Gray
    Write-Host ""
}

# ============================================
# STEP 3: Check Backend Dependencies
# ============================================

if (-not $SkipBuild) {
    Write-Host "🐍 Checking backend..." -ForegroundColor Yellow
    
    Set-Location "$PROJECT_ROOT\backend"
    
    # Check if requirements.txt exists
    if (Test-Path "requirements.txt") {
        Write-Host "✅ requirements.txt found" -ForegroundColor Green
        
        # Show some important packages
        $reqContent = Get-Content "requirements.txt" | Select-String -Pattern "fastapi|uvicorn|sqlalchemy|python-multipart"
        Write-Host "   Key packages:" -ForegroundColor Gray
        $reqContent | ForEach-Object { Write-Host "   - $_" -ForegroundColor Gray }
    } else {
        Write-Host "⚠️  requirements.txt not found!" -ForegroundColor Yellow
    }
    
    Set-Location $PROJECT_ROOT
    Write-Host ""
}

# ============================================
# STEP 4: Prepare Environment File
# ============================================

Write-Host "📝 Checking environment configuration..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env not found, creating from .env.example" -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Created .env file" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️  IMPORTANT: You need to configure .env file!" -ForegroundColor Yellow
        Write-Host "   Opening .env in notepad..." -ForegroundColor Gray
        Start-Sleep -Seconds 1
        notepad .env
        Write-Host ""
        $continue = Read-Host "Have you configured .env? (y/n)"
        if ($continue -ne "y") {
            Write-Host "❌ Please configure .env before deploying" -ForegroundColor Red
            exit 0
        }
    } else {
        Write-Host "❌ .env.example not found!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ .env file found" -ForegroundColor Green
}

# Create .env.production for VPS
Write-Host "📝 Creating .env.production..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Copy-Item ".env" ".env.production"
    
    # Update for production
    $envContent = Get-Content ".env.production"
    $envContent = $envContent -replace "DEBUG=True", "DEBUG=False"
    $envContent = $envContent -replace "ENVIRONMENT=development", "ENVIRONMENT=production"
    $envContent = $envContent -replace "localhost", "postgres"
    $envContent | Set-Content ".env.production"
    
    Write-Host "✅ .env.production created" -ForegroundColor Green
}

Write-Host ""

# ============================================
# STEP 5: Summary Before Upload
# ============================================

Write-Host "📊 Deployment Summary:" -ForegroundColor Cyan
Write-Host "   Frontend: " -NoNewline -ForegroundColor White
if (Test-Path "frontend\dist\index.html") {
    Write-Host "✅ Built" -ForegroundColor Green
} else {
    Write-Host "❌ Not built" -ForegroundColor Red
}

Write-Host "   Backend: " -NoNewline -ForegroundColor White
if (Test-Path "backend\requirements.txt") {
    Write-Host "✅ Ready" -ForegroundColor Green
} else {
    Write-Host "⚠️  Missing requirements.txt" -ForegroundColor Yellow
}

Write-Host "   Environment: " -NoNewline -ForegroundColor White
if (Test-Path ".env.production") {
    Write-Host "✅ Configured" -ForegroundColor Green
} else {
    Write-Host "❌ Not configured" -ForegroundColor Red
}

Write-Host "   Docker: " -NoNewline -ForegroundColor White
if (Test-Path "docker-compose.yml") {
    Write-Host "✅ Ready" -ForegroundColor Green
} else {
    Write-Host "❌ Missing docker-compose.yml" -ForegroundColor Red
}

Write-Host ""
Write-Host "📦 Files to upload:" -ForegroundColor Cyan
Write-Host "   - backend/" -ForegroundColor Gray
Write-Host "   - frontend/dist/" -ForegroundColor Gray
Write-Host "   - nginx/" -ForegroundColor Gray
Write-Host "   - docker-compose.yml" -ForegroundColor Gray
Write-Host "   - .env.production" -ForegroundColor Gray
Write-Host "   - scripts/" -ForegroundColor Gray
Write-Host ""

$proceed = Read-Host "Proceed with upload? (y/n)"
if ($proceed -ne "y") {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Red
    exit 0
}

# ============================================
# STEP 6: Upload to VPS
# ============================================

if (-not $SkipUpload) {
    Write-Host ""
    Write-Host "📤 Uploading to VPS..." -ForegroundColor Yellow
    Write-Host ""
    
    # Check if SCP is available
    $scpAvailable = Get-Command scp -ErrorAction SilentlyContinue
    
    if ($scpAvailable) {
        Write-Host "🔄 Using SCP for upload..." -ForegroundColor Yellow
        Write-Host "   Target: ${VPS_USER}@${VPS_IP}:${VPS_PATH}" -ForegroundColor Gray
        Write-Host ""
        
        # Create remote directory if not exists
        ssh "${VPS_USER}@${VPS_IP}" "mkdir -p ${VPS_PATH}"
        
        # Upload specific directories/files
        Write-Host "   Uploading backend..." -ForegroundColor Gray
        scp -r backend "${VPS_USER}@${VPS_IP}:${VPS_PATH}/"
        
        Write-Host "   Uploading frontend build..." -ForegroundColor Gray
        ssh "${VPS_USER}@${VPS_IP}" "mkdir -p ${VPS_PATH}/frontend"
        scp -r frontend/dist "${VPS_USER}@${VPS_IP}:${VPS_PATH}/frontend/"
        
        Write-Host "   Uploading nginx config..." -ForegroundColor Gray
        scp -r nginx "${VPS_USER}@${VPS_IP}:${VPS_PATH}/"
        
        Write-Host "   Uploading docker-compose..." -ForegroundColor Gray
        scp docker-compose.yml "${VPS_USER}@${VPS_IP}:${VPS_PATH}/"
        
        Write-Host "   Uploading .env..." -ForegroundColor Gray
        scp .env.production "${VPS_USER}@${VPS_IP}:${VPS_PATH}/.env"
        
        Write-Host "   Uploading scripts..." -ForegroundColor Gray
        scp -r scripts "${VPS_USER}@${VPS_IP}:${VPS_PATH}/"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Upload completed!" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "❌ Upload failed!" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "❌ SCP not available!" -ForegroundColor Red
        Write-Host ""
        Write-Host "📝 Manual Upload Instructions:" -ForegroundColor Cyan
        Write-Host "1. Download WinSCP: https://winscp.net/eng/download.php" -ForegroundColor White
        Write-Host "2. Connect to:" -ForegroundColor White
        Write-Host "   - Host: $VPS_IP" -ForegroundColor Yellow
        Write-Host "   - User: $VPS_USER" -ForegroundColor Yellow
        Write-Host "   - Password: $VPS_PASSWORD" -ForegroundColor Yellow
        Write-Host "3. Upload these folders/files to $VPS_PATH:" -ForegroundColor White
        Write-Host "   - backend/" -ForegroundColor Gray
        Write-Host "   - frontend/dist/" -ForegroundColor Gray
        Write-Host "   - nginx/" -ForegroundColor Gray
        Write-Host "   - docker-compose.yml" -ForegroundColor Gray
        Write-Host "   - .env.production (rename to .env)" -ForegroundColor Gray
        Write-Host "   - scripts/" -ForegroundColor Gray
        Write-Host ""
        $uploaded = Read-Host "Press Enter after uploading manually"
    }
} else {
    Write-Host "⏭️  Skipping upload" -ForegroundColor Gray
}

Write-Host ""

# ============================================
# STEP 7: Deploy on VPS
# ============================================

if (-not $SkipDeploy) {
    Write-Host "🚀 Deploying on VPS..." -ForegroundColor Yellow
    Write-Host ""
    
    # SSH commands to run on VPS
    $deployCommands = @"
cd ${VPS_PATH}
echo "📍 Current directory: \$(pwd)"
echo ""

echo "🔧 Making scripts executable..."
chmod +x scripts/*.sh
echo ""

echo "📋 Checking Docker..."
docker --version
docker-compose --version
echo ""

echo "🛑 Stopping old containers..."
docker-compose down
echo ""

echo "🏗️  Building images..."
docker-compose build --no-cache
echo ""

echo "🚀 Starting services..."
docker-compose up -d
echo ""

echo "⏳ Waiting for services to be ready..."
sleep 10
echo ""

echo "📊 Service status:"
docker-compose ps
echo ""

echo "🧪 Testing health endpoint..."
curl -s http://localhost:8000/health
echo ""

echo "✅ Deployment complete!"
echo ""
echo "🌐 Your server is now running at:"
echo "   - Frontend: http://${VPS_IP}"
echo "   - API Docs: http://${VPS_IP}/docs"
echo "   - Health: http://${VPS_IP}/health"
"@
    
    Write-Host "Commands to execute on VPS:" -ForegroundColor Cyan
    Write-Host $deployCommands -ForegroundColor Gray
    Write-Host ""
    
    $runNow = Read-Host "Execute deployment now? (y/n)"
    
    if ($runNow -eq "y") {
        Write-Host ""
        Write-Host "🔗 Connecting to VPS and deploying..." -ForegroundColor Yellow
        Write-Host ""
        
        # Execute deployment via SSH
        echo $deployCommands | ssh "${VPS_USER}@${VPS_IP}" "bash"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ =========================================" -ForegroundColor Green
            Write-Host "✅  DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
            Write-Host "✅ =========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "🌐 Your application is now live!" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "📍 Access points:" -ForegroundColor Yellow
            Write-Host "   - Frontend:  http://${VPS_IP}" -ForegroundColor White
            Write-Host "   - API Docs:  http://${VPS_IP}/docs" -ForegroundColor White
            Write-Host "   - Health:    http://${VPS_IP}/health" -ForegroundColor White
            Write-Host "   - ReDoc:     http://${VPS_IP}/redoc" -ForegroundColor White
            Write-Host ""
            Write-Host "🔍 Next steps:" -ForegroundColor Yellow
            Write-Host "   1. Open http://${VPS_IP} in your browser" -ForegroundColor Gray
            Write-Host "   2. Test file upload and conversion" -ForegroundColor Gray
            Write-Host "   3. Test merge Word files feature" -ForegroundColor Gray
            Write-Host "   4. Check logs: ssh ${VPS_USER}@${VPS_IP} 'cd ${VPS_PATH} && docker-compose logs -f'" -ForegroundColor Gray
            Write-Host ""
        } else {
            Write-Host ""
            Write-Host "❌ =========================================" -ForegroundColor Red
            Write-Host "❌  DEPLOYMENT FAILED!" -ForegroundColor Red
            Write-Host "❌ =========================================" -ForegroundColor Red
            Write-Host ""
            Write-Host "🔍 Troubleshooting steps:" -ForegroundColor Yellow
            Write-Host "   1. SSH to VPS: ssh ${VPS_USER}@${VPS_IP}" -ForegroundColor Gray
            Write-Host "   2. Check logs: cd ${VPS_PATH} && docker-compose logs" -ForegroundColor Gray
            Write-Host "   3. Check services: docker-compose ps" -ForegroundColor Gray
            Write-Host "   4. Try manual deploy: bash scripts/deploy.sh" -ForegroundColor Gray
            Write-Host ""
        }
    } else {
        Write-Host ""
        Write-Host "📝 Manual deployment instructions:" -ForegroundColor Cyan
        Write-Host "1. SSH to VPS:" -ForegroundColor White
        Write-Host "   ssh ${VPS_USER}@${VPS_IP}" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "2. Run deployment:" -ForegroundColor White
        Write-Host "   cd ${VPS_PATH}" -ForegroundColor Yellow
        Write-Host "   bash scripts/deploy.sh" -ForegroundColor Yellow
        Write-Host ""
    }
} else {
    Write-Host "⏭️  Skipping deployment" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
