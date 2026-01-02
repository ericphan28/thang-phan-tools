# Setup VPS PostgreSQL như Cloud Database Service
# Cả localhost và production đều dùng CHUNG connection string

# ============================================
# BƯỚC 1: Expose PostgreSQL trên VPS
# ============================================

# SSH vào VPS
ssh root@165.99.59.47

# 1. Update docker-compose.prod.yml - expose port
cd /opt/utility-server
nano docker-compose.prod.yml

# Sửa postgres service:
services:
  postgres:
    ports:
      - "0.0.0.0:5432:5432"  # Expose ra ngoài

# 2. Allow firewall
sudo ufw allow 5432/tcp

# 3. Update PostgreSQL config để accept remote connections
docker exec utility-postgres-prod bash -c \
  "echo 'host all all 0.0.0.0/0 md5' >> /var/lib/postgresql/data/pg_hba.conf"

docker exec utility-postgres-prod bash -c \
  "echo \"listen_addresses = '*'\" >> /var/lib/postgresql/data/postgresql.conf"

# 4. Restart PostgreSQL
docker-compose restart postgres

# ============================================
# BƯỚC 2: Optional - Setup Domain (Khuyến nghị)
# ============================================

# Thay vì dùng IP, dùng subdomain:
# db.yourdomain.com → 165.99.59.47

# Cloudflare DNS:
# A record: db.yourdomain.com → 165.99.59.47

# ============================================
# BƯỚC 3: Update .env (CHUNG cho local và production)
# ============================================

# Cả localhost và VPS đều dùng connection string này:
DATABASE_URL=postgresql://utility_user:your_password@165.99.59.47:5432/utility_db

# Hoặc nếu có domain:
# DATABASE_URL=postgresql://utility_user:your_password@db.yourdomain.com:5432/utility_db

# ============================================
# BƯỚC 4: Test từ localhost
# ============================================

# Test connection:
psql -h 165.99.59.47 -U utility_user -d utility_db

# Hoặc dùng Python:
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://utility_user:pass@165.99.59.47:5432/utility_db'); print(engine.connect())"

# ============================================
# BƯỚC 5: Deploy - KHÔNG CẦN SỬA GÌ!
# ============================================

# Push code lên GitHub
git add .
git commit -m "Update to use shared database"
git push

# Deploy lên VPS - backend tự động dùng DATABASE_URL từ .env
# Không cần sửa gì vì cả local và production đều dùng chung connection string!

# ============================================
# BẢO MẬT (QUAN TRỌNG!)
# ============================================

# 1. Strong password (20+ chars)
# 2. Restrict firewall chỉ cho IP của bạn:
sudo ufw delete allow 5432/tcp
sudo ufw allow from YOUR_IP to any port 5432
sudo ufw allow from VPS_IP to any port 5432  # Cho chính VPS access

# 3. Setup SSL/TLS:
# Tạo cert và update PostgreSQL config để require SSL

# 4. Change default port (optional):
# Đổi 5432 → 54321 để tránh scan bots

# 5. Fail2ban protection:
sudo apt install fail2ban
# Config fail2ban cho PostgreSQL

# ============================================
# KẾT QUẢ
# ============================================

# ✅ Localhost: DATABASE_URL=postgresql://user:pass@165.99.59.47:5432/db
# ✅ Production: DATABASE_URL=postgresql://user:pass@165.99.59.47:5432/db (GIỐNG NHAU!)

# Khi deploy: KHÔNG CẦN SỬA GÌ! 🎉
