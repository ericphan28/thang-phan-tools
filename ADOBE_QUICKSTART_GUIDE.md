# 🚀 Adobe PDF Services - Quick Start Guide

## 🌟 Tổng Quan

Project đã tích hợp **Adobe PDF Services API** để cung cấp các tính năng xử lý PDF cao cấp với chất lượng 10/10.

### ✨ Tính Năng Mới

#### 1. 🔍 OCR - Nhận Dạng Chữ Thông Minh
- **Khả năng**: Convert PDF scan thành PDF searchable
- **Ngôn ngữ**: 50+ languages (Vietnamese ✅, English, Japanese, Korean, Chinese...)
- **Chất lượng**: 10/10 - AI-powered accuracy
- **Use cases**: 
  - Digitize tài liệu giấy scan
  - Make old documents searchable
  - Process scanned invoices/contracts

#### 2. 🔬 Smart Extract - Trích Xuất Nội Dung AI
- **Khả năng**: AI extraction of tables, images, text with metadata
- **Output**:
  - 📊 **Tables** → Structured Excel-ready data (cells, rows, columns)
  - 🖼️ **Images** → PNG files with width, height, page number
  - 📝 **Text** → Font information (bold, italic, size, family, color)
  - 🏗️ **Structure** → Headings, paragraphs, lists, reading order
- **Use cases**:
  - Extract financial data from reports
  - Convert PDF catalogs to database
  - Data mining from documents

#### 3. 🌐 HTML to PDF - Perfect Rendering
- **Khả năng**: Chrome-quality HTML rendering
- **Features**:
  - Full CSS3 support
  - JavaScript execution
  - Custom page sizes (A4, Letter, Legal, A3)
  - Portrait/Landscape orientation
- **Use cases**:
  - Generate invoices from templates
  - Create certificates/diplomas
  - Export web dashboards to PDF

#### 4. 🎯 Hybrid Processing
Các tính năng có cả local + Adobe versions:

| Feature | Adobe (10/10) | Local Tool (7-8/10) | Strategy |
|---------|---------------|---------------------|----------|
| Compress | ✅ Adobe API | pypdf | Try Adobe first, fallback pypdf |
| Watermark | ✅ Adobe API | pypdf+reportlab | Try Adobe first, fallback pypdf |
| PDF Info | ✅ Adobe API | pypdf | Try Adobe first, fallback pypdf |

---

## 🔧 Setup Instructions

### Step 1: Get Adobe Credentials (Free!)

1. **Đăng ký tài khoản**:
   - Visit: https://developer.adobe.com/document-services/apis/pdf-services/
   - Click "Get started" → Sign in with Adobe ID
   - Free tier: **500 transactions/month**

2. **Tạo Project**:
   - Dashboard → "Create new project"
   - Choose "PDF Services API"
   - Download credentials: `pdfservices-api-credentials.json`

3. **Lấy thông tin**:
   ```json
   {
     "client_credentials": {
       "client_id": "abc123...",
       "client_secret": "p8e-xyz..."
     }
   }
   ```

### Step 2: Configure Backend

**Option A: Using credentials file (Recommended)**
```bash
cd backend
# Copy credentials file vào thư mục backend
cp ~/Downloads/pdfservices-api-credentials.json .
```

Backend sẽ tự động đọc file này.

**Option B: Using environment variables**
```bash
# Edit backend/.env
USE_ADOBE_PDF_API=true
ADOBE_CLIENT_ID=abc123...
ADOBE_CLIENT_SECRET=p8e-xyz...
```

### Step 3: Configure Technology Priority

Edit `backend/.env`:

```bash
# Adobe-first strategy (default - recommended)
COMPRESS_PRIORITY=adobe,pypdf      # Try Adobe (10/10), fallback pypdf (7/10)
WATERMARK_PRIORITY=adobe,pypdf     # Try Adobe (10/10), fallback pypdf (8/10)
PDF_INFO_PRIORITY=adobe,pypdf      # Try Adobe first

# Or local-first strategy (if you want to save quota)
# COMPRESS_PRIORITY=pypdf,adobe
# WATERMARK_PRIORITY=pypdf,adobe
```

### Step 4: Restart Backend

```powershell
# Stop backend (Ctrl+C)
# Start again
cd backend
python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000
```

Check logs:
```
INFO:     Adobe PDF Services: ✅ Enabled (Client ID: abc1****)
INFO:     Technology Priority - Compress: ['adobe', 'pypdf']
INFO:     Technology Priority - Watermark: ['adobe', 'pypdf']
```

---

## 🎮 Usage Guide

### Frontend - Settings Panel

1. **Mở Settings Tab**:
   - Frontend: http://localhost:5173
   - Click tab **"⚙️ Settings"**

2. **Xem Adobe Status**:
   - ☁️ Enabled/Disabled
   - 📊 Quota usage: X/500 transactions

3. **Thay đổi Priority**:
   - View current priorities (Compress, Watermark, PDF Info)
   - Click "↑" để move technology lên trên (higher priority)
   - Click "Reset to Defaults" để về mặc định

4. **Xem Available Technologies**:
   - Adobe PDF Services: Cloud, 10/10 quality
   - pypdf: Local, 7/10 quality (compress), 8/10 (watermark)
   - Gotenberg: Local, 9/10 quality (Office → PDF)
   - pdfplumber: Local, 8/10 quality (PDF → Excel)

### Frontend - Adobe AI Features

#### 1. 🔍 OCR PDF

**Steps:**
1. Upload PDF scan (có chữ viết tay hoặc in)
2. Click **"🔍 OCR PDF"** (purple gradient button)
3. Modal hiện ra:
   - Select language: 🇻🇳 Tiếng Việt, 🇺🇸 English, 🇯🇵 Japanese...
4. Click **"Bắt Đầu OCR"**
5. Download PDF có thể search được

**Example Vietnamese:**
```
Input:  scan_invoice.pdf (ảnh chụp hóa đơn)
Output: scan_invoice_ocr.pdf (có thể Ctrl+F search text)
```

#### 2. 🔬 Extract Content

**Steps:**
1. Upload PDF (financial report, catalog, etc.)
2. Click **"🔬 Extract Content"** (indigo gradient button)
3. Modal hiện ra:
   - Select type:
     - 📚 **All** - Toàn bộ (text, tables, images)
     - 📝 **Text Only** - Chỉ text với font info
     - 📊 **Tables Only** - Chỉ bảng biểu
     - 🖼️ **Images Only** - Chỉ hình ảnh
4. Click **"Trích Xuất"**
5. Nhận JSON response với structured data

**Example JSON Response:**
```json
{
  "success": true,
  "data": {
    "text": [
      {
        "text": "Financial Report 2024",
        "font": {"family": "Arial", "size": 24, "bold": true},
        "bounds": [100, 150, 400, 180]
      }
    ],
    "tables": [
      {
        "cells": [[["Q1", "Sales"], ["$1M", "$2M"]]],
        "rows": 2,
        "columns": 2,
        "data": [["Q1", "Sales"], ["$1M", "$2M"]]
      }
    ],
    "images": [
      {
        "path": "/tmp/image_0.png",
        "width": 800,
        "height": 600,
        "page": 1
      }
    ]
  },
  "technology": {"engine": "adobe", "quality": "10/10"},
  "summary": {
    "text_elements": 125,
    "tables": 3,
    "images": 5
  }
}
```

#### 3. 🌐 HTML to PDF

**Steps:**
1. Click **"🌐 HTML → PDF"** (green gradient button)
2. Modal hiện ra:
   - **HTML Content**: Paste your HTML
   - **Page Size**: A4, Letter, Legal, A3
   - **Orientation**: Portrait / Landscape
3. Click **"Convert to PDF"**
4. Download perfect PDF

**Example HTML Invoice:**
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body {
      font-family: Arial;
      margin: 40px;
    }
    .invoice-header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 30px;
      border-radius: 10px;
    }
    .invoice-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }
    .invoice-table th,
    .invoice-table td {
      border: 1px solid #ddd;
      padding: 12px;
      text-align: left;
    }
    .total {
      font-size: 24px;
      font-weight: bold;
      color: #667eea;
    }
  </style>
</head>
<body>
  <div class="invoice-header">
    <h1>HÓA ĐƠN #2024-001</h1>
    <p>Ngày: 23/11/2024</p>
  </div>

  <h2>Thông Tin Khách Hàng</h2>
  <p><strong>Tên:</strong> Công ty ABC</p>
  <p><strong>Địa chỉ:</strong> 123 Nguyễn Huệ, Q1, TP.HCM</p>

  <table class="invoice-table">
    <thead>
      <tr>
        <th>Sản Phẩm</th>
        <th>Số Lượng</th>
        <th>Đơn Giá</th>
        <th>Thành Tiền</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Adobe PDF API License</td>
        <td>1</td>
        <td>1,000,000đ</td>
        <td>1,000,000đ</td>
      </tr>
      <tr>
        <td>Support Package</td>
        <td>1</td>
        <td>500,000đ</td>
        <td>500,000đ</td>
      </tr>
    </tbody>
  </table>

  <p class="total">Tổng Cộng: 1,500,000đ</p>

  <p style="margin-top: 40px; font-style: italic;">
    Cảm ơn quý khách đã sử dụng dịch vụ!
  </p>
</body>
</html>
```

Result: Beautiful invoice with gradient header, styled table → Professional PDF!

#### 4. 📦 Compress PDF (Hybrid)

**Automatic fallback:**
1. Upload large PDF
2. Click **"📦 Nén PDF"**
3. Backend tries Adobe first (10/10 quality)
4. If Adobe fails/quota exceeded → Auto fallback to pypdf (7/10)
5. Response headers show which technology was used:
   ```
   X-Technology-Engine: adobe
   X-Technology-Quality: 10/10
   X-Technology-Type: cloud
   ```

#### 5. 🖨️ Watermark PDF (Hybrid)

**Automatic fallback:**
1. Upload PDF
2. Click **"🖨️ Thêm Watermark"**
3. Enter watermark text
4. Backend tries Adobe → fallback pypdf
5. Response headers show technology used

---

## 📊 API Usage Examples

### 1. OCR PDF (curl)

```bash
curl -X POST "http://localhost:8000/api/documents/pdf/ocr" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@scan_document.pdf" \
  -F "language=vi-VN" \
  --output ocr_result.pdf

# Check technology used
curl -I "http://localhost:8000/api/documents/pdf/ocr" \
  ... \
  | grep X-Technology
# X-Technology-Engine: adobe
# X-Technology-Quality: 10/10
```

### 2. Extract Content (Python)

```python
import requests

# Upload PDF
with open('financial_report.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/documents/pdf/extract-content',
        files={'file': f},
        data={'extract_type': 'tables'}
    )

result = response.json()

# Access extracted tables
for table in result['data']['tables']:
    print(f"Table with {table['rows']} rows, {table['columns']} columns")
    print(f"Data: {table['data']}")
    
    # Convert to pandas DataFrame
    import pandas as pd
    df = pd.DataFrame(table['data'][1:], columns=table['data'][0])
    df.to_excel('extracted_table.xlsx', index=False)
```

### 3. HTML to PDF (JavaScript)

```javascript
const formData = new FormData();
formData.append('html_content', `
  <!DOCTYPE html>
  <html>
    <head>
      <style>
        body { font-family: Arial; padding: 20px; }
        h1 { color: #667eea; }
      </style>
    </head>
    <body>
      <h1>My Report</h1>
      <p>Generated on ${new Date().toLocaleDateString()}</p>
    </body>
  </html>
`);
formData.append('page_size', 'A4');
formData.append('orientation', 'portrait');

const response = await fetch('http://localhost:8000/api/documents/convert/html-to-pdf', {
  method: 'POST',
  body: formData
});

const blob = await response.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'report.pdf';
a.click();
```

### 4. Compress with Priority Check (Python)

```python
import requests

# Compress PDF
response = requests.post(
    'http://localhost:8000/api/documents/pdf/compress',
    files={'file': open('large.pdf', 'rb')},
    data={'quality': 'medium'}
)

# Check which technology was used
tech_engine = response.headers.get('X-Technology-Engine')
tech_quality = response.headers.get('X-Technology-Quality')

print(f"Compressed using: {tech_engine} (Quality: {tech_quality})")
# Output: Compressed using: adobe (Quality: 10/10)
# or: Compressed using: pypdf (Quality: 7/10)

# Save result
with open('compressed.pdf', 'wb') as f:
    f.write(response.content)
```

---

## 🔍 Admin API - Settings Management

### Get Current Settings

```bash
curl http://localhost:8000/api/settings

# Response:
{
  "adobe_enabled": true,
  "adobe_quota_used": 125,
  "adobe_quota_limit": 500,
  "priorities": {
    "compress": ["adobe", "pypdf"],
    "watermark": ["adobe", "pypdf"],
    "pdf_info": ["adobe", "pypdf"]
  }
}
```

### Update Technology Priority

```bash
# Switch compress to local-first
curl -X POST "http://localhost:8000/api/settings/technology-priority" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "compress",
    "priority": ["pypdf", "adobe"]
  }'

# Response:
{
  "success": true,
  "operation": "compress",
  "old_priority": ["adobe", "pypdf"],
  "new_priority": ["pypdf", "adobe"]
}
```

### Get Available Technologies

```bash
curl http://localhost:8000/api/settings/available-technologies

# Response:
[
  {
    "name": "adobe",
    "display_name": "Adobe PDF Services",
    "type": "cloud",
    "quality_rating": "10/10",
    "capabilities": ["compress", "watermark", "ocr", "extract", "html-to-pdf"]
  },
  {
    "name": "pypdf",
    "display_name": "pypdf",
    "type": "local",
    "quality_rating": "7/10 (compress), 8/10 (watermark)",
    "capabilities": ["compress", "watermark", "merge", "split", "rotate"]
  },
  ...
]
```

### Reset Priorities to Defaults

```bash
curl -X POST "http://localhost:8000/api/settings/reset-priorities"

# Response:
{
  "success": true,
  "priorities": {
    "compress": ["adobe", "pypdf"],
    "watermark": ["adobe", "pypdf"],
    "pdf_info": ["adobe", "pypdf"]
  }
}
```

---

## 📈 Quota Management

### Monitor Usage

```python
import requests

settings = requests.get('http://localhost:8000/api/settings').json()

used = settings['adobe_quota_used']
limit = settings['adobe_quota_limit']
remaining = limit - used

print(f"Adobe Quota: {used}/{limit} ({remaining} remaining)")

if remaining < 50:
    print("⚠️ Warning: Low quota! Consider switching to local-first")
    # Update priority
    requests.post('http://localhost:8000/api/settings/technology-priority', json={
        'operation': 'compress',
        'priority': ['pypdf', 'adobe']  # Local first
    })
```

### Best Practices

1. **Development**: Use Adobe-first for testing quality
2. **Production**: 
   - High-priority documents → Adobe
   - Bulk processing → Local-first
3. **Monitor quota daily**
4. **Set alerts at 400/500 transactions**

---

## 🎯 Decision Guide: Adobe vs Local

### Use Adobe When:
- ✅ Need OCR (no local alternative)
- ✅ Need AI extraction (tables, images with metadata)
- ✅ Need Chrome-quality HTML rendering
- ✅ Quality > Speed (10/10 vs 7/10)
- ✅ Processing important documents (contracts, reports)
- ✅ Have quota available (<500/month)

### Use Local When:
- ✅ Batch processing (100+ files)
- ✅ Offline requirement
- ✅ Budget-constrained (no API costs)
- ✅ Speed > Quality
- ✅ Internal documents (not customer-facing)
- ✅ Adobe quota exhausted

### Hybrid Strategy (Recommended):
```bash
# .env configuration
COMPRESS_PRIORITY=adobe,pypdf     # Try best quality first
WATERMARK_PRIORITY=pypdf,adobe    # Use free local for watermark
PDF_INFO_PRIORITY=pypdf,adobe     # Info extraction is fast locally

# Result:
# - OCR: Always Adobe (no choice)
# - Extract: Always Adobe (no choice)  
# - HTML→PDF: Always Adobe (much better than alternatives)
# - Compress: Adobe first, auto-fallback
# - Watermark: Local first (save quota), Adobe if needed
# - Info: Local first (faster)
```

---

## 🐛 Troubleshooting

### Issue: Adobe features not working

**Check 1: Credentials**
```bash
# View backend logs
# Look for:
INFO:     Adobe PDF Services: ✅ Enabled (Client ID: abc1****)

# If you see:
WARNING:  Adobe PDF Services: ❌ Disabled (credentials not found)

# Fix: Check credentials file or env variables
ls backend/pdfservices-api-credentials.json
cat backend/.env | grep ADOBE
```

**Check 2: Network**
```bash
# Test Adobe API connectivity
curl -v https://pdf-services.adobe.io/

# Should return 401 (expected - means API is reachable)
# If timeout → Check firewall/proxy
```

**Check 3: Quota**
```bash
# Check quota
curl http://localhost:8000/api/settings | jq '.adobe_quota_used'

# If >= 500 → Quota exhausted
# Fix: Wait for monthly reset or upgrade plan
```

### Issue: Fallback not working

**Check priority configuration:**
```bash
curl http://localhost:8000/api/settings | jq '.priorities'

# Should show:
{
  "compress": ["adobe", "pypdf"],  # ✅ Correct
  "watermark": ["adobe"]           # ❌ Missing fallback!
}

# Fix: Add fallback
curl -X POST http://localhost:8000/api/settings/technology-priority \
  -H "Content-Type: application/json" \
  -d '{"operation": "watermark", "priority": ["adobe", "pypdf"]}'
```

### Issue: OCR Vietnamese not accurate

**Tips:**
1. Use high-resolution scans (300 DPI minimum)
2. Ensure good contrast
3. Check language selector: 🇻🇳 **vi-VN** not vi or vie
4. For mixed languages, try OCR separately

### Issue: Extract returns empty tables

**Common causes:**
1. PDF has image-based tables (not selectable text)
   - Solution: OCR first, then extract
2. Complex merged cells
   - Solution: Use `extract_type=all` to get raw data
3. Table spans multiple pages
   - Solution: Each page extracted separately

---

## 📚 Additional Resources

- **Adobe Documentation**: https://developer.adobe.com/document-services/docs/
- **API Reference**: http://localhost:8000/docs (when backend running)
- **Frontend Guide**: See `QUICKSTART.md`
- **Technology Comparison**: See `TECHNOLOGY_PRIORITY_GUIDE.md`

---

## 💡 Pro Tips

1. **Save Quota**: Use local-first for bulk, Adobe for quality
2. **Monitor Daily**: Set up quota alerts
3. **Test Locally**: Use local tools during development
4. **Cache Results**: Don't re-process same file
5. **Batch Operations**: Group similar tasks
6. **Error Handling**: Always check response headers for technology used
7. **Settings Panel**: Bookmark http://localhost:5173 → Settings tab

---

## 🎉 Success!

You're now ready to use Adobe AI-powered PDF features!

**Next Steps:**
1. ✅ Configure Adobe credentials
2. ✅ Test OCR with Vietnamese document
3. ✅ Extract tables from financial report
4. ✅ Generate HTML invoice → PDF
5. ✅ Monitor quota usage in Settings panel

Happy Processing! 🚀
