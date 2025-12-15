# ✅ TỔNG KẾT - MẪU 2C-TCTW-98 SƠ YẾU LÝ LỊCH

## 📁 CÁC FILE QUAN TRỌNG

### ⭐ FILE CHO BẠN:
```
1. mau_2c_TEMPLATE_DE_EDIT.docx     ← MỞ FILE NÀY trong Word
2. README_TAO_TEMPLATE.md           ← ĐỌC hướng dẫn ở đây
3. HUONG_DAN_TAO_TEMPLATE.txt       ← Chi tiết 60+ replacements
4. mau_2c_DATA_FULL.json            ← JSON mẫu để test
5. test_with_new_template.py        ← Script test sau khi xong
```

### 📦 File hỗ trợ:
- `mau_2c_simple.json` - JSON đơn giản (chỉ fields cơ bản)
- `test_2c_correct.pdf` - Output thử nghiệm (159KB)

---

## 🎯 HƯỚNG DẪN NHANH (3 BƯỚC)

### 1️⃣ Mở Word
```
File → Open → mau_2c_TEMPLATE_DE_EDIT.docx
```

### 2️⃣ Find & Replace (Ctrl+H)
Làm theo file `HUONG_DAN_TAO_TEMPLATE.txt`:
- **60+ replacements** cho các field cơ bản
- **5 bảng** cần sửa cẩn thận

**LƯU Ý QUAN TRỌNG:**
- ✅ CHỈ thay dấu chấm (...) bằng {{variables}}
- ✅ GIỮ NGUYÊN mọi text khác
- ✅ GIỮ NGUYÊN "Bố, mẹ", "Vợ", "Chồng" trong bảng
- ✅ GIỮ NGUYÊN định dạng, font, spacing

### 3️⃣ Lưu & Test
```bash
# Lưu thành: mau_2c_template_final.docx

# Test:
cd templates
python test_with_new_template.py
```

---

## 🔧 VÍ DỤ THAY THẾ

### Thay field đơn giản:
```
Tìm: Tỉnh: …………………
Thay: Tỉnh: {{tinh}}
```

### Thay trong bảng (với loop):
```
Bảng Đào tạo, hàng 2:
Cột 1: ................ → {{#dao_tao}}{{ten_truong}}{{/dao_tao}}
Cột 2: ................ → {{#dao_tao}}{{nganh_hoc}}{{/dao_tao}}
```

---

## 📊 CẤU TRÚC JSON

File `mau_2c_DATA_FULL.json` có:

**Fields đơn (60+ fields):**
```json
{
  "tinh": "Bình Dương",
  "ho_ten": "Nguyễn Văn An",
  "ngay": "15",
  "thang": "08",
  "nam": "1997",
  ...
}
```

**Arrays cho bảng:**
```json
{
  "dao_tao": [
    {
      "ten_truong": "Đại học Luật TP.HCM",
      "nganh_hoc": "Luật Kinh tế",
      "thoi_gian": "2015 - 2019",
      "hinh_thuc": "Chính quy",
      "van_bang": "Cử nhân Luật"
    }
  ],
  
  "cong_tac": [...],
  "gia_dinh": [...],
  "gia_dinh_vo_chong": [...],
  "luong": [...]
}
```

---

## ❓ TẠI SAO PHẢI TỰ TAY?

### ❌ Auto script SAI vì:
1. Xóa mất labels trong bảng ("Bố, mẹ", "Vợ", "Chồng")
2. Không giữ được định dạng chính xác
3. Thay thế sai vị trí
4. Không xử lý được bảng phức tạp

### ✅ Tự tay ĐÚNG vì:
1. Kiểm soát 100%
2. Thấy ngay lỗi
3. Giữ nguyên format
4. Chỉ mất 30 phút!

---

## 🆘 NẾU GẶP VẤN ĐỀ

### 1. Không biết thay thế gì?
→ Xem file `HUONG_DAN_TAO_TEMPLATE.txt`

### 2. Bảng bị lỗi?
→ **KHÔNG XÓA** text có sẵn ("Bố, mẹ", "Vợ"...), chỉ thay dấu chấm

### 3. Test lỗi?
→ Check:
- Có đủ `{{` và `}}` không?
- Loop có đúng `{{#array}}...{{/array}}` không?
- Variable name có đúng với JSON không?

### 4. Vẫn không được?
→ Gửi file cho tôi xem!

---

## 🎉 SAU KHI XONG

Bạn sẽ có:
```
✅ mau_2c_template_final.docx  ← Template chuẩn, dùng được
✅ mau_2c_DATA_FULL.json       ← JSON mẫu test
✅ OUTPUT_MAU_2C_FINAL.pdf     ← PDF đã generate
```

Có thể dùng với:
- **Single mode:** 1 cán bộ
- **Batch mode:** 10, 50, 100 cán bộ cùng lúc!

---

## 📚 ADOBE DOCUMENT GENERATION SYNTAX

Tham khảo thêm:
- Variable: `{{field_name}}`
- Loop: `{{#array}}{{item_field}}{{/array}}`
- Condition: `{{#if_condition}}text{{/if_condition}}`
- Else: `{{#if_condition}}yes{{/if_condition}}{{^if_condition}}no{{/if_condition}}`

---

**Made with ❤️ by AI Assistant**
**Date: 2025-11-26**
