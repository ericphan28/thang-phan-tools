# 📦 BATCH DOCUMENT GENERATION - Hướng Dẫn Sử Dụng

## 🎯 Tính năng mới

**Endpoint mới:** `POST /api/v1/pdf/generate-batch`

**Chức năng:**
- ✅ Nhận 1 template + JSON array (nhiều mẫu tin)
- ✅ Generate nhiều documents cùng lúc
- ✅ **Option 1:** Merge thành 1 PDF duy nhất
- ✅ **Option 2:** Trả về ZIP chứa nhiều file PDF/DOCX

---

## 📝 API Specification

### **Endpoint:**
```
POST /api/v1/pdf/generate-batch
```

### **Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `template_file` | File | ✅ Yes | Word template (.docx) |
| `json_data` | String | ✅ Yes | JSON **array** với nhiều objects |
| `output_format` | String | No | `"pdf"` hoặc `"docx"` (default: pdf) |
| `merge_output` | Boolean | No | `true` = merge 1 PDF, `false` = ZIP nhiều files (default: false) |

### **Response:**

**If `merge_output=true`:**
- Single PDF file (merged tất cả documents)
- Headers:
  - `X-Batch-Count`: Số lượng documents đã generate
  - `X-Output-Type`: "merged"

**If `merge_output=false`:**
- ZIP file chứa nhiều PDF/DOCX
- Headers:
  - `X-Batch-Count`: Số lượng files trong ZIP
  - `X-Output-Type`: "zip"

---

## 🚀 Cách Sử Dụng

### **1. Chuẩn bị JSON Array**

**Format:**
```json
[
  { "field1": "value1", "field2": "value2" },
  { "field1": "value3", "field2": "value4" },
  { "field1": "value5", "field2": "value6" }
]
```

**Ví dụ: Thiệp khai trương cho 3 khách mời**
```json
[
  {
    "guest": {
      "name": "Ông Nguyễn Văn A",
      "title": "Giám Đốc Công ty ABC"
    },
    "business": {
      "name": "SHOWROOM ĐIỆN MÁY XANH",
      "slogan": "Uy tín - Chất lượng"
    },
    "venue": {"address": "123 Đường Láng, HN"},
    "event": {"datetime": "08:00, 30/11/2024"},
    "contact": {"phone": "0912 345 678", "email": "info@abc.vn"}
  },
  {
    "guest": {
      "name": "Bà Trần Thị Mai",
      "title": "Phó GĐ Sở Công Thương"
    },
    "business": {
      "name": "SHOWROOM ĐIỆN MÁY XANH",
      "slogan": "Uy tín - Chất lượng"
    },
    "venue": {"address": "123 Đường Láng, HN"},
    "event": {"datetime": "08:00, 30/11/2024"},
    "contact": {"phone": "0912 345 678", "email": "info@abc.vn"}
  },
  {
    "guest": {
      "name": "Ông Phạm Minh Tuấn",
      "title": "Chủ tịch Hội DNTV"
    },
    "business": {
      "name": "SHOWROOM ĐIỆN MÁY XANH",
      "slogan": "Uy tín - Chất lượng"
    },
    "venue": {"address": "123 Đường Láng, HN"},
    "event": {"datetime": "08:00, 30/11/2024"},
    "contact": {"phone": "0912 345 678", "email": "info@abc.vn"}
  }
]
```

---

### **2. Test với cURL**

**Option A: Merge thành 1 PDF**
```bash
cd d:\thang\utility-server\templates

curl -X POST "http://localhost:8000/api/v1/pdf/generate-batch" \
  -F "template_file=@thiep_khai_truong.docx" \
  -F "json_data=@thiep_khai_truong_batch.json" \
  -F "output_format=pdf" \
  -F "merge_output=true" \
  -o batch_merged.pdf
```

**Kết quả:** 1 file PDF chứa 3 thiệp (3 pages)

---

**Option B: ZIP với 3 PDF riêng biệt**
```bash
curl -X POST "http://localhost:8000/api/v1/pdf/generate-batch" \
  -F "template_file=@thiep_khai_truong.docx" \
  -F "json_data=@thiep_khai_truong_batch.json" \
  -F "output_format=pdf" \
  -F "merge_output=false" \
  -o batch_separate.zip
```

**Kết quả:** 1 file ZIP chứa 3 PDF files riêng

---

### **3. Test với Frontend**

**HTML Form:**
```html
<form method="POST" action="http://localhost:8000/api/v1/pdf/generate-batch" enctype="multipart/form-data">
  <label>Template:
    <input type="file" name="template_file" accept=".docx" required>
  </label>
  
  <label>JSON Data:
    <textarea name="json_data" rows="10" required>
[
  {"guest": {"name": "Person 1"}},
  {"guest": {"name": "Person 2"}},
  {"guest": {"name": "Person 3"}}
]
    </textarea>
  </label>
  
  <label>Output Format:
    <select name="output_format">
      <option value="pdf">PDF</option>
      <option value="docx">DOCX</option>
    </select>
  </label>
  
  <label>Merge Output:
    <input type="checkbox" name="merge_output" value="true">
    Merge into single file
  </label>
  
  <button type="submit">Generate Batch</button>
</form>
```

---

## 💡 Use Cases

### **1. Thiệp Mời Hàng Loạt**

**Scenario:** Khai trương showroom, gửi thiệp cho 50 khách VIP

**Setup:**
```json
[
  {"guest": {"name": "Khách 1", "title": "GĐ Công ty A"}, ...},
  {"guest": {"name": "Khách 2", "title": "GĐ Công ty B"}, ...},
  ... (50 items)
]
```

**Output:**
- `merge_output=true` → 1 PDF 50 pages (dễ in hàng loạt)
- `merge_output=false` → ZIP với 50 PDF riêng (gửi email cá nhân hóa)

---

### **2. Hợp Đồng Lao Động Hàng Loạt**

**Scenario:** Ký hợp đồng cho 20 nhân viên mới

**Setup:**
```json
[
  {"employee": {"fullName": "NV 1", "position": "Dev"}, ...},
  {"employee": {"fullName": "NV 2", "position": "Designer"}, ...},
  ... (20 items)
]
```

**Output:**
- `merge_output=false` → ZIP 20 hợp đồng riêng biệt
- Mỗi file tên: `NV_1_001.pdf`, `NV_2_002.pdf`, ...

---

### **3. Giấy Chứng Nhận**

**Scenario:** In 100 giấy chứng nhận hoàn thành khóa học

**Setup:**
```json
[
  {"student": {"name": "Học viên 1", "score": 95}, ...},
  {"student": {"name": "Học viên 2", "score": 88}, ...},
  ... (100 items)
]
```

**Output:**
- `merge_output=true` → 1 PDF 100 pages (gửi in ấn)
- Print tất cả cùng lúc

---

## 🎯 Batch Files Đã Tạo

### **Thiệp Khai Trương:**
📍 `thiep_khai_truong_batch.json`
- 3 khách mời khác nhau
- Cùng 1 sự kiện khai trương
- Personalized: name + title

### **Thiệp Sinh Nhật:**
📍 `thiep_sinh_nhat_batch.json`
- 3 sinh nhật: Kid (5), Adult (30), Senior (60)
- 3 địa điểm khác nhau
- 3 thời gian khác nhau

---

## 📊 Performance

### **Limits:**
- **Maximum:** 100 items per batch
- **Recommended:** 10-50 items for optimal speed
- **Adobe API:** 500 free operations/month

### **Timing:**
- Generate 10 PDFs: ~30-60 seconds
- Generate 50 PDFs: ~2-5 minutes
- Generate 100 PDFs: ~5-10 minutes

### **Tips:**
- Use `merge_output=true` for faster processing (1 API call for merge vs multiple)
- Use `merge_output=false` for personalization (separate files per person)

---

## 🔧 Advanced Examples

### **Example 1: Generate + Email**

```python
import requests
import json

# Step 1: Generate batch with separate files
response = requests.post(
    "http://localhost:8000/api/v1/pdf/generate-batch",
    files={
        "template_file": open("invitation.docx", "rb"),
        "json_data": json.dumps([
            {"guest": {"name": "Person 1", "email": "p1@email.com"}},
            {"guest": {"name": "Person 2", "email": "p2@email.com"}},
        ])
    },
    data={
        "output_format": "pdf",
        "merge_output": "false"
    }
)

# Step 2: Extract ZIP
import zipfile
import io

zip_data = io.BytesIO(response.content)
with zipfile.ZipFile(zip_data) as z:
    for filename in z.namelist():
        pdf_bytes = z.read(filename)
        # Send email with attachment
        send_email(to=..., attachment=pdf_bytes)
```

---

### **Example 2: Print Shop Integration**

```python
# Generate merged PDF for bulk printing
response = requests.post(
    "http://localhost:8000/api/v1/pdf/generate-batch",
    files={
        "template_file": open("certificate.docx", "rb"),
        "json_data": json.dumps(student_list)  # 100 students
    },
    data={
        "output_format": "pdf",
        "merge_output": "true"  # Merge for easy printing
    }
)

# Save merged PDF
with open("certificates_100_pages.pdf", "wb") as f:
    f.write(response.content)

# Send to printer
print_pdf("certificates_100_pages.pdf", copies=1, duplex=False)
```

---

## 🐛 Troubleshooting

### **Error: "JSON must be an array"**
```json
❌ Wrong: {"name": "John"}
✅ Correct: [{"name": "John"}]
```

### **Error: "Maximum 100 items per batch"**
- Split array thành nhiều batches
- Process từng batch riêng

### **Slow performance?**
- Reduce batch size (50 → 20)
- Use `merge_output=true` (faster)
- Check Adobe API quota

### **ZIP extraction error?**
- Ensure `merge_output=false`
- Check file size limits

---

## 📂 File Naming

**ZIP Files:**
- Auto-generated names based on first field in JSON
- Format: `<FirstValue>_<Index>.pdf`
- Example: `Ong_Nguyen_Van_A_001.pdf`

**Merged PDF:**
- Format: `batch_<Count>_merged.pdf`
- Example: `batch_50_merged.pdf`

---

## 🎉 Summary

✅ **New Endpoint:** `/api/v1/pdf/generate-batch`  
✅ **Input:** 1 template + JSON array  
✅ **Output:** Merged PDF hoặc ZIP with multiple files  
✅ **Max:** 100 items per batch  
✅ **Use Cases:** Invitations, Contracts, Certificates  

**Giờ bạn có thể generate hàng loạt documents chỉ với 1 API call!** 🚀

---

**Version:** 1.0  
**Last Updated:** November 26, 2025  
**Status:** ✅ Ready for Testing
