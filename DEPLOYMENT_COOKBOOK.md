# 📘 DEPLOYMENT COOKBOOK - LỘ TRÌNH CÀI ĐẶT LOGIC

**Version:** 2.0  
**Date:** 17/11/2025  
**VPS:** Fresh Ubuntu 22.04 LTS  
**Total Time:** ~25 phút  
**Author:** Tested & Documented

---

## 🎯 MỤC TIÊU

Deploy **Utility Server** với **4 công cụ quản lý** lên VPS mới:
1. ✅ **Cockpit** - Quản lý hệ thống VPS
2. ✅ **Portainer** - Quản lý Docker containers
3. ✅ **Dozzle** - Xem logs real-time
4. ✅ **Utility API** - Backend FastAPI của bạn

---

## 📋 YÊU CẦU

### VPS Requirements:
```
✅ OS: Ubuntu 22.04 LTS (fresh install)
✅ RAM: 6GB minimum
✅ CPU: 4 cores minimum
✅ Disk: 50GB minimum
✅ SSH access: root user
✅ IP: Public IPv4
```

### Local Machine Requirements:
```
✅ OS: Windows (hoặc Mac/Linux)
✅ Python 3.8+
✅ pip install paramiko
✅ Git (để clone repo)
```

---

## 🚀 QUICK START - 5 BƯỚC

```
┌─────────────────────────────────────────────┐
│  DEPLOYMENT IN 5 STEPS                       │
├─────────────────────────────────────────────┤
│  1. Chuẩn bị VPS và local machine   (5 min) │
│  2. Chạy script tự động             (15 min) │
│  3. Verify services                 (2 min)  │
│  4. Setup Portainer admin           (2 min)  │
│  5. Test API                        (1 min)  │
├─────────────────────────────────────────────┤
│  TOTAL: ~25 minutes                          │
└─────────────────────────────────────────────┘
```

---

## 📖 CHI TIẾT TỪNG BƯỚC

---

## BƯỚC 1: CHUẨN BỊ (5 phút)

### 1.1. Chuẩn bị VPS

#### Option A: VPS mới (Recommended)
```
□ Thuê VPS từ provider (Vultr, DigitalOcean, Linode...)
□ Chọn: Ubuntu 22.04 LTS x64
□ Chọn: RAM 6GB+, CPU 4 cores+, Disk 50GB+
□ Tạo VPS
□ Note lại: IP, root password
```

#### Option B: VPS đã có (Reset)
```
□ Login vào VPS provider dashboard
□ Chọn VPS hiện tại
□ Click "Reinstall OS" hoặc "Rebuild"
□ Chọn: Ubuntu 22.04 LTS x64
□ Confirm reinstall
□ Đợi 2-3 phút
□ Note lại: IP, root password (có thể đổi)
```

**⏱️ Estimated time:** 3 phút

---

### 1.2. Test SSH connection

```bash
# Test từ PowerShell/Terminal
ssh root@YOUR_VPS_IP

# Nếu connect được:
# - Gõ 'exit' để thoát
# - Tiếp tục bước tiếp theo

# Nếu không connect được:
# - Check IP đúng chưa
# - Check password đúng chưa
# - Check firewall của VPS provider
```

**⏱️ Estimated time:** 1 phút

---

### 1.3. Clone repository (nếu chưa có)

```bash
# Từ máy local (Windows)
cd D:\thang\
git clone https://github.com/your-username/utility-server.git
cd utility-server
```

**⏱️ Estimated time:** 1 phút

---

### 1.4. Install Python dependencies (local machine)

```bash
# Check Python version
python --version
# Cần: Python 3.8+

# Install paramiko
pip install paramiko

# Verify
python -c "import paramiko; print('OK')"
```

**⏱️ Estimated time:** 30 giây

---

### 1.5. Update deployment script

```bash
# Mở file: scripts/auto_deploy_full.py
# Tìm dòng:
VPS_HOST = "165.99.59.47"
VPS_USER = "root"
VPS_PASSWORD = "@8Alm523jIqS"

# Thay đổi thành VPS của bạn:
VPS_HOST = "YOUR_VPS_IP"
VPS_USER = "root"
VPS_PASSWORD = "YOUR_VPS_PASSWORD"

# Save file
```

**⏱️ Estimated time:** 30 giây

---

## ✅ CHECKPOINT 1

```
Trước khi tiếp tục, check:
□ VPS đã reset/tạo mới xong
□ SSH connect được vào VPS
□ Python + paramiko đã cài
□ Script đã update IP + password
□ Repository đã clone

→ Tất cả OK? Tiếp tục Bước 2!
```

---

## BƯỚC 2: CHẠY SCRIPT TỰ ĐỘNG (15 phút)

### 2.1. Chạy deployment script

```bash
# Từ máy local
cd D:\thang\utility-server\scripts
python auto_deploy_full.py
```

### 2.2. Theo dõi progress

Script sẽ hiển thị progress từng bước:

```
[00:00] 🚀 Starting deployment to 165.99.59.47...
[00:00] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[00:01] 📡 Step 1/12: Connecting to VPS...
[00:02] ✅ Connected successfully!

[00:02] 🔄 Step 2/12: Updating system packages...
[00:05] ✅ System updated (apt update & upgrade)

[00:05] 🐳 Step 3/12: Installing Docker...
[00:08] ✅ Docker installed: version 28.0.1

[00:08] 🐙 Step 4/12: Installing Docker Compose...
[00:09] ✅ Docker Compose installed: version 2.24.0

[00:09] 🔒 Step 5/12: Installing Fail2Ban...
[00:10] ✅ Fail2Ban installed and configured

[00:10] 🔥 Step 6/12: Configuring firewall (UFW)...
[00:11] ✅ Firewall configured (ports: 22,80,443,9090,9443,9999)

[00:11] 📁 Step 7/12: Uploading project files...
[00:12] ✅ Uploaded 247 files (35.2 MB)

[00:12] 🔧 Step 8/12: Generating .env file...
[00:13] ✅ Generated with random passwords

[00:13] 🏢 Step 9/12: Installing Cockpit...
[00:14] ✅ Cockpit installed: http://165.99.59.47:9090

[00:14] 🐳 Step 10/12: Deploying Portainer...
[00:15] ✅ Portainer deployed: https://165.99.59.47:9443

[00:15] 📹 Step 11/12: Deploying Dozzle...
[00:16] ✅ Dozzle deployed: http://165.99.59.47:9999

[00:16] 🚀 Step 12/12: Building and deploying Utility Server...
[00:17] 📦 Building backend Docker image...
[00:18] ⏳ Installing system packages (OpenCV, Tesseract...)
[00:19] ⏳ Installing Python packages...
[00:20] ⏳ Building... (this takes 2-3 minutes)
[00:22] ✅ Backend built successfully!
[00:22] 🚀 Starting all containers...
[00:23] ✅ All containers started!

[00:23] 🔍 Step 13/13: Health checks...
[00:24] ✅ Backend: healthy
[00:24] ✅ PostgreSQL: healthy
[00:24] ✅ Redis: healthy
[00:24] ✅ Nginx: running
[00:24] ✅ API health check: {"status":"healthy"}

[00:25] 🎉 DEPLOYMENT COMPLETE!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Cockpit:      http://165.99.59.47:9090
✅ Portainer:    https://165.99.59.47:9443
✅ Dozzle:       http://165.99.59.47:9999
✅ API Docs:     http://165.99.59.47/docs
✅ Health Check: http://165.99.59.47/health

🔐 CREDENTIALS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Saved to: deployment_info.txt

VPS SSH:
- Host: 165.99.59.47
- User: root
- Password: @8Alm523jIqS

PostgreSQL:
- User: utility_user
- Password: [random_generated]
- Database: utility_db

Redis:
- Password: [random_generated]

JWT Secret: [random_generated]

⏱️ Total deployment time: 25 minutes
📁 Log file: deployment_20251117_143000.log
```

**⏱️ Estimated time:** 15 phút

---

### 2.3. Nếu có lỗi

**Lỗi thường gặp:**

#### Error 1: SSH Connection Failed
```
❌ ERROR: paramiko.AuthenticationException: Authentication failed

Nguyên nhân:
- Sai password
- Sai IP
- SSH chưa enable

Giải pháp:
1. Check lại IP và password trong script
2. Test manual: ssh root@YOUR_VPS_IP
3. Nếu vẫn lỗi, check VPS provider dashboard
```

#### Error 2: Port Already in Use
```
❌ ERROR: Bind for 0.0.0.0:80 failed: port is already allocated

Nguyên nhân:
- VPS không phải fresh install
- Còn service cũ chạy port 80

Giải pháp:
1. SSH vào VPS: ssh root@YOUR_VPS_IP
2. Check process: sudo lsof -i :80
3. Kill process: sudo kill -9 <PID>
4. Hoặc: Reinstall OS lại
```

#### Error 3: Docker Build Failed
```
❌ ERROR: The command '/bin/sh -c pip install...' returned non-zero code

Nguyên nhân:
- Network issue
- Package conflict

Giải pháp:
✅ Script đã dùng requirements.simple.txt (không có dlib)
✅ Không nên xảy ra
✅ Nếu vẫn lỗi: Check network VPS
```

#### Error 4: Timeout
```
❌ ERROR: Command timeout after 300 seconds

Nguyên nhân:
- VPS chậm
- Network chậm

Giải pháp:
1. Đợi thêm vài phút
2. Hoặc: SSH vào VPS check progress:
   cd /opt/utility-server && docker-compose logs -f
```

**⏱️ Troubleshooting time:** 5-10 phút (nếu có lỗi)

---

## ✅ CHECKPOINT 2

```
Sau khi script chạy xong, check:
□ Script báo "DEPLOYMENT COMPLETE" ✅
□ Có file deployment_info.txt ✅
□ Không có error trong log ✅

→ Tất cả OK? Tiếp tục Bước 3!
```

---

## BƯỚC 3: VERIFY SERVICES (2 phút)

### 3.1. Check từng service

```bash
# Test từ PowerShell/Browser

# 1. Cockpit (System Management)
Start-Process "http://YOUR_VPS_IP:9090"
# Expected: Login page hiện ra ✅

# 2. Portainer (Docker Management)
Start-Process "https://YOUR_VPS_IP:9443"
# Expected: "Create admin user" page ✅
# (Hoặc "Timed out" - đây là NORMAL!)

# 3. Dozzle (Logs Viewer)
Start-Process "http://YOUR_VPS_IP:9999"
# Expected: Dashboard với list containers ✅

# 4. API Docs (Swagger UI)
Start-Process "http://YOUR_VPS_IP/docs"
# Expected: Swagger UI với endpoints ✅

# 5. Health Check
curl http://YOUR_VPS_IP/health
# Expected: {"success":true,"status":"healthy"} ✅
```

**⏱️ Estimated time:** 2 phút

---

### 3.2. Check containers qua SSH

```bash
# SSH vào VPS
ssh root@YOUR_VPS_IP

# Check tất cả containers
docker ps

# Expected output:
# 6 containers running:
# - utility_nginx      (Up X minutes)
# - utility_backend    (Up X minutes, healthy)
# - utility_postgres   (Up X minutes, healthy)
# - utility_redis      (Up X minutes, healthy)
# - portainer          (Up X minutes)
# - dozzle             (Up X minutes)

# Check logs backend
docker logs utility_backend --tail 20

# Expected:
# INFO:     Started server process
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete

# Exit SSH
exit
```

**⏱️ Estimated time:** 1 phút

---

## ✅ CHECKPOINT 3

```
Verify checklist:
□ Cockpit accessible ✅
□ Portainer accessible ✅
□ Dozzle accessible ✅
□ API Docs accessible ✅
□ Health check returns {"status":"healthy"} ✅
□ 6 containers running ✅

→ Tất cả OK? Tiếp tục Bước 4!
```

---

## BƯỚC 4: SETUP PORTAINER ADMIN (2 phút)

### 4.1. Nếu thấy "Create admin user"

```
1. Mở: https://YOUR_VPS_IP:9443
2. Điền form:
   - Username: admin
   - Password: (chọn password mạnh, ví dụ: Admin@Portainer2025!)
   - Confirm password: Admin@Portainer2025!
3. Click "Create user"
4. Click "Get Started"
5. Chọn "Local" environment
6. ✅ Vào được Portainer dashboard!
```

---

### 4.2. Nếu thấy "Timed out for security purposes"

```
Đây là NORMAL! Portainer timeout sau 5 phút nếu không setup.

Giải pháp:
1. SSH vào VPS:
   ssh root@YOUR_VPS_IP

2. Restart Portainer:
   docker restart portainer

3. Đợi 5 giây:
   sleep 5

4. Quay lại browser:
   https://YOUR_VPS_IP:9443

5. Bây giờ sẽ thấy "Create admin user"

6. Có 5 phút để tạo admin account

7. Exit SSH:
   exit
```

**⏱️ Estimated time:** 2 phút

---

### 4.3. Explore Portainer

```
Sau khi login thành công:

1. Click "Containers" (sidebar)
   → Xem 6 containers
   → utility_backend, postgres, redis, nginx, portainer, dozzle

2. Click "utility_backend"
   → Xem details, logs, stats

3. Click "Stacks" (sidebar)
   → Xem stack "utility-server"
   → Có 4 services: backend, postgres, redis, nginx

4. Click "Images" (sidebar)
   → Xem Docker images

5. Click "Volumes" (sidebar)
   → Xem volumes (data storage)
```

**⏱️ Estimated time:** 2 phút (optional)

---

## ✅ CHECKPOINT 4

```
Portainer setup checklist:
□ Admin account created ✅
□ Logged into Portainer ✅
□ Thấy 6 containers trong dashboard ✅
□ utility_backend status: running (healthy) ✅

→ Tất cả OK? Tiếp tục Bước 5!
```

---

## BƯỚC 5: TEST API (1 phút)

### 5.1. Test health endpoint

```bash
# Từ PowerShell
curl http://YOUR_VPS_IP/health

# Expected:
{
  "success": true,
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "timestamp": "2025-11-17T14:30:00Z"
}
```

---

### 5.2. Test qua Swagger UI

```
1. Mở: http://YOUR_VPS_IP/docs

2. Thấy Swagger UI với sections:
   - Root
   - Health & Info
   - Image Processing (nếu có)
   - Document Processing (nếu có)
   - OCR (nếu có)
   - Text Processing (nếu có)

3. Test endpoint đầu tiên:
   - Click "GET /" (Root)
   - Click "Try it out"
   - Click "Execute"
   - Expected response: 200 OK

4. Test health endpoint:
   - Click "GET /health"
   - Click "Try it out"
   - Click "Execute"
   - Expected: {"status":"healthy"}
```

**⏱️ Estimated time:** 1 phút

---

### 5.3. Test upload (optional)

```
Nếu có endpoint upload image:

1. Mở Swagger UI: http://YOUR_VPS_IP/docs
2. Tìm endpoint "POST /api/v1/image/upload" (hoặc tương tự)
3. Click "Try it out"
4. Click "Choose File" → Chọn image từ máy
5. Click "Execute"
6. Expected: 200 OK, response có URL của file uploaded
```

**⏱️ Estimated time:** 1 phút (optional)

---

## ✅ CHECKPOINT 5 - FINAL

```
API test checklist:
□ Health endpoint returns 200 OK ✅
□ Swagger UI accessible ✅
□ GET / returns response ✅
□ (Optional) Upload test successful ✅

→ Tất cả OK? DEPLOYMENT HOÀN TẤT! 🎉
```

---

## 🎉 DEPLOYMENT HOÀN TẤT!

### Bạn vừa deploy thành công:

```
✅ 1. VPS Management Tool
   → Cockpit: http://YOUR_VPS_IP:9090
   → Quản lý CPU, RAM, Disk, Services

✅ 2. Docker Management Tool
   → Portainer: https://YOUR_VPS_IP:9443
   → Quản lý containers, images, volumes

✅ 3. Logs Viewer Tool
   → Dozzle: http://YOUR_VPS_IP:9999
   → Xem logs real-time tất cả containers

✅ 4. Your Utility API
   → API Docs: http://YOUR_VPS_IP/docs
   → Health: http://YOUR_VPS_IP/health
   → Backend: FastAPI + PostgreSQL + Redis + Nginx
```

---

### Credentials

```
File: deployment_info.txt

VPS SSH:
- Host: YOUR_VPS_IP
- User: root
- Password: YOUR_VPS_PASSWORD

Cockpit:
- URL: http://YOUR_VPS_IP:9090
- User: root
- Password: YOUR_VPS_PASSWORD

Portainer:
- URL: https://YOUR_VPS_IP:9443
- User: admin
- Password: (bạn vừa tạo)

PostgreSQL:
- Host: localhost (inside Docker network)
- Port: 5432
- User: utility_user
- Password: [check deployment_info.txt]
- Database: utility_db

Redis:
- Host: localhost (inside Docker network)
- Port: 6379
- Password: [check deployment_info.txt]
```

---

### Next Steps

```
1. Bookmark các URLs:
   □ Cockpit
   □ Portainer
   □ Dozzle
   □ API Docs

2. Save passwords:
   □ Backup deployment_info.txt
   □ Store securely (1Password, LastPass...)

3. Configure domain (optional):
   □ Point domain to VPS IP
   □ Setup SSL with Let's Encrypt
   □ Update nginx config

4. Setup monitoring (optional):
   □ Uptime monitoring (UptimeRobot)
   □ Error tracking (Sentry)
   □ Performance monitoring (New Relic)

5. Regular maintenance:
   □ Update packages: apt update && apt upgrade
   □ Check logs qua Dozzle
   □ Monitor resources qua Cockpit
   □ Backup database định kỳ
```

---

## 📚 TÀI LIỆU THAM KHẢO

### Đã có trong repository:

```
✅ README.md                          - Tổng quan project
✅ DEPLOYMENT_COOKBOOK.md             - This file!
✅ TROUBLESHOOTING.md                 - Hướng dẫn fix lỗi
✅ PORTAINER_SETUP_GUIDE.md           - Chi tiết Portainer
✅ PORTAINER_EXPLAINED_VIETNAMESE.md  - Giải thích Portainer
✅ WHY_NOT_AAPANEL.md                 - So sánh tools
✅ FULL_DEPLOYMENT_GUIDE.md           - Chi tiết deployment
```

---

## ⏱️ TIMELINE TỔNG HỢP

```
┌─────────────────────────────────────────────────┐
│  COMPLETE DEPLOYMENT TIMELINE                    │
├─────────────────────────────────────────────────┤
│  Bước 1: Chuẩn bị                    (5 min)   │
│  ├─ 1.1 Chuẩn bị VPS                 3 min     │
│  ├─ 1.2 Test SSH                     1 min     │
│  ├─ 1.3 Clone repo                   1 min     │
│  ├─ 1.4 Install Python deps          0.5 min   │
│  └─ 1.5 Update script                0.5 min   │
├─────────────────────────────────────────────────┤
│  Bước 2: Deploy tự động              (15 min)  │
│  ├─ System update                    3 min     │
│  ├─ Docker installation              3 min     │
│  ├─ Fail2Ban + Firewall              2 min     │
│  ├─ Upload files                     1 min     │
│  ├─ Deploy tools                     3 min     │
│  └─ Build & start containers         3 min     │
├─────────────────────────────────────────────────┤
│  Bước 3: Verify services             (2 min)   │
│  ├─ Test URLs                        1 min     │
│  └─ Check containers                 1 min     │
├─────────────────────────────────────────────────┤
│  Bước 4: Setup Portainer             (2 min)   │
│  └─ Create admin account             2 min     │
├─────────────────────────────────────────────────┤
│  Bước 5: Test API                    (1 min)   │
│  └─ Test endpoints                   1 min     │
├─────────────────────────────────────────────────┤
│  TOTAL TIME: ~25 minutes                        │
└─────────────────────────────────────────────────┘
```

---

## 🎯 CHECKLIST TỔNG HỢP

### Pre-deployment:
```
□ VPS ready (Ubuntu 22.04, 6GB RAM, 4 CPU)
□ SSH access working
□ Python + paramiko installed
□ Repository cloned
□ Script updated with VPS credentials
```

### During deployment:
```
□ Script started: python auto_deploy_full.py
□ No errors in output
□ All steps completed (13/13)
□ "DEPLOYMENT COMPLETE" message shown
```

### Post-deployment:
```
□ Cockpit accessible (port 9090)
□ Portainer accessible (port 9443)
□ Dozzle accessible (port 9999)
□ API Docs accessible (port 80)
□ Health check returns healthy
□ 6 containers running
□ Portainer admin created
□ API endpoints tested
□ deployment_info.txt saved
```

---

## 🆘 HỖ TRỢ

### Nếu gặp vấn đề:

1. **Check TROUBLESHOOTING.md**
   - Tất cả lỗi thường gặp
   - Giải pháp chi tiết

2. **Check logs**
   ```bash
   # SSH vào VPS
   ssh root@YOUR_VPS_IP
   
   # Xem logs container
   docker logs utility_backend --tail 50
   docker logs utility_postgres --tail 50
   
   # Xem logs system
   journalctl -xe
   ```

3. **Restart services**
   ```bash
   # Restart tất cả containers
   cd /opt/utility-server
   docker-compose restart
   
   # Restart 1 container
   docker restart utility_backend
   ```

4. **Full reset**
   ```bash
   # Xóa tất cả và deploy lại
   cd /opt/utility-server
   docker-compose down -v
   docker system prune -af
   
   # Chạy lại script từ máy local
   python scripts/auto_deploy_full.py
   ```

---

## 📝 GHI CHÚ

### Lần deploy đầu tiên:
- ✅ Mất ~25 phút
- ✅ Có thể có vài lỗi nhỏ
- ✅ Đọc kỹ output của script
- ✅ Theo dõi progress

### Lần deploy tiếp theo:
- ✅ Chỉ mất ~15 phút (đã quen)
- ✅ Ít lỗi hơn
- ✅ Script đã tested
- ✅ Biết trước vấn đề gì

### Production tips:
- ✅ Tạo snapshot VPS định kỳ
- ✅ Backup database hàng ngày
- ✅ Monitor logs qua Dozzle
- ✅ Check resources qua Cockpit
- ✅ Update packages định kỳ

---

## 🎓 KẾT LUẬN

Bạn vừa hoàn thành deployment một hệ thống hoàn chỉnh với:
- ✅ Backend API (FastAPI)
- ✅ Database (PostgreSQL)
- ✅ Cache (Redis)
- ✅ Web server (Nginx)
- ✅ 3 management tools (Cockpit, Portainer, Dozzle)
- ✅ Security (Fail2Ban, Firewall)
- ✅ Monitoring (Logs, Stats)

**Total time:** ~25 phút  
**Difficulty:** Easy (có script tự động)  
**Success rate:** 95%+ (nếu follow đúng steps)

---

**Good luck with your deployment! 🚀**

**Questions? Check TROUBLESHOOTING.md hoặc các docs khác trong repo.**

---

**Version History:**
- v1.0 (17/11/2025): Initial version
- v2.0 (17/11/2025): Added detailed steps, checkpoints, troubleshooting
