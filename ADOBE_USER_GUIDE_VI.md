# 📘 Hướng Dẫn Sử Dụng Adobe PDF Services

**Dành cho người dùng cuối** | **Cập nhật**: 25/11/2025

Chào bạn! 👋 Đây là hướng dẫn chi tiết về 8 tính năng xử lý PDF chuyên nghiệp trên trang **/adobe-pdf** của chúng tôi.

---

## 🎯 Tổng Quan 8 Tính Năng

| # | Tính Năng | Màu Sắc | Công Dụng Chính |
|---|-----------|---------|-----------------|
| 1 | **Watermark PDF** | 🔵 Xanh dương | Đóng dấu bản quyền, chống sao chép |
| 2 | **Combine PDF** | 🟢 Xanh lá | Gộp nhiều file PDF thành 1 |
| 3 | **Split PDF** | 🟠 Cam | Tách 1 PDF thành nhiều file nhỏ |
| 4 | **Protect PDF** | 🔴 Đỏ | Mã hóa, đặt mật khẩu bảo mật |
| 5 | **Linearize PDF** | 🟣 Tím | Tối ưu tốc độ xem trên web |
| 6 | **Auto-Tag PDF** | 🟣 Tím đậm | Hỗ trợ người khuyết tật đọc PDF |
| 7 | **Document Generation** | 🔷 Xanh ngọc | Tạo PDF từ mẫu + dữ liệu |
| 8 | **Electronic Seal** | 🟡 Vàng | Ký số điện tử doanh nghiệp |

---

## 1️⃣ Watermark PDF - Đóng Dấu Bản Quyền

### 🤔 Dùng Khi Nào?
- Bạn muốn **đóng logo công ty** lên tài liệu
- Cần đánh dấu "BẢN NHÁP", "MẬT", "CONFIDENTIAL"
- Bảo vệ bản quyền ảnh, thiết kế
- Ngăn người khác sao chép tài liệu

### 📋 Ví Dụ Thực Tế

**Tình huống**: Bạn có file `hop-dong-thue.pdf` cần đóng dấu "BẢN SAO" để gửi cho đối tác xem trước.

**Các bước**:
1. **Tải file PDF** cần đóng dấu
2. **Chọn ảnh watermark** (logo công ty .png có nền trong suốt)
3. **Chọn vị trí**: Ở giữa (Center) hoặc góc (Corner)
4. **Độ mờ**: 30% (để đọc được nội dung bên dưới)
5. Click **"Đóng Dấu"**

**Kết quả**: File `watermarked_hop-dong-thue.pdf` có logo công ty ở mọi trang, độ mờ vừa phải.

### 💡 Tips Hay
- **Logo nền trong suốt** (.PNG) cho hiệu quả đẹp nhất
- **Độ mờ 20-40%** là vừa, không che nội dung
- **Position Center** phù hợp với tài liệu chính thức
- **Position Corner** phù hợp với ảnh, thiết kế

### ⚙️ Tùy Chọn

| Tùy Chọn | Giá Trị | Giải Thích |
|----------|---------|------------|
| **Opacity** | 10% - 100% | 10% = rất mờ, 100% = đậm hoàn toàn |
| **Position** | Center/Corner | Giữa trang hoặc góc |
| **Rotation** | -90° đến +90° | Xoay dấu (ví dụ: 45° chéo) |

---

## 2️⃣ Combine PDF - Gộp File

### 🤔 Dùng Khi Nào?
- Gộp nhiều **hợp đồng** thành 1 file duy nhất
- Tổng hợp **hóa đơn, chứng từ** của tháng
- Ghép **bài luận nhiều phần** thành 1 bản hoàn chỉnh
- Tạo **portfolio** từ nhiều dự án riêng lẻ

### 📋 Ví Dụ Thực Tế

**Tình huống**: Bạn có 5 file hợp đồng riêng biệt cần gộp thành 1 để nộp cho kế toán:
- `hop-dong-1.pdf` (3 trang)
- `hop-dong-2.pdf` (2 trang)
- `phu-luc-A.pdf` (1 trang)
- `phu-luc-B.pdf` (1 trang)
- `chu-ky.pdf` (1 trang)

**Các bước**:
1. Click **"Chọn Files"** → Chọn cả 5 file
2. File sẽ hiện danh sách theo thứ tự đã chọn
3. Click **"Gộp PDF"**
4. Đợi 3-5 giây

**Kết quả**: File `combined.pdf` có 8 trang (3+2+1+1+1), đúng thứ tự.

### 💡 Tips Hay
- **Đặt tên file theo thứ tự**: `01-hop-dong.pdf`, `02-phu-luc.pdf`
- **Kiểm tra trang trống**: Xóa trang trống trước khi gộp
- **Kích thước giới hạn**: Mỗi file ≤ 50MB
- **Số lượng file**: Không giới hạn (nhưng nên ≤ 20 file)

### ⚙️ Quy Trình Kỹ Thuật
```
Input:  hop-dong-1.pdf (3 trang) + hop-dong-2.pdf (2 trang)
        ↓
Adobe:  Merge theo thứ tự, giữ nguyên định dạng
        ↓
Output: combined.pdf (5 trang, kích thước = tổng 2 file)
```

---

## 3️⃣ Split PDF - Tách File

### 🤔 Dùng Khi Nào?
- **Tách từng trang** của 1 file PDF lớn
- **Trích xuất 1 vài trang** quan trọng
- Chia **sách PDF** thành từng chương
- **Giảm kích thước file** để gửi email

### 📋 Ví Dụ Thực Tế

**Tình huống**: Bạn có file `bao-cao-nam-2024.pdf` (50 trang), chỉ cần gửi trang 10-15 (phần tài chính) cho giám đốc.

**Cách 1: Tách Tất Cả**
1. Upload `bao-cao-nam-2024.pdf`
2. Chọn **"Tách tất cả trang"**
3. Click **"Tách PDF"**
4. Nhận file ZIP chứa 50 file nhỏ: `page_1.pdf`, `page_2.pdf`, ..., `page_50.pdf`
5. Chọn lấy `page_10.pdf` đến `page_15.pdf`

**Cách 2: Tách Theo Range** (Nếu UI hỗ trợ)
1. Upload `bao-cao-nam-2024.pdf`
2. Nhập **"Từ trang: 10"**, **"Đến trang: 15"**
3. Click **"Tách PDF"**
4. Nhận đúng 1 file `pages_10-15.pdf` (6 trang)

**Kết quả**: File nhỏ gọn, dễ gửi qua email.

### 💡 Tips Hay
- **Tách tất cả** → Lấy file ZIP → Chọn trang cần
- **Số trang lớn** (>100 trang) → Đợi lâu hơn (30-60s)
- **Đặt tên rõ ràng**: Sau khi tách, đổi tên `page_10.pdf` → `tai-chinh-Q4.pdf`

### ⚙️ Output Format
```
Input:  bao-cao.pdf (50 trang)
        ↓
Split:  Tách từng trang độc lập
        ↓
Output: bao-cao_split.zip
        ├── page_1.pdf
        ├── page_2.pdf
        ├── ...
        └── page_50.pdf
```

---

## 4️⃣ Protect PDF - Bảo Mật

### 🤔 Dùng Khi Nào?
- **Đặt mật khẩu** cho tài liệu nhạy cảm
- **Chặn in ấn, sao chép** nội dung
- **Ngăn chỉnh sửa** hợp đồng đã ký
- Bảo vệ **thông tin cá nhân, CMND**

### 📋 Ví Dụ Thực Tế

**Tình huống**: Bạn có file `luong-thang-11.pdf` cần gửi cho nhân viên, nhưng không muốn họ in hoặc sao chép.

**Các bước**:
1. Upload `luong-thang-11.pdf`
2. **User Password**: Để trống (ai cũng mở được)
3. **Owner Password**: `Admin@2024` (chỉ admin mới chỉnh sửa)
4. **Quyền**:
   - ❌ Không cho in (`Printing: NONE`)
   - ❌ Không cho copy text (`Copy: NONE`)
   - ❌ Không cho chỉnh sửa (`Editing: NONE`)
5. **Mã hóa**: AES-256 (chuẩn ngân hàng)
6. Click **"Bảo Mật"**

**Kết quả**: File `protected_luong-thang-11.pdf`
- ✅ Mở bình thường (không cần password)
- ❌ Không in được
- ❌ Không copy được text
- ❌ Không chỉnh sửa được
- 🔐 Chỉ ai có password `Admin@2024` mới thay đổi quyền

### 💡 Tips Hay
- **User Password**: Dùng khi muốn người khác KHÔNG mở được
- **Owner Password**: Dùng khi muốn kiểm soát quyền in/copy/edit
- **AES-256**: An toàn nhất, dùng cho tài liệu quan trọng
- **Lưu password**: Viết ra giấy, tránh quên!

### ⚙️ Phân Quyền Chi Tiết

| Quyền | NONE | LOW | HIGH |
|-------|------|-----|------|
| **Printing** | Không in | In chất lượng thấp | In đầy đủ |
| **Copy** | Không copy | - | Copy được |
| **Editing** | Không sửa | Chỉ form | Sửa tất cả |
| **Assembly** | Không ghép | - | Ghép trang |

**Ví dụ Use Case**:
- **Hợp đồng đã ký**: Printing=HIGH, Editing=NONE
- **Tài liệu mật**: Printing=NONE, Copy=NONE
- **Form điền thông tin**: Editing=FILL_FORMS

---

## 5️⃣ Linearize PDF - Tối Ưu Web

### 🤔 Dùng Khi Nào?
- **Tải PDF lên website** để khách xem online
- **Catalog sản phẩm** trên web (100+ trang)
- **Tạp chí điện tử** cần tải nhanh
- **Ebook** muốn đọc ngay trang đầu

### 📋 Ví Dụ Thực Tế

**Tình huống**: Bạn có file `catalog-2024.pdf` (150 trang, 50MB) muốn đưa lên website công ty.

**Vấn đề TRƯỚC**:
- Khách phải **đợi 10-15 giây** tải hết 50MB
- Không xem được cho đến khi tải xong 100%
- Khách bỏ đi vì chờ lâu

**Giải pháp**:
1. Upload `catalog-2024.pdf`
2. Click **"Tối Ưu PDF"**
3. Đợi 5-8 giây
4. Download `web_optimized_catalog-2024.pdf`

**Kết quả SAU**:
- Khách xem được **trang 1 ngay lập tức** (1-2 giây)
- Các trang sau tải dần trong khi đọc
- Trải nghiệm mượt mà như đọc sách

### 💡 Giải Thích Kỹ Thuật Đơn Giản

**PDF Thường** (Non-Linearized):
```
[Header][All Pages][All Images][All Fonts] → 50MB
     ↓
Phải tải HẾT 50MB mới xem được
```

**PDF Linearized** (Fast Web View):
```
[Header][Page 1 Data][Page 2 Data]...[Page 150 Data]
     ↓          ↓
  Tải Page 1  Xem ngay!  ← Tải Page 2 trong khi đọc Page 1
```

### ⚙️ So Sánh Hiệu Suất

| Metric | Trước Optimize | Sau Optimize |
|--------|----------------|--------------|
| **Time to First Page** | 10-15s (tải hết) | 1-2s ⚡ |
| **User Experience** | Chờ lâu, bỏ đi | Xem ngay, tiện lợi |
| **Server Load** | Tải 1 lần 50MB | Tải dần 50MB |
| **Bounce Rate** | Cao (~40%) | Thấp (~10%) |

### 💡 Tips Hay
- **Áp dụng cho**: Catalog, brochure, tạp chí, ebook
- **Không cần cho**: PDF nhỏ (<5MB, <20 trang)
- **Upload lên**: Đặt link trên website, không gửi email
- **Kích thước file**: Không thay đổi (vẫn 50MB)

---

## 6️⃣ Auto-Tag PDF - Hỗ Trợ Khuyết Tật

### 🤔 Dùng Khi Nào?
- **Website chính phủ** (bắt buộc WCAG)
- **Trường học, bệnh viện** (hỗ trợ người khuyết tật)
- **Tài liệu công khai** cần accessibility
- **Tuân thủ luật** Section 508 (Mỹ)

### 📋 Ví Dụ Thực Tế

**Tình huống**: Bạn làm việc cho website chính phủ, cần đăng file `thong-bao-chinh-sach.pdf` để người khiếm thị cũng đọc được.

**Vấn đề**: PDF thông thường không có "tags" (thẻ cấu trúc), phần mềm đọc màn hình không hiểu được đâu là:
- Tiêu đề (Heading)
- Đoạn văn (Paragraph)
- Danh sách (List)
- Bảng (Table)
- Hình ảnh (Image)

**Giải pháp**:
1. Upload `thong-bao-chinh-sach.pdf`
2. Tích ✅ **"Tạo báo cáo"** (để kiểm tra chất lượng)
3. Click **"Auto-Tag PDF"**
4. Đợi 10-15 giây (AI đang phân tích)
5. Download file ZIP có:
   - `tagged_thong-bao-chinh-sach.pdf` (PDF đã có tags)
   - `accessibility-report.xlsx` (báo cáo chi tiết)

**Kết quả**:
- Người khiếm thị dùng **NVDA/JAWS** đọc được toàn bộ nội dung
- Screen reader nhận diện đúng cấu trúc:
  - "Heading level 1: THÔNG BÁO CHÍNH SÁCH MỚI"
  - "Paragraph: Kể từ ngày 1/1/2025..."
  - "List item 1: Điều khoản đầu tiên"
- Website đạt chuẩn **WCAG 2.1 Level AA**

### 💡 Báo Cáo Excel Chứa Gì?

File `accessibility-report.xlsx` có:
- **Số lượng tags**: 156 headings, 89 paragraphs, 12 tables...
- **Vấn đề phát hiện**: 3 hình thiếu alt text, 1 table thiếu header
- **Điểm tuân thủ**: 95/100 (WCAG AA)
- **Khuyến nghị**: Thêm mô tả cho 3 hình ảnh

### ⚙️ Công Nghệ Adobe Sensei AI

```
Input PDF (không có tags)
        ↓
Adobe AI phân tích:
  - Nhận diện tiêu đề (font lớn, đậm)
  - Nhận diện đoạn văn (khối text liên tục)
  - Nhận diện bảng (grid structure)
  - Nhận diện danh sách (bullet points)
  - Nhận diện hình ảnh (non-text elements)
        ↓
Gắn tags tự động
        ↓
Output: Tagged PDF (screen reader friendly)
```

### 💡 Tips Hay
- **Luôn tạo báo cáo** để kiểm tra chất lượng
- **Chỉnh sửa thủ công** nếu AI sai (dùng Adobe Acrobat Pro)
- **Kiểm tra bằng NVDA** (free screen reader)
- **Tuân thủ WCAG**: Bắt buộc cho website chính phủ

---

## 7️⃣ Document Generation - Tạo PDF Từ Mẫu

### 🤔 Dùng Khi Nào?
- **Tạo hợp đồng tự động** từ thông tin khách hàng
- **Generate hóa đơn** hàng loạt
- **Tạo chứng chỉ** cho 1000 học viên
- **Email marketing** với PDF cá nhân hóa

### 📋 Ví Dụ Thực Tế

**Tình huống**: Công ty bạn cần tạo 500 hợp đồng lao động, mỗi người khác tên, chức vụ, lương. Làm thủ công mất 1 tuần!

**Giải pháp Tự Động**:

#### Bước 1: Chuẩn Bị Template (.docx)

Tạo file `hop-dong-mau.docx` với placeholders:

```
HỢP ĐỒNG LAO ĐỘNG

Tên nhân viên: {{ten_nhan_vien}}
Chức vụ: {{chuc_vu}}
Lương cơ bản: {{luong}} VNĐ
Ngày bắt đầu: {{ngay_bat_dau}}

Phụ cấp:
{{#phu_cap}}
  - {{ten}}: {{so_tien}} VNĐ
{{/phu_cap}}

Người ký: {{nguoi_ky}}
```

#### Bước 2: Chuẩn Bị Dữ Liệu JSON

```json
{
  "ten_nhan_vien": "Nguyễn Văn A",
  "chuc_vu": "Kỹ sư phần mềm",
  "luong": "20000000",
  "ngay_bat_dau": "01/12/2024",
  "phu_cap": [
    {"ten": "Xăng xe", "so_tien": "1000000"},
    {"ten": "Ăn trưa", "so_tien": "500000"}
  ],
  "nguoi_ky": "Giám đốc Nguyễn Văn B"
}
```

#### Bước 3: Generate

1. Upload `hop-dong-mau.docx`
2. Paste JSON data vào ô
3. Chọn **Output: PDF**
4. Click **"Tạo Tài Liệu"**

#### Kết Quả: `hop-dong-nguyen-van-a.pdf`

```
HỢP ĐỒNG LAO ĐỘNG

Tên nhân viên: Nguyễn Văn A
Chức vụ: Kỹ sư phần mềm
Lương cơ bản: 20000000 VNĐ
Ngày bắt đầu: 01/12/2024

Phụ cấp:
  - Xăng xe: 1000000 VNĐ
  - Ăn trưa: 500000 VNĐ

Người ký: Giám đốc Nguyễn Văn B
```

### 💡 Syntax Template (Mustache)

| Cú pháp | Giải thích | Ví dụ |
|---------|------------|-------|
| `{{bien}}` | Biến đơn giản | `{{ten}}` → "Nguyễn Văn A" |
| `{{#mang}}...{{/mang}}` | Lặp qua mảng | `{{#items}}{{name}}{{/items}}` |
| `{{#dieu_kien}}...{{/dieu_kien}}` | Hiện nếu true | `{{#vip}}VIP{{/vip}}` |
| `{{^dieu_kien}}...{{/dieu_kien}}` | Hiện nếu false | `{{^active}}Inactive{{/active}}` |
| `{{doi_tuong.thuoc_tinh}}` | Nested object | `{{khach.ten}}` |

### 📋 Ví Dụ Nâng Cao: Hóa Đơn

**Template JSON**:
```json
{
  "ma_hoa_don": "HD-2024-001",
  "khach_hang": {
    "ten": "Công ty ABC",
    "dia_chi": "123 Nguyễn Huệ, Q1, TPHCM"
  },
  "san_pham": [
    {"ten": "Laptop Dell", "so_luong": 2, "don_gia": 15000000},
    {"ten": "Chuột Logitech", "so_luong": 5, "don_gia": 200000}
  ],
  "giam_gia": 1000000,
  "thue": 10
}
```

**Template Word**:
```
HÓA ĐƠN: {{ma_hoa_don}}

Khách hàng: {{khach_hang.ten}}
Địa chỉ: {{khach_hang.dia_chi}}

Chi tiết:
{{#san_pham}}
  {{ten}} x {{so_luong}} = {{don_gia}} VNĐ
{{/san_pham}}

Giảm giá: {{giam_gia}} VNĐ
Thuế VAT ({{thue}}%): ...
```

### 💡 Tips Hay
- **Test với 1 record trước** → OK mới chạy hàng loạt
- **Validate JSON** bằng jsonlint.com tránh lỗi syntax
- **Font Unicode** (Arial, Times New Roman) để hiện tiếng Việt
- **Output PDF hoặc DOCX** tùy nhu cầu

---

## 8️⃣ Electronic Seal - Ký Số Doanh Nghiệp

### 🤔 Dùng Khi Nào?
- **Hợp đồng điện tử** cần chữ ký số hợp pháp
- **Văn bản chính thức** của công ty/chính phủ
- **Hóa đơn điện tử** tuân thủ luật
- **Tài liệu pháp lý** cần xác thực

### 📋 Ví Dụ Thực Tế

**Tình huống**: Công ty bạn ký hợp đồng điện tử với đối tác nước ngoài, cần chữ ký số tuân thủ chuẩn quốc tế (eIDAS).

#### Bước 1: Đăng Ký TSP (Trust Service Provider)

**TSP là gì?**: Nhà cung cấp chứng thư số, giống như "ngân hàng số" để xác thực danh tính.

**Các nhà TSP uy tín**:
- **GlobalSign** (Châu Âu, Mỹ)
- **DigiCert** (Toàn cầu)
- **DocuSign** (Mỹ)
- **VNPT-CA** (Việt Nam)
- **Viettel-CA** (Việt Nam)

**Chi phí**: ~$500-2000/năm tùy cấp độ

#### Bước 2: Lấy Thông Tin TSP

Sau khi đăng ký, bạn nhận được 4 thông tin:

```
Provider Name: globalsign.com
Access Token: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Credential ID: 4d2f8a3c-1e7b-4a9f-b2c6-8d5e3f1a9c7b
PIN: 123456
```

#### Bước 3: Ký Số PDF

1. Upload `hop-dong.pdf`
2. Upload `company-seal.png` (con dấu công ty - optional)
3. Điền 4 thông tin TSP:
   - Provider Name: `globalsign.com`
   - Access Token: `eyJhbGci...`
   - Credential ID: `4d2f8a3c...`
   - PIN: `123456`
4. Chọn vị trí con dấu: Trang 1, góc dưới bên phải
5. Tích ✅ **"Hiện con dấu"** (để người đọc thấy)
6. Click **"Ký Số PDF"**

#### Kết Quả: `signed_hop-dong.pdf`

**Khi mở PDF**:
- ✅ Có **biểu tượng chữ ký xanh** ở góc trên (Adobe Reader)
- ✅ Hiện con dấu công ty ở vị trí đã chọn
- ✅ Click vào xem thông tin:
  - Ký bởi: Công ty ABC
  - Thời gian: 25/11/2024 10:30:00
  - Nhà phát hành: GlobalSign
  - Trạng thái: ✅ Valid (Hợp lệ)

**Giá trị pháp lý**:
- Được công nhận tại **EU, Mỹ, châu Á**
- Tuân thủ **eIDAS, ESIGN Act**
- Có thể dùng làm bằng chứng tòa án
- Không thể chỉnh sửa sau khi ký

### 💡 So Sánh: Ký Tay vs Ký Số

| Đặc điểm | Ký Tay | Ký Số |
|----------|--------|-------|
| **Thời gian** | In → Ký → Scan → Gửi (2-3 ngày) | 5 phút ⚡ |
| **Chi phí** | In + Ship (~100k/lần) | Free (sau khi mua TSP) |
| **Bảo mật** | Dễ giả mạo | Không thể giả mạo 🔐 |
| **Pháp lý** | Cần công chứng | Tự động hợp pháp ✅ |
| **Kiểm tra** | Khó | Tự động, tức thì |
| **Môi trường** | Tốn giấy 🌳 | 100% điện tử ♻️ |

### ⚠️ Lưu Ý Quan Trọng

**Enterprise Feature**: Tính năng này dành cho doanh nghiệp, cần:
- ✅ Đăng ký TSP ($500-2000/năm)
- ✅ Xác thực danh tính công ty
- ✅ Có chứng thư số hợp lệ

**Không phải là**: Chữ ký cá nhân đơn giản (.p12/.pfx file)

**Use Cases**:
- ✅ Hợp đồng B2B quốc tế
- ✅ Văn bản chính thức công ty
- ✅ Hóa đơn điện tử
- ❌ Email cá nhân (dùng PGP/GPG thay thế)
- ❌ Chữ ký đơn giản (dùng DocuSign, HelloSign)

---

## 🎯 So Sánh Nhanh 8 Tính Năng

| Tính năng | Thời gian | Khó | Use Case Phổ Biến |
|-----------|-----------|-----|-------------------|
| **1. Watermark** | 2-3s | ⭐ Dễ | Logo công ty, "BẢN NHÁP" |
| **2. Combine** | 3-5s | ⭐ Dễ | Gộp hợp đồng, hóa đơn |
| **3. Split** | 5-10s | ⭐ Dễ | Tách trang cần thiết |
| **4. Protect** | 2-4s | ⭐⭐ TB | Mật khẩu bảo mật |
| **5. Linearize** | 5-8s | ⭐⭐ TB | PDF lên website |
| **6. Auto-Tag** | 10-15s | ⭐⭐⭐ Khó | Website chính phủ |
| **7. Generate** | 3-5s | ⭐⭐⭐⭐ Rất khó | Hợp đồng tự động |
| **8. E-Seal** | 5-7s | ⭐⭐⭐⭐⭐ Rất khó | Ký số doanh nghiệp |

---

## 💡 Tips Chung Cho Tất Cả Tính Năng

### 1. **Kích Thước File**
- ✅ Tối đa: 50MB/file
- ⚠️ File lớn (>20MB): Chờ lâu hơn
- 💡 Nén ảnh trước khi tạo PDF

### 2. **Định Dạng Hỗ Trợ**
- ✅ Input: PDF (tất cả version)
- ✅ Template: DOCX (Document Generation)
- ✅ Watermark: PNG, JPG
- ✅ Seal Image: PNG, JPG

### 3. **Tốc Độ Xử Lý**
| Kích thước | Thời gian |
|------------|-----------|
| <5MB | 2-5 giây |
| 5-20MB | 5-15 giây |
| 20-50MB | 15-30 giây |

### 4. **Lỗi Thường Gặp**

#### ❌ "Vui lòng chọn file PDF"
- **Nguyên nhân**: Chưa upload file
- **Giải pháp**: Click "Chọn File" → Chọn PDF

#### ❌ "JSON data không hợp lệ"
- **Nguyên nhân**: Syntax JSON sai
- **Giải pháp**: Paste vào jsonlint.com kiểm tra

#### ❌ "Adobe PDF Services chưa được cấu hình"
- **Nguyên nhân**: Lỗi server
- **Giải pháp**: Liên hệ admin

#### ❌ "Vui lòng nhập đầy đủ thông tin TSP"
- **Nguyên nhân**: Thiếu Provider/Token/ID/PIN
- **Giải pháp**: Điền đủ 4 trường

### 5. **Bảo Mật & Quyền Riêng Tư**
- 🔐 File được xử lý trên server an toàn
- 🗑️ Tự động xóa sau 1 giờ
- ❌ Không lưu trữ lâu dài
- ✅ HTTPS mã hóa khi upload/download

---

## 🆘 Hỗ Trợ & Liên Hệ

### Cần Giúp Đỡ?

**Hotline**: 1900-xxxx  
**Email**: support@company.com  
**Chat**: Click icon góc dưới phải  
**Giờ làm việc**: 8:00-17:30 (T2-T6)

### Tài Liệu Kỹ Thuật
- [ADOBE_8_FEATURES_COMPLETE.md](./ADOBE_8_FEATURES_COMPLETE.md) - Chi tiết kỹ thuật
- [ADOBE_CREDENTIALS_FIX.md](./ADOBE_CREDENTIALS_FIX.md) - Troubleshooting
- [API Documentation](https://developer.adobe.com/document-services/docs/)

### Video Hướng Dẫn
- 📺 [Watermark PDF trong 1 phút](https://youtube.com/...)
- 📺 [Gộp PDF nhanh nhất](https://youtube.com/...)
- 📺 [Bảo mật PDF chuyên nghiệp](https://youtube.com/...)

---

## 🎓 Học Thêm

### Khóa Học Miễn Phí
1. **PDF Basics** (30 phút) - Hiểu về định dạng PDF
2. **Document Automation** (2 giờ) - Tự động hóa tài liệu
3. **Digital Signature 101** (1 giờ) - Chữ ký số cơ bản

### Chứng Chỉ
- ✅ **Adobe Certified Professional** - Quản lý PDF
- ✅ **Document Security Specialist** - Bảo mật tài liệu

---

## ✅ Checklist Sử Dụng Hiệu Quả

### Trước Khi Bắt Đầu
- [ ] Đọc hướng dẫn tính năng cần dùng
- [ ] Chuẩn bị file PDF chất lượng tốt
- [ ] Kiểm tra kích thước file (<50MB)
- [ ] Backup file gốc

### Khi Xử Lý
- [ ] Upload đúng định dạng
- [ ] Điền đầy đủ thông tin
- [ ] Đợi xử lý xong (không tắt tab)
- [ ] Kiểm tra file output

### Sau Khi Xong
- [ ] Đổi tên file output rõ ràng
- [ ] Lưu vào thư mục phù hợp
- [ ] Kiểm tra nội dung file
- [ ] Chia sẻ hoặc upload

---

## 🎉 Kết Luận

Bạn đã nắm được 8 tính năng Adobe PDF Services! 

**Remember**:
- 🔵 **Watermark** → Đóng dấu bản quyền
- 🟢 **Combine** → Gộp file
- 🟠 **Split** → Tách trang
- 🔴 **Protect** → Mật khẩu bảo mật
- 🟣 **Linearize** → Tối ưu web
- 🟣 **Auto-Tag** → Hỗ trợ khuyết tật
- 🔷 **Generate** → Tạo từ mẫu
- 🟡 **E-Seal** → Ký số doanh nghiệp

**Bắt đầu ngay**: Truy cập **/adobe-pdf** và thử ngay! 🚀

---

**Phiên bản**: 1.0  
**Cập nhật**: 25/11/2025  
**Tác giả**: Technical Writing Team  
**Feedback**: Gửi góp ý qua support@company.com
