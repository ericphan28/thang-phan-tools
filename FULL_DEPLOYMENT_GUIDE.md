# 🚀 HƯỚNG DẪN DEPLOY TOÀN BỘ HỆ THỐNG

## 📋 Tổng quan

Script này sẽ tự động cài đặt và cấu hình:

1. ✅ **Docker & Docker Compose** - Container platform
2. ✅ **Cockpit** - Quản lý toàn diện VPS (http://165.99.59.47:9090)
3. ✅ **Portainer** - Quản lý Docker chuyên sâu (https://165.99.59.47:9443)
4. ✅ **Dozzle** - Xem logs real-time (http://165.99.59.47:9999)
5. ✅ **Utility Server** - API server của bạn (http://165.99.59.47/docs)

---

## ⚡ CÁCH 1: DEPLOY TỪ WINDOWS (KHUYÊN DÙNG)

### Bước 1: Cấu hình .env file

```powershell
cd D:\thang\utility-server
notepad .env
```

Chỉnh sửa các dòng sau:
```env
DB_PASSWORD=YourSecurePassword123!@#
REDIS_PASSWORD=RedisPassword456!@#
SECRET_KEY=your-random-secret-key-here-change-this
JWT_SECRET_KEY=jwt-secret-key-change-this-too
```

**Tạo random keys:**
```powershell
# Trong PowerShell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
```

### Bước 2: Chạy script deploy

```powershell
cd D:\thang\utility-server\scripts
powershell -ExecutionPolicy Bypass -File deploy_all_from_windows.ps1
```

Script sẽ tự động:
- ✅ Upload code lên VPS
- ✅ Cài đặt Docker
- ✅ Cài đặt Cockpit, Portainer, Dozzle
- ✅ Deploy Utility Server
- ✅ Cấu hình firewall
- ✅ Kiểm tra và báo cáo kết quả

### Bước 3: Truy cập các services

Sau khi script chạy xong (5-10 phút), mở browser:

| Service | URL | Login |
|---------|-----|-------|
| 🖥️ Cockpit | http://165.99.59.47:9090 | root / @8Alm523jIqS |
| 🐳 Portainer | https://165.99.59.47:9443 | Tạo account lần đầu |
| 📋 Dozzle | http://165.99.59.47:9999 | Không cần login |
| 🚀 API Docs | http://165.99.59.47/docs | Không cần login |

**XONG!** 🎉

---

## 🔧 CÁCH 2: DEPLOY THỦ CÔNG TỪ VPS

### Bước 1: Upload code lên VPS

**Option A: Dùng WinSCP (Dễ nhất)**
1. Download: https://winscp.net/eng/download.php
2. Kết nối:
   - Host: `165.99.59.47`
   - User: `root`
   - Password: `@8Alm523jIqS`
3. Upload folder `D:\thang\utility-server` lên `/opt/utility-server`

**Option B: Dùng Git**
```bash
# Trên VPS
ssh root@165.99.59.47
cd /opt
git clone https://github.com/your-username/utility-server.git
cd utility-server
```

### Bước 2: Cấu hình .env

```bash
ssh root@165.99.59.47
cd /opt/utility-server

# Copy và edit
cp .env.example .env
nano .env

# Tạo random keys
openssl rand -hex 32  # SECRET_KEY
openssl rand -hex 32  # JWT_SECRET_KEY
```

### Bước 3: Chạy script deploy

```bash
cd /opt/utility-server
chmod +x scripts/full_deploy.sh
bash scripts/full_deploy.sh
```

### Bước 4: Deploy Utility Server

```bash
cd /opt/utility-server
docker-compose up -d --build

# Xem logs
docker-compose logs -f

# Kiểm tra containers
docker-compose ps
```

---

## 📊 SAU KHI DEPLOY

### Kiểm tra services đang chạy

```bash
ssh root@165.99.59.47

# Check all containers
docker ps

# Check specific services
systemctl status cockpit
docker ps | grep portainer
docker ps | grep dozzle
docker ps | grep utility_backend
```

### Xem logs

```bash
# Utility Server logs
docker-compose logs -f backend

# All services logs
docker-compose logs -f

# Dozzle (web interface)
http://165.99.59.47:9999
```

### Test API

```bash
# Health check
curl http://165.99.59.47/health

# API info
curl http://165.99.59.47/api

# Swagger docs
http://165.99.59.47/docs
```

---

## 🎯 QUẢN LÝ HỆ THỐNG

### 1. Cockpit (http://165.99.59.47:9090)

**Chức năng:**
- ✅ Monitoring CPU, RAM, Disk, Network
- ✅ Quản lý services (start/stop/restart)
- ✅ Terminal web (SSH trong browser)
- ✅ Quản lý Docker containers
- ✅ Xem logs hệ thống
- ✅ Quản lý users, firewall

**Cách dùng:**
1. Đăng nhập: root / @8Alm523jIqS
2. Dashboard: Xem overview hệ thống
3. Services: Quản lý systemd services
4. Terminal: SSH trực tiếp trong browser
5. Storage: Quản lý disks, partitions

### 2. Portainer (https://165.99.59.47:9443)

**Chức năng:**
- ✅ Quản lý Docker containers
- ✅ Xem logs, stats, exec console
- ✅ Quản lý images, volumes, networks
- ✅ Deploy stacks (compose files)
- ✅ Container monitoring

**Cách dùng:**
1. Lần đầu: Tạo admin account
2. Connect local environment
3. Dashboard: Xem tất cả containers
4. Container details: Logs, stats, console
5. Stacks: Deploy/update compose files

### 3. Dozzle (http://165.99.59.47:9999)

**Chức năng:**
- ✅ Xem logs real-time
- ✅ Multi-container logs
- ✅ Search trong logs
- ✅ Filter by container

**Cách dùng:**
1. Không cần login
2. Chọn container từ sidebar
3. Xem logs real-time
4. Search text trong logs
5. Download logs

---

## 🔧 QUẢN LÝ UTILITY SERVER

### Start/Stop/Restart

```bash
cd /opt/utility-server

# Stop all
docker-compose down

# Start all
docker-compose up -d

# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart postgres
```

### Update code

```bash
cd /opt/utility-server

# Pull new code (if using Git)
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Or just restart
docker-compose restart
```

### Backup database

```bash
cd /opt/utility-server

# Backup
docker-compose exec postgres pg_dump -U utility_user utility_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
docker-compose exec -T postgres psql -U utility_user utility_db < backup_20241116_120000.sql
```

### View resource usage

```bash
# Docker stats
docker stats

# System resources
htop

# Disk usage
df -h

# Container logs size
docker system df
```

---

## 🆘 TROUBLESHOOTING

### Service không start?

```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Restart
docker-compose restart backend
```

### Port bị chiếm?

```bash
# Check port usage
lsof -i :8000
lsof -i :9090

# Kill process
kill -9 PID
```

### Out of memory?

```bash
# Check memory
free -h

# Check swap
swapon --show

# Clear cache
sync; echo 3 > /proc/sys/vm/drop_caches
```

### Database connection error?

```bash
# Check postgres
docker-compose ps postgres
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres

# Check connection
docker-compose exec postgres psql -U utility_user -d utility_db -c "SELECT 1"
```

### Không truy cập từ bên ngoài?

```bash
# Check firewall
ufw status

# Open ports
ufw allow 80/tcp
ufw allow 443/tcp
ufw reload

# Check nginx
docker-compose logs nginx
```

---

## 📈 MONITORING & ALERTS

### Resource monitoring

**Cockpit Dashboard:**
- CPU usage
- RAM usage
- Disk usage
- Network traffic

**Docker stats:**
```bash
docker stats --no-stream
```

### Log monitoring

**Dozzle:**
- Real-time logs
- Error detection
- Search logs

### Health checks

```bash
# API health
curl http://165.99.59.47/health

# Container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# Service health
systemctl status cockpit
systemctl status docker
```

---

## 🔐 SECURITY

### Change default passwords

```bash
# Change root password
passwd

# Change database password
# Edit .env and restart
nano /opt/utility-server/.env
docker-compose restart postgres
```

### Setup SSL (if you have domain)

```bash
# Install certbot
apt install -y certbot

# Get certificate
certbot certonly --standalone -d yourdomain.com

# Update nginx config
nano /opt/utility-server/nginx/nginx.conf

# Restart nginx
docker-compose restart nginx
```

### Firewall rules

```bash
# Check current rules
ufw status numbered

# Add rule
ufw allow from YOUR_IP to any port 22

# Remove rule
ufw delete NUMBER

# Reset firewall
ufw reset
```

---

## 📞 SUPPORT

### Useful links

- **Cockpit Docs**: https://cockpit-project.org/guide/latest/
- **Portainer Docs**: https://docs.portainer.io/
- **Dozzle Docs**: https://dozzle.dev/
- **Docker Docs**: https://docs.docker.com/

### Quick commands

```bash
# SSH to VPS
ssh root@165.99.59.47

# Check all services
cd /opt/utility-server && docker-compose ps

# View all logs
docker-compose logs -f

# System info
htop
df -h
free -h
```

---

## 🎉 SUCCESS CHECKLIST

- [ ] Cockpit accessible at http://165.99.59.47:9090
- [ ] Portainer accessible at https://165.99.59.47:9443
- [ ] Dozzle accessible at http://165.99.59.47:9999
- [ ] API Docs accessible at http://165.99.59.47/docs
- [ ] Health check returns success: http://165.99.59.47/health
- [ ] All containers running: `docker-compose ps`
- [ ] Database connected: Check API logs
- [ ] Redis connected: Check API logs

---

**Made with ❤️ for Utility Server Management**
