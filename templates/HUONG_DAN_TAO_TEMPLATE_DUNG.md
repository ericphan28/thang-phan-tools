# 🎯 HƯỚNG DẪN TẠO MAILMERGE TEMPLATE ĐÚNG CÁCH

## ❌ VẤN ĐỀ

Script Python tạo MergeField **SAI FORMAT** → mailmerge không đọc được → Output có `«field»` thay vì data thật

## ✅ GIẢI PHÁP: TẠO THỦ CÔNG TRONG WORD (15-20 PHÚT)

### Bước 1: Mở File Gốc

```
File: mau-nha-nuoc/Mau-ly-lich-2C-TCTW-98.docx
```

Mở trong Microsoft Word (không dùng LibreOffice/Google Docs - không work!)

---

### Bước 2: Bật Field Codes

Bấm: **Alt + F9** để xem field codes  
(Hoặc: File → Options → Advanced → Show field codes instead of their values)

---

### Bước 3: Thêm MergeField

#### Ví dụ: Thay "Tỉnh: ............."

**Cách 1 - Dùng Menu (dễ nhất):**

1. Đặt con trỏ **SAU CHỮ "Tỉnh:"** (giữa dấu hai chấm và dấu chấm)
2. Xóa dấu chấm: `Tỉnh: .............` → `Tỉnh: `
3. Bấm: **Insert → Quick Parts → Field...**
4. Trong Field names: Chọn **MergeField**
5. Field name: Nhập `tinh`
6. Click **OK**

**Kết quả:** Sẽ thấy `Tỉnh: <<tinh>>`

**Cách 2 - Dùng Shortcut (nhanh hơn):**

1. Đặt con trỏ vào vị trí cần thay
2. Bấm: **Ctrl + F9** (tạo field brackets)
3. Thấy `{ }` xuất hiện
4. Gõ vào giữa: `MERGEFIELD tinh`
5. Kết quả: `{ MERGEFIELD tinh }`
6. Bấm **Alt + F9** để toggle → Sẽ thấy `<<tinh>>`

---

### Bước 4: Danh Sách FULL 110 Fields

#### **Header Info (3 fields):**
```
Tỉnh: ...................     → tinh
Đơn vị trực thuộc: .......    → don_vi_truc_thuoc
Đơn vị cơ sở: ..............  → don_vi_co_so
```

#### **Personal Info (15 fields):**
```
Họ và tên khai sinh: .......  → ho_ten
Nam, nữ: ...................  → gioi_tinh
Sinh ngày: .. tháng: .. năm:  → ngay, thang, nam (3 fields riêng)
Các tên gọi khác: ...........  → ten_goi_khac
Nơi sinh: ...................  → noi_sinh
Quê quán (xã): ..............  → que_quan_xa
         (huyện): ...........  → que_quan_huyen
         (tỉnh): ............  → que_quan_tinh
Nơi ở hiện nay: .............  → noi_o_hien_nay
đ/thoại: ....................  → dien_thoai
Dân tộc: ....................  → dan_toc
Tôn giáo: ...................  → ton_giao
```

#### **Education & Party (12 fields):**
```
Trình độ giáo dục: ..........  → trinh_do_giao_duc
Trình độ chuyên môn: ........  → trinh_do_chuyen_mon
Học hàm, học vị: ............  → hoc_ham_hoc_vi
Lý luận chính trị: ..........  → ly_luan_chinh_tri
Ngoại ngữ: ..................  → ngoai_ngu
Tin học: ....................  → trinh_do_tin_hoc
Ngày vào Đảng: .. / .. / ..   → ngay_vao_dang
Ngày chính thức: .. / .. / .. → ngay_chinh_thuc
Ngày nhập ngũ: .. / .. / ..   → ngay_nhap_ngu
Ngày xuất ngũ: .. / .. / ..   → ngay_xuat_ngu
Quân hàm: ...................  → quan_ham
```

#### **Current Position (8 fields):**
```
Cấp ủy hiện tại: ............  → cap_uy_hien_tai
Cấp ủy kiêm: ................  → cap_uy_kiem
Chức vụ: ....................  → chuc_vu
Phụ cấp chức vụ: ............  → phu_cap_chuc_vu
Phụ cấp khác: ...............  → phu_cap_khac
Ngạch, bậc, lương: ..........  → ngach_bac_luong
Ngày bổ nhiệm: .. / .. / ..   → ngay_bo_nhiem
```

#### **Tables - CHỈ CẦN 3 FIELDS CHO TABLE HEADERS:**

**Table 1 - Học tập (5 columns):**
```
Thời gian  | Trường, khóa học | Hình thức | Văn bằng | Ghi chú
thoi_gian  | truong_hoc       | hinh_thuc | van_bang | ghi_chu
```

**Table 2 - Công tác (5 columns):**
```
Thời gian  | Đơn vị công tác | Chức vụ | ...
thoi_gian  | don_vi          | chuc_vu | ...
```

**Table 3 - Gia đình (4 columns):**
```
Quan hệ | Họ và tên | Năm sinh | Quê quán, nghề nghiệp
quan_he | ho_ten    | nam_sinh | thong_tin
```

---

### Bước 5: TRICK NHANH - Sử dụng Find & Replace

**Thay vì làm từng field thủ công, dùng trick này:**

1. **Bật Field Codes:** Alt + F9

2. **Find & Replace (Ctrl + H):**
   - Find: `Tỉnh: \.{3,}`  (regex: tìm "Tỉnh: ..." với 3+ dấu chấm)
   - Replace: `Tỉnh: ^d MERGEFIELD tinh ^d`
   - Click **More >> → Use wildcards** ✅
   
   **LƯU Ý:** `^d` = field delimiter (Ctrl+F9)

3. **Nhưng cách này PHỨC TẠP** → Khuyên dùng Insert Field thủ công!

---

### Bước 6: Test Template

1. Save file as: `mau_2c_MANUAL_TEMPLATE.docx`

2. Test với Python:
```python
from mailmerge import MailMerge

doc = MailMerge('mau_2c_MANUAL_TEMPLATE.docx')
print(doc.get_merge_fields())  # Phải thấy {'tinh', 'ho_ten', ...}
```

Nếu thấy **nhiều fields** → Success! ✅

---

### Bước 7: Render với Data

```python
from mailmerge import MailMerge
import json

# Load
doc = MailMerge('mau_2c_MANUAL_TEMPLATE.docx')
with open('mau_2c_DATA_RESTRUCTURED.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Merge simple fields
simple_fields = {k: v for k, v in data.items() if not isinstance(v, list)}
doc.merge(**simple_fields)

# Merge tables
if 'hoc_tap' in data:
    doc.merge_rows('thoi_gian', data['hoc_tap'])

if 'cong_tac' in data:
    doc.merge_rows('thoi_gian', data['cong_tac'])

# Save
doc.write('OUTPUT_FINAL.docx')
```

---

## ⏱️ THỜI GIAN ƯỚC TÍNH

- **Setup:** 2 phút (mở Word, bật field codes)
- **Add 50 fields:** 10-15 phút (dùng Insert Field, copy/paste pattern)
- **Test:** 2 phút
- **Total:** **15-20 phút**

---

## 🎯 TẠI SAO PHẢI THỦ CÔNG?

Python **KHÔNG THỂ** tạo MergeField đúng format vì:
1. Word dùng **complex XML structure** với namespaces đặc biệt
2. MergeField có **internal IDs** và **relationships** phức tạp
3. python-docx **KHÔNG HỖ TRỢ** tạo MergeField (chỉ hỗ trợ đọc)

**Giải pháp duy nhất:** Tạo trong Word → Let Word handle XML!

---

## 💡 TIPS

1. **Dùng Ctrl+F9 + Copy/Paste:**
   - Tạo 1 MergeField: `{ MERGEFIELD tinh }`
   - Copy cả field
   - Paste vào chỗ khác
   - Sửa tên field

2. **Test ngay sau khi tạo 5-10 fields:**
   ```python
   doc = MailMerge('template.docx')
   print(len(doc.get_merge_fields()))  # Should increase
   ```

3. **Backup file trước khi làm:**
   ```
   Copy: Mau-ly-lich-2C-TCTW-98.docx
   → Mau-ly-lich-2C-TCTW-98-BACKUP.docx
   ```

4. **Làm theo sections:**
   - Header info (5 phút)
   - Personal info (5 phút)
   - Education/Party (5 phút)
   - Tables (5 phút)

---

## ✅ KẾT QUẢ MONG ĐỢI

Sau khi làm xong:
- ✅ File có 50-100 MergeFields
- ✅ `doc.get_merge_fields()` return set lớn
- ✅ Render ra OUTPUT_FINAL.docx **GIỐNG NGUYÊN GỐC 100%**
- ✅ Format perfect: Font, bold, italic, spacing, borders

---

## 🚀 SAU KHI XONG

Deploy lên backend:
```python
# Backend chỉ cần 5 dòng!
doc = MailMerge('mau_2c_MANUAL_TEMPLATE.docx')
doc.merge(**data)
doc.merge_rows('thoi_gian', data['hoc_tap'])
doc.merge_rows('thoi_gian', data['cong_tac'])
doc.write(output_path)
```

**SIMPLE & PERFECT!** ✅

---

**Created:** November 27, 2025  
**Status:** READY TO IMPLEMENT  
**Time Required:** 15-20 minutes  
**Difficulty:** Easy (just tedious)

🎯 **LÀM NGAY!**
