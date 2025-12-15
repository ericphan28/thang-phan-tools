#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
So sánh OUTPUT với 2 hình
"""

from docx import Document

doc = Document('OUTPUT_V9_FINAL_CLEANED.docx')

print("="*70)
print("📊 CHI TIẾT CÁC BẢNG TRONG OUTPUT_V9_FINAL_CLEANED.docx")
print("="*70)

for i, table in enumerate(doc.tables):
    print(f"\n{'='*70}")
    print(f"TABLE {i+1}: {len(table.rows)} rows × {len(table.columns)} cols")
    print(f"{'='*70}")
    
    for ri, row in enumerate(table.rows[:5]):  # Show first 5 rows
        print(f"\nRow {ri+1}:")
        for ci, cell in enumerate(row.cells):
            text = cell.text.strip()
            if text:
                # Show first 80 chars
                display = text[:80] + "..." if len(text) > 80 else text
                print(f"  Col {ci+1}: {display}")
    
    if len(table.rows) > 5:
        print(f"\n  ... ({len(table.rows) - 5} more rows)")

print("\n" + "="*70)
print("✅ DONE")
