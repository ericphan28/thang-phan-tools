# 🎯 TECHNOLOGY PRIORITY SYSTEM - Hướng Dẫn Sử Dụng

## 📋 Tổng Quan

Hệ thống Technology Priority cho phép **tùy chỉnh thứ tự công nghệ xử lý** cho từng operation. Mặc định, Adobe PDF Services được ưu tiên cao nhất (10/10 quality), với fallback về pypdf (7/10 quality, miễn phí).

---

## 🎨 Nguyên Tắc Thiết Kế

### ✅ Có Sẵn Rồi → Thêm Adobe Làm Primary
Các tính năng đã hoạt động tốt với pypdf/reportlab:
- **Compress PDF** 📦: pypdf (7/10) → **+ Adobe (10/10)**
- **Watermark** 💧: reportlab+pypdf (8/10) → **+ Adobe (10/10)**
- **PDF Info** 📊: pypdf (basic) → **+ Adobe (rich metadata)**
- **Protect/Unlock** 🔒: pypdf (8/10) → Giữ nguyên (đủ tốt rồi)

### 🆕 Chưa Có → Dùng Adobe Trực Tiếp
Các tính năng mới, không có thay thế local:
- **OCR PDF** 🔍: Adobe only (nhận dạng tiếng Việt)
- **Extract Content** 🔬: Adobe only (AI extraction)
- **HTML to PDF** 🌐: Adobe only (perfect rendering)

---

## ⚙️ Cấu Hình Technology Priority

### 1. Qua File `.env`

```bash
# Format: "tech1,tech2,tech3" (thứ tự ưu tiên từ trái sang phải)

# Compress PDF
COMPRESS_PRIORITY="adobe,pypdf"  # Try Adobe first, fallback pypdf

# Watermark
WATERMARK_PRIORITY="adobe,pypdf"

# PDF Info
PDF_INFO_PRIORITY="adobe,pypdf"
```

**Ví dụ configurations:**

#### Configuration 1: Adobe Priority (Best Quality) - MẶC ĐỊNH ✅
```bash
USE_ADOBE_PDF_API=true
COMPRESS_PRIORITY="adobe,pypdf"
WATERMARK_PRIORITY="adobe,pypdf"
PDF_INFO_PRIORITY="adobe,pypdf"
```
- ✅ Chất lượng tốt nhất (10/10)
- ⚠️ Sử dụng Adobe quota (500 free/month)
- ✅ Có fallback khi Adobe fail

#### Configuration 2: pypdf Priority (Save Quota)
```bash
USE_ADOBE_PDF_API=true
COMPRESS_PRIORITY="pypdf,adobe"  # Try pypdf first
WATERMARK_PRIORITY="pypdf"       # pypdf only
PDF_INFO_PRIORITY="pypdf,adobe"
```
- ✅ Tiết kiệm Adobe quota
- ✅ Vẫn dùng Adobe khi cần (pypdf fail)
- ⚠️ Chất lượng thấp hơn (7/10)

#### Configuration 3: Local Only (No Adobe)
```bash
USE_ADOBE_PDF_API=false
COMPRESS_PRIORITY="pypdf"
WATERMARK_PRIORITY="pypdf"
PDF_INFO_PRIORITY="pypdf"
```
- ✅ Miễn phí, unlimited
- ✅ Không cần internet
- ⚠️ Chất lượng 7/10
- ❌ Không có OCR, Extract, HTML→PDF

#### Configuration 4: Hybrid Strategy (Cân Bằng)
```bash
USE_ADOBE_PDF_API=true
COMPRESS_PRIORITY="adobe,pypdf"  # Adobe for critical compression
WATERMARK_PRIORITY="pypdf"       # pypdf đủ tốt cho watermark
PDF_INFO_PRIORITY="pypdf"        # pypdf nhanh hơn
```

### 2. Qua Admin API (Runtime)

#### Get Current Settings
```bash
GET /api/settings
```

Response:
```json
{
  "adobe_enabled": true,
  "technology_priorities": {
    "compress": ["adobe", "pypdf"],
    "watermark": ["adobe", "pypdf"],
    "pdf_info": ["adobe", "pypdf"]
  },
  "adobe_quota_info": {
    "monthly_limit": 500,
    "note": "Check Adobe console for real-time usage"
  }
}
```

#### Update Priority
```bash
POST /api/settings/technology-priority
Content-Type: application/json

{
  "operation": "compress",
  "priority": "pypdf,adobe"
}
```

Response:
```json
{
  "success": true,
  "message": "Updated compress priority to: pypdf,adobe",
  "note": "This change is runtime only. To make it permanent, update .env file",
  "new_priority": ["pypdf", "adobe"]
}
```

#### Reset to Default
```bash
POST /api/settings/reset-priorities
```

---

## 🔧 Backend Implementation Logic

### Hybrid Function Structure

```python
async def compress_pdf(self, input_file, quality) -> tuple[Path, str]:
    """
    Returns: (output_path, technology_used)
    """
    # 1. Get priority from settings
    priorities = settings.get_technology_priority("compress")
    # priorities = ['adobe', 'pypdf']
    
    # 2. Try each technology in order
    for tech in priorities:
        if tech == "adobe":
            if self.use_adobe and self.adobe_credentials:
                try:
                    await self._compress_pdf_adobe(...)
                    return (output_path, "adobe")  # Success!
                except:
                    continue  # Try next technology
        
        elif tech == "pypdf":
            try:
                await self._compress_pdf_local(...)
                return (output_path, "pypdf")  # Success!
            except:
                continue
    
    # 3. All failed
    raise HTTPException(500, "All compression methods failed")
```

### Key Helper Methods

```python
# In settings.py (core/config.py)

def get_technology_priority(self, operation: str) -> list[str]:
    """
    Get priority list for an operation
    >>> settings.get_technology_priority('compress')
    ['adobe', 'pypdf']
    """

def should_use_adobe_first(self, operation: str) -> bool:
    """
    Check if Adobe is first priority
    >>> settings.should_use_adobe_first('compress')
    True
    """

def get_fallback_technology(self, operation: str, failed_tech: str) -> Optional[str]:
    """
    Get next fallback after failure
    >>> settings.get_fallback_technology('compress', 'adobe')
    'pypdf'
    """
```

---

## 📊 Technology Comparison

| Operation | pypdf (Local) | Adobe (Cloud) | Recommend |
|-----------|---------------|---------------|-----------|
| **Compress PDF** | 7/10 quality<br>30-50% reduction<br>Fast | 10/10 quality<br>50-80% reduction<br>AI-powered | Adobe first |
| **Watermark** | 8/10 quality<br>Basic text watermark<br>Free | 10/10 quality<br>Advanced watermark<br>Costs quota | pypdf sufficient |
| **PDF Info** | Basic info<br>pages, size, version | Rich metadata<br>fonts, compliance, permissions | pypdf faster |
| **Protect PDF** | 8/10 quality<br>256-bit encryption | Not implemented | pypdf only |
| **Split/Merge** | 10/10 quality<br>Pure manipulation | Not needed | pypdf only |
| **OCR** | ❌ Not available | ✅ 10/10 (50+ languages) | Adobe only |
| **Extract Content** | ❌ Basic text only | ✅ AI (tables, images, fonts) | Adobe only |
| **HTML → PDF** | ❌ Not available | ✅ 10/10 rendering | Adobe only |

---

## 🎯 Recommended Strategies

### For Development/Testing
```bash
COMPRESS_PRIORITY="pypdf"           # Fast, local
WATERMARK_PRIORITY="pypdf"
PDF_INFO_PRIORITY="pypdf"
```
- ✅ Fast iteration
- ✅ No quota concerns
- ✅ Offline development

### For Production (High Quality)
```bash
COMPRESS_PRIORITY="adobe,pypdf"     # Best quality with fallback
WATERMARK_PRIORITY="adobe,pypdf"
PDF_INFO_PRIORITY="adobe,pypdf"
```
- ✅ Best user experience
- ✅ Fallback reliability
- ⚠️ Monitor Adobe quota

### For Production (Cost Optimized)
```bash
COMPRESS_PRIORITY="pypdf,adobe"     # Use Adobe only when pypdf fails
WATERMARK_PRIORITY="pypdf"          # pypdf sufficient
PDF_INFO_PRIORITY="pypdf"           # pypdf faster
```
- ✅ Save Adobe quota
- ✅ Good enough quality
- ✅ Adobe safety net

---

## 🔍 Monitoring & Debugging

### Check What Technology Was Used

API responses include `X-Technology-*` headers:

```http
HTTP/1.1 200 OK
Content-Type: application/pdf
X-Technology-Engine: adobe
X-Technology-Name: Adobe Compress PDF
X-Technology-Quality: 10/10
X-Technology-Type: cloud
```

### Frontend Display

TechnologyBadge component shows which technology was used:

```tsx
<TechnologyBadge 
  type="adobe"      // From X-Technology-Engine header
  showQuality 
/>
// Displays: 🔥 Adobe 10/10
```

### Logs

Backend logs show technology selection:

```
INFO: Trying Adobe compress for document.pdf
INFO: Adobe compression successful: document_compressed.pdf
```

or

```
WARNING: Adobe compress failed: quota exceeded, trying next technology
INFO: Using pypdf compress for document.pdf
INFO: pypdf compression successful: document_compressed.pdf
```

---

## 💡 Best Practices

### 1. Always Have Fallback
```bash
# ✅ Good - has fallback
COMPRESS_PRIORITY="adobe,pypdf"

# ⚠️ Risky - no fallback
COMPRESS_PRIORITY="adobe"
```

### 2. Monitor Adobe Quota
- Check usage: https://developer.adobe.com/console
- Set alerts at 80% usage
- Have pypdf fallback ready

### 3. Test Both Paths
```python
# Test Adobe path
await compress_pdf(file, quality="medium")

# Test fallback (disable Adobe temporarily)
settings.USE_ADOBE_PDF_API = False
await compress_pdf(file, quality="medium")
```

### 4. Document Which Tech is Best
In your code comments:
```python
# Compress: Adobe significantly better (10/10 vs 7/10)
# Watermark: pypdf sufficient (8/10), save quota
# Info: pypdf faster and sufficient
```

---

## 🚀 Deployment Checklist

### Before Production:

1. **Set Adobe Credentials**
   ```bash
   USE_ADOBE_PDF_API=true
   PDF_SERVICES_CLIENT_ID="your-client-id"
   PDF_SERVICES_CLIENT_SECRET="your-secret"
   ```

2. **Choose Priority Strategy**
   ```bash
   # For best quality:
   COMPRESS_PRIORITY="adobe,pypdf"
   
   # For cost savings:
   COMPRESS_PRIORITY="pypdf,adobe"
   ```

3. **Test Fallback**
   - Disable Adobe temporarily
   - Verify pypdf fallback works
   - Re-enable Adobe

4. **Monitor Logs**
   - Check which technology is used most
   - Adjust priorities based on usage patterns

5. **Set Up Alerts**
   - Adobe quota > 80%
   - Fallback rate > 10%
   - Error rate > 1%

---

## 📝 Examples

### Example 1: High-Quality Document for Client
```bash
# Use Adobe for best quality
POST /api/documents/pdf/compress
{
  "file": "important_contract.pdf",
  "quality": "high"
}

# Settings: COMPRESS_PRIORITY="adobe,pypdf"
# Result: Uses Adobe (10/10), beautiful compression
# Headers: X-Technology-Engine: adobe
```

### Example 2: Bulk Processing 100 Files
```bash
# Use pypdf to save quota
POST /api/documents/pdf/compress (x100)

# Settings: COMPRESS_PRIORITY="pypdf,adobe"
# Result: 100 files use pypdf (7/10), quota saved
# Only uses Adobe if pypdf fails
```

### Example 3: Adobe Quota Exhausted
```bash
# Adobe returns 429 Too Many Requests
# System automatically falls back to pypdf
# User still gets compressed file (7/10 quality)

# Logs:
# WARNING: Adobe compress failed: 429 quota exceeded
# INFO: Using pypdf compress (fallback)
# INFO: pypdf compression successful
```

---

## 🎓 Summary

**Key Takeaways:**
1. ✅ **Adobe first** = Best quality (10/10)
2. ✅ **pypdf fallback** = Reliability (always works)
3. ✅ **Configurable** = Flexible strategy per environment
4. ✅ **Transparent** = User sees which tech was used
5. ✅ **Monitored** = Logs + headers show technology path

**Default Strategy (Recommended):**
```bash
COMPRESS_PRIORITY="adobe,pypdf"
WATERMARK_PRIORITY="adobe,pypdf"
PDF_INFO_PRIORITY="adobe,pypdf"
```

**Alternative Strategy (Cost Optimized):**
```bash
COMPRESS_PRIORITY="pypdf,adobe"
WATERMARK_PRIORITY="pypdf"
PDF_INFO_PRIORITY="pypdf"
```

---

**Last Updated:** November 23, 2025  
**Author:** GitHub Copilot  
**Project:** Utility Server - Document Processing
