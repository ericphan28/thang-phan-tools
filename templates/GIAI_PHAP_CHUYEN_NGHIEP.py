#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIẢI PHÁP CHUYÊN NGHIỆP: Sử dụng python-docx-template với RichText
Để giữ TOÀN BỘ formatting của template gốc
"""

from docxtpl import DocxTemplate, RichText, InlineImage
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pathlib import Path
import json

print("=" * 80)
print("🎨 GIẢI PHÁP CHUYÊN NGHIỆP - GIỮ 100% FORMATTING")
print("=" * 80)

# Ý TƯỞNG:
# Thay vì tạo template từ file gốc (làm mất format)
# → Tạo template THẬT bằng cách:
#   1. Mở file gốc trong Word
#   2. Replace text bằng {{ variable }} THỦ CÔNG
#   3. Giữ nguyên 100% format, font, spacing, borders

print("""
📋 HƯỚNG DẪN TẠO TEMPLATE CHUYÊN NGHIỆP:

BƯỚC 1: MỞ FILE GỐC TRONG WORD
   - Mở: Mau-ly-lich-2C-TCTW-98.docx
   - Không dùng script tự động!

BƯỚC 2: REPLACE TEXT → JINJA2 VARIABLES (THỦ CÔNG)
   
   Ví dụ trong file gốc:
   
   "Tỉnh: .........................................."
   → "Tỉnh: {{ tinh }}"
   
   "Họ và tên: ......................................"
   → "Họ và tên: {{ ho_ten }}"
   
   "Năm sinh: ........."
   → "Năm sinh: {{ nam_sinh }}"

BƯỚC 3: XỬ LÝ BẢNG (QUAN TRỌNG!)
   
   Trong bảng "Đào tạo", thay vì:
   "......................................................."
   
   → Gõ:
   ```
   {% tr for edu in dao_tao %}
   {{ edu.ten_truong }}
   {{ edu.nganh_hoc }}
   {{ edu.thoi_gian }}
   {{ edu.hinh_thuc }}
   {{ edu.van_bang }}
   {% endtr %}
   ```
   
   ⚠️ CHÚ Ý: Dùng {% tr %} để DUPLICATE ROW, không phá format!

BƯỚC 4: XỬ LÝ ẢNH
   
   Ô ảnh 4x6:
   → Insert → Picture → Placeholder image
   → Resize đúng 4x6 cm
   → Right-click → Edit Alt Text → Description: "{{ image_placeholder }}"
   
   Hoặc dùng InlineImage trong code:
   ```python
   context['anh_4x6'] = InlineImage(doc, 'photo.jpg', width=Inches(1.57))
   ```

BƯỚC 5: LƯU TEMPLATE
   - Save as: mau_2c_template_MANUAL.docx
   - Đây là template CHUẨN, giữ 100% format!

""")

print("=" * 80)
print("💡 SO SÁNH 2 PHƯƠNG PHÁP:")
print("=" * 80)

print("""
❌ PHƯƠNG PHÁP CŨ (Tự động):
   1. Đọc file gốc bằng python-docx
   2. Replace text tự động
   3. Save template mới
   
   VẤN ĐỀ:
   - Mất font formatting
   - Mất paragraph spacing
   - Mất borders, styles
   - Mất images
   → Kết quả: KHÔNG CHUYÊN NGHIỆP!

✅ PHƯƠNG PHÁP MỚI (Thủ công + docxtpl):
   1. Mở file gốc trong Word
   2. Replace text thủ công bằng {{ variables }}
   3. Giữ NGUYÊN 100% format gốc
   4. Save template
   5. Dùng docxtpl render
   
   ƯU ĐIỂM:
   - Giữ 100% font, size, color
   - Giữ 100% spacing, alignment
   - Giữ 100% borders, styles
   - Có thể insert images
   → Kết quả: CHUYÊN NGHIỆP 100%!
""")

print("=" * 80)
print("🔧 CODE MẪU - RENDER VỚI RICHTEXT:")
print("=" * 80)

code_example = '''
from docxtpl import DocxTemplate, RichText, InlineImage
from docx.shared import Inches, Pt

# Load template (đã tạo thủ công)
doc = DocxTemplate("mau_2c_template_MANUAL.docx")

# Prepare context
context = {
    "tinh": "Bình Dương",
    "ho_ten": "Nguyễn Văn An",
    
    # RichText cho text có formatting đặc biệt
    "chuc_vu": RichText("Chuyên viên", bold=True),
    
    # InlineImage cho ảnh
    "anh_4x6": InlineImage(doc, "photo.jpg", width=Inches(1.57)),
    
    # Bảng với {% tr %}
    "dao_tao": [
        {
            "ten_truong": "Đại học Luật TP.HCM",
            "nganh_hoc": "Luật Kinh tế",
            # ...
        }
    ]
}

# Render
doc.render(context)
doc.save("OUTPUT_PROFESSIONAL.docx")
'''

print(code_example)

print("=" * 80)
print("📚 TÀI LIỆU THAM KHẢO:")
print("=" * 80)
print("""
1. docxtpl documentation:
   https://docxtpl.readthedocs.io/

2. Jinja2 trong Word:
   - {{ variable }} - Simple text
   - {% tr for item in list %} - Table rows
   - {% if condition %} - Conditionals
   - {%p for item in list %} - Paragraphs

3. RichText:
   rt = RichText("text", bold=True, italic=True, 
                 color='FF0000', size=Pt(14))

4. InlineImage:
   img = InlineImage(doc, 'photo.jpg', width=Inches(2))

5. Subdocuments (cho phần phức tạp):
   sd = doc.new_subdoc()
   context['my_subdoc'] = sd
""")

print("=" * 80)
print("🎯 HÀNH ĐỘNG TIẾP THEO:")
print("=" * 80)
print("""
1. TẠO TEMPLATE THỦ CÔNG:
   ✅ Mở Mau-ly-lich-2C-TCTW-98.docx trong Word
   ✅ Replace text → {{ variables }} (giữ format)
   ✅ Save as mau_2c_template_MANUAL.docx

2. TEST:
   ✅ Dùng docxtpl render
   ✅ So sánh với file gốc
   ✅ Kiểm tra format có giống 100% không

3. HOÀN THIỆN:
   ✅ Thêm images
   ✅ Thêm RichText cho phần đặc biệt
   ✅ Test với nhiều data khác nhau

⏰ THỜI GIAN:
   - Tạo template thủ công: 30-45 phút
   - Test + fix: 15 phút
   → TỔNG: ~1 giờ
   
💡 Nhưng kết quả sẽ CHUYÊN NGHIỆP 100%!
""")

print("=" * 80)
