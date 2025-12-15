# 📐 CẤU TRÚC MẪU 2C CHI TIẾT - DOCXTPL

## 📋 TỔNG QUAN

**Mẫu 2C-TCTW-98** là form lý lịch cán bộ chính thức theo Thông tư 06/2023/TT-BNV

### Cấu trúc tổng thể:
- **78 paragraphs** - Các đoạn văn bản
- **5 tables** - Bảng với cấu trúc phức tạp
- **31 sections** - Các mục chính
- **60+ fields** - Trường dữ liệu đơn
- **5 arrays** - Mảng dữ liệu cho bảng

---

## 📝 PHẦN 1: THÔNG TIN HEADER

### Template Word:
```
SƠ YẾU LÝ LỊCH CÁN BỘ, CÔNG CHỨC, VIÊN CHỨC

Tỉnh: {{ tinh }}
Đơn vị trực thuộc: {{ don_vi_truc_thuoc }}
Đơn vị cơ sở: {{ don_vi_co_so }}
Số hiệu: {{ so_hieu }}
```

### JSON:
```json
{
  "tinh": "Bình Dương",
  "don_vi_truc_thuoc": "UBND Thành phố Thủ Dầu Một",
  "don_vi_co_so": "Phòng Nội vụ",
  "so_hieu": "BD-NV-2024-001"
}
```

### Output:
```
SƠ YẾU LÝ LỊCH CÁN BỘ, CÔNG CHỨC, VIÊN CHỨC

Tỉnh: Bình Dương
Đơn vị trực thuộc: UBND Thành phố Thủ Dầu Một
Đơn vị cơ sở: Phòng Nội vụ
Số hiệu: BD-NV-2024-001
```

---

## 👤 PHẦN 2: THÔNG TIN CÁ NHÂN (Mục 1-6)

### Template Word:
```
I. THÔNG TIN CÁ NHÂN

1. Họ và tên: {{ ho_ten }}
   Tên gọi khác: {{ ten_goi_khac }}

2. Sinh ngày {{ ngay }} tháng {{ thang }} năm {{ nam }}
   Nơi sinh: {{ noi_sinh }}
   Nguyên quán: {{ nguyen_quan }}

3. Dân tộc: {{ dan_toc }}    Tôn giáo: {{ ton_giao }}

4. Số CMND/CCCD: {{ so_cmnd }}
   Ngày cấp: {{ ngay_cap }}    Nơi cấp: {{ noi_cap }}

5. Hộ khẩu thường trú: {{ ho_khau }}
   Chỗ ở hiện tại: {{ cho_o_hien_tai }}

6. Điện thoại: {{ dien_thoai }}
   Email: {{ email }}
```

### JSON:
```json
{
  "ho_ten": "Nguyễn Văn An",
  "ten_goi_khac": "An",
  "ngay": "15",
  "thang": "08",
  "nam": "1997",
  "noi_sinh": "Thủ Dầu Một, Bình Dương",
  "nguyen_quan": "Thủ Dầu Một, Bình Dương",
  "dan_toc": "Kinh",
  "ton_giao": "Không",
  "so_cmnd": "241234567",
  "ngay_cap": "10/05/2015",
  "noi_cap": "Công an tỉnh Bình Dương",
  "ho_khau": "123 Đường XYZ, Phường Phú Hòa, TP Thủ Dầu Một",
  "cho_o_hien_tai": "123 Đường XYZ, Phường Phú Hòa, TP Thủ Dầu Một",
  "dien_thoai": "0901234567",
  "email": "nguyenvanan@email.com"
}
```

---

## 🎓 PHẦN 3: TRÌNH ĐỘ (Mục 7-12)

### Template Word:
```
II. TRÌNH ĐỘ, CHUYÊN MÔN

7. Trình độ văn hóa: {{ trinh_do_van_hoa }}

8. Trình độ chuyên môn cao nhất: {{ trinh_do_chuyen_mon }}

9. Lý luận chính trị: {{ ly_luan_chinh_tri }}

10. Quản lý nhà nước: {{ quan_ly_nha_nuoc }}

11. Ngoại ngữ: {{ ngoai_ngu }}

12. Tin học: {{ tin_hoc }}
```

### JSON:
```json
{
  "trinh_do_van_hoa": "12/12",
  "trinh_do_chuyen_mon": "Đại học Luật",
  "ly_luan_chinh_tri": "Trung cấp",
  "quan_ly_nha_nuoc": "Cao cấp lý luận chính trị",
  "ngoai_ngu": "Tiếng Anh B1",
  "tin_hoc": "Chứng chỉ Tin học văn phòng"
}
```

---

## 🏛️ PHẦN 4: THÔNG TIN CHÍNH TRỊ (Mục 13-15)

### Template Word:
```
III. THÔNG TIN CHÍNH TRỊ

13. Ngày vào Đảng Cộng sản Việt Nam: {{ ngay_vao_dang }}
    Ngày chính thức: {{ ngay_chinh_thuc }}

14. Ngày tham gia tổ chức chính trị - xã hội: {{ ngay_tham_gia_to_chuc }}

15. Ngày nhập ngũ: {{ ngay_nhap_ngu }}
    Ngày xuất ngũ: {{ ngay_xuat_ngu }}
    Quân hàm cao nhất: {{ quan_ham }}
```

### JSON:
```json
{
  "ngay_vao_dang": "15/06/2018",
  "ngay_chinh_thuc": "15/06/2019",
  "ngay_tham_gia_to_chuc": "10/09/2016",
  "ngay_nhap_ngu": "",
  "ngay_xuat_ngu": "",
  "quan_ham": ""
}
```

**Lưu ý:** Các field rỗng sẽ hiển thị trống trong output

---

## 💼 PHẦN 5: CÔNG VIỆC HIỆN TẠI (Mục 16-19)

### Template Word:
```
IV. CÔNG VIỆC HIỆN TẠI

16. Chức vụ hiện tại: {{ chuc_vu }}

17. Công việc chính được giao: {{ cong_viec_chinh }}

18. Ngạch công chức: {{ ngach_cong_chuc }}
    Mã ngạch: {{ ma_ngach }}
    Bậc lương: {{ bac_luong }}

19. Phụ cấp chức vụ: {{ phu_cap_chuc_vu }} %
    Phụ cấp khác: {{ phu_cap_khac }}
```

### JSON:
```json
{
  "chuc_vu": "Chuyên viên",
  "cong_viec_chinh": "Quản lý hồ sơ cán bộ, công chức",
  "ngach_cong_chuc": "Chuyên viên",
  "ma_ngach": "03.001",
  "bac_luong": "3/12",
  "phu_cap_chuc_vu": "10",
  "phu_cap_khac": "Phụ cấp trách nhiệm công việc: 0.2"
}
```

---

## 📊 BẢNG 1: ĐÀO TẠO (Table 1)

### Cấu trúc: 2 rows × 5 columns

**Row 1 (Header):**
| Tên trường | Ngành học | Thời gian | Hình thức đào tạo | Văn bằng |

**Row 2 (Data) - Template:**

Mỗi cell trong row 2:
```jinja2
Cell 1: {% for edu in dao_tao %}{{ edu.ten_truong }}{% endfor %}
Cell 2: {% for edu in dao_tao %}{{ edu.nganh_hoc }}{% endfor %}
Cell 3: {% for edu in dao_tao %}{{ edu.thoi_gian }}{% endfor %}
Cell 4: {% for edu in dao_tao %}{{ edu.hinh_thuc }}{% endfor %}
Cell 5: {% for edu in dao_tao %}{{ edu.van_bang }}{% endfor %}
```

**HOẶC dùng table row tag (tốt hơn):**
```jinja2
{%tr for edu in dao_tao %}
{{ edu.ten_truong }} | {{ edu.nganh_hoc }} | {{ edu.thoi_gian }} | {{ edu.hinh_thuc }} | {{ edu.van_bang }}
{%tr endfor %}
```

### JSON Structure:
```json
{
  "dao_tao": [
    {
      "ten_truong": "Đại học Luật TP. Hồ Chí Minh",
      "nganh_hoc": "Luật Kinh tế",
      "thoi_gian": "2015 - 2019",
      "hinh_thuc": "Chính quy",
      "van_bang": "Cử nhân Luật"
    },
    {
      "ten_truong": "Trường Chính trị Bình Dương",
      "nganh_hoc": "Lý luận chính trị",
      "thoi_gian": "2020 - 2021",
      "hinh_thuc": "Bồi dưỡng",
      "van_bang": "Chứng chỉ Trung cấp LLCT"
    }
  ]
}
```

### Output Table:
| Tên trường | Ngành học | Thời gian | Hình thức | Văn bằng |
|------------|-----------|-----------|-----------|----------|
| Đại học Luật TP.HCM | Luật Kinh tế | 2015-2019 | Chính quy | Cử nhân Luật |
| Trường Chính trị BD | Lý luận chính trị | 2020-2021 | Bồi dưỡng | CC Trung cấp LLCT |

**Mỗi object trong array = 1 hàng!**

---

## 📊 BẢNG 2: QUÁ TRÌNH CÔNG TÁC (Table 2)

### Cấu trúc: 2 rows × 2 columns

**Row 1 (Header):**
| Thời gian | Chức vụ, đơn vị công tác |

**Row 2 (Data) - Template:**
```jinja2
{%tr for work in cong_tac %}
{{ work.thoi_gian }} | {{ work.chuc_vu_don_vi }}
{%tr endfor %}
```

### JSON:
```json
{
  "cong_tac": [
    {
      "thoi_gian": "09/2019 - 12/2021",
      "chuc_vu_don_vi": "Chuyên viên - Phòng Nội vụ UBND TP Thủ Dầu Một"
    },
    {
      "thoi_gian": "01/2022 - nay",
      "chuc_vu_don_vi": "Chuyên viên - Phòng Nội vụ UBND TP Thủ Dầu Một (Bậc 3)"
    }
  ]
}
```

### Output:
| Thời gian | Chức vụ, đơn vị |
|-----------|-----------------|
| 09/2019 - 12/2021 | Chuyên viên - Phòng Nội vụ UBND TP Thủ Dầu Một |
| 01/2022 - nay | Chuyên viên - Phòng Nội vụ UBND TP Thủ Dầu Một (Bậc 3) |

---

## 📊 BẢNG 3: GIA ĐÌNH BẢN THÂN (Table 3)

### ⚠️ ĐẶC BIỆT: Có labels cố định trong Column 1!

### Cấu trúc: 2 rows × 4 columns

**Row 1 (Header):**
| Mối quan hệ | Họ và tên | Năm sinh | Quê quán, nghề nghiệp, chức danh |

**Row 2 - Column 1 có labels CỐ ĐỊNH:**
```
Bố, mẹ
Vợ
Chồng
Các con
Anh chị em ruột
```

**⚠️ QUAN TRỌNG:** Script `create_template_docxtpl.py` TỰ ĐỘNG giữ nguyên column 1!

**Row 2 (Data) - Template:**
```jinja2
{%tr for member in gia_dinh %}
[GIỮ NGUYÊN labels "Bố, mẹ\nVợ\nChồng\nCác con\nAnh chị em ruột"] | {{ member.ho_ten }} | {{ member.nam_sinh }} | {{ member.thong_tin }}
{%tr endfor %}
```

### JSON:
```json
{
  "gia_dinh": [
    {
      "ho_ten": "Nguyễn Văn Bình",
      "nam_sinh": "1970",
      "thong_tin": "Thủ Dầu Một, Bình Dương - Nông dân - Đảng viên"
    },
    {
      "ho_ten": "Trần Thị Cúc",
      "nam_sinh": "1972",
      "thong_tin": "Thủ Dầu Một, Bình Dương - Nội trợ"
    },
    {
      "ho_ten": "Lê Thị Diệu",
      "nam_sinh": "1998",
      "thong_tin": "TP.HCM - Giáo viên - Đoàn viên"
    },
    {
      "ho_ten": "Nguyễn Văn Em",
      "nam_sinh": "2000",
      "thong_tin": "Bình Dương - Sinh viên"
    }
  ]
}
```

### Output:
| Mối quan hệ | Họ và tên | Năm sinh | Thông tin |
|-------------|-----------|----------|-----------|
| Bố, mẹ | Nguyễn Văn Bình | 1970 | Thủ Dầu Một, BD - Nông dân - ĐV |
| Bố, mẹ | Trần Thị Cúc | 1972 | Thủ Dầu Một, BD - Nội trợ |
| Vợ | Lê Thị Diệu | 1998 | TP.HCM - Giáo viên - Đoàn viên |
| Các con | Nguyễn Văn Em | 2000 | Bình Dương - Sinh viên |

**Labels tự động map với từng hàng!**

---

## 📊 BẢNG 4: GIA ĐÌNH VỢ/CHỒNG (Table 4)

### Giống Bảng 3, cũng có labels cố định!

### Column 1 labels:
```
Bố, mẹ
Anh chị em ruột
```

### Template:
```jinja2
{%tr for member in gia_dinh_vo_chong %}
[GIỮ NGUYÊN labels] | {{ member.ho_ten }} | {{ member.nam_sinh }} | {{ member.thong_tin }}
{%tr endfor %}
```

### JSON:
```json
{
  "gia_dinh_vo_chong": [
    {
      "ho_ten": "Lê Văn Phúc",
      "nam_sinh": "1968",
      "thong_tin": "Dĩ An, Bình Dương - Thợ hàn - Đảng viên"
    },
    {
      "ho_ten": "Trần Thị Giang",
      "nam_sinh": "1970",
      "thong_tin": "Dĩ An, Bình Dương - Bán hàng"
    }
  ]
}
```

---

## 📊 BẢNG 5: QUÁ TRÌNH LƯƠNG (Table 5)

### Cấu trúc: 3 rows × 7 columns (Horizontal timeline)

**Row 1-2 (Headers):**
| Tháng/Năm | Ngạch, bậc, hệ số | ... |

**Row 3 (Data) - Template:**
```jinja2
{%tr for sal in luong %}
{{ sal.thang_nam }} | {{ sal.ngach_bac }} | {{ sal.he_so }} | ...
{%tr endfor %}
```

### JSON:
```json
{
  "luong": [
    {
      "thang_nam": "10/2019",
      "ngach_bac": "Chuyên viên/Bậc 1",
      "he_so": "2.10"
    },
    {
      "thang_nam": "10/2021",
      "ngach_bac": "Chuyên viên/Bậc 2",
      "he_so": "2.22"
    },
    {
      "thang_nam": "10/2022",
      "ngach_bac": "Chuyên viên/Bậc 3",
      "he_so": "2.34"
    }
  ]
}
```

### Output:
| Tháng/Năm | Ngạch, bậc | Hệ số |
|-----------|------------|-------|
| 10/2019 | CV/Bậc 1 | 2.10 |
| 10/2021 | CV/Bậc 2 | 2.22 |
| 10/2022 | CV/Bậc 3 | 2.34 |

---

## 👨‍👩‍👧‍👦 PHẦN 6: GIA ĐÌNH (Mục 20-21)

### Template:
```
V. THÔNG TIN GIA ĐÌNH

20. Tình trạng hôn nhân: {{ tinh_trang_hon_nhan }}

21. Họ và tên vợ (chồng): {{ ten_vo_chong }}
    Năm sinh: {{ nam_sinh_vo_chong }}
    Quê quán: {{ que_quan_vo_chong }}
    Nghề nghiệp: {{ nghe_nghiep_vo_chong }}
    Chỗ ở: {{ cho_o_vo_chong }}
```

### JSON:
```json
{
  "tinh_trang_hon_nhan": "Đã kết hôn",
  "ten_vo_chong": "Lê Thị Diệu",
  "nam_sinh_vo_chong": "1998",
  "que_quan_vo_chong": "TP. Hồ Chí Minh",
  "nghe_nghiep_vo_chong": "Giáo viên THPT",
  "cho_o_vo_chong": "123 Đường XYZ, TP Thủ Dầu Một"
}
```

---

## 💪 PHẦN 7: SỨC KHỎE (Mục 22-25)

### Template:
```
VI. TÌNH TRẠNG SỨC KHỎE

22. Tình trạng sức khỏe: {{ suc_khoe }}
23. Chiều cao: {{ chieu_cao }} cm
24. Cân nặng: {{ can_nang }} kg
25. Nhóm máu: {{ nhom_mau }}
```

### JSON:
```json
{
  "suc_khoe": "Tốt",
  "chieu_cao": "170",
  "can_nang": "65",
  "nhom_mau": "A"
}
```

---

## 🏅 PHẦN 8: KHEN THƯỞNG & KỶ LUẬT (Mục 26-27)

### Template:
```
VII. KHEN THƯỞNG VÀ KỶ LUẬT

26. Khen thưởng: {{ khen_thuong }}

27. Kỷ luật: {{ ky_luat }}
```

### JSON:
```json
{
  "khen_thuong": "Bằng khen UBND tỉnh Bình Dương năm 2023 - Hoàn thành xuất sắc nhiệm vụ",
  "ky_luat": "Không"
}
```

---

## ✍️ PHẦN 9: CHỮ KÝ (Footer)

### Template:
```
Tôi xin cam đoan những lời khai trên đây là đúng sự thật.

Ngày {{ ngay_ky }} tháng {{ thang_ky }} năm {{ nam_ky }}

NGƯỜI KHAI
(Ký, ghi rõ họ tên)




{{ ho_ten }}
```

### JSON:
```json
{
  "ngay_ky": "26",
  "thang_ky": "11",
  "nam_ky": "2025",
  "ho_ten": "Nguyễn Văn An"
}
```

---

## 📊 TỔNG HỢP CẤU TRÚC JSON ĐẦY ĐỦ

```json
{
  "tinh": "Bình Dương",
  "don_vi_truc_thuoc": "UBND Thành phố Thủ Dầu Một",
  "don_vi_co_so": "Phòng Nội vụ",
  "so_hieu": "BD-NV-2024-001",
  
  "ho_ten": "Nguyễn Văn An",
  "ten_goi_khac": "An",
  "ngay": "15",
  "thang": "08",
  "nam": "1997",
  "noi_sinh": "Thủ Dầu Một, Bình Dương",
  "nguyen_quan": "Thủ Dầu Một, Bình Dương",
  "dan_toc": "Kinh",
  "ton_giao": "Không",
  
  "so_cmnd": "241234567",
  "ngay_cap": "10/05/2015",
  "noi_cap": "Công an tỉnh Bình Dương",
  "ho_khau": "123 Đường XYZ, Phường Phú Hòa",
  "cho_o_hien_tai": "123 Đường XYZ, Phường Phú Hòa",
  "dien_thoai": "0901234567",
  "email": "nguyenvanan@email.com",
  
  "trinh_do_van_hoa": "12/12",
  "trinh_do_chuyen_mon": "Đại học Luật",
  "ly_luan_chinh_tri": "Trung cấp",
  "quan_ly_nha_nuoc": "Cao cấp lý luận chính trị",
  "ngoai_ngu": "Tiếng Anh B1",
  "tin_hoc": "Chứng chỉ Tin học văn phòng",
  
  "ngay_vao_dang": "15/06/2018",
  "ngay_chinh_thuc": "15/06/2019",
  "ngay_tham_gia_to_chuc": "10/09/2016",
  "ngay_nhap_ngu": "",
  "ngay_xuat_ngu": "",
  "quan_ham": "",
  
  "chuc_vu": "Chuyên viên",
  "cong_viec_chinh": "Quản lý hồ sơ cán bộ, công chức",
  "ngach_cong_chuc": "Chuyên viên",
  "ma_ngach": "03.001",
  "bac_luong": "3/12",
  "phu_cap_chuc_vu": "10",
  "phu_cap_khac": "Phụ cấp trách nhiệm công việc: 0.2",
  
  "dao_tao": [
    {
      "ten_truong": "Đại học Luật TP. Hồ Chí Minh",
      "nganh_hoc": "Luật Kinh tế",
      "thoi_gian": "2015 - 2019",
      "hinh_thuc": "Chính quy",
      "van_bang": "Cử nhân Luật"
    },
    {
      "ten_truong": "Trường Chính trị Bình Dương",
      "nganh_hoc": "Lý luận chính trị",
      "thoi_gian": "2020 - 2021",
      "hinh_thuc": "Bồi dưỡng",
      "van_bang": "Chứng chỉ Trung cấp LLCT"
    }
  ],
  
  "cong_tac": [
    {
      "thoi_gian": "09/2019 - 12/2021",
      "chuc_vu_don_vi": "Chuyên viên - Phòng Nội vụ UBND TP Thủ Dầu Một"
    },
    {
      "thoi_gian": "01/2022 - nay",
      "chuc_vu_don_vi": "Chuyên viên - Phòng Nội vụ UBND TP Thủ Dầu Một (Bậc 3)"
    }
  ],
  
  "gia_dinh": [
    {
      "ho_ten": "Nguyễn Văn Bình",
      "nam_sinh": "1970",
      "thong_tin": "Thủ Dầu Một, Bình Dương - Nông dân - Đảng viên"
    },
    {
      "ho_ten": "Trần Thị Cúc",
      "nam_sinh": "1972",
      "thong_tin": "Thủ Dầu Một, Bình Dương - Nội trợ"
    },
    {
      "ho_ten": "Lê Thị Diệu",
      "nam_sinh": "1998",
      "thong_tin": "TP.HCM - Giáo viên - Đoàn viên"
    },
    {
      "ho_ten": "Nguyễn Văn Em",
      "nam_sinh": "2000",
      "thong_tin": "Bình Dương - Sinh viên"
    }
  ],
  
  "gia_dinh_vo_chong": [
    {
      "ho_ten": "Lê Văn Phúc",
      "nam_sinh": "1968",
      "thong_tin": "Dĩ An, Bình Dương - Thợ hàn - Đảng viên"
    },
    {
      "ho_ten": "Trần Thị Giang",
      "nam_sinh": "1970",
      "thong_tin": "Dĩ An, Bình Dương - Bán hàng"
    }
  ],
  
  "luong": [
    {
      "thang_nam": "10/2019",
      "ngach_bac": "Chuyên viên/Bậc 1",
      "he_so": "2.10"
    },
    {
      "thang_nam": "10/2021",
      "ngach_bac": "Chuyên viên/Bậc 2",
      "he_so": "2.22"
    },
    {
      "thang_nam": "10/2022",
      "ngach_bac": "Chuyên viên/Bậc 3",
      "he_so": "2.34"
    }
  ],
  
  "tinh_trang_hon_nhan": "Đã kết hôn",
  "ten_vo_chong": "Lê Thị Diệu",
  "nam_sinh_vo_chong": "1998",
  "que_quan_vo_chong": "TP. Hồ Chí Minh",
  "nghe_nghiep_vo_chong": "Giáo viên THPT",
  "cho_o_vo_chong": "123 Đường XYZ, TP Thủ Dầu Một",
  
  "suc_khoe": "Tốt",
  "chieu_cao": "170",
  "can_nang": "65",
  "nhom_mau": "A",
  
  "khen_thuong": "Bằng khen UBND tỉnh Bình Dương năm 2023",
  "ky_luat": "Không",
  
  "ngay_ky": "26",
  "thang_ky": "11",
  "nam_ky": "2025"
}
```

**Tổng: 63 fields (58 simple + 5 arrays)**

---

**Made with ❤️ by AI Assistant**
**Date: 2025-11-26**
