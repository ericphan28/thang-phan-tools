"""
Script kiểm tra nội dung 5 bảng trong OUTPUT
"""

from docx import Document

doc = Document("OUTPUT_MAU_2C_DOCXTPL.docx")

print("="*80)
print("📊 KIỂM TRA NỘI DUNG 5 BẢNG")
print("="*80)

for table_idx, table in enumerate(doc.tables):
    print(f"\n{'='*80}")
    print(f"📋 BẢNG {table_idx + 1}: {len(table.rows)} rows × {len(table.columns)} cols")
    print("="*80)
    
    # Show first 3 rows
    for row_idx, row in enumerate(table.rows[:3]):
        print(f"\n📌 Row {row_idx + 1}:")
        for col_idx, cell in enumerate(row.cells):
            text = cell.text.strip().replace('\n', ' ↵ ')[:80]
            print(f"   Col {col_idx + 1}: {text}")
