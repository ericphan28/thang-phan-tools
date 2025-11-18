# ============================================
# Quick Start Guide - Utility Server
# ============================================

## 📋 Hướng dẫn Deploy lên VPS Ubuntu

### Bước 1: Chuẩn bị VPS

```bash
# SSH vào VPS
ssh root@165.99.59.47

# Hoặc với password
ssh root@165.99.59.47
# Password: @8Alm523jIqS
```

### Bước 2: Chạy script setup

```bash
# Download script setup
curl -o setup_vps.sh https://raw.githubusercontent.com/your-repo/utility-server/main/scripts/setup_vps.sh

# Hoặc nếu đã upload project
cd /opt/utility-server
chmod +x scripts/setup_vps.sh
bash scripts/setup_vps.sh
```

### Bước 3: Upload code lên VPS

**Cách 1: Sử dụng Git**
```bash
cd /opt
git clone https://github.com/your-username/utility-server.git
cd utility-server
```

**Cách 2: Sử dụng SCP từ Windows**
```powershell
# Từ máy Windows, chạy trong PowerShell tại D:\thang\utility-server
scp -r . root@165.99.59.47:/opt/utility-server/
```

**Cách 3: Sử dụng WinSCP**
- Download WinSCP: https://winscp.net
- Connect to 165.99.59.47 with root/@8Alm523jIqS
- Upload folder D:\thang\utility-server to /opt/utility-server

### Bước 4: Cấu hình môi trường

```bash
cd /opt/utility-server

# Copy file .env
cp .env.example .env

# Chỉnh sửa file .env
nano .env

# Thay đổi các giá trị sau:
# DB_PASSWORD=your_secure_password_123
# REDIS_PASSWORD=your_redis_password_456
# SECRET_KEY=your-random-secret-key-here
# JWT_SECRET_KEY=another-random-key-here
```

**Tạo random secret keys:**
```bash
# Tạo SECRET_KEY
openssl rand -hex 32

# Tạo JWT_SECRET_KEY
openssl rand -hex 32
```

### Bước 5: Deploy

```bash
cd /opt/utility-server

# Chạy script deploy
chmod +x scripts/deploy.sh
bash scripts/deploy.sh
```

### Bước 6: Kiểm tra

```bash
# Kiểm tra services đang chạy
docker-compose ps

# Xem logs
docker-compose logs -f

# Test API
curl http://localhost:8000/health

# Test từ browser
http://YOUR_VPS_IP/docs
http://YOUR_VPS_IP/health
```

---

## 🔐 Setup SSL (Optional nhưng nên có)

### Nếu có domain name:

```bash
# Point domain to VPS IP first (in DNS settings)
# Wait for DNS propagation (15-30 minutes)

# Get SSL certificate
certbot certonly --webroot \
  -w /opt/utility-server/certbot/www \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email your-email@example.com \
  --agree-tos

# Update nginx config to enable HTTPS (uncomment SSL server block)
nano /opt/utility-server/nginx/nginx.conf

# Restart nginx
docker-compose restart nginx

# Auto-renew setup
crontab -e
# Add this line:
0 0 * * * certbot renew --quiet && docker-compose -f /opt/utility-server/docker-compose.yml restart nginx
```

---

## 📊 Quản lý Server

### Xem logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Restart services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
```

### Update code
```bash
cd /opt/utility-server
git pull origin main
bash scripts/deploy.sh
```

### Backup database
```bash
# Backup
docker-compose exec postgres pg_dump -U utility_user utility_db > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U utility_user utility_db < backup_20241116.sql
```

### Monitor resources
```bash
# Docker stats
docker stats

# System resources
htop

# Disk usage
df -h

# Memory
free -h
```

---

## 🧪 Testing API

### 1. Health Check
```bash
curl http://YOUR_VPS_IP/health
```

### 2. API Documentation
Mở browser và truy cập:
- Swagger UI: `http://YOUR_VPS_IP/docs`
- ReDoc: `http://YOUR_VPS_IP/redoc`

### 3. Test Face Recognition (sau khi implement API endpoints)
```bash
# Register face
curl -X POST "http://YOUR_VPS_IP/api/face/register" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@photo.jpg" \
  -F "name=John Doe" \
  -F "user_id=12345"

# Recognize face
curl -X POST "http://YOUR_VPS_IP/api/face/recognize" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@unknown.jpg"
```

---

## 🐛 Troubleshooting

### Service không start?
```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Restart
docker-compose restart backend
```

### Port already in use?
```bash
# Check what's using port
lsof -i :8000
lsof -i :80

# Kill process
kill -9 PID
```

### Out of memory?
```bash
# Check memory
free -h

# Check swap
swapon --show

# Add more swap if needed
sudo fallocate -l 4G /swapfile2
sudo chmod 600 /swapfile2
sudo mkswap /swapfile2
sudo swapon /swapfile2
```

### Database connection error?
```bash
# Check postgres is running
docker-compose ps postgres

# Check postgres logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres
```

### Can't connect from outside?
```bash
# Check firewall
sudo ufw status

# Open ports if needed
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

---

## 📈 Performance Optimization

### 1. Increase Docker resources
Edit `/etc/docker/daemon.json`:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### 2. Optimize PostgreSQL
```bash
# Connect to postgres
docker-compose exec postgres psql -U utility_user utility_db

# Run optimization
VACUUM ANALYZE;
REINDEX DATABASE utility_db;
```

### 3. Clear Redis cache
```bash
docker-compose exec redis redis-cli -a YOUR_REDIS_PASSWORD FLUSHALL
```

---

## 🔒 Security Checklist

- [x] Changed all default passwords in `.env`
- [x] Firewall enabled (only ports 22, 80, 443 open)
- [x] SSL certificate installed
- [x] Regular backups scheduled
- [x] Keep system updated: `apt update && apt upgrade`
- [x] Monitor logs regularly
- [x] Use strong passwords
- [x] Disable root SSH login (optional but recommended)

---

## 📞 Support

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Check service status: `docker-compose ps`
3. Restart services: `docker-compose restart`
4. Check VPS resources: `htop` and `df -h`

---

**Good luck with your Utility Server! 🚀**
