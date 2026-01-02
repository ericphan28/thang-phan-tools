# 🚀 Quick Setup Script - Start PostgreSQL Local và Init Database

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  SETUP POSTGRESQL LOCAL - Development Environment             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Step 1: Start PostgreSQL với Docker
Write-Host "1️⃣  Starting PostgreSQL with Docker..." -ForegroundColor Yellow
docker-compose -f docker-compose.local.yml up -d postgres

Start-Sleep -Seconds 3

# Check if container is running
$postgresRunning = docker ps --filter "name=utility-postgres-local" --format "{{.Names}}"
if ($postgresRunning) {
    Write-Host "✅ PostgreSQL container started: $postgresRunning" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start PostgreSQL container" -ForegroundColor Red
    exit 1
}

Write-Host "`n2️⃣  Updating backend/.env..." -ForegroundColor Yellow

# Step 2: Update backend/.env
$envPath = ".\backend\.env"
$envContent = Get-Content $envPath -Raw

# Comment out SQLite
$envContent = $envContent -replace "(DATABASE_URL=sqlite:.*)", "# `$1"

# Add PostgreSQL URL if not exists
if ($envContent -notmatch "DATABASE_URL=postgresql://") {
    $envContent += "`n`n# PostgreSQL Local (Development)`nDATABASE_URL=postgresql://utility_user:dev_password_123@localhost:5432/utility_db`n"
}

Set-Content -Path $envPath -Value $envContent
Write-Host "✅ Updated backend/.env" -ForegroundColor Green

# Step 3: Wait for PostgreSQL to be ready
Write-Host "`n3️⃣  Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
$maxRetries = 30
$retry = 0
$ready = $false

while (-not $ready -and $retry -lt $maxRetries) {
    $retry++
    $healthCheck = docker exec utility-postgres-local pg_isready -U utility_user 2>&1
    if ($healthCheck -match "accepting connections") {
        $ready = $true
        Write-Host "✅ PostgreSQL is ready!" -ForegroundColor Green
    } else {
        Write-Host "   Waiting... ($retry/$maxRetries)" -ForegroundColor Gray
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    Write-Host "❌ PostgreSQL failed to start properly" -ForegroundColor Red
    exit 1
}

# Step 4: Initialize Database
Write-Host "`n4️⃣  Initializing database tables..." -ForegroundColor Yellow
Push-Location ".\backend"
python init_db.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database tables created" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to initialize database" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Step 5: Seed Admin User
Write-Host "`n5️⃣  Creating admin user..." -ForegroundColor Yellow
python seed_admin.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Admin user created" -ForegroundColor Green
} else {
    Write-Host "⚠️  Admin user may already exist" -ForegroundColor Yellow
}

# Step 6: Seed AI Keys
Write-Host "`n6️⃣  Creating AI provider keys..." -ForegroundColor Yellow
python seed_ai_keys.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ AI keys created" -ForegroundColor Green
} else {
    Write-Host "⚠️  AI keys may already exist" -ForegroundColor Yellow
}

Pop-Location

# Step 7: Show Summary
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ SETUP COMPLETE - PostgreSQL Ready!                        ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "📊 Database Info:" -ForegroundColor Cyan
Write-Host "   Type:     PostgreSQL 15" -ForegroundColor Gray
Write-Host "   Host:     localhost:5432" -ForegroundColor Gray
Write-Host "   Database: utility_db" -ForegroundColor Gray
Write-Host "   User:     utility_user" -ForegroundColor Gray
Write-Host "   Password: dev_password_123" -ForegroundColor Gray

Write-Host "`n👤 Default Login:" -ForegroundColor Cyan
Write-Host "   Username: admin" -ForegroundColor Gray
Write-Host "   Password: admin123" -ForegroundColor Gray

Write-Host "`n🔧 Management Tools:" -ForegroundColor Cyan
Write-Host "   pgAdmin:  http://localhost:5050 (start with: docker-compose -f docker-compose.local.yml up -d pgadmin)" -ForegroundColor Gray
Write-Host "   Direct:   psql -h localhost -U utility_user -d utility_db" -ForegroundColor Gray

Write-Host "`n🚀 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Start Backend:  cd backend && python -m uvicorn app.main_simple:app --reload" -ForegroundColor Gray
Write-Host "   2. Start Frontend: cd frontend && npm run dev" -ForegroundColor Gray
Write-Host "   3. Or use:         .\dev.ps1" -ForegroundColor Gray

Write-Host "`n💡 Useful Commands:" -ForegroundColor Cyan
Write-Host "   Stop:     docker-compose -f docker-compose.local.yml down" -ForegroundColor Gray
Write-Host "   Logs:     docker logs -f utility-postgres-local" -ForegroundColor Gray
Write-Host "   Connect:  docker exec -it utility-postgres-local psql -U utility_user -d utility_db" -ForegroundColor Gray
Write-Host "   Backup:   .\sync-database.ps1 -Action export" -ForegroundColor Gray
Write-Host "   Sync VPS: .\sync-database.ps1 -Action push" -ForegroundColor Gray

Write-Host "`n✅ All done! Happy coding! 🎉`n" -ForegroundColor Green
