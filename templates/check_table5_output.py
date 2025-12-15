#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check Table 5 output in detail"""

from docx import Document
from pathlib import Path

output_file = Path("OUTPUT_MAU_2C_DOCXTPL.docx")
doc = Document(output_file)

print("📋 BẢNG 5: LƯƠNG (OUTPUT)")
print("=" * 80)

t5 = doc.tables[4]
print(f"Structure: {len(t5.rows)} rows × {len(t5.rows[0].cells)} cols\n")

for row_idx in range(len(t5.rows)):
    print(f"📝 ROW {row_idx}:")
    for col_idx in range(min(7, len(t5.rows[row_idx].cells))):
        cell_text = t5.rows[row_idx].cells[col_idx].text.strip()
        if cell_text:
            # Show with newlines visible
            cell_text_repr = cell_text.replace('\n', ' → ')
            print(f"  Col {col_idx+1}: {cell_text_repr}")
        else:
            print(f"  Col {col_idx+1}: (empty)")
    print()

print("=" * 80)
print("✅ XEM XONG BẢNG 5")
