# 🔧 TROUBLESHOOTING GUIDE

**Version:** 2.0  
**Date:** 17/11/2025  
**Purpose:** Giải quyết TẤT CẢ vấn đề khi deploy

---

## 🎯 MỤC LỤC

1. [SSH Connection Issues](#1-ssh-connection-issues)
2. [Script Execution Errors](#2-script-execution-errors)
3. [Docker Installation Issues](#3-docker-installation-issues)
4. [Build Failures](#4-build-failures)
5. [Container Start Issues](#5-container-start-issues)
6. [Port Conflicts](#6-port-conflicts)
7. [Portainer Issues](#7-portainer-issues)
8. [API Not Responding](#8-api-not-responding)
9. [Database Issues](#9-database-issues)
10. [Performance Issues](#10-performance-issues)

---

## 1. SSH CONNECTION ISSUES

### ❌ Problem: Cannot connect to VPS via SSH

**Error messages:**
```
ssh: connect to host 165.99.59.47 port 22: Connection refused
ssh: connect to host 165.99.59.47 port 22: Connection timed out
paramiko.AuthenticationException: Authentication failed
```

**Possible causes:**
1. Wrong IP address
2. Wrong password
3. SSH service not running
4. Firewall blocking SSH
5. VPS not ready yet

**Solutions:**

#### Solution 1: Verify VPS is running
```bash
# Check từ VPS provider dashboard
# VPS status phải là "Running"
```

#### Solution 2: Verify IP address
```bash
# Check IP trong VPS provider dashboard
# So sánh với IP trong script
```

#### Solution 3: Verify SSH service
```bash
# SSH qua VNC/Console từ provider dashboard
# Check SSH service:
sudo systemctl status sshd

# Nếu not running:
sudo systemctl start sshd
sudo systemctl enable sshd
```

#### Solution 4: Check firewall
```bash
# SSH qua VNC/Console
# Check firewall:
sudo ufw status

# Nếu active nhưng không có SSH:
sudo ufw allow 22/tcp
sudo ufw reload
```

#### Solution 5: Reset root password
```bash
# Từ VPS provider dashboard
# Click "Reset root password"
# Hoặc "Access console" → Đổi password manual
```

---

## 2. SCRIPT EXECUTION ERRORS

### ❌ Problem: Python script fails to run

**Error messages:**
```
ModuleNotFoundError: No module named 'paramiko'
python: command not found
SyntaxError: invalid syntax
```

**Solutions:**

#### Solution 1: Install paramiko
```bash
# Windows PowerShell
pip install paramiko

# Verify
python -c "import paramiko; print('OK')"
```

#### Solution 2: Check Python version
```bash
# Check version
python --version

# Cần: Python 3.8+
# Nếu < 3.8, update Python
```

#### Solution 3: Use python3 instead of python
```bash
# Some systems use python3
python3 scripts/auto_deploy_full.py

# Install paramiko for python3
pip3 install paramiko
```

---

## 3. DOCKER INSTALLATION ISSUES

### ❌ Problem: Docker installation fails

**Error messages:**
```
E: Unable to locate package docker-ce
error: conflicting requests
docker: command not found (after install)
```

**Solutions:**

#### Solution 1: Clean and retry
```bash
# SSH vào VPS
ssh root@YOUR_VPS_IP

# Remove old Docker
sudo apt remove docker docker-engine docker.io containerd runc

# Clean
sudo apt autoremove
sudo apt autoclean

# Update
sudo apt update

# Install dependencies
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker repo
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update again
sudo apt update

# Install Docker
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Verify
docker --version
```

#### Solution 2: Use convenience script
```bash
# SSH vào VPS
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verify
docker --version
```

---

## 4. BUILD FAILURES

### ❌ Problem: Backend Docker build fails

**Error messages:**
```
ERROR: failed to solve: process "/bin/sh -c pip install..." did not complete successfully
Failed building wheel for dlib
CMake Error: Compatibility with CMake < 3.5 has been removed
```

**Solutions:**

#### Solution 1: Use simplified requirements (RECOMMENDED)
```bash
# Script đã tự động dùng requirements.simple.txt
# KHÔNG có dlib, face-recognition

# Nếu bạn đang build manual, check:
cat /opt/utility-server/backend/requirements.txt | grep dlib

# Nếu thấy dlib → Thay bằng requirements.simple.txt:
cd /opt/utility-server
cp backend/requirements.simple.txt backend/requirements.txt

# Rebuild:
docker-compose down
docker-compose up -d --build
```

#### Solution 2: Check network
```bash
# SSH vào VPS
# Test connectivity:
ping -c 3 pypi.org

# Nếu fail:
# - Check VPS network
# - Check DNS: cat /etc/resolv.conf
# - Update DNS: echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
```

#### Solution 3: Increase Docker memory
```bash
# Nếu VPS có ít RAM:
# Edit docker-compose.yml để giới hạn memory:

services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

---

## 5. CONTAINER START ISSUES

### ❌ Problem: Containers fail to start

**Error messages:**
```
Error response from daemon: driver failed programming external connectivity
Error starting userland proxy: listen tcp4 0.0.0.0:80: bind: address already in use
Container exited with code 1
```

**Solutions:**

#### Solution 1: Check ports in use
```bash
# SSH vào VPS
# Check port 80:
sudo lsof -i :80

# Nếu có process khác:
# Kill process:
sudo kill -9 <PID>

# Hoặc stop service:
sudo systemctl stop apache2  # Nếu có Apache
sudo systemctl stop nginx    # Nếu có Nginx system
```

#### Solution 2: Check container logs
```bash
# SSH vào VPS
cd /opt/utility-server

# Check logs từng container:
docker logs utility_backend --tail 50
docker logs utility_postgres --tail 50
docker logs utility_redis --tail 50
docker logs utility_nginx --tail 50

# Tìm error messages
```

#### Solution 3: Restart all containers
```bash
# SSH vào VPS
cd /opt/utility-server

# Stop all:
docker-compose down

# Wait 5 seconds:
sleep 5

# Start all:
docker-compose up -d

# Check status:
docker-compose ps
```

---

## 6. PORT CONFLICTS

### ❌ Problem: Port already in use

**Error messages:**
```
Bind for 0.0.0.0:80 failed: port is already allocated
Cannot start container: port is already allocated
```

**Solutions:**

#### Solution 1: Identify process using port
```bash
# SSH vào VPS
# Check port 80:
sudo lsof -i :80

# Output example:
# COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
# apache2  1234 root    4u  IPv6  12345      0t0  TCP *:http (LISTEN)

# Kill process:
sudo kill -9 1234
```

#### Solution 2: Check all ports used
```bash
# Script sử dụng các ports:
22   - SSH
80   - Nginx (Utility Server)
443  - Nginx SSL
9090 - Cockpit
9443 - Portainer
9999 - Dozzle

# Check từng port:
sudo lsof -i :80
sudo lsof -i :443
sudo lsof -i :9090
sudo lsof -i :9443
sudo lsof -i :9999
```

#### Solution 3: Change ports (if needed)
```bash
# Edit docker-compose.yml:
services:
  nginx:
    ports:
      - "8080:80"    # Đổi 80 → 8080
      - "8443:443"   # Đổi 443 → 8443

# Restart:
docker-compose down && docker-compose up -d
```

---

## 7. PORTAINER ISSUES

### ❌ Problem: Portainer shows "Timed out for security purposes"

**This is NORMAL!**

**Explanation:**
- Portainer timeout sau 5 phút nếu không có ai setup admin account
- Đây là tính năng bảo mật, KHÔNG PHẢI LỖI!

**Solution:**
```bash
# SSH vào VPS:
ssh root@YOUR_VPS_IP

# Restart Portainer:
docker restart portainer

# Wait 5 seconds:
sleep 5

# Exit SSH:
exit

# Quay lại browser:
# Mở: https://YOUR_VPS_IP:9443
# Bây giờ sẽ thấy "Create admin user" page
# Có 5 phút để tạo account
```

---

### ❌ Problem: Portainer SSL certificate warning

**This is NORMAL!**

**Explanation:**
- Portainer dùng self-signed SSL certificate
- Browser sẽ warning "Not secure"

**Solution:**
```
1. Click "Advanced"
2. Click "Proceed to YOUR_VPS_IP (unsafe)"
3. Hoặc: Setup SSL certificate với Let's Encrypt (advanced)
```

---

### ❌ Problem: Cannot access Portainer

**Error messages:**
```
ERR_CONNECTION_REFUSED
ERR_CONNECTION_TIMED_OUT
This site can't be reached
```

**Solutions:**

#### Solution 1: Check container running
```bash
# SSH vào VPS
docker ps | grep portainer

# Expected output:
# portainer  Up X minutes  0.0.0.0:9443->9443/tcp

# Nếu không thấy:
docker start portainer
```

#### Solution 2: Check firewall
```bash
# SSH vào VPS
sudo ufw status | grep 9443

# Expected:
# 9443/tcp   ALLOW   Anywhere

# Nếu không có:
sudo ufw allow 9443/tcp
sudo ufw reload
```

#### Solution 3: Recreate Portainer
```bash
# SSH vào VPS
# Stop and remove:
docker stop portainer
docker rm portainer

# Recreate:
docker run -d \
  --name portainer \
  --restart always \
  -p 9443:9443 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest

# Wait 10 seconds:
sleep 10

# Check:
docker ps | grep portainer
```

---

## 8. API NOT RESPONDING

### ❌ Problem: API returns 502 Bad Gateway

**Error messages:**
```
502 Bad Gateway
nginx/1.25.0
```

**Possible causes:**
1. Backend container not running
2. Backend crashed
3. Backend still starting
4. Database connection failed

**Solutions:**

#### Solution 1: Check backend container
```bash
# SSH vào VPS
docker ps | grep utility_backend

# Check status:
# Should be: Up X minutes (healthy)

# If not running:
cd /opt/utility-server
docker-compose restart backend

# Check logs:
docker logs utility_backend --tail 50
```

#### Solution 2: Check backend logs
```bash
# SSH vào VPS
docker logs utility_backend --tail 100

# Look for errors:
# - Database connection error
# - Import error
# - Port binding error
# - Missing environment variables
```

#### Solution 3: Check database connection
```bash
# SSH vào VPS
# Check postgres container:
docker ps | grep utility_postgres

# Should be: Up X minutes (healthy)

# Test connection from backend:
docker exec utility_backend ping -c 3 postgres

# Should succeed
```

#### Solution 4: Restart all services
```bash
# SSH vào VPS
cd /opt/utility-server

# Restart all:
docker-compose restart

# Wait 30 seconds:
sleep 30

# Test health:
curl http://localhost/health
```

---

### ❌ Problem: API returns 404 Not Found

**Error messages:**
```
404 Not Found
nginx/1.25.0
```

**Possible causes:**
1. Wrong URL
2. Nginx config wrong
3. Backend not proxied correctly

**Solutions:**

#### Solution 1: Check correct URLs
```
✅ Correct:
http://YOUR_VPS_IP/docs
http://YOUR_VPS_IP/health
http://YOUR_VPS_IP/api

❌ Wrong:
http://YOUR_VPS_IP:8000/docs  (port 8000 không expose)
https://YOUR_VPS_IP/docs      (chưa có SSL)
```

#### Solution 2: Check Nginx config
```bash
# SSH vào VPS
# Check nginx config:
docker exec utility_nginx cat /etc/nginx/nginx.conf

# Should have:
# proxy_pass http://backend:8000;

# Test nginx config:
docker exec utility_nginx nginx -t

# Should say: "syntax is ok"
```

---

## 9. DATABASE ISSUES

### ❌ Problem: Database connection failed

**Error messages:**
```
FATAL: password authentication failed for user "utility_user"
FATAL: database "utility_db" does not exist
could not connect to server: Connection refused
```

**Solutions:**

#### Solution 1: Check postgres container
```bash
# SSH vào VPS
docker ps | grep utility_postgres

# Should be: Up X minutes (healthy)

# Check logs:
docker logs utility_postgres --tail 50

# Look for:
# "database system is ready to accept connections"
```

#### Solution 2: Check .env file
```bash
# SSH vào VPS
cat /opt/utility-server/.env | grep POSTGRES

# Should have:
# POSTGRES_USER=utility_user
# POSTGRES_PASSWORD=...
# POSTGRES_DB=utility_db

# Backend should use same credentials
```

#### Solution 3: Recreate database
```bash
# ⚠️ CAUTION: This will DELETE all data!

# SSH vào VPS
cd /opt/utility-server

# Stop all:
docker-compose down

# Remove postgres volume:
docker volume rm utility-server_postgres_data

# Start again:
docker-compose up -d

# Database will be recreated
```

---

## 10. PERFORMANCE ISSUES

### ❌ Problem: VPS running slow

**Symptoms:**
- High CPU usage
- High RAM usage
- Slow API responses
- Containers restarting

**Solutions:**

#### Solution 1: Check resource usage
```bash
# SSH vào VPS

# Check overall:
htop  # Press q to quit

# Check Docker stats:
docker stats

# Look for containers using high CPU/RAM
```

#### Solution 2: Check logs for errors
```bash
# SSH vào VPS

# Check backend logs:
docker logs utility_backend --tail 100 | grep -i error

# Check postgres logs:
docker logs utility_postgres --tail 100 | grep -i error

# Check system logs:
journalctl -xe | grep -i error
```

#### Solution 3: Restart heavy containers
```bash
# SSH vào VPS

# Restart backend:
docker restart utility_backend

# Restart postgres:
docker restart utility_postgres

# Clear cache (Redis):
docker exec utility_redis redis-cli FLUSHALL
```

#### Solution 4: Check disk space
```bash
# SSH vào VPS

# Check disk usage:
df -h

# Should have at least 10GB free

# If low, clean Docker:
docker system prune -af --volumes

# ⚠️ CAUTION: This removes unused data
```

---

## 🆘 EMERGENCY PROCEDURES

### Full Reset - Option 1: Soft reset

```bash
# SSH vào VPS
cd /opt/utility-server

# Stop all:
docker-compose down

# Remove containers (keep data):
docker-compose rm -f

# Rebuild:
docker-compose up -d --build

# Check:
docker-compose ps
```

### Full Reset - Option 2: Hard reset

```bash
# SSH vào VPS
cd /opt/utility-server

# Stop all:
docker-compose down -v  # ⚠️ Removes volumes (data)!

# Clean Docker:
docker system prune -af --volumes  # ⚠️ Removes ALL unused data!

# Rebuild:
docker-compose up -d --build

# Check:
docker-compose ps
```

### Full Reset - Option 3: VPS reinstall

```
1. Login vào VPS provider dashboard
2. Click "Reinstall OS" hoặc "Rebuild"
3. Chọn: Ubuntu 22.04 LTS
4. Confirm
5. Đợi 2-3 phút
6. Chạy lại script: python scripts/auto_deploy_full.py
```

---

## 📞 SUPPORT COMMANDS

### Quick diagnostics:

```bash
# SSH vào VPS
ssh root@YOUR_VPS_IP

# 1. Check all containers:
docker ps -a

# 2. Check resource usage:
docker stats --no-stream

# 3. Check logs của tất cả containers:
cd /opt/utility-server
docker-compose logs --tail 20

# 4. Health check:
curl http://localhost/health

# 5. Check disk space:
df -h

# 6. Check memory:
free -h

# 7. Check firewall:
sudo ufw status

# 8. Check processes:
top  # Press q to quit
```

---

## 📝 COMMON ERROR CODES

### HTTP Status Codes:

```
200 OK              → Success ✅
400 Bad Request     → Client error (check request params)
401 Unauthorized    → Auth failed (check credentials)
403 Forbidden       → No permission
404 Not Found       → Wrong URL or endpoint doesn't exist
500 Internal Error  → Server error (check backend logs)
502 Bad Gateway     → Backend not responding (check backend)
503 Service Unavail → Service down (check containers)
504 Gateway Timeout → Backend too slow (check performance)
```

### Docker Exit Codes:

```
Exit 0   → Normal exit ✅
Exit 1   → Application error (check logs)
Exit 2   → Misuse of command
Exit 126 → Command cannot execute
Exit 127 → Command not found
Exit 137 → Killed (OOM - out of memory)
Exit 139 → Segmentation fault
Exit 143 → Terminated (SIGTERM)
```

---

## 🎓 PREVENTION TIPS

### Để tránh lỗi:

```
1. ✅ Luôn dùng fresh Ubuntu 22.04 install
2. ✅ Check VPS specs đủ (6GB RAM, 4 CPU)
3. ✅ Update system trước khi cài: apt update && apt upgrade
4. ✅ Đảm bảo SSH working trước khi chạy script
5. ✅ Đọc kỹ output của script
6. ✅ Không tắt script giữa chừng
7. ✅ Backup .env file sau khi deploy
8. ✅ Tạo snapshot VPS sau khi deploy thành công
9. ✅ Monitor logs định kỳ qua Dozzle
10. ✅ Update packages định kỳ
```

---

## ❓ FAQ

### Q: Script bị stuck ở bước build backend?
**A:** Bình thường! Build mất 2-3 phút. Đợi thêm.

### Q: Portainer timeout là lỗi?
**A:** KHÔNG! Đây là tính năng bảo mật. Restart portainer là xong.

### Q: Tại sao backend dùng nhiều RAM?
**A:** FastAPI + các libraries (OpenCV, etc) tốn RAM. Bình thường ~400MB.

### Q: Có thể dừng script và chạy lại không?
**A:** CÓ! Script idempotent. Chạy lại sẽ skip các bước đã xong.

### Q: Làm sao biết deployment thành công?
**A:** 
- Script báo "DEPLOYMENT COMPLETE"
- `curl http://YOUR_VPS_IP/health` returns `{"status":"healthy"}`
- 6 containers running: `docker ps`

---

## 📚 RESOURCES

- Docker docs: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- Portainer docs: https://docs.portainer.io/
- Cockpit docs: https://cockpit-project.org/guide/latest/
- FastAPI docs: https://fastapi.tiangolo.com/
- Ubuntu docs: https://help.ubuntu.com/

---

**Last updated:** 17/11/2025  
**Version:** 2.0
