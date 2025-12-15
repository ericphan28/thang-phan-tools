# 📦 Hướng Dẫn Sử Dụng Batch Mode

## ✨ Tính Năng Mới

Đã thêm **Batch Mode** vào Document Generation - cho phép tạo nhiều tài liệu cùng lúc từ 1 template!

## 🎯 2 Chế Độ

### 📄 Single Document Mode (Mặc định)
- Tạo **1 tài liệu** từ **1 JSON object**
- Upload file: `sample1.json`, `sample2.json`
- JSON format: `{...}`

### 📦 Batch Generation Mode (Mới!)
- Tạo **nhiều tài liệu** từ **1 JSON array**
- Upload file: `batch.json`
- JSON format: `[{...}, {...}, {...}]`
- Tối đa: **100 bản ghi** mỗi batch

---

## 🚀 Cách Sử Dụng Batch Mode

### Bước 1: Chọn Mode
Click nút **"📦 Batch Generation"** ở đầu form

### Bước 2: Upload Template
Upload file Word template (ví dụ: `thiep_khai_truong.docx`)

### Bước 3: Upload JSON
**Chọn 1 trong 2 cách:**

**Cách 1: Upload file JSON**
- Click "Upload JSON File"
- Chọn file batch: `thiep_khai_truong_batch.json`
- Hệ thống sẽ hiển thị số bản ghi: "📊 Số lượng bản ghi: 5"

**Cách 2: Nhập JSON thủ công**
```json
[
  {
    "guest": {"name": "Ông A", "title": "Giám Đốc"},
    "business": {"name": "ABC Corp"}
  },
  {
    "guest": {"name": "Bà B", "title": "Phó Giám Đốc"},
    "business": {"name": "XYZ Ltd"}
  }
]
```

### Bước 4: Chọn Output Options

#### ✅ Option 1: Gộp thành 1 PDF
- ☑️ Check "🔗 Gộp tất cả thành 1 file PDF"
- Kết quả: 1 file PDF với nhiều trang (1 trang = 1 bản ghi)
- File tải về: `batch_5_merged.pdf`
- **Use case:** Gửi in hàng loạt, xem preview toàn bộ

#### ❌ Option 2: File riêng lẻ (ZIP)
- ☐ Uncheck merge option
- Kết quả: 1 file ZIP chứa nhiều PDF riêng
- File tải về: `batch_5_files.zip`
- **Use case:** Gửi email cá nhân, phân phối riêng lẻ

### Bước 5: Chọn Định Dạng
- **PDF** (khuyến nghị cho batch): Hỗ trợ merge
- **DOCX**: Không hỗ trợ merge (chỉ trả về ZIP)

### Bước 6: Generate
Click nút **"Tạo 5 Tài Liệu"**

---

## 📋 Ví Dụ Thực Tế

### Ví Dụ 1: Thiệp Mời Khai Trương (5 khách VIP)

**File template:** `thiep_khai_truong.docx`

**File JSON:** `thiep_khai_truong_batch.json`
```json
[
  {"guest": {"name": "Ông Nguyễn Văn A", ...}},
  {"guest": {"name": "Bà Trần Thị Mai", ...}},
  {"guest": {"name": "Ông Phạm Minh Tuấn", ...}},
  {"guest": {"name": "Bà Lê Thu Hương", ...}},
  {"guest": {"name": "Ông Hoàng Minh Đức", ...}}
]
```

**Chọn merge = true:**
- Tải về: `batch_5_merged.pdf` (606KB)
- Mở file → 5 trang, mỗi trang 1 thiệp với tên khách khác nhau
- Gửi qua email → In hàng loạt tại tiệm

**Chọn merge = false:**
- Tải về: `batch_5_files.zip` (1.16MB)
- Giải nén → 5 file PDF riêng:
  - `Ong_Nguyen_Van_A_001.pdf`
  - `Ba_Tran_Thi_Mai_002.pdf`
  - `Ong_Pham_Minh_Tuan_003.pdf`
  - `Ba_Le_Thu_Huong_004.pdf`
  - `Ong_Hoang_Minh_Duc_005.pdf`
- Gửi email cá nhân cho từng khách

---

### Ví Dụ 2: Thiệp Sinh Nhật (3 người)

**File:** `thiep_sinh_nhat_batch.json`
```json
[
  {"celebrant": {"name": "Bé Minh An", "age": "5"}},
  {"celebrant": {"name": "Ms. Sarah", "age": "30"}},
  {"celebrant": {"name": "Ông Hải", "age": "60"}}
]
```

**Kết quả:** 
- Merge: 1 PDF 3 trang
- ZIP: 3 PDF riêng

---

### Ví Dụ 3: Hợp Đồng Lao Động (10 nhân viên mới)

**Scenario:** Công ty tuyển 10 nhân viên, cần tạo 10 hợp đồng

**JSON:** `employees_batch.json` (10 records)

**Options:**
- Format: **PDF**
- Merge: **Không check** ❌

**Kết quả:**
- `batch_10_files.zip` chứa 10 hợp đồng PDF riêng
- Mỗi nhân viên nhận hợp đồng riêng của mình
- Dễ quản lý, ký số, lưu trữ

---

## ⚠️ Lưu Ý Quan Trọng

### ✅ Batch Mode Accepts:
```json
[
  {"name": "A"},
  {"name": "B"}
]
```
✅ Array of objects

### ❌ Single Mode Accepts:
```json
{"name": "A"}
```
✅ Single object

### 🚫 Lỗi Thường Gặp:

**Lỗi 1:** Upload `batch.json` khi đang ở Single Mode
```
❌ Single mode yêu cầu JSON phải là object {...}, không phải array
```
**Fix:** Chuyển sang Batch Mode hoặc dùng file `sample1.json`

**Lỗi 2:** Upload `sample1.json` khi đang ở Batch Mode
```
❌ Batch mode yêu cầu JSON phải là mảng [...]
```
**Fix:** Chuyển sang Single Mode hoặc dùng file `batch.json`

**Lỗi 3:** Quá nhiều bản ghi
```
❌ Tối đa 100 bản ghi mỗi batch
```
**Fix:** Chia nhỏ JSON thành nhiều batch

---

## 📊 So Sánh 2 Chế Độ

| Tính năng | Single Mode | Batch Mode |
|-----------|-------------|------------|
| **JSON format** | Object `{...}` | Array `[...]` |
| **Số tài liệu** | 1 | 1-100 |
| **File JSON** | `sample1.json` | `batch.json` |
| **Output options** | PDF hoặc DOCX | PDF merge, ZIP, hoặc DOCX ZIP |
| **Use case** | 1 hợp đồng, 1 thiệp | Nhiều thiệp, nhiều hợp đồng |

---

## 🎓 Tips & Tricks

### 💡 Tip 1: Preview trước khi batch
1. Chọn Single Mode
2. Upload template + 1 object từ array
3. Generate để xem kết quả
4. Nếu OK → Chuyển sang Batch Mode

### 💡 Tip 2: Filename thông minh
Hệ thống tự động đặt tên file dựa trên field đầu tiên trong JSON:
```json
{"guest": {"name": "Ông A"}}
```
→ File: `Ong_A_001.pdf`

### 💡 Tip 3: Quản lý file batch
Tạo thư mục riêng cho mỗi loại batch:
```
templates/
├── batch_khai_truong/
│   ├── thiep_khai_truong_batch.json
│   └── guests_vip.json
├── batch_sinh_nhat/
│   └── birthdays_november.json
└── batch_hop_dong/
    └── new_employees_2024.json
```

---

## 🔍 Troubleshooting

### Vấn đề: File ZIP tải về bị lỗi
**Nguyên nhân:** Browser cache
**Fix:** Xóa cache hoặc dùng Incognito mode

### Vấn đề: Merge không hoạt động
**Kiểm tra:**
1. ✅ Batch Mode đã bật?
2. ✅ Format = PDF?
3. ✅ Checkbox merge đã tick?

### Vấn đề: Thiếu dữ liệu trong output
**Kiểm tra:**
1. Template có đúng {{variable}} không?
2. JSON có đủ fields không?
3. Thử Single Mode với 1 record trước

---

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra console (F12) xem có lỗi không
2. Thử với file mẫu trước: `thiep_khai_truong_batch.json`
3. Đảm bảo backend đang chạy: `http://localhost:8000`

---

## ✅ Checklist Sử Dụng

- [ ] Đã chuyển sang Batch Mode
- [ ] Đã upload template .docx
- [ ] Đã upload hoặc nhập JSON array
- [ ] Thấy số bản ghi hiển thị đúng
- [ ] Đã chọn merge/ZIP option
- [ ] Đã chọn format (PDF/DOCX)
- [ ] Click "Tạo X Tài Liệu"
- [ ] Chờ processing (có thể mất 10-30s với batch lớn)
- [ ] Tải file về thành công
- [ ] Kiểm tra quality output

---

**🎉 Chúc bạn sử dụng Batch Mode hiệu quả!**
