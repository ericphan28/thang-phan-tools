#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create JSON với cấu trúc gia đình ĐÚNG theo form
Bảng gia đình có cấu trúc:
- Bố, mẹ (2 người)
- Vợ/Chồng (1 người)  
- Các con (có thể nhiều người)
- Anh chị em ruột (có thể nhiều người)
"""

import json
from pathlib import Path

# Load existing data
json_file = Path("mau_2c_DATA_COMPLETE_V3.json")
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Restructure family data theo đúng form
# Instead of one array "gia_dinh", split into 4 arrays:

# 1. Bố mẹ (bo_me) - 2 people
data['bo_me'] = [
    {
        "ho_ten": "Nguyễn Văn Bình",
        "nam_sinh": "1970",
        "thong_tin": "Nông dân, xã Bình An, Dĩ An, Bình Dương. Đang canh tác tại quê."
    },
    {
        "ho_ten": "Trần Thị Cúc",
        "nam_sinh": "1972",
        "thong_tin": "Nội trợ, xã Bình An, Dĩ An, Bình Dương. Ở quê nhà."
    }
]

# 2. Vợ/Chồng (vo_chong) - 1 person
data['vo_chong'] = [
    {
        "ho_ten": "Lê Thị Diệu",
        "nam_sinh": "1998",
        "thong_tin": "Giáo viên mầm non, Trường MN Hoa Mai, Thủ Dầu Một. Đang công tác."
    }
]

# 3. Các con (cac_con) - multiple children
data['cac_con'] = [
    {
        "ho_ten": "Nguyễn Văn Minh",
        "nam_sinh": "2020",
        "thong_tin": "Học sinh mẫu giáo, Trường MN Hoa Mai, Thủ Dầu Một."
    },
    {
        "ho_ten": "Nguyễn Thị Mai",
        "nam_sinh": "2022",
        "thong_tin": "Nhà trẻ, đang ở nhà với ông bà."
    }
]

# 4. Anh chị em ruột (anh_chi_em) - siblings
data['anh_chi_em'] = [
    {
        "ho_ten": "Nguyễn Văn Bảo",
        "nam_sinh": "2000",
        "thong_tin": "Công nhân, Công ty Samsung Việt Nam, KCN Vsip. Đang làm việc."
    },
    {
        "ho_ten": "Nguyễn Thị Lan",
        "nam_sinh": "1995",
        "thong_tin": "Kế toán, Công ty TNHH Dệt May Bình Dương. Đã lập gia đình."
    }
]

# Similarly for spouse's family (gia_dinh_vo_chong)
# Restructure into:
# - Bố mẹ vợ/chồng
# - Anh chị em vợ/chồng

data['bo_me_vo_chong'] = [
    {
        "ho_ten": "Lê Văn Phúc",
        "nam_sinh": "1968",
        "thong_tin": "Thợ hàn tự do, Thủ Dầu Một. Đang sinh sống tại TP."
    },
    {
        "ho_ten": "Trần Thị Giang",
        "nam_sinh": "1970",
        "thong_tin": "Buôn bán chợ Bình Dương. Kinh doanh nhỏ."
    }
]

data['anh_chi_em_vo_chong'] = [
    {
        "ho_ten": "Lê Thị Hoa",
        "nam_sinh": "2002",
        "thong_tin": "Sinh viên, Đại học Kinh tế TP.HCM. Đang học năm 3."
    },
    {
        "ho_ten": "Lê Văn Tuấn",
        "nam_sinh": "1996",
        "thong_tin": "Lập trình viên, Công ty Phần mềm FPT. Đang công tác tại TP.HCM."
    }
]

# Keep old arrays for backward compatibility
# But they won't be used in new template

# Save
output_file = Path("mau_2c_DATA_RESTRUCTURED.json")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

file_size = output_file.stat().st_size

print("=" * 80)
print("✅ ĐÃ TẠO JSON MỚI VỚI CẤU TRÚC ĐÚNG!")
print("=" * 80)
print(f"📄 File: {output_file}")
print(f"📊 Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
print()
print("📋 GIA ĐÌNH:")
print(f"   - Bố mẹ: {len(data['bo_me'])} người")
print(f"   - Vợ/Chồng: {len(data['vo_chong'])} người")
print(f"   - Các con: {len(data['cac_con'])} người")
print(f"   - Anh chị em ruột: {len(data['anh_chi_em'])} người")
print()
print("📋 GIA ĐÌNH VỢ/CHỒNG:")
print(f"   - Bố mẹ vợ/chồng: {len(data['bo_me_vo_chong'])} người")
print(f"   - Anh chị em vợ/chồng: {len(data['anh_chi_em_vo_chong'])} người")
print()
print("💡 TỔNG:")
total_family = (len(data['bo_me']) + len(data['vo_chong']) + 
                len(data['cac_con']) + len(data['anh_chi_em']))
total_spouse = (len(data['bo_me_vo_chong']) + len(data['anh_chi_em_vo_chong']))
print(f"   - Tổng gia đình: {total_family} người")
print(f"   - Tổng gia đình vợ/chồng: {total_spouse} người")
print(f"   - TỔNG CỘNG: {total_family + total_spouse} người")
print("=" * 80)
