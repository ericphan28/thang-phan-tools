# Script tự động setup VPS PostgreSQL như "Cloud Database"
# Sau khi chạy script này, cả localhost và production đều dùng CHUNG connection string!

param(
    [Parameter(Mandatory=$false)]
    [string]$VpsIp = "165.99.59.47",
    
    [Parameter(Mandatory=$false)]
    [string]$YourIp = ""  # IP của máy bạn - sẽ auto-detect nếu không cung cấp
)

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  SETUP SHARED DATABASE - Zero Config Deploy                   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "🎯 Mục tiêu: Localhost và Production dùng CHUNG database config" -ForegroundColor Yellow
Write-Host "   → Khi deploy: KHÔNG cần sửa gì!" -ForegroundColor Green
Write-Host ""

# Auto-detect your public IP
if (-not $YourIp) {
    Write-Host "🔍 Detecting your public IP..." -ForegroundColor Cyan
    try {
        $YourIp = (Invoke-RestMethod -Uri "https://api.ipify.org?format=json").ip
        Write-Host "✅ Your IP: $YourIp" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Cannot auto-detect IP. Please provide manually:" -ForegroundColor Yellow
        $YourIp = Read-Host "Enter your public IP"
    }
}

Write-Host "`n📋 Setup Plan:" -ForegroundColor Cyan
Write-Host "1. SSH to VPS and expose PostgreSQL port" -ForegroundColor Gray
Write-Host "2. Configure firewall (allow only your IP)" -ForegroundColor Gray
Write-Host "3. Update PostgreSQL to accept remote connections" -ForegroundColor Gray
Write-Host "4. Get database password from VPS" -ForegroundColor Gray
Write-Host "5. Update local backend/.env" -ForegroundColor Gray
Write-Host "6. Test connection" -ForegroundColor Gray

Write-Host "`n⚠️  WARNING: This will expose PostgreSQL port to internet!" -ForegroundColor Red
Write-Host "   We will restrict access to your IP only: $YourIp" -ForegroundColor Yellow

$confirm = Read-Host "`nContinue? (y/n)"
if ($confirm -ne "y") {
    Write-Host "Cancelled." -ForegroundColor Red
    exit 0
}

Write-Host "`n" -ForegroundColor Gray
Write-Host "═" * 60 -ForegroundColor Gray

# Step 1: SSH commands to execute on VPS
$sshCommands = @"
#!/bin/bash
set -e

echo "📋 Step 1: Backup current docker-compose.prod.yml"
cd /opt/utility-server
cp docker-compose.prod.yml docker-compose.prod.yml.backup

echo "✅ Backup created: docker-compose.prod.yml.backup"

echo ""
echo "📋 Step 2: Update PostgreSQL ports to expose"
# Update docker-compose to expose port
sed -i 's|"5432:5432"|"0.0.0.0:5432:5432"|g' docker-compose.prod.yml

echo "✅ Updated docker-compose.prod.yml"

echo ""
echo "📋 Step 3: Configure firewall"
# Delete any existing rules for 5432
sudo ufw delete allow 5432/tcp 2>/dev/null || true

# Allow only specific IPs
sudo ufw allow from $YourIp to any port 5432 comment 'PostgreSQL for developer'
sudo ufw allow from $VpsIp to any port 5432 comment 'PostgreSQL for VPS self'

echo "✅ Firewall configured (only $YourIp and $VpsIp)"

echo ""
echo "📋 Step 4: Update PostgreSQL configuration"
# Update pg_hba.conf to allow remote connections
docker exec utility-postgres-prod bash -c "grep -q '0.0.0.0/0' /var/lib/postgresql/data/pg_hba.conf || echo 'host all all 0.0.0.0/0 md5' >> /var/lib/postgresql/data/pg_hba.conf"

# Update postgresql.conf to listen on all interfaces
docker exec utility-postgres-prod bash -c "grep -q \"listen_addresses = '*'\" /var/lib/postgresql/data/postgresql.conf || echo \"listen_addresses = '*'\" >> /var/lib/postgresql/data/postgresql.conf"

echo "✅ PostgreSQL configured for remote connections"

echo ""
echo "📋 Step 5: Restart PostgreSQL"
cd /opt/utility-server
docker-compose restart postgres

echo "✅ PostgreSQL restarted"

echo ""
echo "📋 Step 6: Get database credentials"
echo "DATABASE_CREDENTIALS:"
echo "DB_USER=\$(grep POSTGRES_USER docker-compose.prod.yml | grep -v '#' | cut -d':' -f2 | tr -d ' ' | head -1)"
echo "DB_PASSWORD=\$(grep POSTGRES_PASSWORD docker-compose.prod.yml | grep -v '#' | cut -d':' -f2 | tr -d ' ' | head -1 || cat .env | grep DB_PASSWORD | cut -d'=' -f2)"
echo "DB_NAME=\$(grep POSTGRES_DB docker-compose.prod.yml | grep -v '#' | cut -d':' -f2 | tr -d ' ' | head -1)"

# Get actual values
DB_USER=\$(grep POSTGRES_USER docker-compose.prod.yml | grep -v '#' | cut -d':' -f2 | tr -d ' \${}' | head -1)
DB_PASSWORD=\$(cat .env | grep DB_PASSWORD | cut -d'=' -f2)
DB_NAME=\$(grep POSTGRES_DB docker-compose.prod.yml | grep -v '#' | cut -d':' -f2 | tr -d ' \${}' | head -1)

# If variables, get from .env
[ -z "\$DB_USER" ] && DB_USER=\$(cat .env | grep DB_USER | cut -d'=' -f2)
[ -z "\$DB_NAME" ] && DB_NAME=\$(cat .env | grep DB_NAME | cut -d'=' -f2)

echo ""
echo "CREDENTIALS:"
echo "User: \$DB_USER"
echo "Password: \$DB_PASSWORD"
echo "Database: \$DB_NAME"
echo ""
echo "CONNECTION_STRING:"
echo "postgresql://\$DB_USER:\$DB_PASSWORD@$VpsIp:5432/\$DB_NAME"

echo ""
echo "✅ Setup completed on VPS!"
"@

# Write SSH commands to temp file
$tempScript = [System.IO.Path]::GetTempFileName() + ".sh"
$sshCommands | Out-File -FilePath $tempScript -Encoding UTF8

Write-Host "🚀 Executing setup on VPS..." -ForegroundColor Cyan
Write-Host ""

# Execute on VPS
try {
    $result = ssh root@$VpsIp "bash -s" < $tempScript
    Write-Host $result
    
    # Extract connection string from output
    $connectionString = $result | Select-String -Pattern "postgresql://.*@" | Select-Object -Last 1
    
    if ($connectionString) {
        Write-Host "`n" -ForegroundColor Gray
        Write-Host "═" * 60 -ForegroundColor Gray
        Write-Host "✅ VPS setup completed!" -ForegroundColor Green
        Write-Host ""
        
        # Update local .env
        Write-Host "📝 Updating local backend/.env..." -ForegroundColor Cyan
        
        $envPath = ".\backend\.env"
        $envContent = Get-Content $envPath -Raw
        
        # Comment out old DATABASE_URL
        $envContent = $envContent -replace "^(DATABASE_URL=.*)", "# `$1 (old - commented)"
        
        # Add new connection string
        $newConnection = "`n`n# Shared Database - Same for localhost and production!`n$($connectionString.ToString().Trim())`n"
        $envContent += $newConnection
        
        Set-Content -Path $envPath -Value $envContent
        
        Write-Host "✅ Updated backend/.env" -ForegroundColor Green
        
        # Test connection
        Write-Host "`n🧪 Testing connection from localhost..." -ForegroundColor Cyan
        
        Push-Location ".\backend"
        $testResult = python -c @"
try:
    from sqlalchemy import create_engine
    from app.core.config import settings
    engine = create_engine(settings.DATABASE_URL, connect_args={'connect_timeout': 5})
    conn = engine.connect()
    result = conn.execute('SELECT version();').fetchone()
    print('✅ Connection successful!')
    print(f'PostgreSQL: {result[0][:80]}...')
    conn.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
"@ 2>&1
        Pop-Location
        
        Write-Host $testResult
        
        if ($testResult -match "✅") {
            Write-Host "`n" -ForegroundColor Gray
            Write-Host "═" * 60 -ForegroundColor Gray
            Write-Host "🎉 SUCCESS! Setup completed!" -ForegroundColor Green
            Write-Host ""
            Write-Host "📋 Summary:" -ForegroundColor Cyan
            Write-Host "✅ VPS PostgreSQL exposed on port 5432" -ForegroundColor Gray
            Write-Host "✅ Firewall restricted to your IP: $YourIp" -ForegroundColor Gray
            Write-Host "✅ Local backend/.env updated" -ForegroundColor Gray
            Write-Host "✅ Connection tested successfully" -ForegroundColor Gray
            Write-Host ""
            Write-Host "🚀 Next Steps:" -ForegroundColor Yellow
            Write-Host "1. Start backend: cd backend && python -m uvicorn app.main_simple:app --reload" -ForegroundColor Gray
            Write-Host "2. Test on browser: http://localhost:8000/docs" -ForegroundColor Gray
            Write-Host "3. When ready to deploy:" -ForegroundColor Gray
            Write-Host "   git add ." -ForegroundColor Gray
            Write-Host "   git commit -m 'Use shared database'" -ForegroundColor Gray
            Write-Host "   git push" -ForegroundColor Gray
            Write-Host ""
            Write-Host "💡 No need to change anything when deploying!" -ForegroundColor Green
            Write-Host "   Both localhost and production use the same DATABASE_URL!" -ForegroundColor Green
        } else {
            Write-Host "`n❌ Connection test failed. Check your network/firewall." -ForegroundColor Red
        }
        
    } else {
        Write-Host "⚠️  Could not extract connection string. Check VPS output above." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Error executing on VPS: $_" -ForegroundColor Red
    Write-Host "`n💡 Try running manually:" -ForegroundColor Yellow
    Write-Host "   ssh root@$VpsIp" -ForegroundColor Gray
    Write-Host "   # Then copy commands from setup-shared-db.sh" -ForegroundColor Gray
} finally {
    # Cleanup temp file
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force
    }
}

Write-Host "`n"
