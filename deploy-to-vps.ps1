# ==================================================
# DEPLOY TO VPS - Quick Deploy Script
# ==================================================
# Usage: .\deploy-to-vps.ps1

$VPS_IP = "165.99.59.47"
$VPS_USER = "root"
$VPS_PATH = "/opt/utility-server"

Write-Host ""
Write-Host "🚀 DEPLOYING TO VPS..." -ForegroundColor Cyan
Write-Host "   Target: ${VPS_USER}@${VPS_IP}:${VPS_PATH}" -ForegroundColor Gray
Write-Host ""

# Step 1: Upload docker-compose.prod.yml
Write-Host "📤 [1/4] Uploading docker-compose.prod.yml..." -ForegroundColor Yellow
scp docker-compose.prod.yml "${VPS_USER}@${VPS_IP}:${VPS_PATH}/docker-compose.prod.yml"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to upload docker-compose.prod.yml" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Uploaded successfully`n" -ForegroundColor Green

# Step 2: Pull latest images from GHCR
Write-Host "📥 [2/4] Pulling latest images from GitHub Container Registry..." -ForegroundColor Yellow
ssh "${VPS_USER}@${VPS_IP}" "cd ${VPS_PATH} && docker compose -f docker-compose.prod.yml pull"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to pull images" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Images pulled successfully`n" -ForegroundColor Green

# Step 3: Deploy stack
Write-Host "🚀 [3/4] Deploying stack..." -ForegroundColor Yellow
ssh "${VPS_USER}@${VPS_IP}" "cd ${VPS_PATH} && docker compose -f docker-compose.prod.yml up -d"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to deploy stack" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Stack deployed successfully`n" -ForegroundColor Green

# Step 4: Verify deployment
Write-Host "🔍 [4/4] Verifying deployment..." -ForegroundColor Yellow
ssh "${VPS_USER}@${VPS_IP}" "cd ${VPS_PATH} && docker compose -f docker-compose.prod.yml ps"

Write-Host ""
Write-Host "✅ ========================================" -ForegroundColor Green
Write-Host "✅  DEPLOYMENT COMPLETED!" -ForegroundColor Green
Write-Host "✅ ========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access your application:" -ForegroundColor Cyan
Write-Host "   Frontend:  http://${VPS_IP}" -ForegroundColor White
Write-Host "   API Docs:  http://${VPS_IP}/docs" -ForegroundColor White
Write-Host "   Health:    http://${VPS_IP}/health" -ForegroundColor White
Write-Host "   Portainer: http://${VPS_IP}:9000" -ForegroundColor White
Write-Host ""
Write-Host "📋 Useful commands:" -ForegroundColor Cyan
Write-Host "   View logs: ssh ${VPS_USER}@${VPS_IP} 'docker compose -f ${VPS_PATH}/docker-compose.prod.yml logs -f'" -ForegroundColor Gray
Write-Host "   Restart:   ssh ${VPS_USER}@${VPS_IP} 'docker compose -f ${VPS_PATH}/docker-compose.prod.yml restart'" -ForegroundColor Gray
Write-Host ""
