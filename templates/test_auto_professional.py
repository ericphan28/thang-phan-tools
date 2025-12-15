#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test template tự động với format được giữ nguyên"""

from docxtpl import DocxTemplate
from pathlib import Path
import json

print("🚀 TEST TEMPLATE TỰ ĐỘNG CHUYÊN NGHIỆP")
print("=" * 80)

# Load template
template_file = Path("mau_2c_template_AUTO_PROFESSIONAL.docx")

if not template_file.exists():
    print("❌ Template not found! Run create_auto_professional.py first!")
    exit(1)

print(f"📖 Loading template: {template_file}")
doc = DocxTemplate(template_file)

# Load data
json_file = Path("mau_2c_DATA_RESTRUCTURED.json")
print(f"📖 Loading data: {json_file}")

with open(json_file, 'r', encoding='utf-8') as f:
    context = json.load(f)

print(f"✅ Loaded {len(context)} fields")

# Render
print("\n🔧 Rendering...")
try:
    doc.render(context)
    print("✅ Render successful!")
except Exception as e:
    print(f"❌ Render failed: {e}")
    exit(1)

# Save
output_file = Path("OUTPUT_AUTO_PROFESSIONAL.docx")
doc.save(str(output_file))

file_size = output_file.stat().st_size

print(f"\n💾 Saved: {output_file}")
print(f"📊 Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")

print("\n" + "=" * 80)
print("✅ DONE!")
print("=" * 80)

print("\n💡 KIỂM TRA:")
print("   1. Mở: OUTPUT_AUTO_PROFESSIONAL.docx")
print("   2. So sánh với: mau-nha-nuoc/Mau-ly-lich-2C-TCTW-98.docx")
print("\n📋 CHECKLIST:")
print("   ✓ Font có giống không? (Times New Roman 13)")
print("   ✓ Line spacing có đúng không?")
print("   ✓ Paragraph spacing có đúng không?")
print("   ✓ Table borders có đúng không?")
print("   ✓ Bold/Italic có giữ được không?")
print("\n🎯 Nếu GIỐNG 80%+ → THÀNH CÔNG!")
print("   (Một số format nhỏ có thể khác, nhưng tổng thể phải chuyên nghiệp)")

print("=" * 80)
