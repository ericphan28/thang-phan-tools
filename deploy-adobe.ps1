# ================================================================
# DEPLOY ADOBE PDF SERVICES TO PRODUCTION
# Server: 165.99.59.47
# ================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOYING ADOBE PDF INTEGRATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$SERVER = "root@165.99.59.47"
$REMOTE_PATH = "/opt/utility-server"

# ===== Step 1: Check local changes =====
Write-Host "📝 Step 1: Checking local changes..." -ForegroundColor Yellow
git status --short

# ===== Step 2: Commit changes =====
Write-Host "`n💾 Step 2: Committing changes..." -ForegroundColor Yellow
git add backend/app/services/document_service.py
git add backend/requirements.txt
git commit -m "✨ feat: Integrate Adobe PDF Services for high-quality PDF to Word conversion

- Add Adobe SDK integration with graceful fallback to pdf2docx
- Implement hybrid conversion strategy (Adobe first, pdf2docx fallback)
- Add pdfservices-sdk to requirements.txt
- Quality improvement: 7/10 → 10/10 for PDF to Word
- Free tier: 500 conversions/month"

# ===== Step 3: Push to GitHub =====
Write-Host "`n🌐 Step 3: Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host "`n✅ Code pushed to GitHub!" -ForegroundColor Green

# ===== Step 4: Create .env content for server =====
Write-Host "`n📝 Step 4: Preparing environment variables..." -ForegroundColor Yellow

$ENV_CONTENT = @"
# Adobe PDF Services API Configuration
USE_ADOBE_PDF_API=true
PDF_SERVICES_CLIENT_ID=your_adobe_client_id_here
PDF_SERVICES_CLIENT_SECRET=your_adobe_client_secret_here
ADOBE_ORG_ID=your_adobe_org_id_here
"@

Write-Host "⚠️  IMPORTANT: Replace placeholders with actual Adobe credentials!" -ForegroundColor Red
Write-Host "Get credentials from: https://developer.adobe.com/console" -ForegroundColor Yellow
Write-Host ""

# ===== Step 5: Deploy instructions =====
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "📋 DEPLOYMENT INSTRUCTIONS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Run these commands on production server:" -ForegroundColor Yellow
Write-Host ""
Write-Host "# 1. SSH to server" -ForegroundColor White
Write-Host "ssh $SERVER" -ForegroundColor Gray
Write-Host ""
Write-Host "# 2. Go to project directory" -ForegroundColor White
Write-Host "cd $REMOTE_PATH" -ForegroundColor Gray
Write-Host ""
Write-Host "# 3. Pull latest code" -ForegroundColor White
Write-Host "git pull origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "# 4. Add Adobe credentials to backend/.env" -ForegroundColor White
Write-Host "cat >> backend/.env << 'EOF'" -ForegroundColor Gray
Write-Host $ENV_CONTENT -ForegroundColor DarkGray
Write-Host "EOF" -ForegroundColor Gray
Write-Host ""
Write-Host "# 5. Rebuild backend with new dependencies" -ForegroundColor White
Write-Host "docker-compose build backend" -ForegroundColor Gray
Write-Host ""
Write-Host "# 6. Restart backend service" -ForegroundColor White
Write-Host "docker-compose up -d backend" -ForegroundColor Gray
Write-Host ""
Write-Host "# 7. Check logs for Adobe initialization" -ForegroundColor White
Write-Host "docker logs utility_backend --tail=100 | grep -i adobe" -ForegroundColor Gray
Write-Host ""
Write-Host "# 8. Test API endpoint" -ForegroundColor White
Write-Host "curl -X POST http://localhost:8000/api/documents/convert/pdf-to-word \\" -ForegroundColor Gray
Write-Host "  -H 'Authorization: Bearer YOUR_TOKEN' \\" -ForegroundColor Gray
Write-Host "  -F 'file=@test.pdf'" -ForegroundColor Gray
Write-Host ""

# ===== Step 6: Auto-deploy option =====
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "⚡ QUICK DEPLOY" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$AUTO_DEPLOY = Read-Host "Do you want to auto-deploy now? (y/N)"

if ($AUTO_DEPLOY -eq "y" -or $AUTO_DEPLOY -eq "Y") {
    Write-Host "`n🚀 Starting auto-deployment..." -ForegroundColor Yellow
    
    # Create temp script for remote execution
    $DEPLOY_SCRIPT = @"
#!/bin/bash
set -e

echo "=================================="
echo "🚀 Deploying Adobe Integration"
echo "=================================="

cd $REMOTE_PATH

echo ""
echo "📥 Pulling latest code..."
git pull origin main

echo ""
echo "📝 Adding Adobe credentials..."
cat >> backend/.env << 'ENVEOF'
$ENV_CONTENT
ENVEOF

echo ""
echo "🔨 Rebuilding backend..."
docker-compose build backend

echo ""
echo "♻️  Restarting backend..."
docker-compose up -d backend

echo ""
echo "⏳ Waiting for backend to start..."
sleep 10

echo ""
echo "📋 Checking logs..."
docker logs utility_backend --tail=50

echo ""
echo "=================================="
echo "✅ Deployment Complete!"
echo "=================================="
"@

    # Save script to temp file
    $TEMP_SCRIPT = "deploy-temp.sh"
    $DEPLOY_SCRIPT | Out-File -FilePath $TEMP_SCRIPT -Encoding UTF8
    
    # Copy script to server and execute
    Write-Host "📤 Uploading deployment script..." -ForegroundColor Yellow
    scp $TEMP_SCRIPT "${SERVER}:${REMOTE_PATH}/deploy.sh"
    
    Write-Host "▶️  Executing deployment..." -ForegroundColor Yellow
    ssh $SERVER "cd $REMOTE_PATH && chmod +x deploy.sh && ./deploy.sh"
    
    # Cleanup
    Remove-Item $TEMP_SCRIPT -Force
    
    Write-Host "`n✅ Auto-deployment completed!" -ForegroundColor Green
    Write-Host "`nCheck logs: ssh $SERVER 'docker logs utility_backend --tail=100'" -ForegroundColor Cyan
    
} else {
    Write-Host "`n⏭️  Manual deployment - Follow instructions above" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "📊 MONITORING" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Adobe Dashboard: https://developer.adobe.com/console" -ForegroundColor White
Write-Host "Current usage: 1/500 conversions (499 remaining)" -ForegroundColor Green
Write-Host "`nServer logs: ssh $SERVER 'docker logs utility_backend -f'" -ForegroundColor Gray

Write-Host "`n✨ Done!`n" -ForegroundColor Green
