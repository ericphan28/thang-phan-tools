# HƯỚNG DẪN TẠO TEMPLATE MẪU 2C - KHOA HỌC & CHUẨN XÁC

## 📋 TẬP TIN ĐÃ CHUẨN BỊ SẴN

```
✅ mau_2c_TEMPLATE_DE_EDIT.docx  ← File Word để bạn edit
✅ mau_2c_DATA_FULL.json         ← File JSON mẫu đầy đủ
✅ HUONG_DAN_TAO_TEMPLATE.txt    ← Hướng dẫn chi tiết từng bước
```

## 🎯 CÁCH LÀM NHANH NHẤT (3 BƯỚC)

### BƯỚC 1: Mở Word
```
1. Mở file: mau_2c_TEMPLATE_DE_EDIT.docx trong Microsoft Word
2. Bấm Ctrl+H (Find & Replace)
```

### BƯỚC 2: Thay thế theo danh sách

**Copy-paste từng dòng vào Find & Replace:**

#### Header (3 mục):
```
Tìm: Tỉnh: …………………
Thay: Tỉnh: {{tinh}}

Tìm: Đơn vị trực thuộc: .........................
Thay: Đơn vị trực thuộc: {{don_vi_truc_thuoc}}

Tìm: Đơn vị cơ sở: ................................
Thay: Đơn vị cơ sở: {{don_vi_co_so}}
```

#### Mục 1-5 (9 replacements):
```
Ho ten: ……………………………………..
→ {{ho_ten}}

Nam, nữ: ...............
→ {{gioi_tinh}}

2) Các tên gọi khác: ................................................
→ {{ten_khac}}

3) Cấp ủy hiện tại: .......................................
→ {{cap_uy}}

Cấp ủy kiêm: .........................................
→ {{cap_uy_kiem}}

Chức vụ (Đảng, đoàn thể, Chính quyền, kể cả chức vụ kiêm nhiệm): ................................................
→ {{chuc_vu}}

Phụ cấp chức vụ: ...........................
→ {{phu_cap}}

4) Sinh ngày: .......... tháng .......... năm ...............
→ {{ngay}} tháng {{thang}} năm {{nam}}

5) Nơi sinh: ..................................................
→ {{noi_sinh}}
```

**⏩ Tiếp tục với 20 mục còn lại theo file HUONG_DAN_TAO_TEMPLATE.txt**

### BƯỚC 3: Sửa 5 bảng

#### 🔧 Bảng 1 (Đào tạo):
- Hàng 2, thay dấu chấm từng cột:
  ```
  Cột 1: {{#dao_tao}}{{ten_truong}}{{/dao_tao}}
  Cột 2: {{#dao_tao}}{{nganh_hoc}}{{/dao_tao}}
  Cột 3: {{#dao_tao}}{{thoi_gian}}{{/dao_tao}}
  Cột 4: {{#dao_tao}}{{hinh_thuc}}{{/dao_tao}}
  Cột 5: {{#dao_tao}}{{van_bang}}{{/dao_tao}}
  ```

#### 🔧 Bảng 2 (Quá trình công tác):
- Hàng 2:
  ```
  Cột 1: {{#cong_tac}}{{thoi_gian}}{{/cong_tac}}
  Cột 2: {{#cong_tac}}{{chuc_vu_don_vi}}{{/cong_tac}}
  ```

#### 🔧 Bảng 3 (Gia đình bản thân):
⚠️ **QUAN TRỌNG:** Cột 1 đã có "Bố, mẹ", "Vợ", "Chồng" → KHÔNG XÓA!
- Chỉ sửa cột 2-4:
  ```
  Cột 2: {{#gia_dinh}}{{ho_ten}}{{/gia_dinh}}
  Cột 3: {{#gia_dinh}}{{nam_sinh}}{{/gia_dinh}}
  Cột 4: {{#gia_dinh}}{{thong_tin}}{{/gia_dinh}}
  ```

#### 🔧 Bảng 4 (Gia đình vợ/chồng):
- Tương tự bảng 3:
  ```
  Cột 2: {{#gia_dinh_vo_chong}}{{ho_ten}}{{/gia_dinh_vo_chong}}
  Cột 3: {{#gia_dinh_vo_chong}}{{nam_sinh}}{{/gia_dinh_vo_chong}}
  Cột 4: {{#gia_dinh_vo_chong}}{{thong_tin}}{{/gia_dinh_vo_chong}}
  ```

#### 🔧 Bảng 5 (Quá trình lương):
- Bảng ngang, các cột từ cột 2 trở đi:
  ```
  Row 1: {{#luong}}{{thang_nam}}{{/luong}}
  Row 2: {{#luong}}{{ngach_bac}}{{/luong}}
  Row 3: {{#luong}}{{he_so}}{{/luong}}
  ```

---

## ✅ SAU KHI HOÀN TẤT

1. **Lưu file:** `mau_2c_template_final.docx`
2. **Test ngay:**
   ```bash
   cd templates
   python test_with_new_template.py
   ```

---

## 🚀 HOẶC NẾU BẠN MUỐN NHANH HƠN

Tôi có thể viết Python script để:
- Tự động mở Word qua COM
- Tự động Find & Replace hết
- Nhưng **KHÔNG KHUYẾN KHÍCH** vì:
  - Dễ lỗi font, spacing
  - Không kiểm soát được
  - **TỐT NHẤT: TỰ TAY** (30 phút, chính xác 100%)

---

## 📞 NẾU GẶP VẤN ĐỀ

1. Check file `HUONG_DAN_TAO_TEMPLATE.txt` - có list đầy đủ 60+ replacements
2. Check file `mau_2c_DATA_FULL.json` - xem cấu trúc JSON
3. Hỏi lại tôi!
