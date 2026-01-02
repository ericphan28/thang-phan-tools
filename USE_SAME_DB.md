# 🔄 THỐNG NHẤT DATABASE: Dùng PostgreSQL cho Cả Localhost & Production

## ❌ Vấn Đề Hiện Tại
- **Localhost:** SQLite (file utility.db)
- **Production:** PostgreSQL (Docker volume)
- **Kết quả:** Không thể đồng bộ, schema khác nhau, khó debug

---

## ✅ GIẢI PHÁP: Dùng PostgreSQL cho CẢ HAI

### Option 1: PostgreSQL Local (Khuyến nghị ⭐)

#### Bước 1: Start PostgreSQL Local với Docker
```powershell
# Tạo docker-compose.local.yml (đã có sẵn)
cd d:\Thang\thang-phan-tools
docker-compose -f docker-compose.local.yml up -d postgres
```

#### Bước 2: Update backend/.env
```dotenv
# Comment SQLite
# DATABASE_URL=sqlite:///./utility.db

# Use PostgreSQL
DATABASE_URL=postgresql://utility_user:dev_password@localhost:5432/utility_db
```

#### Bước 3: Init Database
```powershell
cd backend
python init_db.py
python seed_admin.py
python seed_ai_keys.py
```

#### Bước 4: Start Backend
```powershell
# Backend sẽ tự động connect PostgreSQL
python -m uvicorn app.main_simple:app --reload
```

---

### Option 2: Giữ SQLite Local (Đơn giản hơn)

**Ưu điểm:**
- Không cần Docker
- Không cần setup gì
- File backup đơn giản

**Nhược điểm:**
- Schema có thể khác PostgreSQL
- Không test được production environment
- Không đồng bộ được data

---

### Option 3: Đồng Bộ Data Giữa SQLite ↔ PostgreSQL

Dùng script `sync-database.ps1` để:
- Export data từ SQLite → SQL file
- Import vào PostgreSQL
- Hoặc ngược lại: PostgreSQL → SQLite

```powershell
# Sync từ Local (SQLite) lên VPS (PostgreSQL)
.\sync-database.ps1 -Direction "LocalToVPS"

# Sync từ VPS (PostgreSQL) về Local (SQLite)
.\sync-database.ps1 -Direction "VPSToLocal"
```

---

## 🎯 KHUYẾN NGHỊ: Option 1 (PostgreSQL cho cả 2)

### Tại sao?
1. ✅ **Parity:** Dev = Production → ít bug hơn
2. ✅ **Migration:** Test migration trên local trước
3. ✅ **Features:** Test full-text search, JSON fields, etc.
4. ✅ **Backup/Restore:** Dùng pg_dump cho cả 2
5. ✅ **Team work:** Mọi người dùng chung schema

### Docker Compose Local Setup
```yaml
# docker-compose.local.yml
services:
  postgres:
    image: postgres:15-alpine
    container_name: utility-postgres-local
    environment:
      POSTGRES_USER: utility_user
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: utility_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_local:/var/lib/postgresql/data

volumes:
  postgres_local:
```

---

## 📋 Checklist Setup PostgreSQL Local

- [ ] 1. Tạo `docker-compose.local.yml` (hoặc dùng có sẵn)
- [ ] 2. Start: `docker-compose -f docker-compose.local.yml up -d`
- [ ] 3. Update `backend/.env` với `DATABASE_URL` PostgreSQL
- [ ] 4. Run `python init_db.py`
- [ ] 5. Run `python seed_admin.py`
- [ ] 6. Test login: localhost:5173
- [ ] 7. Verify tables: `docker exec -it utility-postgres-local psql -U utility_user -d utility_db -c "\dt"`

---

## 🔄 Script Đồng Bộ Data

### 1. Export từ Local SQLite
```powershell
# Tạo SQL dump từ SQLite
python export-sqlite-to-sql.py
# Output: backup-sqlite-2024-12-25.sql
```

### 2. Import vào VPS PostgreSQL
```bash
ssh root@165.99.59.47
cd /opt/utility-server
docker exec -i utility-postgres-prod psql -U utility_user -d utility_db < backup-sqlite-2024-12-25.sql
```

### 3. Hoặc dùng script tự động
```powershell
.\sync-database.ps1 -Action "push"  # Local → VPS
.\sync-database.ps1 -Action "pull"  # VPS → Local
```

---

## 🎯 KẾT LUẬN

**Lựa chọn tốt nhất:**
1. **Development:** PostgreSQL trong Docker (port 5432)
2. **Production:** PostgreSQL trong Docker (port 5432)
3. **Đồng bộ:** `pg_dump` và `psql` restore

**Thay đổi cần làm:**
1. ✅ Fix `backend/app/core/config.py` (đã làm)
2. ⏳ Tạo `docker-compose.local.yml`
3. ⏳ Tạo script `sync-database.ps1`
4. ⏳ Update documentation

---

## 🚀 Quick Start (5 phút)

```powershell
# 1. Start PostgreSQL local
docker-compose -f docker-compose.local.yml up -d

# 2. Update .env
echo "DATABASE_URL=postgresql://utility_user:dev_password@localhost:5432/utility_db" >> backend/.env

# 3. Init database
cd backend
python init_db.py
python seed_admin.py

# 4. Start servers
cd ..
.\dev.ps1

# 5. Login
# http://localhost:5173
# admin / admin123
```

✅ Done! Giờ dev và production dùng cùng PostgreSQL!
