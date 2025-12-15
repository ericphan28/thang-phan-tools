# 🎨 HƯỚNG DẪN TẠO WORD TEMPLATE CHUYÊN NGHIỆP 100%

## ❌ VẤN ĐỀ HIỆN TẠI

Output của chúng ta **THIẾU CHUYÊN NGHIỆP** vì:

1. ❌ Không có ảnh 4x6
2. ❌ Font chữ không đúng
3. ❌ Line spacing bị thay đổi
4. ❌ Bold/Italic bị mất
5. ❌ Table borders không đúng
6. ❌ Paragraph alignment sai
7. ❌ Page margins khác

**NGUYÊN NHÂN:** Dùng python-docx để tạo template TỰ ĐỘNG làm **MẤT FORMAT**!

---

## ✅ GIẢI PHÁP CHUYÊN NGHIỆP

### 🎯 Phương pháp: **MANUAL TEMPLATE với docxtpl**

**Ý tưởng:**
1. Mở file gốc trong **Microsoft Word** (không dùng code!)
2. Replace text → `{{ variables }}` **THỦ CÔNG** (giữ format 100%)
3. Save template
4. Dùng `docxtpl` để render data

**Kết quả:** Giữ **100% format gốc**! 🎉

---

## 📋 HƯỚNG DẪN CHI TIẾT

### BƯỚC 1: MỞ FILE GỐC

```
File: Mau-ly-lich-2C-TCTW-98.docx
→ Double-click để mở trong Microsoft Word
```

### BƯỚC 2: REPLACE TEXT → JINJA2 VARIABLES

**Tìm và thay thế (Ctrl+H):**

| TÌM | THAY BẰNG |
|-----|----------|
| `Tỉnh: ..............................` | `Tỉnh: {{ tinh }}` |
| `Họ và tên: ..........................` | `Họ và tên: {{ ho_ten }}` |
| `Sinh ngày: ... tháng: ... năm: ...` | `Sinh ngày: {{ ngay }} tháng: {{ thang }} năm: {{ nam }}` |
| `Quê quán: ..........................` | `Quê quán: {{ que_quan }}` |

**💡 MẸO:** 
- Giữ nguyên **font, size, color** của text xung quanh
- Chỉ replace phần dấu chấm `...` thành `{{ variable }}`
- **KHÔNG** copy-paste từ file khác (sẽ mất format)

### BƯỚC 3: XỬ LÝ BẢNG (QUAN TRỌNG!)

**🔴 SAI (Phương pháp cũ):**
```
Thay toàn bộ nội dung cell bằng:
{% for edu in dao_tao %}{{ edu.ten_truong }}{% endfor %}
```
→ Phá vỡ cấu trúc bảng!

**✅ ĐÚNG (Phương pháp {% tr %}):**

1. Trong bảng "Đào tạo", **select toàn bộ data row** (row thứ 2)
2. **Trước row**, thêm dòng:
   ```
   {% tr for edu in dao_tao %}
   ```
3. **Trong các cells**, replace:
   - Cell 1: `{{ edu.ten_truong }}`
   - Cell 2: `{{ edu.nganh_hoc }}`
   - Cell 3: `{{ edu.thoi_gian }}`
   - Cell 4: `{{ edu.hinh_thuc }}`
   - Cell 5: `{{ edu.van_bang }}`
4. **Sau row**, thêm dòng:
   ```
   {% endtr %}
   ```

**Kết quả:**
```
┌─────────────────────────────────────────┐
│ Tên trường | Ngành học | ... (header)  │
├─────────────────────────────────────────┤
│ {% tr for edu in dao_tao %}             │  ← Thêm dòng này
│ {{ edu.ten_truong }} | {{ edu.nganh_hoc }} | ... │
│ {% endtr %}                             │  ← Thêm dòng này
└─────────────────────────────────────────┘
```

**💡 LỢI ÍCH {% tr %}:**
- Tự động **duplicate row** với đúng format
- Giữ nguyên borders, shading, cell width
- Giữ nguyên font, alignment

### BƯỚC 4: XỬ LÝ ẢNH 4x6

**Cách 1: Placeholder trong template**

1. Trong Word, click vào ô ảnh 4x6
2. **Insert** → **Picture** → Chọn ảnh bất kỳ (placeholder)
3. Resize ảnh: **4cm × 6cm**
4. Right-click ảnh → **Size and Position**
   - Width: 4 cm
   - Height: 6 cm
   - Lock aspect ratio: ❌ (uncheck)
5. Right-click → **Edit Alt Text**
   - Description: `{{ anh_4x6 }}`

**Cách 2: Code insert ảnh**

```python
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Cm

doc = DocxTemplate("template.docx")

context = {
    "anh_4x6": InlineImage(
        doc, 
        "photo.jpg",
        width=Cm(4),
        height=Cm(6)
    )
}
```

### BƯỚC 5: XỬ LÝ TEXT ĐẶC BIỆT (Bold, Italic, Color)

**Nếu cần text có format đặc biệt trong data:**

```python
from docxtpl import RichText
from docx.shared import Pt, RGBColor

context = {
    "chuc_vu": RichText(
        "Chuyên viên",
        bold=True,
        size=Pt(12)
    ),
    
    "phong_ban": RichText(
        "Phòng Nội vụ",
        italic=True,
        color=RGBColor(255, 0, 0)  # Red
    )
}
```

### BƯỚC 6: SAVE TEMPLATE

```
File → Save As → mau_2c_template_MANUAL.docx
```

**⚠️ QUAN TRỌNG:**
- Save ở format `.docx` (không phải `.doc`)
- Kiểm tra lại tất cả `{{ variables }}`
- Đảm bảo không có lỗi syntax Jinja2

---

## 🔧 CODE RENDER TEMPLATE

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render template thủ công với docxtpl"""

from docxtpl import DocxTemplate, RichText, InlineImage
from docx.shared import Cm, Pt
from pathlib import Path
import json

# 1. Load template (đã tạo thủ công)
template_path = Path("mau_2c_template_MANUAL.docx")
doc = DocxTemplate(template_path)

# 2. Load JSON data
with open("mau_2c_DATA_RESTRUCTURED.json", 'r', encoding='utf-8') as f:
    context = json.load(f)

# 3. Thêm ảnh (nếu có)
# context['anh_4x6'] = InlineImage(doc, "photo.jpg", width=Cm(4))

# 4. Thêm RichText (nếu cần)
# context['chuc_vu_bold'] = RichText(context['chuc_vu'], bold=True)

# 5. Render
doc.render(context)

# 6. Save
output_path = Path("OUTPUT_PROFESSIONAL.docx")
doc.save(str(output_path))

print(f"✅ Đã tạo: {output_path}")
print(f"📊 Size: {output_path.stat().st_size:,} bytes")
```

---

## 📊 SO SÁNH 2 PHƯƠNG PHÁP

| Tiêu chí | Tự động (python-docx) | Thủ công (docxtpl) |
|----------|----------------------|-------------------|
| **Font** | ❌ Có thể thay đổi | ✅ Giữ 100% |
| **Spacing** | ❌ Có thể sai | ✅ Giữ 100% |
| **Borders** | ❌ Có thể mất | ✅ Giữ 100% |
| **Images** | ❌ Khó thêm | ✅ Dễ dàng |
| **Bold/Italic** | ❌ Có thể mất | ✅ Giữ 100% |
| **Table layout** | ❌ Có thể phá | ✅ Giữ 100% |
| **Thời gian setup** | ⏱️ 5 phút (code) | ⏱️ 45 phút (manual) |
| **Kết quả** | ⭐⭐ (70%) | ⭐⭐⭐⭐⭐ (100%) |

---

## 🎯 EXAMPLE: BẢNG GIA ĐÌNH

**Trong Word template (thủ công):**

```
a) Về bản thân: Bố, Mẹ, Vợ (chồng), các con, anh chị em ruột

┌──────────┬──────────────┬─────────┬─────────────────────┐
│ Quan hệ  │ Họ và tên    │ Năm sinh│ Quê quán, nghề...   │
├──────────┼──────────────┼─────────┼─────────────────────┤
│ {% tr for member in bo_me %}                             │
│ Bố, mẹ   │ {{ member.ho_ten }} │ {{ member.nam_sinh }} │ {{ member.thong_tin }} │
│ {% endtr %}                                              │
│ ..........│              │         │                     │
│ {% tr for member in vo_chong %}                          │
│ Vợ       │ {{ member.ho_ten }} │ {{ member.nam_sinh }} │ {{ member.thong_tin }} │
│ Chồng    │              │         │                     │
│ {% endtr %}                                              │
│          │              │         │                     │
│ {% tr for child in cac_con %}                            │
│ Các con: │ {{ child.ho_ten }} │ {{ child.nam_sinh }} │ {{ child.thong_tin }} │
│ {% endtr %}                                              │
│          │              │         │                     │
│ {% tr for sib in anh_chi_em %}                           │
│ Anh chị  │ {{ sib.ho_ten }} │ {{ sib.nam_sinh }} │ {{ sib.thong_tin }} │
│ em ruột  │              │         │                     │
│ {% endtr %}                                              │
└──────────┴──────────────┴─────────┴─────────────────────┘
```

**⚠️ LƯU Ý với {% tr %}:**
- Phải đặt `{% tr %}` và `{% endtr %}` **NGOÀI** table cells
- Hoặc dùng comment trong Word: `{# tr for ... #}` ... `{# endtr #}`
- Hoặc tốt nhất: Dùng 1 row template, docxtpl sẽ tự duplicate

---

## 💡 TIPS & TRICKS

### 1. Debug Jinja2 trong Word

Nếu gặp lỗi, thêm:
```jinja2
{%p if debug %}
Variables: {{ debug_vars }}
{%p endif %}
```

### 2. Conditional formatting

```jinja2
{% if gender == 'Nam' %}Anh{% else %}Chị{% endif %} {{ ho_ten }}
```

### 3. Date formatting

```python
from datetime import datetime

context['ngay_hom_nay'] = datetime.now().strftime("%d/%m/%Y")
```

### 4. Table có header cố định

```
┌─────────────────────────────────┐
│ Header row (không {% tr %})     │  ← Giữ nguyên
├─────────────────────────────────┤
│ {% tr for item in items %}      │
│ Data row với {{ variables }}    │  ← Sẽ bị duplicate
│ {% endtr %}                     │
└─────────────────────────────────┘
```

---

## 🚀 HÀNH ĐỘNG TIẾP THEO

### ✅ TODO:

1. **MỞ FILE GỐC**
   ```
   Mau-ly-lich-2C-TCTW-98.docx
   ```

2. **REPLACE THỦ CÔNG** (30-45 phút)
   - Tất cả text fields
   - Tất cả bảng với {% tr %}
   - Thêm ảnh placeholder

3. **SAVE TEMPLATE**
   ```
   mau_2c_template_MANUAL.docx
   ```

4. **TEST**
   ```bash
   python test_manual_template.py
   ```

5. **SO SÁNH**
   - Mở OUTPUT_PROFESSIONAL.docx
   - Mở Mau-ly-lich-2C-TCTW-98.docx
   - Compare side-by-side
   - Format phải giống 100%!

---

## 📚 TÀI LIỆU THAM KHẢO

- **docxtpl docs:** https://docxtpl.readthedocs.io/
- **Jinja2 docs:** https://jinja.palletsprojects.com/
- **python-docx docs:** https://python-docx.readthedocs.io/

---

## ⏰ THỜI GIAN ƯỚC TÍNH

| Task | Time |
|------|------|
| Tạo template thủ công | 45 phút |
| Test + debug | 15 phút |
| Hoàn thiện | 15 phút |
| **TỔNG** | **~75 phút** |

**💰 GIÁ TRỊ:**
- 1 lần làm đúng → Dùng mãi mãi
- Format CHUYÊN NGHIỆP 100%
- Không phải sửa formatting sau này

---

**🎯 KẾT QUẢ CUỐI CÙNG:**

✅ Word document với format **GIỐNG 100%** file gốc  
✅ Tất cả fonts, colors, spacing **ĐÚNG**  
✅ Tables, borders **HOÀN HẢO**  
✅ Images **ĐÚNG SIZE**  
✅ **CHUYÊN NGHIỆP TỚI 100%!** 🎉

---

**Ngày:** 2024-01-24  
**Version:** PROFESSIONAL GUIDE v1.0
