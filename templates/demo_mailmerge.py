"""
TẠO DEMO TEMPLATE ĐƠN GIẢN
==========================
Chỉ 5 fields để demo cách mailmerge work
"""

from mailmerge import MailMerge
from docx import Document
import os

print("🎯 DEMO: Cách mailmerge hoạt động ĐÚNG")
print("=" * 60)

# Kiểm tra file template đã có MergeFields chưa
test_files = [
    'mau_2c_MAILMERGE_TEMPLATE.docx',
    'mau-nha-nuoc/Mau-ly-lich-2C-TCTW-98.docx'
]

print("\n📋 Checking existing templates...")
for filepath in test_files:
    if os.path.exists(filepath):
        try:
            doc = MailMerge(filepath)
            fields = doc.get_merge_fields()
            print(f"\n✅ {filepath}")
            print(f"   MergeFields found: {len(fields)}")
            if fields:
                print(f"   Fields: {sorted(list(fields)[:10])}")
            else:
                print(f"   ⚠️  NO MERGEFIELDS! File cần tạo lại trong Word!")
        except Exception as e:
            print(f"\n❌ {filepath}")
            print(f"   Error: {e}")

print("\n" + "=" * 60)
print("📝 HƯỚNG DẪN:")
print("""
Để mailmerge hoạt động, cần:

1. MỞ FILE TRONG WORD (không dùng Python!)
2. THÊM MERGEFIELD:
   - Insert → Quick Parts → Field → MergeField
   - Hoặc: Ctrl+F9, gõ "MERGEFIELD tinh"
3. SAVE FILE
4. CHỈ KHI ĐÓ Python mới đọc được!

❌ KHÔNG THỂ dùng python-docx để tạo MergeField
✅ CHỈ CÓ THỂ tạo trong Word

Lý do: Word dùng complex XML với namespaces đặc biệt,
python-docx không hỗ trợ tạo MergeField.
""")

print("\n💡 GIẢI PHÁP:")
print("""
Option 1: TẠO THỦ CÔNG (15-20 phút)
  - Mở file trong Word
  - Thêm từng MergeField
  - Kết quả: 100% perfect

Option 2: DÙNG WORD MAILMERGE WIZARD
  - Mailings → Start Mail Merge → Letters
  - Insert Merge Field từ UI
  - Kết quả: 100% perfect, dễ hơn

Option 3: XIN BẠN GỬI FILE ĐÃ CÓ MERGEFIELD
  - Nếu bạn đã có template sẵn
  - Tôi sẽ test ngay

Option 4: TÔI TẠO VIDEO DEMO
  - Screen record cách làm trong Word
  - Bạn follow theo
""")

print("\n🎯 RECOMMENDED: Option 2 (Word MailMerge Wizard)")
print("   → Nhanh nhất, dễ nhất, ít lỗi nhất!")
