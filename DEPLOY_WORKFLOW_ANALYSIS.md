# PHÂN TÍCH LUỒNG NGHIỆP VỤ QUY TRÌNH DEPLOY

**Ngày phân tích:** 22/12/2025  
**Phiên bản hiện tại:** Backend 2.0.2 (code) vs 1.0.0 (production)  
**Vấn đề:** Version mismatch - quy trình deploy chưa hoàn chỉnh

---

## 1. QUY TRÌNH DEPLOY LÝ THUYẾT (Thiết kế ban đầu)

### 1.1. Giai đoạn Development (Local)
```
Developer → Code changes → Git commit → Git push to main
```

### 1.2. Giai đoạn CI/CD (GitHub Actions)
```
Push event trigger
    ↓
GitHub Actions workflow: .github/workflows/backend-image-ghcr.yml
    ↓
Job 1: Build Backend Image
    - Checkout code
    - Setup Docker Buildx
    - Login to GHCR (GitHub Container Registry)
    - Build Docker image với cache từ GHA
    - Push image với 2 tags:
        + latest
        + sha-<commit_hash>
    ↓
Job 2: Build Frontend Image (depends on backend)
    - Tương tự backend
    - Push frontend image to GHCR
    ↓
Kết quả: 2 images mới trên GHCR
    - ghcr.io/ericphan28/thang-phan-tools-backend:latest
    - ghcr.io/ericphan28/thang-phan-tools-frontend:latest
```

**Thời gian:** ~4-5 phút với cache

### 1.3. Giai đoạn Deployment (VPS Production)
```
Manual trigger or automation
    ↓
SSH vào VPS (165.99.59.47)
    ↓
cd /opt/utility-server
    ↓
docker compose -f docker-compose.prod.yml pull backend
    ↓
Docker pull image mới từ GHCR
    - Nếu image đã tồn tại (cached): ~6-8 giây
    - Nếu image mới (code changes): ~8-10 phút (download ~446MB layers)
    ↓
docker compose -f docker-compose.prod.yml up -d backend
    ↓
Docker restart container với image mới
    ↓
Backend chạy version mới
```

**Thời gian lý thuyết:**
- Pull cached: 6-8 giây
- Pull new: 8-10 phút lần đầu, sau đó 6-8 giây

---

## 2. THỰC TẾ HIỆN TẠI (Phân tích chi tiết)

### 2.1. Trạng thái Code
```bash
# Git commit gần nhất:
6438b88 - test: bump version to 2.0.2 - test deploy speed

# Code version trong backend/app/main_simple.py:
version="2.0.2"  # Test fast deploy
```

### 2.2. Trạng thái GitHub Actions
```yaml
Workflow: backend-image-ghcr.yml
Last run: Commit 6438b88
Status: ✅ Success
Duration: 4m 18s
Output: 
    - Backend image pushed to GHCR with tags: latest, sha-6438b88
    - Frontend image pushed to GHCR with tags: latest, sha-6438b88
```

### 2.3. Trạng thái VPS Production

#### Image trên VPS:
```
REPOSITORY: ghcr.io/ericphan28/thang-phan-tools-backend
TAG: latest
IMAGE ID: 946b5af7f110
SIZE: 2.02GB (compressed: 493MB)
CREATED: 2025-12-22T10:33:18.885502074Z (~16 phút trước)
```

**Nhận xét:** Image đã được pull về VPS, timestamp khớp với test deploy

#### Container đang chạy:
```
CONTAINER ID: 665cc05676af
IMAGE: ghcr.io/ericphan28/thang-phan-tools-backend:latest
STATUS: Up 16 minutes (unhealthy) ⚠️
PORT: 0.0.0.0:8000->8000/tcp
```

#### Version thực tế khi query API:
```bash
curl http://localhost:8000/health
→ {"status":"healthy","version":"1.0.0"} ❌

# Expected: version="2.0.2"
# Actual: version="1.0.0"
```

---

## 3. VẤN ĐỀ PHÁT HIỆN (Root Cause Analysis)

### 3.1. Hiện tượng: Version Mismatch
- **Code version:** 2.0.2 (committed 6438b88)
- **Image tag:** latest (created 16 minutes ago)
- **Container version:** 1.0.0 ❌

### 3.2. Nguyên nhân khả dĩ:

#### A. Image cũ vẫn được cache
```
Scenario:
1. VPS đã có image cũ với tag "latest" (version 1.0.0)
2. GitHub Actions build image mới (version 2.0.2) 
3. VPS pull nhưng Docker vẫn dùng cached image cũ
```

**Bằng chứng:**
- Container status: "unhealthy" - có thể do image cũ không khớp healthcheck
- Image created time: ~16 phút trước (khớp với test deploy)
- Nhưng version API trả về: 1.0.0 (cũ)

#### B. Pull bị interrupt
```
Scenario:
1. docker compose pull backend bắt đầu download
2. Download layers: 186.6MB + 260.3MB = ~446MB
3. User nhấn Ctrl+C interrupt ⚠️
4. Pull không hoàn thành, image mới không được extract
5. Docker fallback dùng image cũ
```

**Bằng chứng:**
- Test output cho thấy pull took long time (~8-10 phút)
- User đã interrupt với Ctrl+C trong log trước đó
- Container restart nhưng vẫn dùng image cũ

#### C. Docker Compose caching issue
```yaml
# docker-compose.prod.yml
backend:
    image: ${BACKEND_IMAGE:-ghcr.io/ericphan28/thang-phan-tools-backend:latest}
```

Docker Compose có thể:
- Cache image reference cũ
- Không force pull image mới
- Dùng local image thay vì registry image

---

## 4. LUỒNG DEPLOY THỰC TẾ (Với vấn đề)

```
┌─────────────────────────────────────────────────────────┐
│ 1. Developer Push Code (version 2.0.2)                 │
│    ✅ Success - commit 6438b88                          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. GitHub Actions Build & Push                         │
│    ✅ Success - 4m 18s                                  │
│    Output: latest + sha-6438b88 → GHCR                 │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. VPS Pull Image                                       │
│    ⚠️  PROBLEM HERE                                     │
│                                                          │
│    Pull started → Download 446MB                        │
│         ↓                                                │
│    User interrupt (Ctrl+C) ❌                           │
│         ↓                                                │
│    Pull incomplete                                       │
│         ↓                                                │
│    Old image (1.0.0) still in use                       │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 4. Container Restart                                    │
│    ⚠️  Using OLD image                                  │
│                                                          │
│    docker compose up -d backend                         │
│         ↓                                                │
│    Container ID: 665cc05676af                           │
│    Image: latest (but old cached version)               │
│    Status: Up 16 minutes (unhealthy)                    │
│         ↓                                                │
│    API returns: version="1.0.0" ❌                      │
└─────────────────────────────────────────────────────────┘
```

---

## 5. ĐIỂM YẾU TRONG QUY TRÌNH

### 5.1. Không có Version Verification
```
Current: Pull → Restart → ❌ Không verify version
Should be: Pull → Restart → ✅ Verify version → Rollback if failed
```

### 5.2. Pull không có --no-cache flag
```bash
# Current (có thể dùng cached image):
docker compose -f docker-compose.prod.yml pull backend

# Should be (force download mới):
docker compose -f docker-compose.prod.yml pull --no-cache backend
```

### 5.3. Không có monitoring cho pull progress
```bash
# Current: Chạy pull và chờ
# Should be: Monitor pull progress + retry nếu fail
```

### 5.4. Healthcheck không kiểm tra version
```yaml
# Current healthcheck chỉ check endpoint:
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]

# Should check version match:
healthcheck:
  test: ["CMD", "sh", "-c", "curl -f http://localhost:8000/health | grep '2.0.2'"]
```

### 5.5. Manual deployment process
```
Current: Manual SSH + pull + restart
Should be: Automated deployment với validation
```

---

## 6. SO SÁNH DEPLOY SPEED (3 phương pháp)

### Method 1: Build on VPS (Old - trước khi optimize)
```
Thao tác:
    1. SSH vào VPS
    2. git pull code mới
    3. docker compose build backend (build từ Dockerfile)
    4. docker compose up -d backend

Thời gian:
    - Build từ scratch: 10-15 phút ❌
    - Build với cache: 5-8 phút
    - Tốn tài nguyên VPS nhiều (CPU, RAM)

Ưu điểm:
    + Không cần external registry
    + Source code luôn sync

Nhược điểm:
    - Chậm mỗi lần deploy
    - Tốn tài nguyên VPS
    - Không có image versioning
    - Không có rollback dễ dàng
```

### Method 2: Pull from GHCR (Current - sau optimize)
```
Thao tác:
    1. GitHub Actions build image (4-5 phút)
    2. SSH vào VPS
    3. docker compose pull backend
    4. docker compose up -d backend

Thời gian:
    Case A - Không có code changes (cached image):
        - Pull check: ~2 giây ✅
        - Restart: ~4-6 giây
        - Total: 6-8 giây ✅
    
    Case B - Có code changes (new image):
        - Pull download: 8-10 phút ⚠️ (lần đầu)
        - Restart: ~4-6 giây
        - Total lần 1: 8-10 phút
        - Total các lần sau: 6-8 giây ✅

Ưu điểm:
    + Rất nhanh khi không có changes (6-8s)
    + Nhanh hơn nhiều so với build on VPS
    + Có image versioning (tags)
    + Dễ rollback
    + Không tốn tài nguyên VPS để build

Nhược điểm:
    - Lần pull đầu tiên vẫn chậm (8-10 phút)
    - Phụ thuộc vào network speed
    - Cần GitHub Actions quota
```

### Method 3: Watchtower (Automated - có thể implement)
```
Thao tác:
    1. Setup Watchtower container trên VPS
    2. Watchtower tự động check GHCR mỗi X phút
    3. Nếu có image mới → auto pull + restart

Thời gian:
    - Zero manual intervention ✅
    - Auto deploy trong vài phút sau push

Ưu điểm:
    + Hoàn toàn tự động
    + Không cần SSH manual
    + Deploy ngay khi có image mới

Nhược điểm:
    - Cần setup thêm Watchtower
    - Khó control deploy timing
    - Có thể deploy khi không mong muốn
```

---

## 7. GIẢI PHÁP KHẮC PHỤC

### 7.1. Immediate Fix (Khắc phục ngay)
```bash
# Bước 1: Force pull image mới không dùng cache
ssh root@165.99.59.47 "cd /opt/utility-server && \
    docker compose -f docker-compose.prod.yml pull --no-cache backend"

# Bước 2: Remove container cũ hoàn toàn
ssh root@165.99.59.47 "cd /opt/utility-server && \
    docker compose -f docker-compose.prod.yml down backend"

# Bước 3: Recreate container từ image mới
ssh root@165.99.59.47 "cd /opt/utility-server && \
    docker compose -f docker-compose.prod.yml up -d backend"

# Bước 4: Verify version
ssh root@165.99.59.47 "sleep 10 && \
    curl -s http://localhost:8000/health | grep '2.0.2' && \
    echo 'Version verified: 2.0.2 ✅' || \
    echo 'Version mismatch ❌'"
```

### 7.2. Short-term Improvement (Cải thiện ngắn hạn)
```bash
# Tạo deploy script với validation
# File: deploy-backend.sh
#!/bin/bash
set -e

EXPECTED_VERSION="2.0.2"
HEALTH_URL="http://localhost:8000/health"
COMPOSE_FILE="/opt/utility-server/docker-compose.prod.yml"

echo "🚀 Starting deployment..."

# Pull with retries
echo "📦 Pulling image..."
for i in {1..3}; do
    if docker compose -f $COMPOSE_FILE pull --no-cache backend; then
        echo "✅ Pull successful"
        break
    else
        echo "❌ Pull failed, retry $i/3..."
        sleep 5
    fi
done

# Stop old container
echo "🛑 Stopping old container..."
docker compose -f $COMPOSE_FILE stop backend

# Remove old container
echo "🗑️  Removing old container..."
docker compose -f $COMPOSE_FILE rm -f backend

# Start new container
echo "🔄 Starting new container..."
docker compose -f $COMPOSE_FILE up -d backend

# Wait for healthcheck
echo "⏳ Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -sf $HEALTH_URL > /dev/null; then
        echo "✅ Backend is healthy"
        break
    else
        echo "Waiting... ($i/30)"
        sleep 2
    fi
done

# Verify version
ACTUAL_VERSION=$(curl -s $HEALTH_URL | grep -oP '"version":"\K[^"]+')
if [ "$ACTUAL_VERSION" = "$EXPECTED_VERSION" ]; then
    echo "✅ Version verified: $ACTUAL_VERSION"
    exit 0
else
    echo "❌ Version mismatch! Expected: $EXPECTED_VERSION, Got: $ACTUAL_VERSION"
    exit 1
fi
```

### 7.3. Long-term Solution (Giải pháp dài hạn)

#### Option A: GitHub Actions tự động deploy lên VPS
```yaml
# .github/workflows/deploy-to-vps.yml
name: Deploy to VPS

on:
  push:
    branches: ["main"]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: build-and-push
    steps:
      - name: Deploy to VPS
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /opt/utility-server
            docker compose -f docker-compose.prod.yml pull --no-cache
            docker compose -f docker-compose.prod.yml up -d --force-recreate
            
            # Wait and verify
            sleep 10
            VERSION=$(curl -s http://localhost:8000/health | grep -oP '"version":"\K[^"]+')
            echo "Deployed version: $VERSION"
```

**Ưu điểm:**
- Hoàn toàn tự động sau git push
- Có verification built-in
- Deploy trong ~5 phút tổng (build + deploy)

#### Option B: Watchtower auto-update
```yaml
# Thêm vào docker-compose.prod.yml
services:
  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_POLL_INTERVAL=300  # Check mỗi 5 phút
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_INCLUDE_RESTARTING=true
    command: utility-backend-prod utility-frontend-prod
```

**Ưu điểm:**
- Zero manual work
- Auto-deploy trong 5-10 phút sau push

**Nhược điểm:**
- Ít control hơn
- Có thể deploy unexpected

---

## 8. SO SÁNH THỜI GIAN DEPLOY (Thực tế vs Lý thuyết)

### 8.1. Một lần deploy
```
Method                  | Build/Pull | Restart | Total   | Note
------------------------|------------|---------|---------|------------------
Build on VPS (old)      | 10-15 min  | 10 s    | 10-15m  | ❌ Chậm
Pull GHCR (cached)      | 6 s        | 6 s     | 12 s    | ✅ Rất nhanh
Pull GHCR (new)         | 8-10 min   | 6 s     | 8-10m   | ⚠️ Chậm lần đầu
```

### 8.2. Nhiều lần deploy (10 deploys)
```
Scenario: 10 lần deploy, 3 lần có code changes, 7 lần không có changes

Method Old (Build on VPS):
    10 deploys × 10 min = 100 phút = 1h 40m ❌

Method New (Pull GHCR):
    3 deploys (new) × 8 min = 24 phút
    7 deploys (cached) × 12s = 84 giây (~1.4 phút)
    Total = ~25.4 phút ✅
    
Tiết kiệm: 100 - 25.4 = 74.6 phút (~75% faster) 🚀
```

### 8.3. Reality Check
```
Câu hỏi user: "deploy chỉ mất 30-60s thôi ha?"

Trả lời:
    ✅ ĐÚNG nếu: không có code changes (cached image)
        → Pull check 6s + Restart 6s = ~12 giây
    
    ❌ SAI nếu: có code changes (new image)
        → Pull download 8-10 phút + Restart 6s = ~8-10 phút (lần đầu)
        → Các lần restart sau: ~12 giây
        
Kết luận:
    - Lần deploy ĐẦU TIÊN sau code changes: 8-10 phút
    - Các lần RESTART sau đó: 10-15 giây ✅
    - Trung bình: Nhanh hơn 75-90% so với build on VPS
```

---

## 9. KHUYẾN NGHỊ

### 9.1. Khắc phục immediate
1. ✅ Fix version mismatch ngay (pull --no-cache + recreate container)
2. ✅ Verify version sau mỗi deploy

### 9.2. Cải thiện workflow
1. ⭐ Implement deploy script với validation
2. ⭐ Add version check vào healthcheck
3. ⭐ Auto-deploy từ GitHub Actions

### 9.3. Monitoring
1. 📊 Track deploy time cho mỗi deploy
2. 📊 Monitor image size changes
3. 📊 Alert nếu deploy fail hoặc version mismatch

### 9.4. Documentation
1. 📝 Document clear deploy process
2. 📝 Troubleshooting guide
3. 📝 Rollback procedure

---

## 10. KẾT LUẬN

### Trạng thái hiện tại:
- ⚠️ **CI/CD pipeline hoạt động TỐT** (build + push to GHCR)
- ❌ **Deployment process CHƯA HOÀN CHỈNH** (version mismatch)
- ⚠️ **Speed improvement CÓ THẬT** nhưng conditional

### Vấn đề cốt lõi:
1. Pull bị interrupt → image cũ vẫn được dùng
2. Không có verification sau deploy
3. Manual process dễ bị lỗi

### Giải pháp ngắn hạn:
→ **Force pull --no-cache + recreate container + verify version**

### Giải pháp dài hạn:
→ **Automated deploy từ GitHub Actions với built-in verification**

### ROI (Return on Investment):
```
Đầu tư:
    - Setup CI/CD: ~4 giờ (đã xong)
    - Fix deploy script: ~1 giờ
    - Setup auto-deploy: ~2 giờ
    Total: ~7 giờ

Tiết kiệm:
    - Mỗi deploy: 10 phút → 10 giây (nếu cached)
    - Trung bình: ~75% faster
    - 10 deploys: tiết kiệm ~75 phút
    - 100 deploys: tiết kiệm ~750 phút = 12.5 giờ
    
Break-even: Sau ~10-15 deploys ✅
```

---

**Tác giả:** GitHub Copilot  
**Ngày:** 22/12/2025  
**Status:** Version 2.0.2 pending deployment
