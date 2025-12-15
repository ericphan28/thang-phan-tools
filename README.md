# 🚀 Utility Server - Multi-Purpose API Server

Server đa năng cung cấp các API tiện ích cho xử lý hình ảnh, nhận diện khuôn mặt, xử lý tài liệu và nhiều hơn nữa.

## ⚡ Quick Start (Windows)

### ✨ Cách 1: VS Code Tasks (KHUYÊN DÙNG - Đơn giản nhất!)

**Chạy servers:**
1. Mở project trong VS Code
2. Nhấn `Ctrl+Shift+P` → Gõ "Run Task"
3. Chọn **"🚀 Start All Servers"**
4. Hoặc nhấn phím tắt: **`Ctrl+Shift+S`**

**Dừng servers:**
- Nhấn **`Ctrl+Shift+K`** (kill all)
- Hoặc click vào thùng rác ở Terminal panel

**Ưu điểm:**
- ✅ Tự động mở 2 terminal panels
- ✅ Logs rõ ràng, dễ theo dõi
- ✅ Không bị conflict giữa các processes
- ✅ VS Code tự động quản lý lifecycle
- ✅ Có thể restart từng server riêng lẻ

### 🔧 Cách 2: Batch Files (Đơn giản)
```cmd
:: Double-click hoặc chạy trong CMD
START.bat
```
Sẽ tự động mở 2 CMD windows cho Backend và Frontend.

### 💻 Cách 3: Manual (Full control)
```powershell
# Terminal 1 - Backend
cd backend
$env:PYTHONPATH="D:\thang\utility-server\backend"
python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Sau khi chạy:**
- 🌐 Frontend: http://localhost:5173
- 🔧 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs
- 👤 Login: `admin` / `admin123`

## 📋 Tính năng

### 1. Face Recognition API
- ✅ Đăng ký khuôn mặt mới
- ✅ Nhận diện khuôn mặt từ ảnh
- ✅ So sánh 2 khuôn mặt
- ✅ Face detection & landmarks
- ✅ Liveness detection (phát hiện ảnh giả)

### 2. Image Processing API
- ✅ Resize, crop, rotate ảnh
- ✅ Nén và tối ưu hóa ảnh
- ✅ Xóa background
- ✅ Thêm watermark
- ✅ Áp dụng filters (grayscale, blur, sharpen, etc.)
- ✅ Format conversion (JPG, PNG, WEBP, etc.)

### 3. Document Processing API

#### 🔧 Local Processing (Free, Unlimited)
- ✅ Convert Word → PDF (Gotenberg - LibreOffice)
- ✅ Convert PDF → Word (pdf2docx - 7/10 quality)
- ✅ Convert PDF → Excel (pdfplumber - 8/10 quality for tables)
- ✅ Convert PDF → Images
- ✅ Merge multiple PDFs
- ✅ Split PDF
- ✅ Extract text từ PDF
- ✅ Compress PDF (pypdf - 7/10 quality)
- ✅ Add watermark to PDF (pypdf + reportlab - 8/10 quality)

#### ☁️ Adobe PDF Services (Cloud, 500 free/month, 10/10 quality)
- ✨ **NEW: OCR PDF** - Vietnamese AI text recognition (50+ languages)
- ✨ **NEW: Smart Extract** - AI-powered content extraction:
  - 📊 Tables → Structured Excel data
  - 🖼️ Images → PNG files with metadata
  - 📝 Text with font information (bold, italic, size, family)
  - 🏗️ Document structure (headings, paragraphs, lists)
- ✨ **NEW: HTML to PDF** - Perfect Chrome-quality rendering
- ✨ **Hybrid Compress** - Adobe first (10/10), fallback pypdf (7/10)
- ✨ **Hybrid Watermark** - Adobe first (10/10), fallback pypdf (8/10)
- 🎯 **Configurable Priority** - Choose Adobe-first or local-first via Settings

**Technology Comparison:**
| Feature | Adobe (Cloud) | Local Tools | Winner |
|---------|---------------|-------------|--------|
| Quality | 10/10 | 7-8/10 | Adobe |
| Speed | Medium (API call) | Fast | Local |
| Cost | 500 free/month | Unlimited free | Local |
| OCR Support | ✅ 50+ languages | ❌ | Adobe |
| AI Extract | ✅ Smart detection | ❌ | Adobe |
| Offline | ❌ | ✅ | Local |

### 4. OCR Service
- ✅ OCR tiếng Việt & tiếng Anh
- ✅ Nhận diện text từ ảnh
- ✅ Trích xuất thông tin từ CMND/CCCD
- ✅ Trích xuất thông tin từ hộ chiếu
- ✅ Nhận diện bảng biểu (table detection)

### 5. Text Processing API
- ✅ Text translation
- ✅ Text summarization
- ✅ Keyword extraction
- ✅ Sentiment analysis

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS
- **PDF Processing**: 
  - ☁️ Adobe PDF Services API (10/10 quality, 500 free/month)
  - 🖥️ Gotenberg (LibreOffice headless - Office → PDF)
  - 🖥️ pypdf (PDF manipulation - 7/10 quality)
  - 🖥️ pdf2docx (PDF → Word - 7/10 quality)
  - 🖥️ pdfplumber (PDF → Excel - 8/10 quality)
- **AI/ML Libraries**:
  - face_recognition (dlib)
  - OpenCV
  - Tesseract OCR
  - Pillow (PIL)
  - python-docx
- **Database**: PostgreSQL 15 (optional)
- **Cache/Queue**: Redis (optional)
- **Task Queue**: Celery (optional)
- **Container**: Docker & Docker Compose

## 📂 Cấu trúc dự án

```
utility-server/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   │   ├── face.py
│   │   │   ├── image.py
│   │   │   ├── document.py
│   │   │   ├── ocr.py
│   │   │   └── text.py
│   │   ├── services/         # Business logic
│   │   │   ├── face_service.py
│   │   │   ├── image_service.py
│   │   │   ├── document_service.py
│   │   │   ├── ocr_service.py
│   │   │   └── text_service.py
│   │   ├── models/           # Database models
│   │   │   └── models.py
│   │   ├── core/             # Config & utilities
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   └── main.py           # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
├── nginx/
│   └── nginx.conf
├── scripts/
│   ├── setup_vps.sh
│   └── deploy.sh
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 Cài đặt trên VPS Ubuntu

### Bước 1: Chuẩn bị VPS

```bash
# SSH vào VPS
ssh root@165.99.59.47

# Clone project (hoặc upload lên VPS)
cd /opt
git clone <your-repo> utility-server
cd utility-server

# Chạy script setup
chmod +x scripts/setup_vps.sh
./scripts/setup_vps.sh
```

### Bước 2: Cấu hình môi trường

```bash
# Copy và chỉnh sửa file .env
cp .env.example .env
nano .env

# Điền các thông tin:
# - DB_PASSWORD
# - REDIS_PASSWORD
# - SECRET_KEY
# - DOMAIN (nếu có)
```

#### 🌟 Optional: Adobe PDF Services Configuration

To enable Adobe AI-powered features (OCR, Smart Extract, HTML→PDF):

1. **Get Adobe Credentials** (Free 500 transactions/month):
   - Visit: https://developer.adobe.com/document-services/apis/pdf-services/
   - Create account → Get credentials
   - **📘 Detailed Guide**: See **[ADOBE_CREDENTIALS_GUIDE.md](./ADOBE_CREDENTIALS_GUIDE.md)**
   - **⚡ Quick Setup**: See **[ADOBE_QUICK_SETUP.md](./ADOBE_QUICK_SETUP.md)**

2. **Configure Backend**:
   ```bash
   cd backend
   
   # Edit .env
   USE_ADOBE_PDF_API=true
   PDF_SERVICES_CLIENT_ID=your_client_id_here
   PDF_SERVICES_CLIENT_SECRET=your_client_secret_here
   ADOBE_ORG_ID=your_org_id_here  # optional
   ```

3. **Test Configuration**:
   ```bash
   # Run test script
   python test_adobe_credentials.py
   
   # Expected output:
   # ✅ Config loaded successfully
   # ✅ Adobe SDK imported successfully
   # 🎉 SUCCESS! Adobe API is configured correctly!
   ```

4. **Configure Technology Priority** (in `.env`):
   ```bash
   # Choose Adobe-first (10/10 quality) or local-first (free unlimited)
   COMPRESS_PRIORITY=adobe,pypdf    # Try Adobe first, fallback pypdf
   WATERMARK_PRIORITY=adobe,pypdf   # Try Adobe first, fallback pypdf
   PDF_INFO_PRIORITY=adobe,pypdf    # Try Adobe first, fallback pypdf
   
   # Or reverse for local-first:
   # COMPRESS_PRIORITY=pypdf,adobe
   ```

4. **Runtime Configuration**:
   - Frontend: Go to **Settings** tab
   - Switch priorities on-the-fly
   - View Adobe quota usage (X/500)
   - Reset to defaults

**Adobe Features Comparison:**
- ✅ **OCR**: Vietnamese + 50 languages (Adobe only - no local alternative)
- ✅ **Smart Extract**: AI table/image extraction (Adobe only)
- ✅ **HTML→PDF**: Chrome-quality rendering (Adobe 10/10 vs wkhtmltopdf 6/10)
- ✅ **Compress**: Adobe 10/10 vs pypdf 7/10
- ✅ **Watermark**: Adobe 10/10 vs pypdf 8/10

### Bước 3: Deploy với Docker

```bash
# Build và start services
docker-compose up -d

# Kiểm tra logs
docker-compose logs -f

# Kiểm tra services đang chạy
docker-compose ps
```

### Bước 4: Setup SSL (tùy chọn)

```bash
# Nếu có domain
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 📖 API Documentation

Sau khi chạy server, truy cập:
- **Swagger UI**: http://your-server-ip:8000/docs
- **ReDoc**: http://your-server-ip:8000/redoc

## 🔐 Authentication

Server sử dụng JWT token cho authentication:

```bash
# Đăng ký user mới
curl -X POST "http://your-server/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Login và nhận token
curl -X POST "http://your-server/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Sử dụng token trong các request
curl -X POST "http://your-server/api/face/register" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@photo.jpg" \
  -F "name=John Doe"
```

## 📝 Ví dụ sử dụng

### 1. Face Recognition

```python
import requests

# Đăng ký khuôn mặt
files = {'file': open('person.jpg', 'rb')}
data = {'name': 'Nguyen Van A', 'user_id': '12345'}
response = requests.post('http://your-server/api/face/register', 
                        files=files, data=data,
                        headers={'Authorization': 'Bearer YOUR_TOKEN'})

# Nhận diện khuôn mặt
files = {'file': open('unknown.jpg', 'rb')}
response = requests.post('http://your-server/api/face/recognize',
                        files=files,
                        headers={'Authorization': 'Bearer YOUR_TOKEN'})
print(response.json())
```

### 2. Image Processing

```python
# Resize ảnh
files = {'file': open('image.jpg', 'rb')}
data = {'width': 800, 'height': 600}
response = requests.post('http://your-server/api/image/resize',
                        files=files, data=data,
                        headers={'Authorization': 'Bearer YOUR_TOKEN'})

# Xóa background
files = {'file': open('person.jpg', 'rb')}
response = requests.post('http://your-server/api/image/remove-background',
                        files=files,
                        headers={'Authorization': 'Bearer YOUR_TOKEN'})
```

### 3. Document Processing

```python
# Convert Word to PDF
files = {'file': open('document.docx', 'rb')}
response = requests.post('http://your-server/api/document/word-to-pdf',
                        files=files,
                        headers={'Authorization': 'Bearer YOUR_TOKEN'})

# Extract text from PDF
files = {'file': open('document.pdf', 'rb')}
response = requests.post('http://your-server/api/document/extract-text',
                        files=files,
                        headers={'Authorization': 'Bearer YOUR_TOKEN'})
```

### 4. OCR

```python
# OCR tiếng Việt
files = {'file': open('text_image.jpg', 'rb')}
data = {'language': 'vie'}
response = requests.post('http://your-server/api/ocr/extract',
                        files=files, data=data,
                        headers={'Authorization': 'Bearer YOUR_TOKEN'})
```

## 🔧 Quản lý

### Monitoring

```bash
# Xem logs
docker-compose logs -f backend

# Xem resource usage
docker stats

# Truy cập Flower (Celery monitoring)
http://your-server:5555
```

### Backup Database

```bash
# Backup
docker-compose exec postgres pg_dump -U utility_user utility_db > backup.sql

# Restore
docker-compose exec -T postgres psql -U utility_user utility_db < backup.sql
```

### Update code

```bash
# Pull code mới
git pull origin main

# Rebuild và restart
docker-compose down
docker-compose up -d --build
```

## 📊 Performance Tips

1. **Redis Cache**: Tất cả face embeddings được cache trong Redis để tăng tốc
2. **Celery Queue**: Các tác vụ nặng chạy background qua Celery
3. **File Storage**: Upload files được lưu trong volume riêng biệt
4. **Rate Limiting**: API có rate limit để tránh abuse
5. **Image Optimization**: Ảnh được tự động resize trước khi xử lý

## ⚠️ Security Notes

- ✅ Đổi tất cả passwords mặc định trong `.env`
- ✅ Bật firewall chỉ mở port 80, 443, 22
- ✅ Setup SSL certificate với Certbot
- ✅ Thường xuyên backup database
- ✅ Update packages định kỳ
- ✅ Monitor logs để phát hiện bất thường

## 🆘 Troubleshooting

### Service không start được?
```bash
# Check logs
docker-compose logs backend

# Restart service
docker-compose restart backend
```

### Out of memory?
```bash
# Check memory
free -h

# Tăng swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Slow performance?
- Kiểm tra CPU/RAM usage
- Tăng số Celery workers
- Optimize database queries
- Tăng Redis memory

## 📞 Support

- Email: your-email@example.com
- Issues: GitHub Issues

## 📄 License

MIT License

---

**Made with ❤️ for Utility Server**
