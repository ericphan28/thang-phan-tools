"""
TEST MAILMERGE TEMPLATE
=======================
Render template với mailmerge library (format 100%!)
"""

from mailmerge import MailMerge
import json
from datetime import date

print("🧪 TEST MAILMERGE SOLUTION")
print("=" * 60)

# Load template
template_file = 'mau_2c_MAILMERGE_TEMPLATE.docx'
print(f"\n📖 Loading template: {template_file}")
document = MailMerge(template_file)

# Show available fields
print(f"   ✅ Merge fields found: {len(document.get_merge_fields())}")
print(f"   📋 Fields: {document.get_merge_fields()}")

# Load data
data_file = 'mau_2c_DATA_RESTRUCTURED.json'
print(f"\n📖 Loading data: {data_file}")
with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"   ✅ Loaded {len(data)} fields from JSON")

# Prepare merge data - flatten nested structures
merge_data = {}

# Simple fields
simple_fields = [
    'tinh', 'don_vi_truc_thuoc', 'don_vi_co_so',
    'ho_ten', 'gioi_tinh', 'ten_goi_khac',
    'noi_sinh', 'que_quan', 'dan_toc', 'ton_giao',
    'ho_khau_thuong_tru', 'noi_o_hien_nay',
    'dien_thoai', 'email',
    'ngay_vao_dang', 'ngay_chinh_thuc',
    'ngay_nhap_ngu', 'ngay_xuat_ngu', 'quan_ham',
    'trinh_do_giao_duc', 'trinh_do_chuyen_mon',
    'hoc_ham_hoc_vi', 'ly_luan_chinh_tri',
    'ngoai_ngu', 'trinh_do_tin_hoc',
    'cap_uy_hien_tai', 'cap_uy_kiem', 'chuc_vu',
    'phu_cap_chuc_vu', 'phu_cap_khac',
    'ngach_bac_luong', 'ngay_bo_nhiem',
    'khen_thuong', 'ky_luat', 'dac_diem_lich_su'
]

for field in simple_fields:
    if field in data:
        merge_data[field] = data[field]
    else:
        merge_data[field] = ''  # Empty if missing

# Handle date fields specially
if 'ngay' in data and 'thang' in data and 'nam' in data:
    merge_data['ngay_thang_nam_sinh'] = f"{data['ngay']}/{data['thang']}/{data['nam']}"

print(f"\n🔧 Merging simple fields...")
print(f"   Fields to merge: {len(merge_data)}")

# Merge
try:
    document.merge(**merge_data)
    print("   ✅ Simple merge successful!")
except Exception as e:
    print(f"   ⚠️  Warning: {e}")
    print("   💡 Continuing with partial merge...")

# Handle tables if they exist
print(f"\n🔧 Checking for table data...")

# Education table (Table 1)
if 'hoc_tap' in data and isinstance(data['hoc_tap'], list):
    try:
        # mailmerge expects field name from first column
        document.merge_rows('hoc_tap_thoi_gian', data['hoc_tap'])
        print(f"   ✅ Merged education table: {len(data['hoc_tap'])} rows")
    except Exception as e:
        print(f"   ⚠️  Education table merge failed: {e}")

# Work history table (Table 2)
if 'cong_tac' in data and isinstance(data['cong_tac'], list):
    try:
        document.merge_rows('cong_tac_thoi_gian', data['cong_tac'])
        print(f"   ✅ Merged work history table: {len(data['cong_tac'])} rows")
    except Exception as e:
        print(f"   ⚠️  Work history table merge failed: {e}")

# Family tables (Tables 3-4)
if 'bo_me' in data:
    try:
        families = []
        families.extend(data.get('bo_me', []))
        families.extend(data.get('vo_chong', []))
        families.extend(data.get('cac_con', []))
        families.extend(data.get('anh_chi_em', []))
        
        if families:
            document.merge_rows('family_ho_ten', families)
            print(f"   ✅ Merged family table: {len(families)} members")
    except Exception as e:
        print(f"   ⚠️  Family table merge failed: {e}")

# Save
output_file = 'OUTPUT_MAILMERGE.docx'
print(f"\n💾 Saving to: {output_file}")
document.write(output_file)

# Get file size
import os
size_bytes = os.path.getsize(output_file)
size_kb = size_bytes / 1024

print("\n" + "=" * 60)
print("✅ MAILMERGE HOÀN THÀNH!")
print(f"📄 Output: {output_file}")
print(f"📊 Size: {size_bytes:,} bytes ({size_kb:.2f} KB)")
print("\n💡 KIỂM TRA:")
print("   1. Mở file OUTPUT_MAILMERGE.docx trong Word")
print("   2. So sánh với file gốc:")
print("      - Font có giống không?")
print("      - Spacing có đúng không?")
print("      - Bold/Italic có giữ được không?")
print("      - Table borders có đẹp không?")
print("\n🎯 NẾU FORMAT HOÀN HẢO → ĐÂY LÀ GIẢI PHÁP ĐÚNG!")
