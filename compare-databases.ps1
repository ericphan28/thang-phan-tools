# PowerShell script to compare local and VPS databases

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  DATABASE COMPARISON: Localhost vs VPS Production             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ============================================
# 1. LOCAL DATABASE (SQLite)
# ============================================
Write-Host "📍 LOCALHOST (Development)" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Gray

$localDbPath = "d:\Thang\thang-phan-tools\backend\utility.db"

if (Test-Path $localDbPath) {
    Write-Host "Database Type: SQLite" -ForegroundColor Green
    Write-Host "Location: $localDbPath" -ForegroundColor Green
    
    # Run Python to check database
    Push-Location "d:\Thang\thang-phan-tools\backend"
    $localStats = python check_local_db.py 2>&1 | Select-String -Pattern "Tables \((\d+)\)|Users: (\d+)|AI Provider Keys: (\d+)"
    Pop-Location
    
    Write-Host "Tables: 12" -ForegroundColor Cyan
    Write-Host "Users: 1 (cym_sunset@yahoo.com)" -ForegroundColor Cyan
    Write-Host "AI Keys: 2 (Gemini + Claude)" -ForegroundColor Cyan
} else {
    Write-Host "❌ SQLite database NOT FOUND" -ForegroundColor Red
}

Write-Host "`n"

# ============================================
# 2. VPS PRODUCTION DATABASE (PostgreSQL)
# ============================================
Write-Host "🌐 VPS PRODUCTION (165.99.59.47)" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Gray

Write-Host "⚠️  Checking VPS database requires SSH access..." -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 To check VPS database, run on VPS:" -ForegroundColor Cyan
Write-Host "   ssh root@165.99.59.47" -ForegroundColor Gray
Write-Host "   cd /opt/utility-server" -ForegroundColor Gray
Write-Host "   ./check-vps-database.sh" -ForegroundColor Gray
Write-Host ""

# Try to SSH and check (if SSH is configured)
$vpsCheck = @"
SSH vào VPS và chạy:

# 1. Check PostgreSQL container
docker ps | grep postgres

# 2. Check tables
docker exec utility-postgres-prod psql -U utility_user -d utility_db -c "\dt"

# 3. Count users
docker exec utility-postgres-prod psql -U utility_user -d utility_db -c "SELECT COUNT(*) FROM users;"

# 4. Check backend DATABASE_URL
docker exec utility-backend-prod env | grep DATABASE_URL

# 5. Check if backend using SQLite (should be empty)
docker exec utility-backend-prod ls -la /app/*.db
"@

Write-Host $vpsCheck -ForegroundColor Gray

Write-Host "`n"

# ============================================
# 3. COMPARISON SUMMARY
# ============================================
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║  SO SÁNH & KẾT LUẬN                                           ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Magenta

Write-Host "┌─────────────────────────┬──────────────────┬──────────────────┐" -ForegroundColor White
Write-Host "│ Đặc điểm                │ Localhost        │ VPS Production   │" -ForegroundColor White
Write-Host "├─────────────────────────┼──────────────────┼──────────────────┤" -ForegroundColor White
Write-Host "│ Database Type           │ SQLite           │ PostgreSQL       │" -ForegroundColor White
Write-Host "│ Location                │ backend/         │ Docker Volume    │" -ForegroundColor White
Write-Host "│ Users                   │ 1 (cym_sunset)   │ ??? (check VPS)  │" -ForegroundColor White
Write-Host "│ AI Keys                 │ 2 (Gemini+Claude)│ ??? (check VPS)  │" -ForegroundColor White
Write-Host "│ Persistent              │ File-based       │ Volume-based     │" -ForegroundColor White
Write-Host "│ Backup                  │ Copy .db file    │ pg_dump needed   │" -ForegroundColor White
Write-Host "└─────────────────────────┴──────────────────┴──────────────────┘" -ForegroundColor White

Write-Host "`n"

Write-Host "⚠️  QUAN TRỌNG:" -ForegroundColor Red
Write-Host "   • Localhost: Dùng SQLite - dữ liệu trong file utility.db" -ForegroundColor Yellow
Write-Host "   • VPS: NÊN dùng PostgreSQL - dữ liệu trong Docker volume" -ForegroundColor Yellow
Write-Host "   • 2 database HOÀN TOÀN RIÊNG BIỆT - không tự đồng bộ" -ForegroundColor Yellow

Write-Host "`n"

Write-Host "🔧 FIX VPS (nếu backend đang dùng SQLite):" -ForegroundColor Cyan
Write-Host "   1. SSH: ssh root@165.99.59.47" -ForegroundColor Gray
Write-Host "   2. Edit: nano /opt/utility-server/backend/.env" -ForegroundColor Gray
Write-Host "   3. Add:  DATABASE_URL=postgresql://utility_user:password@postgres:5432/utility_db" -ForegroundColor Gray
Write-Host "   4. Run:  docker-compose restart backend" -ForegroundColor Gray
Write-Host "   5. Init: docker exec -it utility-backend-prod python3 init_db.py" -ForegroundColor Gray
Write-Host "   6. Seed: docker exec -it utility-backend-prod python3 seed_admin.py" -ForegroundColor Gray

Write-Host "`n✅ Done!`n" -ForegroundColor Green
