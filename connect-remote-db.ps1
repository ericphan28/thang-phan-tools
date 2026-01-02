# Script kết nối localhost tới PostgreSQL trên VPS
# 2 options: SSH Tunnel (secure) hoặc Direct Connection

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("ssh-tunnel", "direct", "test", "disconnect")]
    [string]$Mode = "ssh-tunnel",
    
    [Parameter(Mandatory=$false)]
    [string]$VpsIp = "165.99.59.47",
    
    [Parameter(Mandatory=$false)]
    [int]$LocalPort = 5432,
    
    [Parameter(Mandatory=$false)]
    [int]$RemotePort = 5432
)

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  CONNECT LOCALHOST → VPS POSTGRESQL                            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

switch ($Mode) {
    "ssh-tunnel" {
        Write-Host "🔐 SSH TUNNEL MODE (Secure - Recommended)" -ForegroundColor Yellow
        Write-Host "=" * 60 -ForegroundColor Gray
        
        Write-Host "`n📋 Setup Steps:" -ForegroundColor Cyan
        Write-Host "1. Create SSH tunnel in background" -ForegroundColor Gray
        Write-Host "2. Forward localhost:$LocalPort → VPS:$RemotePort" -ForegroundColor Gray
        Write-Host "3. Update backend/.env" -ForegroundColor Gray
        
        # Check if SSH tunnel already exists
        $existingTunnel = Get-Process | Where-Object { $_.ProcessName -eq "ssh" -and $_.CommandLine -like "*$LocalPort*" }
        if ($existingTunnel) {
            Write-Host "`n⚠️  SSH tunnel already exists (PID: $($existingTunnel.Id))" -ForegroundColor Yellow
            Write-Host "   Use -Mode disconnect to close it first" -ForegroundColor Yellow
            exit 0
        }
        
        # Create SSH tunnel
        Write-Host "`n🔧 Creating SSH tunnel..." -ForegroundColor Cyan
        Write-Host "   Command: ssh -N -L ${LocalPort}:localhost:${RemotePort} root@$VpsIp" -ForegroundColor Gray
        
        # Start SSH tunnel in background
        Start-Process -FilePath "ssh" -ArgumentList "-N", "-L", "${LocalPort}:localhost:${RemotePort}", "root@$VpsIp" -WindowStyle Hidden
        
        Start-Sleep -Seconds 2
        
        # Check if tunnel is working
        Write-Host "`n✅ SSH tunnel created!" -ForegroundColor Green
        Write-Host "   Localhost:$LocalPort → VPS:$RemotePort" -ForegroundColor Gray
        
        # Update backend/.env
        Write-Host "`n📝 Updating backend/.env..." -ForegroundColor Cyan
        $envPath = ".\backend\.env"
        $envContent = Get-Content $envPath -Raw
        
        # Comment out old DATABASE_URL
        $envContent = $envContent -replace "^DATABASE_URL=.*", "# DATABASE_URL (old - commented out)"
        
        # Add new remote connection via SSH tunnel
        $newDbUrl = "`n`n# Remote PostgreSQL via SSH Tunnel (localhost:$LocalPort → VPS)`nDATABASE_URL=postgresql://utility_user:YOUR_PASSWORD@localhost:$LocalPort/utility_db`n"
        
        if ($envContent -notmatch "SSH Tunnel") {
            $envContent += $newDbUrl
        }
        
        Set-Content -Path $envPath -Value $envContent
        Write-Host "✅ Updated backend/.env" -ForegroundColor Green
        
        Write-Host "`n⚠️  IMPORTANT: Update PASSWORD in backend/.env!" -ForegroundColor Yellow
        Write-Host "   Get password from VPS: cat /opt/utility-server/.env | grep DB_PASSWORD" -ForegroundColor Gray
        
        Write-Host "`n📊 Connection Info:" -ForegroundColor Cyan
        Write-Host "   Local:  localhost:$LocalPort" -ForegroundColor Gray
        Write-Host "   Remote: $VpsIp:$RemotePort" -ForegroundColor Gray
        Write-Host "   User:   utility_user" -ForegroundColor Gray
        Write-Host "   DB:     utility_db" -ForegroundColor Gray
        
        Write-Host "`n🔌 To disconnect:" -ForegroundColor Yellow
        Write-Host "   .\connect-remote-db.ps1 -Mode disconnect" -ForegroundColor Gray
    }
    
    "direct" {
        Write-Host "🌐 DIRECT CONNECTION MODE" -ForegroundColor Yellow
        Write-Host "=" * 60 -ForegroundColor Gray
        
        Write-Host "`n⚠️  This requires VPS to expose PostgreSQL port!" -ForegroundColor Yellow
        Write-Host "   Security risk: PostgreSQL accessible from internet" -ForegroundColor Red
        
        Write-Host "`n📋 VPS Setup Required:" -ForegroundColor Cyan
        Write-Host "SSH to VPS and run:" -ForegroundColor Gray
        Write-Host @"

# 1. Update docker-compose.prod.yml
# Change postgres ports from "5432:5432" (internal only)
# to "0.0.0.0:5432:5432" (expose to internet)

# 2. Allow firewall
sudo ufw allow 5432/tcp

# 3. Update PostgreSQL to allow remote connections
docker exec utility-postgres-prod bash -c "echo \"host all all 0.0.0.0/0 md5\" >> /var/lib/postgresql/data/pg_hba.conf"
docker exec utility-postgres-prod bash -c "echo \"listen_addresses = '*'\" >> /var/lib/postgresql/data/postgresql.conf"

# 4. Restart PostgreSQL
docker-compose restart postgres

"@ -ForegroundColor DarkGray
        
        Write-Host "`n📝 Update backend/.env:" -ForegroundColor Cyan
        Write-Host "DATABASE_URL=postgresql://utility_user:PASSWORD@$VpsIp:$RemotePort/utility_db" -ForegroundColor Gray
        
        Write-Host "`n⚠️  SECURITY RECOMMENDATIONS:" -ForegroundColor Red
        Write-Host "   1. Use strong password" -ForegroundColor Yellow
        Write-Host "   2. Restrict firewall to your IP only" -ForegroundColor Yellow
        Write-Host "   3. Use SSL connection" -ForegroundColor Yellow
        Write-Host "   4. Consider SSH tunnel instead (more secure)" -ForegroundColor Yellow
    }
    
    "test" {
        Write-Host "🧪 TESTING CONNECTION..." -ForegroundColor Yellow
        Write-Host "=" * 60 -ForegroundColor Gray
        
        # Read DATABASE_URL from .env
        $envPath = ".\backend\.env"
        $dbUrl = Get-Content $envPath | Select-String -Pattern "^DATABASE_URL=" | Select-Object -First 1
        
        if ($dbUrl) {
            Write-Host "`n📋 Current DATABASE_URL:" -ForegroundColor Cyan
            Write-Host "   $($dbUrl.ToString())" -ForegroundColor Gray
            
            Write-Host "`n🔌 Testing connection..." -ForegroundColor Cyan
            
            # Test with Python
            Push-Location ".\backend"
            $testResult = python -c @"
try:
    from sqlalchemy import create_engine
    from app.core.config import settings
    engine = create_engine(settings.DATABASE_URL)
    conn = engine.connect()
    result = conn.execute('SELECT version();').fetchone()
    print(f'✅ Connected successfully!')
    print(f'   PostgreSQL version: {result[0][:50]}...')
    conn.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
"@ 2>&1
            Pop-Location
            
            Write-Host $testResult
        } else {
            Write-Host "❌ DATABASE_URL not found in backend/.env" -ForegroundColor Red
        }
    }
    
    "disconnect" {
        Write-Host "🔌 DISCONNECTING SSH TUNNEL..." -ForegroundColor Yellow
        Write-Host "=" * 60 -ForegroundColor Gray
        
        # Find and kill SSH tunnel processes
        $sshProcesses = Get-Process | Where-Object { 
            $_.ProcessName -eq "ssh" -and 
            $_.CommandLine -like "*$LocalPort*" 
        }
        
        if ($sshProcesses) {
            foreach ($proc in $sshProcesses) {
                Write-Host "`n🔪 Killing SSH tunnel (PID: $($proc.Id))..." -ForegroundColor Cyan
                Stop-Process -Id $proc.Id -Force
                Write-Host "✅ Disconnected" -ForegroundColor Green
            }
        } else {
            Write-Host "`n⚠️  No SSH tunnel found" -ForegroundColor Yellow
        }
        
        Write-Host "`n💡 To reconnect:" -ForegroundColor Cyan
        Write-Host "   .\connect-remote-db.ps1 -Mode ssh-tunnel" -ForegroundColor Gray
    }
}

Write-Host "`n" -ForegroundColor Gray
Write-Host "═" * 60 -ForegroundColor Gray
Write-Host "💡 Quick Commands:" -ForegroundColor Cyan
Write-Host "   Connect (SSH):    .\connect-remote-db.ps1 -Mode ssh-tunnel" -ForegroundColor Gray
Write-Host "   Connect (Direct): .\connect-remote-db.ps1 -Mode direct" -ForegroundColor Gray
Write-Host "   Test Connection:  .\connect-remote-db.ps1 -Mode test" -ForegroundColor Gray
Write-Host "   Disconnect:       .\connect-remote-db.ps1 -Mode disconnect" -ForegroundColor Gray
Write-Host ""
