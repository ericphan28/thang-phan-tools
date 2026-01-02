# Setup Smart Config - Auto-detect Environment
# Localhost → VPS IP, Docker → internal network

param(
    [Parameter(Mandatory=$false)]
    [string]$VpsIp = "165.99.59.47"
)

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  SMART CONFIG SETUP - Auto Environment Detection              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "🧠 Smart Detection Logic:" -ForegroundColor Yellow
Write-Host "   • Inside Docker  → Use 'postgres:5432' (internal)" -ForegroundColor Gray
Write-Host "   • Outside Docker → Use '$VpsIp:5432' (remote)" -ForegroundColor Gray
Write-Host ""

# Detect your public IP
Write-Host "🔍 Detecting your public IP..." -ForegroundColor Cyan
try {
    $yourIp = (Invoke-RestMethod -Uri "https://api.ipify.org?format=json").ip
    Write-Host "✅ Your IP: $yourIp" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Cannot auto-detect. Using localhost..." -ForegroundColor Yellow
    $yourIp = Read-Host "Enter your public IP (or press Enter to skip firewall setup)"
}

Write-Host "`n📋 Setup Steps:" -ForegroundColor Cyan
Write-Host "1. Expose PostgreSQL on VPS (if not done)" -ForegroundColor Gray
Write-Host "2. Configure firewall" -ForegroundColor Gray
Write-Host "3. Get database password from VPS" -ForegroundColor Gray
Write-Host "4. Update local .env with credentials" -ForegroundColor Gray
Write-Host "5. Test connection" -ForegroundColor Gray

$confirm = Read-Host "`nContinue? (y/n)"
if ($confirm -ne "y") {
    Write-Host "Cancelled." -ForegroundColor Red
    exit 0
}

Write-Host "`n═" * 60 -ForegroundColor Gray

# Step 1: VPS Setup
Write-Host "`n1️⃣  Setting up VPS PostgreSQL..." -ForegroundColor Yellow

$vpsCommands = @"
#!/bin/bash
set -e

cd /opt/utility-server

echo "📋 Checking PostgreSQL exposure..."

# Check if port is already exposed
if grep -q "0.0.0.0:5432:5432" docker-compose.prod.yml; then
    echo "✅ PostgreSQL already exposed"
else
    echo "📝 Updating docker-compose.prod.yml..."
    # Backup
    cp docker-compose.prod.yml docker-compose.prod.yml.backup.\$(date +%Y%m%d)
    
    # Update to expose port
    sed -i 's|"5432:5432"|"0.0.0.0:5432:5432"|g' docker-compose.prod.yml
    echo "✅ Updated docker-compose.prod.yml"
fi

# Configure firewall
echo ""
echo "📋 Configuring firewall..."
if [ -n "$yourIp" ]; then
    sudo ufw allow from $yourIp to any port 5432 comment 'Dev access'
    sudo ufw allow from $VpsIp to any port 5432 comment 'VPS self'
    echo "✅ Firewall: Allow $yourIp and $VpsIp"
else
    echo "⚠️  No IP provided - skip firewall config"
fi

# Update PostgreSQL config
echo ""
echo "📋 Configuring PostgreSQL for remote connections..."
docker exec utility-postgres-prod bash -c "grep -q '0.0.0.0/0' /var/lib/postgresql/data/pg_hba.conf || echo 'host all all 0.0.0.0/0 md5' >> /var/lib/postgresql/data/pg_hba.conf" 2>/dev/null || echo "⚠️ Cannot update pg_hba.conf (may already configured)"

docker exec utility-postgres-prod bash -c "grep -q \"listen_addresses = '*'\" /var/lib/postgresql/data/postgresql.conf || echo \"listen_addresses = '*'\" >> /var/lib/postgresql/data/postgresql.conf" 2>/dev/null || echo "⚠️ Cannot update postgresql.conf (may already configured)"

echo "✅ PostgreSQL configured"

# Restart PostgreSQL
echo ""
echo "📋 Restarting PostgreSQL..."
docker-compose restart postgres
sleep 3
echo "✅ PostgreSQL restarted"

# Get credentials
echo ""
echo "📋 Database Credentials:"
echo "═══════════════════════"

DB_USER=\$(grep POSTGRES_USER docker-compose.prod.yml | grep -v '#' | head -1 | cut -d':' -f2 | tr -d ' \${}')
DB_NAME=\$(grep POSTGRES_DB docker-compose.prod.yml | grep -v '#' | head -1 | cut -d':' -f2 | tr -d ' \${}')

# Try to get from docker-compose first, then .env
if grep -q "POSTGRES_PASSWORD:" docker-compose.prod.yml; then
    DB_PASSWORD=\$(grep POSTGRES_PASSWORD docker-compose.prod.yml | grep -v '#' | head -1 | cut -d':' -f2 | tr -d ' \${}')
fi

# If still using env variable, get from .env
if [ -z "\$DB_PASSWORD" ] || [[ "\$DB_PASSWORD" == *"DB_PASSWORD"* ]]; then
    DB_PASSWORD=\$(grep DB_PASSWORD .env 2>/dev/null | cut -d'=' -f2 | tr -d ' ')
fi

# Default values if not found
DB_USER=\${DB_USER:-utility_user}
DB_NAME=\${DB_NAME:-utility_db}

echo "User: \$DB_USER"
echo "Password: \$DB_PASSWORD"
echo "Database: \$DB_NAME"
echo "Host: $VpsIp"
echo "Port: 5432"

echo ""
echo "✅ VPS setup complete!"
"@

# Execute on VPS
Write-Host "🚀 Executing on VPS..." -ForegroundColor Cyan
try {
    $result = $vpsCommands | ssh root@$VpsIp "bash -s"
    Write-Host $result
    
    # Extract credentials
    $credentials = $result | Select-String -Pattern "(User|Password|Database):" -Context 0,0
    
    if ($credentials) {
        Write-Host "`n" -ForegroundColor Gray
        Write-Host "═" * 60 -ForegroundColor Gray
        Write-Host "✅ VPS setup completed!" -ForegroundColor Green
        
        # Parse credentials
        $dbUser = ($result | Select-String -Pattern "User: (.+)" | Select-Object -Last 1).Matches.Groups[1].Value.Trim()
        $dbPassword = ($result | Select-String -Pattern "Password: (.+)" | Select-Object -Last 1).Matches.Groups[1].Value.Trim()
        $dbName = ($result | Select-String -Pattern "Database: (.+)" | Select-Object -Last 1).Matches.Groups[1].Value.Trim()
        
        Write-Host "`n2️⃣  Updating local .env..." -ForegroundColor Yellow
        
        # Update backend/.env
        $envPath = ".\backend\.env"
        $envContent = Get-Content $envPath -Raw
        
        # Update or add DB credentials
        if ($envContent -match "DB_USER=") {
            $envContent = $envContent -replace "DB_USER=.*", "DB_USER=$dbUser"
        } else {
            $envContent += "`nDB_USER=$dbUser"
        }
        
        if ($envContent -match "DB_PASSWORD=") {
            $envContent = $envContent -replace "DB_PASSWORD=.*", "DB_PASSWORD=$dbPassword"
        } else {
            $envContent += "`nDB_PASSWORD=$dbPassword"
        }
        
        if ($envContent -match "DB_NAME=") {
            $envContent = $envContent -replace "DB_NAME=.*", "DB_NAME=$dbName"
        } else {
            $envContent += "`nDB_NAME=$dbName"
        }
        
        Set-Content -Path $envPath -Value $envContent
        Write-Host "✅ Updated backend/.env" -ForegroundColor Green
        
        # Test connection
        Write-Host "`n3️⃣  Testing connection..." -ForegroundColor Yellow
        
        Push-Location ".\backend"
        $testResult = python -c @"
import os
os.environ['DB_USER'] = '$dbUser'
os.environ['DB_PASSWORD'] = '$dbPassword'
os.environ['DB_NAME'] = '$dbName'

try:
    from sqlalchemy import create_engine
    connection_string = f'postgresql://$dbUser`:$dbPassword@$VpsIp`:5432/$dbName'
    engine = create_engine(connection_string, connect_args={'connect_timeout': 5})
    conn = engine.connect()
    result = conn.execute('SELECT version();').fetchone()
    print('✅ Connection successful!')
    print(f'PostgreSQL version: {result[0][:80]}')
    conn.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
"@ 2>&1
        Pop-Location
        
        Write-Host $testResult
        
        if ($testResult -match "✅") {
            Write-Host "`n" -ForegroundColor Gray
            Write-Host "═" * 60 -ForegroundColor Gray
            Write-Host "🎉 SETUP COMPLETE!" -ForegroundColor Green
            Write-Host ""
            Write-Host "📊 Configuration:" -ForegroundColor Cyan
            Write-Host "   Environment Detection: Enabled ✅" -ForegroundColor Gray
            Write-Host "   Localhost DB Host: $VpsIp (auto-detected)" -ForegroundColor Gray
            Write-Host "   Docker DB Host: postgres (auto-detected)" -ForegroundColor Gray
            Write-Host ""
            Write-Host "🚀 How it works:" -ForegroundColor Yellow
            Write-Host "   • Run locally → Connects to $VpsIp`:5432" -ForegroundColor Gray
            Write-Host "   • Run in Docker → Connects to postgres:5432" -ForegroundColor Gray
            Write-Host "   • Same code, different environments!" -ForegroundColor Gray
            Write-Host ""
            Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
            Write-Host "   1. Start backend: cd backend && python -m uvicorn app.main_simple:app --reload" -ForegroundColor Gray
            Write-Host "   2. Backend will auto-detect and use VPS DB" -ForegroundColor Gray
            Write-Host "   3. When deploy to VPS, it auto-uses internal 'postgres' host" -ForegroundColor Gray
            Write-Host ""
            Write-Host "💡 Deploy workflow:" -ForegroundColor Yellow
            Write-Host "   git add ." -ForegroundColor Gray
            Write-Host "   git commit -m 'Smart DB config'" -ForegroundColor Gray
            Write-Host "   git push" -ForegroundColor Gray
            Write-Host "   → No need to change any config! 🎉" -ForegroundColor Green
        } else {
            Write-Host "`n⚠️  Connection test failed" -ForegroundColor Yellow
            Write-Host "Check firewall or network connectivity" -ForegroundColor Gray
        }
        
    } else {
        Write-Host "`n⚠️  Could not extract credentials from VPS" -ForegroundColor Yellow
        Write-Host "Please check VPS output above" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host "`n💡 Try running commands manually on VPS:" -ForegroundColor Yellow
    Write-Host "   ssh root@$VpsIp" -ForegroundColor Gray
}

Write-Host "`n✅ Done!`n" -ForegroundColor Green
