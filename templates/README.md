# 📋 HỢP ĐỒNG LAO ĐỘNG - Template Chuyên Nghiệp

## ✅ Đã tạo xong 2 files:

### 1. **hop_dong_lao_dong.docx** - Template Word đẹp sẵn
📍 Location: `d:\thang\utility-server\templates\hop_dong_lao_dong.docx`

**Tính năng:**
- ✅ Viền trang màu xanh dương chuyên nghiệp
- ✅ Header chuẩn Việt Nam (CHXHCNVN + Độc lập Tự do Hạnh phúc)
- ✅ Tiêu đề nổi bật, màu xanh dương đậm
- ✅ Bảng thông tin đẹp với borders và cell shading
- ✅ Font Times New Roman chuẩn văn bản
- ✅ Spacing và margins chuẩn A4
- ✅ Điều khoản được đánh số và format rõ ràng
- ✅ Phần ký tên 2 bên đẹp, có vị trí ký
- ✅ Hỗ trợ vòng lặp cho Tasks và Benefits

### 2. **hop_dong_lao_dong.json** - Dữ liệu mẫu
📍 Location: `d:\thang\utility-server\templates\hop_dong_lao_dong.json`

**Nội dung:**
- Thông tin công ty: Vietnam Tech
- Nhân viên: Trần Thị Bình - Lập trình viên Senior
- Lương: 30.000.000 VNĐ (25tr + 5tr phụ cấp)
- 4 nhiệm vụ cụ thể
- 12 chế độ phúc lợi

---

## 🚀 Cách sử dụng:

### **Option 1: Test trực tiếp với API**

1. Mở frontend của bạn
2. Vào tính năng **Document Generation**
3. Upload file: `d:\thang\utility-server\templates\hop_dong_lao_dong.docx`
4. Copy JSON từ: `d:\thang\utility-server\templates\hop_dong_lao_dong.json`
5. Click Generate → Nhận PDF đẹp!

### **Option 2: Test với cURL**

```bash
curl -X POST "http://localhost:8000/api/v1/pdf/document-generation" \
  -F "template=@d:\thang\utility-server\templates\hop_dong_lao_dong.docx" \
  -F "data=@d:\thang\utility-server\templates\hop_dong_lao_dong.json" \
  -F "output_format=PDF" \
  -o hop_dong_output.pdf
```

---

## 📝 Variables trong template:

### **Single values:**
- `{{contractNumber}}` - Số hợp đồng
- `{{signDate}}` - Ngày ký
- `{{company.name}}` - Tên công ty
- `{{employee.fullName}}` - Tên nhân viên
- v.v.

### **Arrays (loops):**

**Tasks:**
```
{% for task in tasks %}
{{task.name}}
{{task.description}}
{% endfor %}
```

**Benefits:**
```
{% for benefit in benefits %}
{{benefit}}
{% endfor %}
```

---

## 🎨 Tính năng format đẹp:

1. **Viền trang:** Màu xanh dương (#2E75B6)
2. **Tiêu đề chính:** Size 18pt, màu xanh dương, bold
3. **Tiêu đề điều khoản:** Size 13pt, màu xanh dương, bold
4. **Bảng thông tin:** Light Grid Accent 1 style
5. **Bullet points:** Chuẩn Word formatting
6. **Chữ ký:** Canh giữa, có dòng hướng dẫn italic
7. **Margins:** 2cm mỗi bên (A4 standard)
8. **Font:** Times New Roman 12pt

---

## 🔧 Customize JSON:

Bạn có thể sửa JSON để tạo hợp đồng khác:

```json
{
  "contractNumber": "HĐLĐ-2024-999",
  "signDate": "26/11/2024",
  "company": {
    "name": "CÔNG TY CỦA BẠN"
  },
  "employee": {
    "fullName": "Tên Nhân Viên Mới"
  },
  "salary": {
    "base": "50.000.000"
  }
}
```

---

## ✨ Kết quả mong đợi:

PDF output sẽ có:
- ✅ Logo + Header Việt Nam đẹp
- ✅ Viền trang xanh dương chuyên nghiệp
- ✅ Bảng thông tin rõ ràng
- ✅ Danh sách nhiệm vụ đầy đủ
- ✅ Phúc lợi liệt kê chi tiết
- ✅ Phần ký tên 2 bên chuẩn

---

**Giờ bạn test thử xem có đẹp không nha!** 🎉
