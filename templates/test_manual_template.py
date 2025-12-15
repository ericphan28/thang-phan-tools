#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test template THẬT (tạo thủ công trong Word)
Giữ 100% formatting của file gốc
"""

from docxtpl import DocxTemplate, RichText, InlineImage
from docx.shared import Cm, Pt, RGBColor
from pathlib import Path
import json

print("=" * 80)
print("🎨 TEST TEMPLATE CHUYÊN NGHIỆP (THỦ CÔNG)")
print("=" * 80)

# Check if manual template exists
manual_template = Path("mau_2c_template_MANUAL.docx")

if not manual_template.exists():
    print("\n❌ CHƯA CÓ TEMPLATE THỦ CÔNG!")
    print("\n📋 HƯỚNG DẪN:")
    print("   1. Mở file: Mau-ly-lich-2C-TCTW-98.docx")
    print("   2. Replace text → {{ variables }} (giữ format)")
    print("   3. Replace bảng → {% tr for ... %}")
    print("   4. Save as: mau_2c_template_MANUAL.docx")
    print("\n📖 Xem chi tiết: HUONG_DAN_TEMPLATE_CHUYEN_NGHIEP.md")
    print("=" * 80)
    exit(1)

print(f"\n✅ Tìm thấy template: {manual_template}")

# Load template
doc = DocxTemplate(manual_template)

# Load JSON data
json_file = Path("mau_2c_DATA_RESTRUCTURED.json")
print(f"📖 Load data: {json_file}")

with open(json_file, 'r', encoding='utf-8') as f:
    context = json.load(f)

print(f"✅ Loaded {len(context)} fields")

# Optional: Add image (if you have photo)
photo_file = Path("photo.jpg")
if photo_file.exists():
    context['anh_4x6'] = InlineImage(
        doc,
        str(photo_file),
        width=Cm(4),
        height=Cm(6)
    )
    print(f"📷 Thêm ảnh: {photo_file}")
else:
    print("ℹ️  Không có ảnh (bỏ qua)")

# Optional: Add RichText for special formatting
# Example: Bold text cho chức vụ
if 'chuc_vu' in context:
    context['chuc_vu_bold'] = RichText(
        context['chuc_vu'],
        bold=True
    )
    print("✨ Thêm RichText cho chức vụ (bold)")

# Render
print("\n🔧 Rendering...")
try:
    doc.render(context)
    print("✅ Render thành công!")
except Exception as e:
    print(f"❌ LỖI: {e}")
    print("\n💡 KIỂM TRA:")
    print("   - Syntax Jinja2 trong template có đúng không?")
    print("   - Variables trong template có match với JSON không?")
    print("   - {% tr %} và {% endtr %} có đúng vị trí không?")
    exit(1)

# Save
output_file = Path("OUTPUT_PROFESSIONAL.docx")
doc.save(str(output_file))

file_size = output_file.stat().st_size

print(f"\n💾 Lưu file: {output_file}")
print(f"📊 Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")

print("\n" + "=" * 80)
print("✅ HOÀN THÀNH!")
print("=" * 80)
print("\n💡 KIỂM TRA:")
print("   1. Mở file: OUTPUT_PROFESSIONAL.docx")
print("   2. So sánh với: Mau-ly-lich-2C-TCTW-98.docx")
print("   3. Kiểm tra:")
print("      - Font có giống không?")
print("      - Line spacing có đúng không?")
print("      - Table borders có đúng không?")
print("      - Bold/Italic có giữ được không?")
print("      - Ảnh 4x6 có đúng size không?")
print("\n🎯 Nếu format giống 100% → THÀNH CÔNG! 🎉")
print("=" * 80)
