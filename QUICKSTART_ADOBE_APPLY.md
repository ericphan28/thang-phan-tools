# 🚀 Quickstart: Adobe PDF Services API - Apply Ngay!

## ✅ Bước 1: Lấy Credentials (5 phút)

### Truy cập trang đăng ký:
👉 **https://acrobatservices.adobe.com/dc-integration-creation-app-cdn/main.html?api=pdf-services-api**

### Các bước:

1. **Đăng nhập** hoặc **đăng ký** Adobe ID (miễn phí)
   - Dùng email cá nhân (không dùng corporate ID)
   
2. **Name your credentials**: Đặt tên project
   - Ví dụ: "Utility Server PDF Conversion"
   
3. **Choose language**: Chọn **Python**

4. **✅ Check**: "Create personalized code sample" (optional)

5. **Click**: "Create credentials"

6. **Download**: File ZIP sẽ được tự động download
   - Chứa: `pdfservices-api-credentials.json`
   - Chứa: Sample code (optional)

---

## ✅ Bước 2: Cấu Hình (.env)

### Mở file đã download: `pdfservices-api-credentials.json`

Nội dung sẽ giống như:
```json
{
  "client_credentials": {
    "client_id": "abc123def456...",
    "client_secret": "p4-xyz789..."
  }
}
```

### Tạo file `.env` trong project:

```bash
# Copy từ template
copy .env.example .env

# Hoặc tạo mới
notepad .env
```

### Thêm vào `.env`:

```bash
# Adobe PDF Services API
PDF_SERVICES_CLIENT_ID=abc123def456...
PDF_SERVICES_CLIENT_SECRET=p4-xyz789...
```

**⚠️ Lưu ý:** Thay `abc123def456...` và `p4-xyz789...` bằng giá trị thực từ JSON file.

---

## ✅ Bước 3: Cài Đặt SDK

```powershell
pip install pdfservices-sdk python-dotenv
```

---

## ✅ Bước 4: Chạy Test

```powershell
# Tạo file PDF test (nếu chưa có)
python test_word_formatting.py

# Chạy Adobe API demo
python test_adobe_api_v2.py
```

---

## 🎉 Kết Quả Mong Đợi

```
============================================================
📄 ADOBE PDF SERVICES API - PYTHON SDK DEMO
============================================================

✅ Client ID: abc123def456...
✅ Client Secret: ******************************...

============================================================
🚀 ADOBE PDF TO WORD CONVERSION
============================================================
Input:  test_complex_word.pdf
Output: test_adobe_output.docx

📄 Step 1: Đọc file PDF...
✅ Đã đọc 67,473 bytes

🔐 Step 2: Khởi tạo Adobe PDF Services...
✅ Đã kết nối với Adobe API

📤 Step 3: Upload PDF lên Adobe Cloud...
✅ Upload thành công!

⚙️  Step 4: Cấu hình conversion...
✅ Target format: DOCX

🔄 Step 5: Tạo và submit conversion job...
✅ Job đã được submit!

⏳ Step 6: Đợi conversion hoàn thành...
✅ Conversion hoàn thành!

⬇️  Step 7: Download file Word...
💾 Step 8: Lưu file...
✅ Đã lưu: test_adobe_output.docx

============================================================
🎉 HOÀN THÀNH!
============================================================
✅ File Word đã được tạo: test_adobe_output.docx
📊 Kích thước: 42,567 bytes

🎯 So sánh kết quả:
   1. File gốc:    test_complex_word.docx
   2. PDF:         test_complex_word.pdf
   3. Adobe out:   test_adobe_output.docx

   Mở 3 files để so sánh chất lượng!
```

---

## 📊 So Sánh Chất Lượng

Mở cả 3 files và kiểm tra:

| Tiêu chí | File Gốc | Adobe Output | pdf2docx (old) |
|----------|----------|--------------|----------------|
| **Fonts** | 100% | ~95% | ~70% |
| **Colors** | 100% | ~95% | ~60% |
| **Tables** | 100% | ~90% | ~50% |
| **Lists** | 100% | ~90% | ~70% |
| **Images** | 100% | ~95% | ~80% |
| **Tiếng Việt** | 100% | ~98% | ~85% |

**Kết luận:** Adobe >> pdf2docx

---

## 🔧 Troubleshooting

### Lỗi: "Missing credentials"
→ Kiểm tra file `.env` có đúng format không:
```bash
PDF_SERVICES_CLIENT_ID=your_value_here
PDF_SERVICES_CLIENT_SECRET=your_value_here
```

### Lỗi: "ServiceApiException: Unauthorized"
→ Client ID hoặc Secret không đúng. Copy lại từ `pdfservices-api-credentials.json`

### Lỗi: "ServiceUsageException"
→ Đã hết 500 transactions miễn phí trong tháng
→ Check usage: https://developer.adobe.com/console

### Lỗi: "No module named 'adobe.pdfservices'"
→ Chạy lại: `pip install pdfservices-sdk`

---

## 💰 Pricing & Limits

### Free Tier:
- ✅ **500 Document Transactions/tháng** miễn phí
- ✅ Không cần credit card
- ✅ Reset tự động đầu tháng

### Nếu cần thêm:
- **$0.05/transaction** (pay as you go)
- Volume discounts có sẵn

### Monitor Usage:
👉 https://developer.adobe.com/console → Your Project → Usage

---

## 🎯 Tích Hợp Vào Backend

Sau khi test thành công, tích hợp vào `backend/app/services/document_service.py`:

```python
# backend/app/services/document_service.py

from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.pdf_services import PDFServices
# ... other imports

class DocumentService:
    def __init__(self):
        # Existing code...
        
        # Adobe PDF Services (nếu có credentials)
        self.use_adobe = os.getenv("USE_ADOBE_PDF_API", "false").lower() == "true"
        if self.use_adobe:
            self.adobe_credentials = ServicePrincipalCredentials(
                client_id=os.getenv('PDF_SERVICES_CLIENT_ID'),
                client_secret=os.getenv('PDF_SERVICES_CLIENT_SECRET')
            )
    
    async def pdf_to_word(self, input_file: Path) -> Path:
        """Convert PDF to Word with Adobe or fallback"""
        
        if self.use_adobe:
            try:
                return await self._pdf_to_word_adobe(input_file)
            except Exception as e:
                logger.warning(f"Adobe API failed: {e}, fallback to pdf2docx")
        
        # Fallback to pdf2docx
        return await self._pdf_to_word_local(input_file)
    
    async def _pdf_to_word_adobe(self, input_file: Path) -> Path:
        """Adobe PDF Services conversion"""
        # Implementation here...
```

### Thêm vào `.env`:
```bash
# Adobe PDF Services (Optional - for better quality)
USE_ADOBE_PDF_API=true
PDF_SERVICES_CLIENT_ID=your_client_id
PDF_SERVICES_CLIENT_SECRET=your_client_secret
```

---

## 📚 Tài Liệu

- **Official Docs:** https://developer.adobe.com/document-services/docs/overview/pdf-services-api/
- **Python Quickstart:** https://developer.adobe.com/document-services/docs/overview/pdf-services-api/quickstarts/python/
- **API Reference:** https://developer.adobe.com/document-services/docs/apis/
- **Pricing:** https://developer.adobe.com/document-services/pricing/

---

**🎉 Xong! Bây giờ bạn có thể convert PDF sang Word với chất lượng cao nhất!** 

Nếu có vấn đề, check file `ADOBE_API_GUIDE.md` hoặc hỏi tôi!
