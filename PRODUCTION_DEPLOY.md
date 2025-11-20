# 🚀 Hướng Dẫn Deploy Production - Utility Server

## 📋 Thông Tin VPS

```
IP: 165.99.59.47
User: root
Password: @8Alm523jIqS
Port: 22
```

## ✅ Checklist Trước Khi Deploy

### 1. Kiểm tra Code Hoàn Chỉnh
- [x] All features tested locally
- [x] No TypeScript/Python errors
- [x] UI/UX improvements completed
- [x] Drag & drop file reordering works
- [x] Merge Word files works
- [x] Cancel operation works
- [ ] Frontend production build successful
- [ ] Backend dependencies installed
- [ ] .env files configured

### 2. Chuẩn Bị Files
- [ ] Commit all changes to git
- [ ] Create .env.production for backend
- [ ] Build frontend for production
- [ ] Test docker-compose locally (optional)

---

## 🔧 Bước 1: Chuẩn Bị Code

### A. Build Frontend Production

```powershell
# Từ D:\thang\utility-server

# Build frontend
cd frontend
npm run build

# Check build output
ls dist/
```

**Kết quả mong đợi:**
```
frontend/dist/
  ├── index.html
  ├── assets/
  │   ├── index-[hash].js
  │   └── index-[hash].css
  └── ...
```

### B. Kiểm Tra Backend Dependencies

```powershell
cd ../backend

# Check requirements.txt
cat requirements.txt

# Test local import
python -c "from app.main_simple import app; print('✅ Backend OK')"
```

### C. Tạo .env.production

```powershell
# Copy từ .env hiện tại
cp .env .env.production

# Hoặc tạo mới
New-Item -Path ".env.production" -ItemType File
```

**Nội dung `.env.production`:**
```env
# Database
DATABASE_URL=postgresql://utility_user:secure_production_password_123@postgres:5432/utility_db
DB_USER=utility_user
DB_PASSWORD=secure_production_password_123
DB_NAME=utility_db
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://:redis_production_password_456@redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_production_password_456

# Security
SECRET_KEY=<GENERATE_WITH_openssl_rand_hex_32>
JWT_SECRET_KEY=<GENERATE_WITH_openssl_rand_hex_32>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production
DEBUG=False

# CORS
CORS_ORIGINS=http://165.99.59.47,http://localhost:3000

# API
API_V1_PREFIX=/api/v1
```

### D. Commit Changes

```powershell
# Check status
git status

# Add all changes
git add .

# Commit
git commit -m "feat: UI/UX improvements + merge Word files + cancel operation"

# Push to repository (if you have one)
git push origin main
```

---

## 🚀 Bước 2: Deploy Lên VPS

### Option A: Deploy Tự Động (RECOMMENDED)

```powershell
# Từ D:\thang\utility-server

# Chạy script deploy từ Windows
.\scripts\deploy_from_windows.ps1

# Script sẽ tự động:
# 1. Build frontend
# 2. Upload code lên VPS qua SCP
# 3. SSH vào VPS và chạy docker-compose
# 4. Kiểm tra services
```

### Option B: Deploy Thủ Công

#### 2.1. Test SSH Connection

```powershell
# Test SSH
ssh root@165.99.59.47

# Nếu được hỏi "Are you sure?", gõ: yes
# Nhập password: @8Alm523jIqS

# Nếu kết nối thành công:
exit
```

#### 2.2. Upload Code Lên VPS

**Cách 1: Sử dụng SCP (Nhanh)**

```powershell
# Từ D:\thang\utility-server

# Upload toàn bộ project
scp -r . root@165.99.59.47:/opt/utility-server/

# Hoặc upload từng phần quan trọng
scp -r backend root@165.99.59.47:/opt/utility-server/
scp -r frontend/dist root@165.99.59.47:/opt/utility-server/frontend/
scp docker-compose.yml root@165.99.59.47:/opt/utility-server/
scp -r nginx root@165.99.59.47:/opt/utility-server/
scp .env.production root@165.99.59.47:/opt/utility-server/.env
```

**Cách 2: Sử dụng Git (Clean)**

```powershell
# Đảm bảo code đã được push lên GitHub/GitLab

# SSH vào VPS
ssh root@165.99.59.47

# Clone hoặc pull code
cd /opt
git clone https://github.com/YOUR_USERNAME/utility-server.git
# Hoặc nếu đã có:
cd /opt/utility-server
git pull origin main

exit
```

**Cách 3: Sử dụng WinSCP (GUI)**

1. Download WinSCP: https://winscp.net/eng/download.php
2. Install và mở WinSCP
3. New Site:
   - Protocol: SFTP
   - Host: 165.99.59.47
   - Port: 22
   - Username: root
   - Password: @8Alm523jIqS
4. Login
5. Navigate to `/opt/`
6. Create folder `utility-server` (nếu chưa có)
7. Upload tất cả files từ `D:\thang\utility-server`

#### 2.3. SSH Vào VPS và Deploy

```powershell
# SSH vào VPS
ssh root@165.99.59.47
```

**Trên VPS, chạy:**

```bash
# 1. Đi đến project folder
cd /opt/utility-server

# 2. Kiểm tra files đã upload
ls -la

# 3. Copy .env.production thành .env
cp .env.production .env

# 4. Tạo random secret keys (nếu chưa có)
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env

# 5. Kiểm tra .env
cat .env

# 6. Build và start services
docker-compose down  # Stop old services if any
docker-compose build --no-cache  # Build fresh images
docker-compose up -d  # Start in background

# 7. Kiểm tra services
docker-compose ps

# 8. Xem logs
docker-compose logs -f
# Nhấn Ctrl+C để thoát logs

# 9. Test API
curl http://localhost:8000/health
curl http://localhost:8000/docs

# 10. Exit SSH
exit
```

---

## 🧪 Bước 3: Kiểm Tra Production

### A. Kiểm Tra Services

```powershell
# SSH vào VPS
ssh root@165.99.59.47

# Check tất cả services
docker-compose ps

# Expected output:
# NAME                    STATUS              PORTS
# utility-server-backend  Up 2 minutes        0.0.0.0:8000->8000/tcp
# utility-server-postgres Up 2 minutes        5432/tcp
# utility-server-redis    Up 2 minutes        6379/tcp
# utility-server-nginx    Up 2 minutes        0.0.0.0:80->80/tcp
```

### B. Test API Endpoints

**Từ VPS:**
```bash
# Health check
curl http://localhost:8000/health

# API docs (should return HTML)
curl http://localhost:8000/docs

# Test document conversion
curl -X POST "http://localhost:8000/api/v1/documents/convert/word-to-pdf" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.docx"
```

**Từ Browser (máy Windows):**

1. **Frontend:** http://165.99.59.47
2. **API Docs:** http://165.99.59.47/docs
3. **Health Check:** http://165.99.59.47/health

### C. Test Tính Năng Mới

#### Test 1: Merge Word Files
1. Mở http://165.99.59.47
2. Click tab "Documents"
3. Click "🔗 Gộp NHIỀU Word → 1 PDF"
4. Upload 3-4 files Word
5. Drag & drop để sắp xếp thứ tự
6. Click "Gộp X Word → 1 PDF"
7. Kiểm tra file PDF tải về

#### Test 2: Cancel Operation
1. Upload 5 files Word để merge
2. Click "Gộp 5 Word → 1 PDF"
3. Trong lúc đang xử lý (progress 30-50%)
4. Click nút "❌ Hủy"
5. Kiểm tra operation đã bị hủy
6. Toast notification: "❌ Đã hủy thao tác!"

#### Test 3: Concurrent Operations Warning
1. Start một operation (VD: Word → PDF)
2. Trong khi đang chạy, click nút khác (VD: Excel → PDF)
3. Kiểm tra toast: "⚠️ Một thao tác khác đang chạy!"
4. Nút Excel không disabled, chỉ show warning

### D. Kiểm Tra Logs

```bash
# Xem logs tất cả services
docker-compose logs -f

# Xem logs backend only
docker-compose logs -f backend

# Xem 100 dòng cuối
docker-compose logs --tail=100 backend

# Search for errors
docker-compose logs backend | grep -i error
docker-compose logs backend | grep -i exception
```

---

## 🔧 Bước 4: Cấu Hình Production

### A. Setup Firewall (UFW)

```bash
# Enable firewall
ufw enable

# Allow SSH (IMPORTANT!)
ufw allow 22/tcp

# Allow HTTP
ufw allow 80/tcp

# Allow HTTPS (for future SSL)
ufw allow 443/tcp

# Check status
ufw status

# Expected output:
# Status: active
# To                         Action      From
# --                         ------      ----
# 22/tcp                     ALLOW       Anywhere
# 80/tcp                     ALLOW       Anywhere
# 443/tcp                    ALLOW       Anywhere
```

### B. Setup Nginx Properly

**Edit nginx config:**
```bash
nano /opt/utility-server/nginx/nginx.conf
```

**Đảm bảo có:**
```nginx
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name 165.99.59.47;
    client_max_body_size 100M;  # For large file uploads

    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # For large file uploads
        proxy_request_buffering off;
        proxy_buffering off;
    }

    # API docs
    location /docs {
        proxy_pass http://backend/docs;
        proxy_set_header Host $host;
    }

    location /redoc {
        proxy_pass http://backend/redoc;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://backend/openapi.json;
        proxy_set_header Host $host;
    }

    # Health check
    location /health {
        proxy_pass http://backend/health;
    }
}
```

**Restart nginx:**
```bash
docker-compose restart nginx
```

### C. Setup Auto-Start on Boot

```bash
# Enable Docker to start on boot
systemctl enable docker

# Create systemd service for docker-compose
cat > /etc/systemd/system/utility-server.service <<EOF
[Unit]
Description=Utility Server
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/utility-server
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Enable service
systemctl enable utility-server

# Start service
systemctl start utility-server

# Check status
systemctl status utility-server
```

### D. Setup Automatic Backups

```bash
# Create backup script
cat > /opt/backup_utility.sh <<'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
mkdir -p $BACKUP_DIR

# Backup database
docker-compose -f /opt/utility-server/docker-compose.yml exec -T postgres \
  pg_dump -U utility_user utility_db > $BACKUP_DIR/db_$DATE.sql

# Backup uploads folder
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /opt/utility-server/uploads/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "uploads_*.tar.gz" -mtime +7 -delete

echo "✅ Backup completed: $DATE"
EOF

chmod +x /opt/backup_utility.sh

# Add to crontab (run daily at 2 AM)
crontab -e
# Add this line:
0 2 * * * /opt/backup_utility.sh >> /var/log/utility_backup.log 2>&1
```

---

## 📊 Bước 5: Monitoring & Maintenance

### A. Check System Resources

```bash
# CPU, Memory, Disk usage
htop

# Disk space
df -h

# Memory
free -h

# Docker stats
docker stats

# Specific container stats
docker stats utility-server-backend
```

### B. View Logs Regularly

```bash
# Real-time logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Logs from last hour
docker-compose logs --since 1h

# Save logs to file
docker-compose logs > logs_$(date +%Y%m%d).txt
```

### C. Update Code

```bash
# SSH vào VPS
ssh root@165.99.59.47

cd /opt/utility-server

# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker-compose logs -f
```

### D. Database Maintenance

```bash
# Connect to database
docker-compose exec postgres psql -U utility_user utility_db

# Inside psql:
# Check database size
SELECT pg_size_pretty(pg_database_size('utility_db'));

# Check table sizes
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Optimize database
VACUUM ANALYZE;

# Reindex
REINDEX DATABASE utility_db;

# Exit
\q
```

---

## 🐛 Troubleshooting

### Issue 1: Container Không Start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Port already in use
# - Environment variables missing
# - Database not ready

# Solution: Restart all
docker-compose down
docker-compose up -d
```

### Issue 2: Can't Access from Browser

```bash
# Check nginx logs
docker-compose logs nginx

# Check if services are running
docker-compose ps

# Check firewall
ufw status

# Check nginx config
docker-compose exec nginx nginx -t
```

### Issue 3: Database Connection Error

```bash
# Check postgres is running
docker-compose ps postgres

# Check postgres logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres

# Test connection
docker-compose exec postgres psql -U utility_user utility_db -c "SELECT 1;"
```

### Issue 4: Out of Disk Space

```bash
# Check disk usage
df -h

# Clean Docker images
docker system prune -a

# Clean logs
docker-compose logs --tail=0 > /dev/null

# Remove old backups
rm -rf /opt/backups/*_20231*.sql
```

### Issue 5: High Memory Usage

```bash
# Check memory
free -h

# Check which container uses most memory
docker stats --no-stream

# Restart heavy containers
docker-compose restart backend

# Add more swap if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 🔐 Security Checklist

- [ ] Changed default passwords in `.env`
- [ ] Firewall enabled (ufw)
- [ ] Only necessary ports open (22, 80, 443)
- [ ] Strong passwords for DB and Redis
- [ ] Regular backups configured
- [ ] SSL certificate installed (optional but recommended)
- [ ] Keep system updated: `apt update && apt upgrade`
- [ ] Monitor logs regularly
- [ ] Disable root SSH login (optional):
  ```bash
  # In /etc/ssh/sshd_config
  PermitRootLogin no
  # Then: systemctl restart sshd
  ```

---

## 📈 Performance Tips

1. **Use CDN for Static Files** (future improvement)
2. **Enable Redis Caching** (already configured)
3. **Optimize Database Queries** (add indexes)
4. **Use Nginx Gzip Compression** (already configured)
5. **Monitor with Prometheus + Grafana** (optional)

---

## 🎉 Post-Deploy Checklist

- [ ] All services running: `docker-compose ps`
- [ ] Frontend accessible: http://165.99.59.47
- [ ] API docs working: http://165.99.59.47/docs
- [ ] Health check OK: http://165.99.59.47/health
- [ ] Can upload and convert files
- [ ] Merge Word files works
- [ ] Cancel operation works
- [ ] Drag & drop reordering works
- [ ] All buttons show correct loading states
- [ ] Logs show no errors
- [ ] Firewall configured
- [ ] Backups configured
- [ ] Auto-start configured

---

## 📞 Quick Commands Cheat Sheet

```bash
# SSH to VPS
ssh root@165.99.59.47

# Check services
docker-compose ps

# View logs
docker-compose logs -f

# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend

# Stop all
docker-compose down

# Start all
docker-compose up -d

# Update code
git pull && docker-compose down && docker-compose build --no-cache && docker-compose up -d

# Check disk space
df -h

# Check memory
free -h

# Monitor resources
htop
docker stats
```

---

**🎊 Chúc mừng! Server của bạn đã sẵn sàng production! 🚀**
