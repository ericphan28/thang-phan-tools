# 🔑 Hướng Dẫn Lấy Adobe PDF Services API Credentials

## 📌 Tại Sao Cần Adobe API?

Adobe PDF Services API cung cấp các tính năng **cao cấp** mà thư viện local không làm được:

| Tính Năng | Adobe (10/10) | Tesseract/Local (7/10) |
|-----------|---------------|------------------------|
| **OCR PDF** | ✅ Perfect layout, 50+ ngôn ngữ | ⚠️ Basic, cần cài Tesseract |
| **PDF to Word** | ✅ Giữ nguyên format 100% | ⚠️ Mất format phức tạp |
| **Extract Tables** | ✅ AI nhận dạng tables → Excel | ❌ Không có |
| **Extract Images** | ✅ Tách images với metadata | ❌ Không có |
| **HTML to PDF** | ✅ Render hoàn hảo | ⚠️ Cần Gotenberg |
| **Compress PDF** | ✅ AI optimize | ⚠️ Basic compression |

**Free Tier**: 500 transactions/tháng (đủ để test và dùng cá nhân)

---

## 🚀 Các Bước Lấy Credentials (5 phút)

### **Bước 1: Tạo Adobe Account**

1. Truy cập: **https://acrobatservices.adobe.com/dc-integration-creation-app-cdn/main.html**
2. Click **"Get started"** hoặc **"Start free trial"**
3. Đăng ký bằng:
   - 📧 Email (tạo Adobe ID mới)
   - 🔵 Google account
   - 🔵 Facebook account  
   - 🍎 Apple ID

> **Tip**: Dùng Google account để đăng ký nhanh nhất!

---

### **Bước 2: Tạo Project**

1. Sau khi đăng nhập, bạn sẽ vào **Adobe Developer Console**
2. Hoặc truy cập trực tiếp: **https://developer.adobe.com/console**
3. Click **"Create new project"**
4. Đặt tên project (ví dụ: **"My PDF Tools"** hoặc **"Utility Server"**)

---

### **Bước 3: Thêm PDF Services API**

1. Trong project vừa tạo, click **"Add API"**
2. Tìm và chọn **"PDF Services API"**
3. Click **"Next"**

---

### **Bước 4: Chọn Authentication Method**

Chọn **"OAuth Server-to-Server"** (Recommended):
- ✅ Dễ setup nhất
- ✅ Không cần private key file
- ✅ Chỉ cần Client ID và Client Secret

Click **"Save configured API"**

---

### **Bước 5: Lấy Credentials**

Sau khi tạo xong, trong **Credentials** section bạn sẽ thấy:

```
Client ID: abc123def456789...
Client Secret: p8-xyz789abc123...
Technical Account ID: ... (không cần)
Organization ID: ... (optional)
```

**Lưu ý quan trọng:**
- ⚠️ **Client Secret** chỉ hiện 1 lần! Copy ngay!
- 🔐 Không share credentials này với ai
- 📋 Lưu vào file an toàn (password manager, .env file)

---

## ⚙️ Cấu Hình Backend

### **Option A: Environment Variables** (Recommended)

1. Mở file **`backend/.env`**
2. Tìm section **"Adobe PDF Services API"**
3. Điền thông tin:

```env
# Adobe PDF Services API
USE_ADOBE_PDF_API=true
PDF_SERVICES_CLIENT_ID="your_client_id_here"
PDF_SERVICES_CLIENT_SECRET="your_client_secret_here"
ADOBE_ORG_ID="your_org_id_here"
```

**Ví dụ thực tế:**

```env
USE_ADOBE_PDF_API=true
PDF_SERVICES_CLIENT_ID="abc123def456789xyz"
PDF_SERVICES_CLIENT_SECRET="p8-1a2b3c4d5e6f7g8h"
ADOBE_ORG_ID="1234567890ABCDEF@AdobeOrg"
```

4. **Save file**
5. **Restart backend server** (uvicorn sẽ tự động reload nếu đang chạy với `--reload` flag)

---

### **Option B: JSON Credentials File** (Alternative)

Nếu bạn download file JSON từ Adobe Console:

1. Download file **`pdfservices-api-credentials.json`**
2. Đặt vào folder **`backend/`**
3. File có format:

```json
{
  "client_credentials": {
    "client_id": "abc123...",
    "client_secret": "p8-xyz..."
  },
  "service_principal_credentials": {
    "organization_id": "...",
    "account_id": "...",
    "private_key_file": "private.key"
  }
}
```

4. Backend sẽ tự động detect và load credentials từ file này

---

## ✅ Kiểm Tra Cấu Hình

### **Test từ Terminal:**

```powershell
# Windows PowerShell
cd backend
python -c "from app.core.config import settings; print('Adobe enabled:', settings.USE_ADOBE_PDF_API); print('Client ID:', settings.PDF_SERVICES_CLIENT_ID[:10] + '...' if settings.PDF_SERVICES_CLIENT_ID else 'Not set')"
```

**Kết quả mong đợi:**
```
Adobe enabled: True
Client ID: abc123def4...
```

---

### **Test từ API:**

1. Start backend server:
   ```powershell
   cd backend
   python -m uvicorn app.main_simple:app --reload
   ```

2. Truy cập API docs: **http://localhost:8000/docs**

3. Thử endpoint **`POST /api/v1/documents/pdf/ocr`**:
   - Upload một file PDF scan
   - Click "Execute"
   - Kết quả:
     - ✅ Success → Adobe API hoạt động!
     - ❌ Error → Check credentials

---

## 🎯 Usage Limits & Pricing

### **Free Tier** (Developer Plan)
- ✅ **500 transactions/month** miễn phí
- ✅ Không cần credit card
- ✅ Đủ để test và dùng cá nhân
- Transaction reset đầu mỗi tháng

### **Paid Plans** (Nếu cần nhiều hơn)
| Plan | Transactions | Price |
|------|--------------|-------|
| Free | 500/month | $0 |
| Essential | 5,000/month | $99/month |
| Professional | 25,000/month | $299/month |

---

## 🔍 Tracking Usage

Check usage tại: **https://developer.adobe.com/console**

1. Vào project
2. Click **"Insights"** hoặc **"Usage"**
3. Xem số transactions đã dùng trong tháng

---

## ❓ Troubleshooting

### **Error: "Invalid credentials"**
- ✅ Check lại Client ID và Client Secret (không có space, dấu ngoặc thừa)
- ✅ Client Secret chỉ hiện 1 lần khi tạo → phải tạo lại nếu quên
- ✅ Restart backend server sau khi update .env

### **Error: "Quota exceeded"**
- ✅ Đã dùng hết 500 transactions/month
- ✅ Đợi đầu tháng mới reset
- ✅ Hoặc nâng cấp lên paid plan

### **Error: "Service unavailable"**
- ✅ Check internet connection
- ✅ Adobe API có thể bảo trì (hiếm khi)
- ✅ Fallback to Tesseract sẽ tự động chạy

---

## 🔗 Links Hữu Ích

- 📘 **Get Started**: https://acrobatservices.adobe.com/dc-integration-creation-app-cdn/main.html
- 🔧 **Developer Console**: https://developer.adobe.com/console
- 📖 **Documentation**: https://developer.adobe.com/document-services/docs/overview/
- 💡 **API Reference**: https://developer.adobe.com/document-services/apis/pdf-services/
- 🎓 **Tutorials**: https://developer.adobe.com/document-services/docs/overview/pdf-services-api/howtos/

---

## 📝 Summary

**TL;DR - Quick Steps:**

1. Tạo account: https://acrobatservices.adobe.com
2. Tạo project + Add "PDF Services API"
3. Chọn "OAuth Server-to-Server"
4. Copy **Client ID** và **Client Secret**
5. Paste vào `backend/.env`:
   ```env
   USE_ADOBE_PDF_API=true
   PDF_SERVICES_CLIENT_ID="your_id"
   PDF_SERVICES_CLIENT_SECRET="your_secret"
   ```
6. Restart backend
7. Test OCR endpoint → Done! 🎉

**Free tier**: 500 transactions/month

---

Need help? Check backend logs hoặc contact support!
