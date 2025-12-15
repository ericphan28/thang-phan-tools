# 📊 BÁO CÁO DỮ LIỆU MẪU - MẪU 2C-TCTW-98

**Ngày:** 26/11/2024
**File phân tích:** `OUTPUT_MAU_2C_DOCXTPL.docx`
**Template:** `mau_2c_template_FULL_MAPPING.docx`
**JSON data:** `mau_2c_DATA_FULL.json` (95 fields)

---

## ✅ TỔNG KẾT

| Chỉ số | Trước cập nhật | Sau cập nhật | Cải thiện |
|--------|----------------|--------------|-----------|
| **Paragraphs có dữ liệu** | 66 | 66 | - |
| **Paragraphs thiếu dữ liệu** | **48** | **25** | 📉 **-48%** |
| **Fields trong JSON** | 63 | **95** | 📈 **+51%** |
| **Table cells thiếu** | 4 | 4 | ⚠️ Vẫn cần xử lý |

---

## 📋 PHÂN LOẠI FIELDS THIẾU (25 fields)

### 🟡 **Nhóm 1: Ngày tháng năm (9 fields)** - QUAN TRỌNG
Các trường này cần format đặc biệt hoặc logic phức tạp:

1. **Sinh ngày/tháng/năm** ❗ (Mục 4)
   - ❌ Hiện tại: `4) Sinh ngày: .......... tháng .......... năm ...............`
   - ✅ Cần: `{{ ngay }}/{{ thang }}/{{ nam }}`
   - 📌 **Template chưa map đúng!**

2. **Ngày được tuyển dụng** (Mục 12)
   - ❌ Format: `01/09/2019 / ........... / ..........`
   - ✅ Có data: `"ngay_tuyen_dung": "01/09/2019"`
   - 📌 **Template có vấn đề với format ngày**

3. **Ngày vào cơ quan** (Mục 13)
   - ❌ Format: `15/09/2019 / ....... / ......`
   - 📌 Tương tự như trên

4-6. **Ngày vào Đảng, ngày chính thức** (Mục 14)
   - ❌ `......... / .......... / ........`
   - 📌 **Chưa có trong JSON!**

7-9. **Ngày nhập ngũ/xuất ngũ** (Mục 16)
   - ❌ `Không / ... / ....`
   - 📌 Có data nhưng template chưa xử lý trường hợp "Không"

---

### 🟢 **Nhóm 2: Trường văn bản đơn giản (6 fields)** - DỄ SỬA

10. **Đơn vị cơ sở** (Header)
    - ✅ Có data: `"don_vi_co_so": "Phòng Nội vụ"`
    - ❌ Nhưng output hiện: `Đơn vị cơ sở: Phòng Nội vụ                 ..................`
    - 📌 **Template thêm dấu "..." thừa!**

11. **Phụ cấp chức vụ** (Mục 3)
    - ❌ Hiện: `.........       Phụ cấp chức vụ: ...`
    - ✅ Có data: `"phu_cap_chuc_vu": "0.2 (hệ số)"`
    - 📌 Paragraph format lỗi

12. **Ngạch công chức - format** (Mục 19)
    - ✅ Có data đầy đủ nhưng còn thừa: `từ t...`
    - 📌 Template xử lý từ khoá chưa sạch

---

### 🔵 **Nhóm 3: Ghi chú và trường đặc biệt (5 fields)** - KÉM QUAN TRỌNG

13-17. **Các trường ghi chú mẫu**
    - `(Ghi là công nhân, nông dân...)` 
    - `(Ghi nghề được đào tạo...)`
    - `(GS, PGS, TS, PTS, Thạc sĩ...)`
    - `(Anh (A/B/C/D) Nga...)`
    - `Ghi chú: Hình thức học...`
    
    📌 **Đây là TEXT MẪU hướng dẫn điền, KHÔNG phải fields cần data!**

---

### 🔴 **Nhóm 4: Lịch sử chính trị (4 fields)** - CẦN THÊM JSON

18-21. **Đặc điểm lịch sử, quan hệ nước ngoài**
    - Mục 28: `a) Khai rõ: bị bắt, bị tù...`
    - Mục 28: `b) Bản thân có làm việc trong chế độ cũ...`
    - Mục 29: `Quan hệ với nước ngoài...`
    - Mục 29: `Thân nhân ở nước ngoài...`
    
    📌 **Cần thêm 4 fields vào JSON:**
    ```json
    "lich_su_bi_bat": "Không",
    "lam_viec_che_do_cu": "Không",
    "quan_he_nuoc_ngoai": "Không",
    "than_nhan_nuoc_ngoài": "Không"
    ```

---

### 🟣 **Nhóm 5: Hoàn cảnh kinh tế (4 fields)** - CẦN BỔ SUNG JSON

22-25. **Nhà ở, đất đai chi tiết**
    - Mục 31: `- Nhà ở: + Được cấp: Không, tổng diện tích sử dụng: ........... m2`
    - Mục 31: `+ Tự mua: Căn hộ chung cư, 65 m², tổng diện tích sử dụng: ........... m2`
    - Mục 31: `- Đất ở: + Đất cấp:... + Đất mua:...`
    - Mục 31: `- Đất sản xuất: Không`
    
    📌 **JSON có nhưng thiếu tổng diện tích:**
    ```json
    "nha_o_duoc_cap": "Không",
    "nha_o_duoc_cap_dien_tich": "0 m²",  // ⬅️ THÊM
    "nha_o_tu_mua": "Căn hộ chung cư",
    "nha_o_tu_mua_dien_tich": "65 m²",   // ⬅️ THÊM
    ```

---

## 📊 TABLE CELLS THIẾU (4 cells)

### Bảng 3 & 4: Gia đình bản thân và vợ/chồng

❌ **Cell [1,4]:** "Quê quán, nghề nghiệp, chức danh, chức vụ, đơn vị,..."
   - Đây là HEADER mẫu, không phải data
   - ✅ **Bỏ qua**

❌ **Cell [2,1]:** "Bố, mẹ\n..........\nVợ\nChồng\n\n\nCác con:\n..."
   - Đây là LABEL cột để người dùng điền thủ công
   - ✅ **GIỮ NGUYÊN** (đúng thiết kế form)

📌 **Kết luận:** 4 table cells này là **thiết kế form**, không phải lỗi!

---

## 🎯 KHUYẾN NGHỊ HÀNH ĐỘNG

### ✅ **Ưu tiên 1: Sửa template (15 phút)**

1. **Fix format ngày sinh** (Mục 4)
   ```
   Hiện tại: 4) Sinh ngày: .......... tháng .......... năm ...............
   Sửa thành: 4) Sinh ngày: {{ ngay }} tháng {{ thang }} năm {{ nam }}
   ```

2. **Fix format ngày tuyển dụng/vào cơ quan** (Mục 12-13)
   ```
   Pattern: Ngày DD/MM/YYYY / ......... / ..........
   Sửa: Tách thành 3 fields riêng hoặc dùng filter format
   ```

3. **Xóa dấu "..." thừa sau fields có data**
   - `Đơn vị cơ sở: {{ don_vi_co_so }}`  (xóa `..................` phía sau)
   - Tương tự cho các trường khác

### ✅ **Ưu tiên 2: Bổ sung JSON (10 phút)**

Thêm 8 fields vào `mau_2c_DATA_FULL.json`:

```json
{
  // ... existing fields ...
  
  "_section_history": "=== LỊCH SỬ CHÍNH TRỊ ===",
  "lich_su_bi_bat": "Không",
  "lam_viec_che_do_cu": "Không",
  "quan_he_nuoc_ngoai": "Không",
  "than_nhan_nuoc_ngoai": "Không",
  
  "_section_economy": "=== KINH TẾ CHI TIẾT ===",
  "nha_o_duoc_cap_dien_tich": "0 m²",
  "nha_o_tu_mua_dien_tich": "65 m²",
  "dat_o_duoc_cap_dien_tich": "0 m²",
  "dat_o_tu_mua_dien_tich": "0 m²"
}
```

### ⚠️ **Ưu tiên 3: Xử lý ngày đặc biệt (20 phút)**

Các trường "Không" cần logic:
```python
# Template Jinja2
{% if ngay_nhap_ngu == "Không" %}
Ngày nhập ngũ: Không
{% else %}
Ngày nhập ngũ: {{ ngay_nhap_ngu }}
{% endif %}
```

### ℹ️ **Không cần sửa: Ghi chú mẫu (0 phút)**

Các text như `(Ghi là công nhân, nông dân...)`, `(GS, PGS, TS...)` là hướng dẫn form, GIỮ NGUYÊN!

---

## 📈 KẾT QUẢ DỰ KIẾN SAU KHI SỬA

| Chỉ số | Hiện tại | Sau sửa | Mục tiêu |
|--------|----------|---------|----------|
| **Paragraphs thiếu** | 25 | **~5** | < 10 |
| **% dữ liệu đầy đủ** | 62% | **~92%** | > 90% |
| **Fields JSON** | 95 | **103** | 100+ |
| **Độ chính xác template** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 5/5 |

---

## 🔗 FILES LIÊN QUAN

- ✅ **Template hiện tại:** `mau_2c_template_FULL_MAPPING.docx` (19.5 KB)
- ✅ **JSON data:** `mau_2c_DATA_FULL.json` (95 fields)
- ✅ **Output test:** `OUTPUT_MAU_2C_DOCXTPL.docx` (19.4 KB)
- 📄 **Script phân tích:** `analyze_missing_data.py`
- 📄 **Script cập nhật:** `update_template_mapping.py`

---

## 📝 GHI CHÚ

### ✅ Đã làm tốt:
- Tăng từ 63 → 95 fields (+51%)
- Giảm paragraphs thiếu từ 48 → 25 (-48%)
- Template map đúng 60+ trường
- Bảng có dữ liệu đầy đủ (5/5 tables)

### ⚠️ Cần cải thiện:
- Format ngày tháng năm phức tạp
- Template còn thừa dấu "..." sau fields có data
- Thiếu 8 fields cho lịch sử chính trị và kinh tế chi tiết

### 💡 Lưu ý:
- **Ghi chú mẫu** (5 trường) là text hướng dẫn, KHÔNG cần data
- **Table labels** (4 cells) là thiết kế form, GIỮ NGUYÊN
- **20 fields thiếu thực sự:** 9 ngày tháng + 3 format + 8 cần thêm JSON

---

**Tạo bởi:** `analyze_missing_data.py`  
**Ngày:** 26/11/2024
