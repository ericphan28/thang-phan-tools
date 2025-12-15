#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test template V5 with restructured data"""

from docxtpl import DocxTemplate
from pathlib import Path
import json

print("🚀 TEST TEMPLATE V5 - CẤU TRÚC GIA ĐÌNH ĐÚNG")
print("=" * 80)

# Load template V5
template_path = Path("mau_2c_template_FINAL_V5.docx")
print(f"📖 Load template: {template_path}")

# Load restructured JSON data
json_path = Path("mau_2c_DATA_RESTRUCTURED.json")
print(f"📖 Load JSON data: {json_path}")

with open(json_path, 'r', encoding='utf-8') as f:
    context = json.load(f)

# Count fields
simple_fields = sum(1 for k, v in context.items() if not isinstance(v, list))
array_fields = sum(1 for k, v in context.items() if isinstance(v, list))
print(f"✅ Loaded {simple_fields + array_fields} fields")
print(f"   - Simple fields: {simple_fields}")
print(f"   - Array fields: {array_fields}")

# Show family structure
print("\n📋 CẤU TRÚC GIA ĐÌNH:")
print(f"   - Bố mẹ: {len(context.get('bo_me', []))} người")
print(f"   - Vợ/Chồng: {len(context.get('vo_chong', []))} người")
print(f"   - Các con: {len(context.get('cac_con', []))} người")
print(f"   - Anh chị em ruột: {len(context.get('anh_chi_em', []))} người")
print(f"   - Bố mẹ vợ/chồng: {len(context.get('bo_me_vo_chong', []))} người")
print(f"   - Anh chị em vợ/chồng: {len(context.get('anh_chi_em_vo_chong', []))} người")

# Render
print("\n🔧 Render template with data...")
doc = DocxTemplate(template_path)
doc.render(context)
print("   ✅ Render thành công!")

# Save
output_path = Path("OUTPUT_MAU_2C_V5.docx")
doc.save(str(output_path))
print(f"\n💾 Lưu file: {output_path}")

file_size = output_path.stat().st_size

print("\n" + "=" * 80)
print("✅ THÀNH CÔNG!")
print("=" * 80)
print(f"📄 Output: {output_path}")
print(f"📊 Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
print("\n💡 KIỂM TRA:")
print("   1. Mở file: OUTPUT_MAU_2C_V5.docx")
print("   2. Xem bảng 3: Gia đình")
print("      - Bố mẹ phải ở đúng vị trí")
print("      - Vợ/Chồng phải ở đúng vị trí")
print("      - Các con phải ở đúng vị trí")
print("      - Anh chị em ruột phải ở đúng vị trí")
print("   3. Xem bảng 4: Gia đình vợ/chồng")
print("      - Bố mẹ vợ/chồng phải ở đúng vị trí")
print("      - Anh chị em vợ/chồng phải ở đúng vị trí")
print("\n🎉 TEST HOÀN TẤT!")
print("=" * 80)
