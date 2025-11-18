# 🐳 PORTAINER SETUP GUIDE - CHI TIẾT

## 📋 TỔNG QUAN

Portainer là công cụ quản lý Docker với giao diện web, giúp bạn:
- ✅ Quản lý containers (start/stop/restart/delete)
- ✅ Xem logs real-time
- ✅ Exec vào container (terminal)
- ✅ Monitor CPU, RAM, Network
- ✅ Quản lý images, volumes, networks
- ✅ Deploy stacks (docker-compose)

---

## 🎯 BƯỚC 1: TRỬ CẬP LẦN ĐẦU

### URL:
```
https://165.99.59.47:9443
```

### Lưu ý:
- ⚠️ **HTTPS** (có chữ 's'), không phải HTTP
- ⚠️ Browser sẽ cảnh báo "Not secure" vì self-signed certificate
- ✅ Click "Advanced" → "Proceed to 165.99.59.47"

---

## 🔐 BƯỚC 2: TẠO ADMIN ACCOUNT

Lần đầu truy cập, bạn sẽ thấy màn hình "Create the first administrator user".

### Điền thông tin:

**Username:**
```
admin
```

**Password:** (chọn password mạnh, ít nhất 12 ký tự)

Ví dụ:
```
Admin@Portainer2025!
```

**Confirm Password:**
```
Admin@Portainer2025!
```

### ✅ Click "Create user"

---

## 🌐 BƯỚC 3: CONNECT TO ENVIRONMENT

Sau khi tạo account, bạn sẽ thấy màn hình "Quick Setup".

### Chọn Environment:

**Option 1: Get Started (Recommended)**
- Click nút **"Get Started"**
- Tự động connect tới local Docker environment
- ✅ Đơn giản nhất!

**Option 2: Manual Setup**
1. Click "Local" environment
2. Name: `VPS Docker`
3. Environment URL: `/var/run/docker.sock` (mặc định)
4. Click "Connect"

---

## 🎛️ BƯỚC 4: KHÁM PHÁ DASHBOARD

### Main Dashboard Sections:

#### 1. **Home** - Tổng quan
```
- Environment list
- Quick stats (containers, images, volumes)
- Resource usage
```

#### 2. **Containers** - Quản lý containers
```
├─ List view: Tất cả containers
├─ Quick actions:
│  ├─ Start / Stop / Restart / Pause
│  ├─ Kill / Remove
│  └─ Duplicate
└─ Filters: Running / Stopped / All
```

#### 3. **Images** - Quản lý images
```
├─ Local images
├─ Pull new image
├─ Remove unused images
└─ Image details (layers, size, history)
```

#### 4. **Volumes** - Quản lý data volumes
```
├─ List all volumes
├─ Create new volume
├─ Browse volume data
└─ Remove unused volumes
```

#### 5. **Networks** - Quản lý networks
```
├─ Bridge / Host / Overlay networks
├─ Create custom network
└─ Network inspection
```

#### 6. **Stacks** - Deploy docker-compose
```
├─ Upload docker-compose.yml
├─ Web editor
├─ Git repository deploy
└─ Stack management
```

---

## 📦 BƯỚC 5: XEM CONTAINERS

### Navigate: Home → Containers

Bạn sẽ thấy danh sách containers:

```
┌──────────────────────┬────────────┬────────────┬────────────┐
│ Name                 │ Status     │ Image      │ Actions    │
├──────────────────────┼────────────┼────────────┼────────────┤
│ portainer            │ Running ✅  │ portainer/ │ [Actions]  │
│ dozzle               │ Running ✅  │ amir20/    │ [Actions]  │
│ utility_backend      │ Building 🔄│ backend    │ [Actions]  │
│ utility_postgres     │ Running ✅  │ postgres   │ [Actions]  │
│ utility_redis        │ Running ✅  │ redis      │ [Actions]  │
│ utility_nginx        │ Running ✅  │ nginx      │ [Actions]  │
└──────────────────────┴────────────┴────────────┴────────────┘
```

### Actions cho mỗi container:

**1. Quick Actions (icon buttons):**
- ▶️ Start
- ⏸️ Pause
- 🔄 Restart
- ⏹️ Stop
- 🗑️ Remove

**2. Container Details (click vào tên):**
- Logs
- Inspect
- Stats
- Console
- Attach

---

## 📊 BƯỚC 6: XEM LOGS

### Method 1: Via Container List
1. Click vào container name (e.g., `utility_backend`)
2. Click tab **"Logs"**
3. ✅ Real-time logs streaming
4. Options:
   - Auto-refresh ON/OFF
   - Timestamps ON/OFF
   - Search/filter
   - Download logs

### Method 2: Quick Logs
1. Hover over container
2. Click icon **"📋 Logs"**
3. Popup window với logs

---

## 💻 BƯỚC 7: EXEC VÀO CONTAINER

### Use Case: Run commands inside container

**Steps:**
1. Click vào container name
2. Click tab **"Console"**
3. Chọn shell:
   - `/bin/bash` (Linux containers)
   - `/bin/sh` (Alpine containers)
4. Click **"Connect"**
5. ✅ Terminal opens!

**Example Commands:**
```bash
# Check Python version
python --version

# List files
ls -la

# Check environment variables
env

# Test database connection
psql -U utility_user -d utility_db -c "SELECT version();"

# Check Redis
redis-cli ping
```

---

## 📈 BƯỚC 8: MONITOR RESOURCES

### Container Stats (Real-time)

**Navigate:** Container → Stats tab

**Metrics:**
```
┌─────────────────────────────────────┐
│ CPU Usage:        15.23%           │
│ Memory Usage:     512 MB / 2 GB    │
│ Memory Percent:   25.6%            │
│ Network RX:       1.2 MB           │
│ Network TX:       890 KB           │
│ Block I/O Read:   450 MB           │
│ Block I/O Write:  120 MB           │
└─────────────────────────────────────┘
```

**Charts:**
- CPU usage over time
- Memory usage over time
- Network I/O over time
- Block I/O over time

---

## 🚀 BƯỚC 9: DEPLOY STACK (DOCKER-COMPOSE)

### Use Case: Deploy new application

**Steps:**
1. Navigate to **Stacks** (left sidebar)
2. Click **"+ Add stack"**
3. Điền thông tin:

**Name:**
```
my-app
```

**Build method:** Chọn 1 trong 3:
- Web editor (paste docker-compose.yml)
- Upload from computer
- Git repository

**Web Editor Example:**
```yaml
version: '3.8'
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    restart: unless-stopped
```

4. Click **"Deploy the stack"**
5. ✅ Stack deployed!

---

## 🎯 BƯỚC 10: QUẢN LÝ IMAGES

### Navigate: Home → Images

**Actions:**

**1. Pull New Image:**
```
Click "Pull a new image"
Image: python:3.11-slim
Registry: DockerHub
Click "Pull"
```

**2. Build from Dockerfile:**
```
Upload Dockerfile
Set build context
Add build args
Click "Build image"
```

**3. Remove Unused Images:**
```
Select unused images
Click "Remove"
Confirm
```

---

## 🔐 BƯỚC 11: BẢO MẬT

### Recommended Settings:

**1. Change Default Port (Optional):**
```bash
ssh root@165.99.59.47
docker stop portainer
docker rm portainer
docker run -d -p 8443:9443 --name portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest
```

**2. Setup Automatic Logout:**
- Settings → Session timeout: 5 minutes

**3. Create Additional Users (Optional):**
- Settings → Users → Add user
- Assign roles: Administrator / Operator / Read-only

**4. Setup Webhook (Optional):**
- Containers → Select container → Webhooks
- Create webhook URL for automated restarts

---

## 🎓 BƯỚC 12: ADVANCED FEATURES

### 1. **Templates** - Quick Deploy Apps
```
Home → App Templates
- WordPress
- MySQL
- PostgreSQL
- Redis
- Nginx
- More...
```

### 2. **Registries** - Private Docker Registry
```
Registries → Add registry
- DockerHub
- Private registry
- Azure Container Registry
- AWS ECR
```

### 3. **Endpoints** - Multiple Docker Hosts
```
Endpoints → Add endpoint
- Docker API
- Docker Swarm
- Kubernetes
- Azure ACI
```

### 4. **Notifications** - Webhooks & Email
```
Settings → Notifications
- Webhook URLs
- Email alerts
- Slack integration
```

---

## 📱 MOBILE ACCESS

Portainer có responsive design tuyệt vời!

**Sử dụng trên điện thoại:**
1. Mở browser trên điện thoại
2. Truy cập: https://165.99.59.47:9443
3. Login với account đã tạo
4. ✅ Full functionality!

**Mobile Features:**
- ✅ View all containers
- ✅ Start/stop containers
- ✅ View logs
- ✅ Check stats
- ✅ Exec console (limited)

---

## 🆘 TROUBLESHOOTING

### Issue 1: "Session timed out"
**Giải pháp:**
```powershell
ssh root@165.99.59.47 "docker restart portainer"
```
Chờ 10 giây, refresh browser.

### Issue 2: Forgot password
**Giải pháp:**
```powershell
ssh root@165.99.59.47 "docker exec portainer /portainer --admin-password='NewPassword123!'"
docker restart portainer
```

### Issue 3: Can't connect to Docker
**Giải pháp:**
```powershell
ssh root@165.99.59.47 "docker ps"
# Nếu Docker working, restart Portainer
docker restart portainer
```

### Issue 4: Port 9443 not accessible
**Check firewall:**
```powershell
ssh root@165.99.59.47 "ufw status | grep 9443"
# Should show: 9443/tcp ALLOW Anywhere
```

---

## 📚 LEARNING RESOURCES

### Official Docs:
- Homepage: https://www.portainer.io/
- Docs: https://docs.portainer.io/
- YouTube: Search "Portainer Tutorial"

### Video Tutorials:
1. "Portainer - Docker Made Easy" (10 minutes)
2. "Portainer Advanced Features" (20 minutes)
3. "Portainer Best Practices" (15 minutes)

---

## 🎯 QUICK REFERENCE

### Common Tasks:

**Restart Container:**
```
Containers → Select container → Restart button
```

**View Logs:**
```
Containers → Click name → Logs tab
```

**Exec Command:**
```
Containers → Click name → Console tab → Connect
```

**Deploy App:**
```
Stacks → Add stack → Paste docker-compose.yml → Deploy
```

**Check Stats:**
```
Containers → Click name → Stats tab
```

**Remove Container:**
```
Containers → Select checkbox → Remove button
```

---

## ✅ CHECKLIST - SETUP COMPLETE

- [ ] Truy cập https://165.99.59.47:9443
- [ ] Tạo admin account
- [ ] Connect to local environment
- [ ] Xem danh sách containers
- [ ] Xem logs của 1 container
- [ ] Exec vào 1 container
- [ ] Check stats real-time
- [ ] Explore Stacks/Images/Volumes

**Khi hoàn thành tất cả, bạn đã master Portainer!** 🎉

---

**Last Updated:** November 17, 2025  
**Portainer Version:** CE 2.x  
**Your VPS:** 165.99.59.47:9443
