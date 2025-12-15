# 🚀 Adobe API - Quick Setup (2 phút)

## 1️⃣ Lấy Credentials

**Link**: https://acrobatservices.adobe.com/dc-integration-creation-app-cdn/main.html

1. Create account (Google login nhanh nhất)
2. Create project → Add "PDF Services API"
3. Chọn "OAuth Server-to-Server"
4. Copy **Client ID** và **Client Secret**

---

## 2️⃣ Cấu Hình

Edit file **`backend/.env`**:

```env
USE_ADOBE_PDF_API=true
PDF_SERVICES_CLIENT_ID="paste_client_id_here"
PDF_SERVICES_CLIENT_SECRET="paste_client_secret_here"
```

---

## 3️⃣ Restart Server

```powershell
# Backend sẽ tự động reload nếu đang chạy với --reload flag
# Hoặc restart lại:
cd backend
python -m uvicorn app.main_simple:app --reload
```

---

## 4️⃣ Test

Frontend → Upload PDF → Click "OCR PDF"

**Expected**: 
- ✅ Success → Nhận được PDF có text searchable
- ❌ Error → Check backend logs

---

## 📊 Free Tier

- **500 transactions/month** miễn phí
- Không cần credit card
- Reset đầu mỗi tháng

---

## 🔗 Full Guide

Xem chi tiết: **[ADOBE_CREDENTIALS_GUIDE.md](./ADOBE_CREDENTIALS_GUIDE.md)**

---

## ⚡ Không Muốn Dùng Adobe?

**Alternative**: Dùng Tesseract OCR (free)

1. Install Tesseract binary:
   ```powershell
   choco install tesseract
   ```

2. Download Vietnamese language data:
   - Link: https://github.com/tesseract-ocr/tessdata/blob/main/vie.traineddata
   - Copy vào: `C:\Program Files\Tesseract-OCR\tessdata\`

3. Restart backend → OCR sẽ tự động dùng Tesseract

**Quality**: 7/10 (vs Adobe 10/10) nhưng FREE và unlimited!

---

**Note**: Nếu không có Adobe credentials, system sẽ tự động fallback sang Tesseract.
