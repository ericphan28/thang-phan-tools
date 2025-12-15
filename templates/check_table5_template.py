#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check Table 5 template structure"""

from docx import Document
from pathlib import Path

template_file = Path("mau_2c_template_FINAL_V4.docx")
doc = Document(template_file)

print("📋 KIỂM TRA BẢNG 5 (LƯƠNG) - TEMPLATE")
print("=" * 80)

t5 = doc.tables[4]
print(f"Structure: {len(t5.rows)} rows × {len(t5.rows[0].cells)} cols")

print("\n📄 Row 1 (Header):")
for i, cell in enumerate(t5.rows[0].cells):
    print(f"  Col {i+1}: {cell.text[:80]}")

if len(t5.rows) > 1:
    print("\n📝 Row 2 (Data template):")
    for i, cell in enumerate(t5.rows[1].cells):
        text = cell.text.strip()
        if text:
            print(f"  Col {i+1}: {text[:150]}")
        else:
            print(f"  Col {i+1}: (empty)")

if len(t5.rows) > 2:
    print("\n📝 Row 3 (if exists):")
    for i, cell in enumerate(t5.rows[2].cells):
        text = cell.text.strip()
        if text:
            print(f"  Col {i+1}: {text[:150]}")
        else:
            print(f"  Col {i+1}: (empty)")

print("=" * 80)
