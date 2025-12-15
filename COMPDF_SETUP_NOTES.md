# 🔧 ComPDF API - Setup Notes

## ✅ Credentials Đã Có

Bạn đã có API keys từ ComPDF dashboard:

```
Public Key:  public_key_1fb69e380c8b8452c86bcf3cbe947e2e
Secret Key:  secret_key_12ef29c45538a1de93e565f22ab63dd3
```

Dashboard: https://api-dashboard.compdf.com/api/keys

---

## 📚 Tài Liệu API

- **Main Docs:** https://api.compdf.com/api-libraries/overview
- **API Reference:** https://api.compdf.com/api-reference/overview  
- **Authentication:** https://api.compdf.com/api-reference/authentication
- **Python Guide:** https://api.compdf.com/api-libraries/in-python
- **PDF to Word:** https://api.compdf.com/api-libraries/pdf-to-word

---

## 🔐 Authentication Method

ComPDF sử dụng **simple API key authentication**:

```http
x-api-key: your_public_key_here
```

Không cần JWT token như Adobe, chỉ cần pass Public Key trong header.

---

## 📦 Python SDK

ComPDF có official Python SDK:

```bash
pip install compdfkit-api-python
```

### Cách Dùng SDK (Theo Documentation):

```python
from compdfkit_api_python import CPDFClient
from compdfkit_api_python.constant import CPDFConversionEnum
from compdfkit_api_python.parameter import CPDFToWordParameter

# Create client
client = CPDFClient(public_key, secret_key)

# Create task
result = client.createTask(CPDFConversionEnum.PDF_TO_WORD)
task_id = result.getTaskId()

# Configure parameters
file_parameter = CPDFToWordParameter()
file_parameter.setIsContainAnnot("1")  # Include annotations
file_parameter.setIsContainImg("1")    # Include images
file_parameter.setIsFlowLayout("1")    # Flow layout (giữ format)

# Upload file
client.uploadFile("test.pdf", task_id, file_parameter)

# Execute
client.executeTask(task_id)

# Get result
task_info = client.getTaskInfo(task_id)
```

---

## ⚠️ Current Status

### ❌ SDK Install Issue

SDK đã được cài đặt (`pip list` shows `compdfkit-api-python 1.3.3`) nhưng không import được:

```python
>>> import compdfkit_api_python
ModuleNotFoundError: No module named 'compdfkit_api_python'
```

**Possible causes:**
1. Package structure issue (module name không match package name)
2. Installation corrupted
3. Wrong Python environment

### 🔧 Workarounds

**Option 1: Dùng REST API trực tiếp** (đang implement trong `test_compdf_api.py`)
- Không phụ thuộc vào SDK
- Full control
- Nhưng cần research endpoint structure

**Option 2: Contact ComPDF support**
- Email: support@compdf.com
- Ask về Python SDK installation issue

**Option 3: Dùng alternative API** (Adobe, Aspose, etc.)

---

## 💡 So Sánh với Adobe

| Feature | ComPDF | Adobe PDF Services |
|---------|--------|-------------------|
| **Authentication** | Simple API key | OAuth 2.0 / JWT |
| **Pricing** | ~$50/month (1000 files) | Free: 500/month, Paid: $0.05/file |
| **Quality** | Good (cần test) | Excellent (AI-powered) |
| **Python SDK** | ❌ Import issue | ✅ Works well |
| **Documentation** | OK | Excellent |
| **Support** | Email | Enterprise support |

---

## 🎯 Recommendation

### Immediate Action:

1. ✅ **Test Adobe API first** (đã có script `test_adobe_api.py`)
   - Adobe có SDK hoạt động tốt
   - Free tier 500 files/month
   - Quality proven excellent

2. ⏸️ **ComPDF - Hold for now**
   - SDK issue cần resolve
   - Có thể dùng sau khi fix SDK
   - Or implement REST API wrapper (cần time research)

3. 📧 **Contact ComPDF Support**
   - Report SDK import issue
   - Request working example code
   - Ask về REST API endpoint structure

---

## 📝 Files Created

- ✅ `test_compdf_api.py` - Demo script (REST API approach)
- ✅ `.env.example` - Updated with ComPDF credentials
- ✅ `COMPDF_SETUP_NOTES.md` - This file

---

## 🚀 Next Steps

### When SDK is Fixed:

```python
# test_compdf_api_v2.py
from compdfkit_api_python import CPDFClient

client = CPDFClient(
    "public_key_1fb69e380c8b8452c86bcf3cbe947e2e",
    "secret_key_12ef29c45538a1de93e565f22ab63dd3"
)

# Use as documented...
```

### Alternative: Use Adobe

```bash
# Test Adobe API
python test_adobe_api.py

# If quality good → integrate into backend
# Hybrid approach: simple → pdf2docx, complex → Adobe
```

---

## 📞 Support Contacts

**ComPDF:**
- Email: support@compdf.com
- Dashboard: https://api-dashboard.compdf.com

**Adobe:**
- Forum: https://community.adobe.com/
- Console: https://developer.adobe.com/console

---

*Last updated: November 22, 2025*
*Status: ComPDF credentials ready, SDK issue pending*
