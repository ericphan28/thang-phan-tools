# 🎯 Quick Start: Test Adobe PDF API

## Các Bước Thực Hiện

### 1️⃣ Đăng Ký và Lấy API Key

**Truy cập:** https://developer.adobe.com/console

1. **Đăng nhập** hoặc **đăng ký** tài khoản Adobe miễn phí
2. Click **"Create new project"**
3. Trong project, click **"Add API"**
4. Chọn **"Adobe PDF Services API"**
5. Chọn authentication: **"OAuth Server-to-Server"** (recommended)
6. Copy **Client ID** và **Client Secret**

📖 **Hướng dẫn chi tiết:** Xem file `ADOBE_API_GUIDE.md`

---

### 2️⃣ Cài Đặt Dependencies

```powershell
pip install requests python-dotenv
```

---

### 3️⃣ Cấu Hình Credentials

Tạo file `.env` (copy từ `.env.example`):

```powershell
copy .env.example .env
```

Mở file `.env` và thay đổi:

```bash
ADOBE_CLIENT_ID=abc123def456...  # Thay bằng Client ID của bạn
ADOBE_CLIENT_SECRET=xyz789...     # Thay bằng Client Secret của bạn
```

⚠️ **Lưu ý:** File `.env` đã được thêm vào `.gitignore`, không lo bị commit nhầm lên Git.

---

### 4️⃣ Tạo File PDF Test (Nếu Chưa Có)

```powershell
python test_word_formatting.py
```

Script này sẽ tạo:
- `test_complex_word.docx` (Word gốc)
- `test_complex_word.pdf` (PDF để test)

---

### 5️⃣ Chạy Demo Adobe API

```powershell
python test_adobe_api.py
```

Kết quả mong đợi:
```
============================================================
📄 ADOBE PDF SERVICES API - DEMO SCRIPT
============================================================

✅ Client ID: abc123def456...
✅ Client Secret: ********************

============================================================
🚀 ADOBE PDF TO WORD CONVERSION
============================================================
Input:  test_complex_word.pdf
Output: test_adobe_output.docx

🔐 Đang lấy access token từ Adobe...
✅ Access token đã lấy thành công (expires in 24.0h)
📤 Đang upload file: test_complex_word.pdf...
✅ Upload thành công! Asset ID: urn:aaid:AS:UE1:23c3...
🔄 Đang chuyển đổi PDF sang Word...
✅ Chuyển đổi thành công! Asset ID: urn:aaid:AS:UE1:45d6...
⬇️  Đang download file: test_adobe_output.docx...
✅ Download thành công: test_adobe_output.docx (42,567 bytes)

============================================================
🎉 HOÀN THÀNH!
============================================================
✅ File Word đã được tạo: test_adobe_output.docx
📊 Kích thước: 42,567 bytes

🎯 So sánh kết quả:
   1. File gốc:  test_complex_word.docx
   2. PDF:       test_complex_word.pdf
   3. Adobe out: test_adobe_output.docx

   Mở 3 files để so sánh chất lượng!
```

---

### 6️⃣ So Sánh Kết Quả

Bây giờ bạn có 3 files để so sánh:

| File | Mô tả |
|------|-------|
| `test_complex_word.docx` | Word gốc (100% định dạng) |
| `test_complex_word.pdf` | PDF trung gian (converted bởi Gotenberg) |
| `test_adobe_output.docx` | Word từ Adobe API (PDF → Word) |

**Mở cả 3 files** và so sánh:
- ✅ Fonts có giống nhau không?
- ✅ Colors có chính xác không?
- ✅ Tables có bị lệch không?
- ✅ Lists có đúng format không?
- ✅ Tiếng Việt có hiển thị đúng không?

---

## 🔧 Troubleshooting

### Lỗi: "THIẾU CREDENTIALS!"
→ Bạn chưa tạo file `.env` hoặc chưa điền credentials.

**Giải pháp:**
```powershell
copy .env.example .env
# Sau đó mở .env và điền ADOBE_CLIENT_ID và ADOBE_CLIENT_SECRET
```

### Lỗi: "Không tìm thấy file test: test_complex_word.pdf"
→ Chạy lệnh tạo file test trước:
```powershell
python test_word_formatting.py
```

### Lỗi: "401 Unauthorized"
→ Client ID hoặc Client Secret không đúng.

**Giải pháp:**
1. Kiểm tra lại credentials trong `.env`
2. Truy cập https://developer.adobe.com/console
3. Vào project → Credentials → Copy lại Client ID và Secret

### Lỗi: "429 Too Many Requests"
→ Vượt quá rate limit của Free Tier.

**Giải pháp:**
- Chờ 1-2 phút rồi thử lại
- Free tier có giới hạn requests/giây

### Lỗi: "Monthly Transaction Limit Exceeded"
→ Đã dùng hết 500 transactions miễn phí trong tháng.

**Giải pháp:**
- Chờ đến đầu tháng sau (reset tự động)
- Hoặc upgrade lên paid plan

---

## 📊 So Sánh Chất Lượng

Sau khi test xong, bạn có thể đánh giá:

### Adobe PDF Services API vs pdf2docx (hiện tại)

| Tiêu chí | pdf2docx | Adobe API |
|----------|----------|-----------|
| **Fonts** | Thường thay đổi | Giữ nguyên tốt |
| **Colors** | Đôi khi sai màu | Chính xác cao |
| **Tables** | Hay bị lệch | Layout chuẩn |
| **Lists** | Mất format | Giữ nguyên |
| **Images** | OK | Excellent |
| **Vietnamese** | OK | Perfect |
| **Complex layouts** | ⚠️ Hay lỗi | ✅ Xử lý tốt |

---

## 💰 Cost Analysis

### Free Tier: 500 transactions/tháng

Ví dụ traffic của bạn:
- 10 users/ngày × 2 PDF to Word/user = 20 conversions/ngày
- 20 × 30 ngày = **600 conversions/tháng**
- → **Cần paid plan** hoặc hybrid approach

### Hybrid Approach (Tiết kiệm nhất):

```python
# Pseudocode
async def smart_convert(pdf_file):
    if is_simple_pdf(pdf_file):
        # Simple PDF → dùng pdf2docx (free)
        return await pdf2docx_convert(pdf_file)
    else:
        # Complex PDF → dùng Adobe (chính xác hơn)
        return await adobe_convert(pdf_file)
```

**Kết quả:**
- 70% files simple → pdf2docx (free)
- 30% files complex → Adobe (180 transactions/tháng)
- → **Vẫn trong Free Tier!** ✅

---

## 🚀 Next Steps

Nếu Adobe API chất lượng tốt hơn:

1. ✅ Tích hợp vào `backend/app/services/document_service.py`
2. ✅ Thêm config toggle: `USE_ADOBE_API=true/false`
3. ✅ Implement hybrid logic (simple → pdf2docx, complex → Adobe)
4. ✅ Monitor usage tại Adobe Console
5. ✅ Set up alerts khi gần hết quota (450/500)

---

## 📚 Tài Liệu Liên Quan

1. 📖 `ADOBE_API_GUIDE.md` - Hướng dẫn chi tiết lấy API key
2. 📖 `PDF_TO_WORD_ANALYSIS.md` - So sánh các giải pháp
3. 🐍 `test_adobe_api.py` - Script demo
4. 🔧 `.env.example` - Template config

---

**Good luck! 🎉**

Nếu có vấn đề, hãy check file `ADOBE_API_GUIDE.md` hoặc hỏi tôi!
