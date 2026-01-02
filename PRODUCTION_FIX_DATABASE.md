# 🔧 FIX PRODUCTION DATABASE ERROR

## ❌ Vấn Đề
Backend trên production đang dùng **SQLite** thay vì **PostgreSQL**, dẫn đến lỗi "no such table: users" khi login.

## 🎯 Nguyên Nhân
1. File `.env` trên VPS chưa có `DATABASE_URL` cho PostgreSQL
2. Backend default dùng SQLite local
3. PostgreSQL container đang chạy nhưng backend không kết nối

## ✅ Giải Pháp

### Bước 1: SSH vào VPS
```bash
ssh root@165.99.59.47
cd /opt/utility-server
```

### Bước 2: Update File .env
Thêm dòng này vào file `backend/.env`:

```bash
nano backend/.env
```

Thêm/sửa dòng:
```dotenv
# Database - PostgreSQL for Production
DATABASE_URL=postgresql://utility_user:your_password_here@postgres:5432/utility_db

# Thay your_password_here bằng password thật trong docker-compose.prod.yml
```

**Lấy password từ docker-compose:**
```bash
# Xem password trong docker-compose.prod.yml
grep DB_PASSWORD docker-compose.prod.yml
```

Hoặc tạo password mới và update cả 2 chỗ:
```dotenv
# Trong backend/.env:
DATABASE_URL=postgresql://utility_user:SecurePass123@postgres:5432/utility_db

# Trong docker-compose.prod.yml (hoặc .env root):
DB_PASSWORD=SecurePass123
DB_USER=utility_user
DB_NAME=utility_db
```

### Bước 3: Khởi Tạo Database Tables
Chạy lệnh init database:

```bash
# Vào container backend
docker exec -it utility-backend-prod bash

# Chạy init script
python3 init_db.py

# Tạo admin user
python3 seed_admin.py

# Exit container
exit
```

### Bước 4: Restart Backend Container
```bash
docker-compose restart backend
```

### Bước 5: Kiểm Tra Logs
```bash
docker logs -f utility-backend-prod
```

Tìm dòng:
- ✅ `Connected to PostgreSQL database`
- ✅ `Database initialized successfully`

### Bước 6: Test Login
Truy cập: http://165.99.59.47/login

Thử đăng nhập với:
- **Username:** `admin`
- **Password:** `admin123`

---

## 🚨 Nếu Vẫn Lỗi

### Option A: Recreate Database (Mất dữ liệu cũ)
```bash
# Stop all containers
docker-compose down

# Remove old volumes
docker volume rm utility-server_postgres_data

# Start again
docker-compose up -d

# Init database
docker exec -it utility-backend-prod python3 init_db.py
docker exec -it utility-backend-prod python3 seed_admin.py
```

### Option B: Manually Create Tables
```bash
# Connect to PostgreSQL
docker exec -it utility-postgres-prod psql -U utility_user -d utility_db

# Check tables
\dt

# If no tables, exit and run init_db.py
\q
docker exec -it utility-backend-prod python3 init_db.py
```

---

## 📋 Checklist
- [ ] SSH vào VPS
- [ ] Update `backend/.env` với `DATABASE_URL` PostgreSQL
- [ ] Restart backend container
- [ ] Chạy `init_db.py` nếu chưa có tables
- [ ] Chạy `seed_admin.py` để tạo admin user
- [ ] Test login trên browser
- [ ] Check logs không có lỗi

---

## 🎯 Kết Quả Mong Đợi

**Trước fix:**
```
(sqlite3.OperationalError) no such table: users
```

**Sau fix:**
- ✅ Login thành công
- ✅ Backend kết nối PostgreSQL
- ✅ Tables được tạo: users, roles, permissions, activity_logs, ai_provider_keys...
- ✅ Admin user hoạt động: admin/admin123

---

## 📝 Lưu Ý

1. **Local Development** → dùng SQLite (không cần setup gì)
2. **Production** → dùng PostgreSQL (cần DATABASE_URL trong .env)

3. File `config.py` đã được fix để ưu tiên DATABASE_URL từ environment variable

4. Nếu muốn reset hoàn toàn database:
```bash
docker-compose down
docker volume rm utility-server_postgres_data
docker-compose up -d
docker exec -it utility-backend-prod python3 init_db.py
docker exec -it utility-backend-prod python3 seed_admin.py
```

---

## 🔗 Connection String Format
```
postgresql://username:password@host:port/database_name

# Example local:
postgresql://utility_user:password123@localhost:5432/utility_db

# Example Docker (internal network):
postgresql://utility_user:password123@postgres:5432/utility_db
```

**Chú ý:** Dùng `postgres` (service name) thay vì `localhost` trong Docker network!
