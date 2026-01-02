# GIẢI PHÁP: Localhost & Production dùng CHUNG DATABASE CONFIG

## 🎯 Yêu Cầu
- Localhost backend kết nối tới VPS database
- Push code lên GitHub → Deploy lên VPS
- **KHÔNG cần sửa config database** khi deploy

---

## 📋 4 PHƯƠNG ÁN

### 🥇 **PHƯƠNG ÁN 1: Hosted Database Service (Giống Supabase)**

**Ý tưởng:** Dùng dịch vụ PostgreSQL cloud, cả local và production đều connect qua internet.

#### Services có thể dùng:

| Service | Free Tier | Location | Latency VN |
|---------|-----------|----------|------------|
| **Supabase** | 2GB, 500MB bandwidth | Singapore | ~20-50ms |
| **Neon** | 0.5GB | AWS Singapore | ~30-60ms |
| **Railway** | $5/month | Global | ~50-100ms |
| **ElephantSQL** | 20MB | Singapore | ~30-60ms |
| **Aiven** | 1 month free trial | Multiple | Varies |

#### Setup Supabase (Khuyến nghị):

**Bước 1: Tạo project trên Supabase**
```
1. Đăng ký tại: https://supabase.com
2. New Project → Chọn Singapore region
3. Copy connection string
```

**Bước 2: Update backend/.env**
```dotenv
# Connection string giống nhau cho local và production!
DATABASE_URL=postgresql://postgres.xxxx:password@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
```

**Bước 3: Migrate data từ VPS**
```bash
# Export từ VPS
ssh root@165.99.59.47
docker exec utility-postgres-prod pg_dump -U utility_user -d utility_db > backup.sql

# Import vào Supabase
psql "postgresql://postgres.xxxx:password@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres" < backup.sql
```

**Bước 4: Commit & Deploy**
```bash
git add backend/.env
git commit -m "Switch to Supabase database"
git push
```

✅ **Done! Không cần sửa gì khi deploy!**

**Ưu điểm:**
- ✅ Zero config khi deploy
- ✅ Backup tự động
- ✅ Monitoring dashboard
- ✅ High availability
- ✅ Connection pooling built-in
- ✅ Free tier rộng rãi

**Nhược điểm:**
- ⚠️ Phụ thuộc third-party
- ⚠️ Có giới hạn free tier (đủ dùng cho dev)

---

### 🥈 **PHƯƠNG ÁN 2: Expose VPS PostgreSQL với Public Endpoint**

**Ý tưởng:** Setup VPS PostgreSQL như một "cloud database", accessible từ internet.

#### Setup:

**Bước 1: Expose PostgreSQL port trên VPS**
```bash
ssh root@165.99.59.47
cd /opt/utility-server

# Update docker-compose.prod.yml
nano docker-compose.prod.yml

# Sửa:
services:
  postgres:
    ports:
      - "0.0.0.0:5432:5432"  # Expose ra ngoài internet

# Allow firewall
sudo ufw allow 5432/tcp

# Update PostgreSQL config
docker exec utility-postgres-prod bash -c \
  "echo 'host all all 0.0.0.0/0 md5' >> /var/lib/postgresql/data/pg_hba.conf"

docker exec utility-postgres-prod bash -c \
  "echo \"listen_addresses = '*'\" >> /var/lib/postgresql/data/postgresql.conf"

# Restart
docker-compose restart postgres
```

**Bước 2: Optional - Setup Domain**
```
Tạo A record trong Cloudflare/DNS:
db.yourdomain.com → 165.99.59.47
```

**Bước 3: Update backend/.env (CHUNG cho local & production)**
```dotenv
# Connection string giống nhau!
DATABASE_URL=postgresql://utility_user:password@165.99.59.47:5432/utility_db

# Hoặc với domain:
# DATABASE_URL=postgresql://utility_user:password@db.yourdomain.com:5432/utility_db
```

**Bước 4: Bảo mật (QUAN TRỌNG!)**
```bash
# Restrict firewall chỉ cho IP của bạn
sudo ufw delete allow 5432/tcp
sudo ufw allow from YOUR_IP to any port 5432
sudo ufw allow from 165.99.59.47 to any port 5432  # VPS self

# Change default port (tránh bots scan)
# Đổi 5432 → 54321 trong docker-compose

# Strong password (20+ chars random)
```

**Ưu điểm:**
- ✅ Tự host, không phụ thuộc third-party
- ✅ Zero config khi deploy
- ✅ Không giới hạn dung lượng

**Nhược điểm:**
- ⚠️ Rủi ro bảo mật (cần setup firewall tốt)
- ⚠️ Exposed port có thể bị scan/attack
- ⚠️ Cần maintain & backup tự động

---

### 🥉 **PHƯƠNG ÁN 3: Environment Detection + Docker Internal**

**Ý tưởng:** Code tự detect environment và chọn connection string phù hợp.

#### Setup trong `backend/app/core/config.py`:

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... other settings ...
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Auto-detect environment:
        - Production (inside Docker): use internal 'postgres' hostname
        - Development (outside Docker): use VPS public IP
        """
        # Check if running inside Docker
        if os.path.exists('/.dockerenv'):
            # Production - use Docker internal network
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@postgres:5432/{self.DB_NAME}"
        else:
            # Development - use public endpoint
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@165.99.59.47:5432/{self.DB_NAME}"
    
    # Or từ env var:
    DB_USER: str = "utility_user"
    DB_PASSWORD: str = "your_password"
    DB_NAME: str = "utility_db"
    DB_HOST: str = os.getenv("DB_HOST", "165.99.59.47")  # Default to VPS IP
```

**backend/.env:**
```dotenv
# Production sẽ override DB_HOST
DB_USER=utility_user
DB_PASSWORD=your_strong_password
DB_NAME=utility_db
# DB_HOST=postgres  # Uncomment trong VPS .env
```

**Trên VPS (.env):**
```dotenv
DB_USER=utility_user
DB_PASSWORD=your_strong_password
DB_NAME=utility_db
DB_HOST=postgres  # Use Docker internal network
```

**Ưu điểm:**
- ✅ Linh hoạt
- ✅ Có thể switch giữa local DB và remote DB
- ✅ Không expose port nếu dùng DB_HOST=postgres trên VPS

**Nhược điểm:**
- ⚠️ Code phức tạp hơn
- ⚠️ Vẫn cần expose port cho localhost access

---

### 🏅 **PHƯƠNG ÁN 4: Docker Compose Override**

**Ý tưởng:** Dùng `docker-compose.override.yml` cho localhost, VPS dùng file gốc.

**docker-compose.yml (Production):**
```yaml
services:
  backend:
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/db
```

**docker-compose.override.yml (Development - local):**
```yaml
services:
  backend:
    environment:
      DATABASE_URL: postgresql://user:pass@165.99.59.47:5432/db
```

Git ignore override file:
```gitignore
docker-compose.override.yml
```

**Ưu điểm:**
- ✅ Clean separation
- ✅ Override file không commit lên Git

**Nhược điểm:**
- ⚠️ Vẫn cần expose VPS port
- ⚠️ Phải maintain 2 files

---

## 🎯 **KHUYẾN NGHỊ**

### Cho Solo Developer:
**→ PHƯƠNG ÁN 2 (Expose VPS PostgreSQL)**
- Đơn giản
- Không phụ thuộc third-party
- Zero config khi deploy

### Cho Production App:
**→ PHƯƠNG ÁN 1 (Supabase/Neon)**
- Professional
- Backup tự động
- High availability
- Dashboard đẹp

### Cho Team:
**→ PHƯƠNG ÁN 3 (Environment Detection)**
- Flexible
- Mỗi người có thể dùng DB riêng để dev

---

## 🚀 **QUICK START (Phương án 2 - Đơn giản nhất)**

```bash
# 1. SSH vào VPS
ssh root@165.99.59.47

# 2. Expose PostgreSQL
cd /opt/utility-server
nano docker-compose.prod.yml
# Sửa ports: "0.0.0.0:5432:5432"

# 3. Firewall (chỉ cho IP của bạn)
sudo ufw allow from YOUR_IP to any port 5432

# 4. Update PostgreSQL config
docker exec utility-postgres-prod bash -c \
  "echo 'host all all 0.0.0.0/0 md5' >> /var/lib/postgresql/data/pg_hba.conf"
docker-compose restart postgres

# 5. Update local backend/.env
# DATABASE_URL=postgresql://utility_user:password@165.99.59.47:5432/utility_db

# 6. Test
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://utility_user:pass@165.99.59.47:5432/utility_db'); print('✅ Connected!')"

# 7. Commit & Push
git add backend/.env
git commit -m "Use shared VPS database"
git push
```

✅ **Done! Deploy không cần sửa gì!**

---

## 📊 SO SÁNH

| Phương án | Setup | Bảo mật | Cost | Maintain | Deploy Config |
|-----------|-------|---------|------|----------|---------------|
| 1. Supabase | Dễ | Cao | Free/Paid | Low | ✅ Zero |
| 2. Expose VPS | Trung bình | Trung bình | Free | Medium | ✅ Zero |
| 3. Env Detection | Trung bình | Cao | Free | Medium | ✅ Zero |
| 4. Override | Trung bình | Cao | Free | Low | ⚠️ Need override file |

---

## 🎉 KẾT LUẬN

**Lựa chọn tốt nhất cho bạn: PHƯƠNG ÁN 2 (Expose VPS PostgreSQL)**

Lý do:
- ✅ Đơn giản nhất
- ✅ Không phụ thuộc third-party
- ✅ Zero config khi deploy
- ✅ Free hoàn toàn
- ⚠️ Chỉ cần setup bảo mật tốt (firewall + strong password)

**Alternative:** Nếu muốn professional hơn → Dùng Supabase (có free tier 2GB).
