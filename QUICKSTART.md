# 🚀 HƯỚNG DẪN NHANH - UTILITY SERVER

## 📦 Bạn đang có gì?

✅ **Một hệ thống server hoàn chỉnh** với các tính năng:
- Face Recognition (Nhận diện khuôn mặt)
- Image Processing (Xử lý hình ảnh)
- Document Processing (Xử lý tài liệu PDF, Word)
- OCR (Nhận dạng chữ từ ảnh)
- Text Processing (Xử lý văn bản)

✅ **Stack công nghệ:**
- Backend: FastAPI (Python)
- Database: PostgreSQL
- Cache: Redis
- Web Server: Nginx
- Container: Docker

✅ **Code đã có trong:** `D:\thang\utility-server`

---

## ⚡ CÁCH 1: DEPLOY NHANH TỪ WINDOWS (KHUYÊN DÙNG)

### Bước 1: Cấu hình file .env
```powershell
cd D:\thang\utility-server
copy .env.example .env
notepad .env
```

Thay đổi các dòng sau trong file `.env`:
```
DB_PASSWORD=MatKhau123!@#        # Đổi password database
REDIS_PASSWORD=Redis456!@#       # Đổi password Redis
SECRET_KEY=random-key-here       # Random string bất kỳ
JWT_SECRET_KEY=jwt-key-here      # Random string bất kỳ
```

### Bước 2: Chạy script deploy
```powershell
cd D:\thang\utility-server\scripts
powershell -ExecutionPolicy Bypass -File deploy_from_windows.ps1
```

Script sẽ tự động:
- Upload code lên VPS
- Cài đặt Docker và dependencies
- Chạy tất cả services
- Báo cho bạn địa chỉ truy cập

### Bước 3: Kiểm tra
Mở browser và truy cập:
```
http://165.99.59.47/docs
```

**XONG! 🎉**

---

## 🔧 CÁCH 2: DEPLOY THỦ CÔNG (CHI TIẾT HƠN)

### A. Upload code lên VPS

**Option 1: Dùng WinSCP (Dễ nhất)**
1. Download WinSCP: https://winscp.net/eng/download.php
2. Kết nối:
   - Host: `165.99.59.47`
   - User: `root`
   - Password: `@8Alm523jIqS`
3. Upload folder `D:\thang\utility-server` lên `/opt/utility-server`

**Option 2: Dùng Git**
```powershell
# Tạo Git repository
cd D:\thang\utility-server
git init
git add .
git commit -m "Initial commit"

# Push lên GitHub (tạo repo trước trên GitHub)
git remote add origin https://github.com/your-username/utility-server.git
git push -u origin main

# Sau đó trên VPS:
ssh root@165.99.59.47
cd /opt
git clone https://github.com/your-username/utility-server.git
```

### B. Chạy trên VPS

```bash
# SSH vào VPS
ssh root@165.99.59.47
# Password: @8Alm523jIqS

# Vào thư mục project
cd /opt/utility-server

# Chỉnh sửa .env
nano .env
# Thay đổi passwords và secret keys

# Chạy script setup
chmod +x scripts/*.sh
bash scripts/setup_vps.sh

# Deploy
bash scripts/deploy.sh
```

### C. Kiểm tra

```bash
# Check services
docker-compose ps

# Check logs
docker-compose logs -f

# Test API
curl http://localhost:8000/health
```

---

## 📱 TRUY CẬP API

Sau khi deploy xong, bạn có thể truy cập:

### 🌐 Web Interface
- **API Documentation**: http://165.99.59.47/docs
- **ReDoc**: http://165.99.59.47/redoc
- **Health Check**: http://165.99.59.47/health

### 🔌 API Endpoints (sẽ có sau khi hoàn thiện)

**Face Recognition:**
```bash
# Đăng ký khuôn mặt
POST http://165.99.59.47/api/face/register
Body: file (image), name, user_id

# Nhận diện khuôn mặt
POST http://165.99.59.47/api/face/recognize
Body: file (image)
```

**Image Processing:**
```bash
# Resize ảnh
POST http://165.99.59.47/api/image/resize
Body: file (image), width, height

# Xóa background
POST http://165.99.59.47/api/image/remove-background
Body: file (image)
```

**Document Processing:**
```bash
# Convert Word to PDF
POST http://165.99.59.47/api/document/word-to-pdf
Body: file (docx)

# Extract text from PDF
POST http://165.99.59.47/api/document/extract-text
Body: file (pdf)
```

**OCR:**
```bash
# OCR tiếng Việt
POST http://165.99.59.47/api/ocr/extract
Body: file (image), language=vie
```

---

## 🎯 TEST NHANH

### Test từ PowerShell (Windows)
```powershell
# Health check
Invoke-RestMethod -Uri "http://165.99.59.47/health"

# API info
Invoke-RestMethod -Uri "http://165.99.59.47/api"
```

### Test từ curl
```bash
# Health check
curl http://165.99.59.47/health

# Upload và test face recognition (khi API đã có)
curl -X POST "http://165.99.59.47/api/face/register" \
  -F "file=@photo.jpg" \
  -F "name=John Doe"
```

### Test từ Python
```python
import requests

# Health check
response = requests.get("http://165.99.59.47/health")
print(response.json())

# Face recognition (khi API đã có)
files = {'file': open('photo.jpg', 'rb')}
data = {'name': 'John Doe'}
response = requests.post(
    "http://165.99.59.47/api/face/register",
    files=files,
    data=data
)
print(response.json())
```

---

## 🛠️ QUẢN LÝ HẰNG NGÀY

### Xem logs
```bash
ssh root@165.99.59.47
cd /opt/utility-server
docker-compose logs -f
```

### Restart services
```bash
ssh root@165.99.59.47
cd /opt/utility-server
docker-compose restart
```

### Update code
```bash
# Nếu dùng Git
ssh root@165.99.59.47
cd /opt/utility-server
git pull
bash scripts/deploy.sh

# Nếu upload thủ công
# Upload lại bằng WinSCP, sau đó:
ssh root@165.99.59.47
cd /opt/utility-server
bash scripts/deploy.sh
```

### Backup database
```bash
ssh root@165.99.59.47
cd /opt/utility-server
docker-compose exec postgres pg_dump -U utility_user utility_db > backup.sql
```

---

## ❓ TROUBLESHOOTING

### Service không chạy?
```bash
docker-compose ps              # Check status
docker-compose logs backend    # Check logs
docker-compose restart         # Restart all
```

### Không truy cập được từ bên ngoài?
```bash
# Check firewall
ufw status

# Open ports
ufw allow 80/tcp
ufw allow 443/tcp
```

### Out of memory?
```bash
free -h                        # Check memory
docker stats                   # Check container usage
```

---

## 📚 TÀI LIỆU CHI TIẾT

- **README.md** - Tổng quan hệ thống
- **DEPLOY.md** - Hướng dẫn deploy chi tiết
- **API Docs** - http://165.99.59.47/docs (sau khi deploy)

---

## 🎉 TIẾP THEO?

Sau khi deploy thành công, bạn cần:

1. ✅ **Hoàn thiện API endpoints** - Hiện tại mới có cấu trúc, cần code các endpoints
2. ✅ **Thêm authentication** - JWT tokens cho bảo mật
3. ✅ **Test đầy đủ** - Test tất cả các tính năng
4. ✅ **Setup SSL** - Nếu có domain name
5. ✅ **Monitor** - Setup monitoring và alerts

---

**Chúc bạn thành công! 🚀**

Nếu gặp vấn đề gì, check logs đầu tiên:
```bash
docker-compose logs -f
```
