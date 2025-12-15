#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check family data structure"""

import json
from pathlib import Path

json_file = Path("mau_2c_DATA_COMPLETE_V3.json")
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 80)
print("📊 KIỂM TRA CẤU TRÚC GIA ĐÌNH")
print("=" * 80)

print("\n🔍 GIA ĐÌNH (gia_dinh):")
gia_dinh = data.get('gia_dinh', [])
print(f"   Total: {len(gia_dinh)} members")
for i, member in enumerate(gia_dinh, 1):
    print(f"   {i}. Quan hệ: {member.get('quan_he', 'N/A')}")
    print(f"      Họ tên: {member.get('ho_ten', 'N/A')}")
    print(f"      Năm sinh: {member.get('nam_sinh', 'N/A')}")
    print(f"      Thông tin: {member.get('thong_tin', 'N/A')[:50]}...")
    print()

print("\n🔍 GIA ĐÌNH VỢ/CHỒNG (gia_dinh_vo_chong):")
gia_dinh_vc = data.get('gia_dinh_vo_chong', [])
print(f"   Total: {len(gia_dinh_vc)} members")
for i, member in enumerate(gia_dinh_vc, 1):
    print(f"   {i}. Quan hệ: {member.get('quan_he', 'N/A')}")
    print(f"      Họ tên: {member.get('ho_ten', 'N/A')}")
    print(f"      Năm sinh: {member.get('nam_sinh', 'N/A')}")
    print(f"      Thông tin: {member.get('thong_tin', 'N/A')[:50]}...")
    print()

print("=" * 80)

# Check the actual structure from the image
print("\n📋 CẤU TRÚC TRONG ẢNH:")
print("   Bảng Gia đình phải có:")
print("   - Bố, mẹ")
print("   - Vợ/Chồng")
print("   - Các con")
print("   - Anh chị em ruột")
print("\n❓ NHƯNG DATA CỦA CHÚNG TA:")
print(f"   - Có {len(gia_dinh)} entries")
print(f"   - Quan hệ: {[m.get('quan_he') for m in gia_dinh]}")
print("\n⚠️ VẤN ĐỀ: Có thể thiếu cấu trúc phân chia rõ ràng!")
