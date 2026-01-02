# Script đồng bộ database giữa Local (SQLite/PostgreSQL) và VPS (PostgreSQL)

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("push", "pull", "export", "import")]
    [string]$Action = "export",
    
    [Parameter(Mandatory=$false)]
    [string]$VpsIp = "165.99.59.47",
    
    [Parameter(Mandatory=$false)]
    [string]$VpsPath = "/opt/utility-server",
    
    [Parameter(Mandatory=$false)]
    [string]$BackupPath = ".\backups"
)

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupFile = "$BackupPath\db-backup-$timestamp.sql"

# Create backup directory if not exists
if (-not (Test-Path $BackupPath)) {
    New-Item -ItemType Directory -Path $BackupPath | Out-Null
}

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         DATABASE SYNC TOOL - Local ↔ VPS                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

switch ($Action) {
    "export" {
        Write-Host "📤 EXPORTING Local Database..." -ForegroundColor Yellow
        Write-Host "=" * 60 -ForegroundColor Gray
        
        # Check if using SQLite or PostgreSQL
        $envFile = ".\backend\.env"
        $dbUrl = Get-Content $envFile | Select-String -Pattern "DATABASE_URL" | Select-Object -First 1
        
        if ($dbUrl -match "sqlite") {
            Write-Host "Source: SQLite (backend/utility.db)" -ForegroundColor Cyan
            
            # Export SQLite to SQL
            Push-Location ".\backend"
            python -c @"
import sqlite3
import sys

conn = sqlite3.connect('utility.db')

# Get schema
schema_sql = ''
for line in conn.iterdump():
    schema_sql += line + '\n'

# Write to file
with open('$($backupFile.Replace('\', '/'))', 'w', encoding='utf-8') as f:
    f.write(schema_sql)

conn.close()
print('✅ Exported SQLite to $backupFile')
"@
            Pop-Location
            
        } else {
            Write-Host "Source: PostgreSQL (localhost:5432)" -ForegroundColor Cyan
            
            # Export PostgreSQL
            docker exec utility-postgres-local pg_dump -U utility_user -d utility_db -f "/tmp/backup.sql"
            docker cp utility-postgres-local:/tmp/backup.sql $backupFile
            Write-Host "✅ Exported PostgreSQL to $backupFile" -ForegroundColor Green
        }
        
        Write-Host "`n📊 Backup Info:" -ForegroundColor Cyan
        Write-Host "   File: $backupFile" -ForegroundColor Gray
        Write-Host "   Size: $([math]::Round((Get-Item $backupFile).Length / 1KB, 2)) KB" -ForegroundColor Gray
    }
    
    "push" {
        Write-Host "🚀 PUSHING Local → VPS..." -ForegroundColor Yellow
        Write-Host "=" * 60 -ForegroundColor Gray
        
        # Export first
        & $PSCommandPath -Action "export"
        
        # Copy to VPS
        Write-Host "`n📤 Uploading to VPS..." -ForegroundColor Cyan
        scp $backupFile root@${VpsIp}:${VpsPath}/backup.sql
        
        # Import on VPS
        Write-Host "`n📥 Importing on VPS..." -ForegroundColor Cyan
        ssh root@$VpsIp @"
cd $VpsPath
# Drop existing database and recreate
docker exec utility-postgres-prod psql -U utility_user -d postgres -c "DROP DATABASE IF EXISTS utility_db;"
docker exec utility-postgres-prod psql -U utility_user -d postgres -c "CREATE DATABASE utility_db OWNER utility_user;"
# Import backup
docker exec -i utility-postgres-prod psql -U utility_user -d utility_db < backup.sql
echo "✅ Import completed on VPS"
"@
        
        Write-Host "`n✅ Push completed!" -ForegroundColor Green
    }
    
    "pull" {
        Write-Host "📥 PULLING VPS → Local..." -ForegroundColor Yellow
        Write-Host "=" * 60 -ForegroundColor Gray
        
        # Export from VPS
        Write-Host "📤 Exporting from VPS..." -ForegroundColor Cyan
        ssh root@$VpsIp @"
cd $VpsPath
docker exec utility-postgres-prod pg_dump -U utility_user -d utility_db > vps-backup.sql
"@
        
        # Download from VPS
        Write-Host "`n📥 Downloading from VPS..." -ForegroundColor Cyan
        scp root@${VpsIp}:${VpsPath}/vps-backup.sql $backupFile
        
        # Import to local
        Write-Host "`n📥 Importing to Local..." -ForegroundColor Cyan
        
        # Check local DB type
        $envFile = ".\backend\.env"
        $dbUrl = Get-Content $envFile | Select-String -Pattern "DATABASE_URL" | Select-Object -First 1
        
        if ($dbUrl -match "sqlite") {
            Write-Host "⚠️  Cannot import PostgreSQL dump to SQLite!" -ForegroundColor Red
            Write-Host "   Please switch to PostgreSQL locally first:" -ForegroundColor Yellow
            Write-Host "   1. docker-compose -f docker-compose.local.yml up -d" -ForegroundColor Gray
            Write-Host "   2. Update backend/.env: DATABASE_URL=postgresql://..." -ForegroundColor Gray
            Write-Host "   3. Re-run this script" -ForegroundColor Gray
        } else {
            # Import to local PostgreSQL
            docker exec utility-postgres-local psql -U utility_user -d postgres -c "DROP DATABASE IF EXISTS utility_db;"
            docker exec utility-postgres-local psql -U utility_user -d postgres -c "CREATE DATABASE utility_db OWNER utility_user;"
            Get-Content $backupFile | docker exec -i utility-postgres-local psql -U utility_user -d utility_db
            Write-Host "`n✅ Pull completed!" -ForegroundColor Green
        }
    }
    
    "import" {
        Write-Host "📥 IMPORTING from backup file..." -ForegroundColor Yellow
        Write-Host "=" * 60 -ForegroundColor Gray
        
        # Get latest backup file
        $latestBackup = Get-ChildItem $BackupPath -Filter "db-backup-*.sql" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        
        if (-not $latestBackup) {
            Write-Host "❌ No backup files found in $BackupPath" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "Using backup: $($latestBackup.Name)" -ForegroundColor Cyan
        
        # Import to local PostgreSQL
        docker exec utility-postgres-local psql -U utility_user -d postgres -c "DROP DATABASE IF EXISTS utility_db;"
        docker exec utility-postgres-local psql -U utility_user -d postgres -c "CREATE DATABASE utility_db OWNER utility_user;"
        Get-Content $latestBackup.FullName | docker exec -i utility-postgres-local psql -U utility_user -d utility_db
        
        Write-Host "`n✅ Import completed!" -ForegroundColor Green
    }
}

Write-Host "`n" -ForegroundColor Gray
Write-Host "💡 Usage Examples:" -ForegroundColor Cyan
Write-Host "   .\sync-database.ps1 -Action export  # Export local DB to backup file" -ForegroundColor Gray
Write-Host "   .\sync-database.ps1 -Action push    # Push local → VPS" -ForegroundColor Gray
Write-Host "   .\sync-database.ps1 -Action pull    # Pull VPS → local" -ForegroundColor Gray
Write-Host "   .\sync-database.ps1 -Action import  # Import from latest backup" -ForegroundColor Gray
Write-Host ""
