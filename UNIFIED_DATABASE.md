# 🎯 THỐNG NHẤT DATABASE: Dev = Production

## ❌ Vấn Đề Cũ
- **Localhost:** SQLite (`utility.db`)
- **Production:** PostgreSQL (Docker)
- **Kết quả:** Không đồng bộ, khó debug, schema khác nhau

## ✅ Giải Pháp Mới
**Dùng PostgreSQL cho CẢ HAI môi trường!**

---

## 🚀 SETUP NHANH (3 phút)

### Cách 1: Chạy Script Tự Động (Khuyến nghị)
```powershell
# Một lệnh duy nhất - setup tất cả!
.\setup-postgres-local.ps1
```

Script này sẽ:
1. ✅ Start PostgreSQL container
2. ✅ Update backend/.env
3. ✅ Tạo database tables
4. ✅ Seed admin user (admin/admin123)
5. ✅ Seed AI keys (Gemini + Claude)

### Cách 2: Manual Setup
```powershell
# 1. Start PostgreSQL
docker-compose -f docker-compose.local.yml up -d postgres

# 2. Update backend/.env
# Thêm dòng này:
DATABASE_URL=postgresql://utility_user:dev_password_123@localhost:5432/utility_db

# 3. Init database
cd backend
python init_db.py
python seed_admin.py
python seed_ai_keys.py

# 4. Start servers
cd ..
.\dev.ps1
```

---

## 📊 KẾT QUẢ

| Môi trường | Database | Port | Location |
|------------|----------|------|----------|
| **Localhost** | PostgreSQL 15 | 5432 | Docker container |
| **Production** | PostgreSQL 15 | 5432 | Docker container |

**Giống nhau 100%!** → Dễ debug, dễ test, dễ deploy

---

## 🔄 ĐỒNG BỘ DATA

### Export/Backup Local
```powershell
.\sync-database.ps1 -Action export
# → Tạo file: backups/db-backup-YYYYMMDD-HHMMSS.sql
```

### Push Local → VPS
```powershell
.\sync-database.ps1 -Action push
# → Copy toàn bộ data từ local lên VPS
```

### Pull VPS → Local
```powershell
.\sync-database.ps1 -Action pull
# → Copy toàn bộ data từ VPS về local
```

### Import từ Backup
```powershell
.\sync-database.ps1 -Action import
# → Import backup file mới nhất
```

---

## 🛠️ QUẢN LÝ DATABASE

### Xem Tables
```powershell
docker exec -it utility-postgres-local psql -U utility_user -d utility_db -c "\dt"
```

### Connect với psql
```powershell
docker exec -it utility-postgres-local psql -U utility_user -d utility_db
```

### Xem Logs
```powershell
docker logs -f utility-postgres-local
```

### Dùng pgAdmin (Web UI)
```powershell
# Start pgAdmin
docker-compose -f docker-compose.local.yml up -d pgadmin

# Open browser: http://localhost:5050
# Email: admin@localhost.com
# Password: admin123

# Add server:
#   Host: postgres (or host.docker.internal)
#   Port: 5432
#   User: utility_user
#   Password: dev_password_123
```

---

## 📋 CREDENTIALS

### Local PostgreSQL
```
Host:     localhost
Port:     5432
Database: utility_db
User:     utility_user
Password: dev_password_123
```

### App Login
```
Username: admin
Password: admin123
```

---

## ⚙️ TROUBLESHOOTING

### Lỗi: "Connection refused"
```powershell
# Check container running
docker ps | grep postgres

# Restart container
docker-compose -f docker-compose.local.yml restart postgres
```

### Lỗi: "Database does not exist"
```powershell
# Recreate database
docker exec -it utility-postgres-local psql -U utility_user -d postgres -c "DROP DATABASE IF EXISTS utility_db;"
docker exec -it utility-postgres-local psql -U utility_user -d postgres -c "CREATE DATABASE utility_db OWNER utility_user;"

# Re-init
cd backend
python init_db.py
python seed_admin.py
```

### Reset Database Hoàn Toàn
```powershell
# Stop và xóa volume
docker-compose -f docker-compose.local.yml down -v

# Start lại và init
.\setup-postgres-local.ps1
```

---

## 🎯 LỢI ÍCH

### Trước (SQLite local)
- ❌ Schema khác với production
- ❌ Không test được PostgreSQL features
- ❌ Không đồng bộ data
- ❌ Migration phức tạp
- ❌ Team khó sync

### Sau (PostgreSQL local)
- ✅ Dev = Production 100%
- ✅ Test full-text search, JSON, etc.
- ✅ Đồng bộ data dễ dàng (pg_dump)
- ✅ Migration test được trước
- ✅ Team dùng chung schema

---

## 📝 FILE QUAN TRỌNG

| File | Mục đích |
|------|----------|
| `docker-compose.local.yml` | Config PostgreSQL local |
| `setup-postgres-local.ps1` | Setup tự động |
| `sync-database.ps1` | Đồng bộ data |
| `backend/.env` | Database connection string |
| `backend/init_db.py` | Tạo tables |
| `backend/seed_admin.py` | Tạo admin user |

---

## 🚀 WORKFLOW MỚI

### Development Flow
```
1. Code trên localhost với PostgreSQL
2. Test trên localhost
3. Export data (nếu cần): .\sync-database.ps1 -Action export
4. Commit code
5. Push to GitHub → Auto deploy to VPS
6. Sync data (nếu cần): .\sync-database.ps1 -Action push
```

### Production Parity
```
Development (localhost)     Production (VPS)
┌─────────────────────┐    ┌─────────────────────┐
│ PostgreSQL 15       │ ←→ │ PostgreSQL 15       │
│ Port: 5432          │    │ Port: 5432          │
│ utility_db          │    │ utility_db          │
│ Same schema ✅      │    │ Same schema ✅      │
└─────────────────────┘    └─────────────────────┘
```

---

## ✅ CHECKLIST

**Setup lần đầu:**
- [ ] Chạy `.\setup-postgres-local.ps1`
- [ ] Verify: `docker ps | grep postgres`
- [ ] Test login: http://localhost:5173 (admin/admin123)
- [ ] Check tables: `docker exec -it utility-postgres-local psql -U utility_user -d utility_db -c "\dt"`

**Hàng ngày:**
- [ ] Start: `docker-compose -f docker-compose.local.yml up -d`
- [ ] Code như bình thường
- [ ] Stop: `docker-compose -f docker-compose.local.yml down`

**Khi cần sync:**
- [ ] Export: `.\sync-database.ps1 -Action export`
- [ ] Push lên VPS: `.\sync-database.ps1 -Action push`
- [ ] Hoặc pull về: `.\sync-database.ps1 -Action pull`

---

## 🎉 KẾT LUẬN

**Không còn 2 database khác nhau!**
- ✅ Development = Production
- ✅ Dễ test, dễ debug, dễ deploy
- ✅ Đồng bộ data đơn giản
- ✅ Team work hiệu quả hơn

**One database to rule them all!** 👑
