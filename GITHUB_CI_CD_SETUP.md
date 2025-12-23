# 🚀 GITHUB CI/CD SETUP - AUTO DEPLOY TO VPS

## 📋 TÓM TẮT WORKFLOW

```mermaid
graph LR
    A[Push Code] --> B[GitHub Actions]
    B --> C[Build Docker Images]
    C --> D[Push to GHCR]
    D --> E[Watchtower on VPS]
    E --> F[Auto Pull & Restart]
```

1. **Push code** lên GitHub (branch `main`)
2. **GitHub Actions** tự động build Docker images
3. **Push images** lên GitHub Container Registry (GHCR)
4. **Watchtower** trên VPS tự động phát hiện image mới
5. **Pull & restart** containers tự động

---

## ✅ ĐÃ CÓ SẴN

### 1. GitHub Actions Workflow
File: `.github/workflows/backend-image-ghcr.yml`

**Trigger khi:**
- Push vào branch `main`
- Có thay đổi trong `backend/**`, `frontend/**`, hoặc `docker-compose*.yml`
- Manual trigger (workflow_dispatch)

**Làm gì:**
- Build backend Docker image
- Build frontend Docker image  
- Push cả 2 lên GHCR với tag `latest` và `sha-<commit>`

### 2. Docker Compose Production
File: `docker-compose.prod.yml`

**Images sử dụng:**
- Backend: `ghcr.io/ericphan28/thang-phan-tools-backend:latest`
- Frontend: `ghcr.io/ericphan28/thang-phan-tools-frontend:latest`

---

## 🔧 SETUP TỪNG BƯỚC

### BƯỚC 1: Cấu hình GitHub Repository

#### 1.1. Enable GitHub Packages
Workflow đã có quyền write packages (dùng `GITHUB_TOKEN` tự động)

#### 1.2. Set Repository Visibility
Nếu repo **private**, cần tạo Personal Access Token (PAT) để VPS pull images

**Tạo PAT:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Scopes cần chọn:
   - ✅ `read:packages`
   - ✅ `write:packages` (nếu muốn push từ local)
4. Copy token: `ghp_xxxxxxxxxxxxxxxxxxxx`

---

### BƯỚC 2: Setup VPS

#### 2.1. Kết nối VPS
```bash
ssh user@your-vps-ip
```

#### 2.2. Cài đặt Docker & Docker Compose
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker compose version
```

#### 2.3. Clone Repository trên VPS
```bash
cd /opt
sudo git clone https://github.com/ericphan28/thang-phan-tools.git
sudo chown -R $USER:$USER thang-phan-tools
cd thang-phan-tools
```

#### 2.4. Login vào GHCR (Nếu repo private)
```bash
# Sử dụng PAT đã tạo ở Bước 1.2
echo "ghp_YOUR_TOKEN_HERE" | docker login ghcr.io -u ericphan28 --password-stdin
```

Nếu **repo public**, skip bước này (không cần login)

#### 2.5. Tạo file `.env` cho backend
```bash
cd /opt/thang-phan-tools/backend
nano .env
```

Paste nội dung:
```env
# Database
DATABASE_URL=postgresql://postgres:your_password@postgres:5432/utility_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=utility_db

# JWT
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI API Keys
GEMINI_API_KEY=your-gemini-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Adobe PDF Services
ADOBE_CLIENT_ID=your-adobe-client-id
ADOBE_CLIENT_SECRET=your-adobe-client-secret

# Other
ENVIRONMENT=production
DEBUG=False
```

**Lưu:** Ctrl+O, Enter, Ctrl+X

---

### BƯỚC 3: Setup Watchtower (Tự động Update)

#### 3.1. Thêm Watchtower vào docker-compose.prod.yml

File đã có Watchtower service (check cuối file):

```yaml
watchtower:
  image: containrrr/watchtower:latest
  container_name: watchtower
  restart: unless-stopped
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
    - ~/.docker/config.json:/config.json:ro  # For GHCR auth
  environment:
    - WATCHTOWER_CLEANUP=true
    - WATCHTOWER_POLL_INTERVAL=300  # Check every 5 minutes
    - WATCHTOWER_INCLUDE_STOPPED=false
    - WATCHTOWER_REVIVE_STOPPED=false
    - WATCHTOWER_ROLLING_RESTART=true
  command: --interval 300 --cleanup
```

**Watchtower sẽ:**
- Kiểm tra GHCR mỗi 5 phút
- Phát hiện image mới (tag `latest`)
- Tự động pull về
- Restart containers
- Xóa old images

#### 3.2. Start Production Stack
```bash
cd /opt/thang-phan-tools

# Pull images lần đầu
docker compose -f docker-compose.prod.yml pull

# Start all services
docker compose -f docker-compose.prod.yml up -d

# Check logs
docker compose -f docker-compose.prod.yml logs -f
```

#### 3.3. Verify Watchtower
```bash
# Check Watchtower logs
docker logs watchtower -f

# Should see:
# "Checking for updated images"
# "Found new image for utility-backend-prod"
```

---

### BƯỚC 4: Test CI/CD Pipeline

#### 4.1. Từ máy local, push code
```bash
git add .
git commit -m "feat: test CI/CD auto deploy"
git push origin main
```

#### 4.2. Kiểm tra GitHub Actions
1. Vào repository trên GitHub
2. Tab "Actions"
3. Xem workflow "Build & Push Images (GHCR)" đang chạy
4. Đợi khoảng 5-10 phút

#### 4.3. Kiểm tra Watchtower trên VPS
```bash
# Watch logs
docker logs watchtower -f

# After ~5 minutes, you should see:
# "Found new image for utility-backend-prod"
# "Stopping utility-backend-prod"
# "Updating utility-backend-prod"
# "Starting utility-backend-prod"
```

#### 4.4. Verify Deployment
```bash
# Check running containers
docker ps

# Check backend version/commit
curl http://localhost:8000/health

# Check frontend
curl http://localhost:80
```

---

## 📊 MONITORING & DEBUGGING

### Check Container Status
```bash
docker ps -a
```

### View Logs
```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker logs utility-backend-prod -f --tail 100
docker logs utility-frontend-prod -f --tail 100
docker logs watchtower -f
```

### Restart Services
```bash
# Restart all
docker compose -f docker-compose.prod.yml restart

# Restart specific service
docker restart utility-backend-prod
```

### Force Pull New Images
```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### Check Watchtower Schedule
```bash
docker logs watchtower | grep "Checking"
```

---

## 🔒 SECURITY BEST PRACTICES

### 1. Use Strong Secrets
- Random `SECRET_KEY` (min 32 characters)
- Strong database password
- Rotate API keys regularly

### 2. Firewall Configuration
```bash
# Allow SSH, HTTP, HTTPS only
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Regular Updates
```bash
# Update VPS packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker compose -f docker-compose.prod.yml pull
```

### 4. Backup Database
```bash
# Backup PostgreSQL
docker exec utility-postgres-prod pg_dump -U postgres utility_db > backup_$(date +%Y%m%d).sql

# Restore
docker exec -i utility-postgres-prod psql -U postgres utility_db < backup_20241223.sql
```

---

## ⚙️ ADVANCED CONFIGURATION

### Watchtower với Email Notifications
```yaml
watchtower:
  environment:
    - WATCHTOWER_NOTIFICATIONS=email
    - WATCHTOWER_NOTIFICATION_EMAIL_FROM=notifications@example.com
    - WATCHTOWER_NOTIFICATION_EMAIL_TO=admin@example.com
    - WATCHTOWER_NOTIFICATION_EMAIL_SERVER=smtp.gmail.com
    - WATCHTOWER_NOTIFICATION_EMAIL_SERVER_PORT=587
    - WATCHTOWER_NOTIFICATION_EMAIL_SERVER_USER=your-email@gmail.com
    - WATCHTOWER_NOTIFICATION_EMAIL_SERVER_PASSWORD=your-app-password
```

### Custom Update Schedule
```yaml
watchtower:
  environment:
    - WATCHTOWER_SCHEDULE=0 0 4 * * *  # Cron: 4 AM daily
```

### Only Update Specific Containers
```bash
docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  utility-backend-prod utility-frontend-prod
```

---

## 🐛 TROUBLESHOOTING

### Issue: Watchtower không pull image mới

**Giải pháp:**
```bash
# 1. Check Watchtower logs
docker logs watchtower

# 2. Verify GHCR login (nếu repo private)
cat ~/.docker/config.json

# 3. Manually test pull
docker pull ghcr.io/ericphan28/thang-phan-tools-backend:latest

# 4. Restart Watchtower
docker restart watchtower
```

### Issue: GitHub Actions build fail

**Giải pháp:**
1. Check logs trong GitHub Actions tab
2. Verify Dockerfile syntax
3. Check file paths trong workflow

### Issue: Container crash sau update

**Giải pháp:**
```bash
# Rollback to previous version
docker compose -f docker-compose.prod.yml down
docker pull ghcr.io/ericphan28/thang-phan-tools-backend:sha-abc123
docker compose -f docker-compose.prod.yml up -d

# Check logs
docker logs utility-backend-prod
```

---

## 📚 USEFUL COMMANDS

```bash
# View all images
docker images

# Remove old images
docker image prune -a

# View system info
docker system df

# Clean everything
docker system prune -a --volumes

# Export/Import images
docker save -o backend.tar ghcr.io/ericphan28/thang-phan-tools-backend:latest
docker load -i backend.tar
```

---

## ✅ CHECKLIST HOÀN THÀNH

- [ ] GitHub Actions workflow hoạt động
- [ ] GHCR có images mới sau mỗi push
- [ ] VPS đã cài Docker & Docker Compose
- [ ] Đã clone repo trên VPS
- [ ] File `.env` đã cấu hình đúng
- [ ] Watchtower đang chạy
- [ ] Test push code → auto deploy thành công
- [ ] Firewall đã cấu hình
- [ ] Backup strategy đã setup

---

## 🎯 KẾT QUẢ MONG ĐỢI

Sau khi setup xong:

1. **Push code lên GitHub** → Chờ 5-10 phút
2. **GitHub Actions build** → Images mới trên GHCR
3. **Watchtower phát hiện** → Auto pull & restart
4. **VPS update thành công** → Không cần manual deploy!

**Deployment time:** ~10-15 phút từ push → production

---

**🔥 Status:** Production Ready  
**📅 Updated:** 23/12/2024  
**👤 Owner:** ericphan28
