# 📚 TEMPLATES INDEX - ĐẦY ĐỦ VÀ CHI TIẾT

## 🎯 Overview

**Tổng số files:** 13 files
- ✅ 3 Word templates (.docx)
- ✅ 3 JSON data files (.json)
- ✅ 4 Documentation files (.md)
- ✅ 3 Python scripts (.py)

**Tổng dung lượng:** ~160KB

---

## 📁 File Structure

```
d:\thang\utility-server\templates\
│
├── 📄 WORD TEMPLATES (3 files)
│   ├── hop_dong_lao_dong.docx          38.7 KB - Hợp đồng lao động
│   ├── thiep_khai_truong.docx          37.3 KB - Thiệp khai trương ⭐
│   └── thiep_sinh_nhat.docx            37.1 KB - Thiệp sinh nhật ⭐
│
├── 📊 JSON DATA (3 files)
│   ├── hop_dong_lao_dong.json           2.4 KB - Data hợp đồng
│   ├── thiep_khai_truong.json           513 B  - Data khai trương ⭐
│   └── thiep_sinh_nhat.json             341 B  - Data sinh nhật ⭐
│
├── 🐍 PYTHON SCRIPTS (3 files)
│   ├── create_template.py                    - Tạo hợp đồng
│   ├── create_invitation_grand_opening.py    - Tạo thiệp khai trương ⭐
│   └── create_invitation_birthday.py         - Tạo thiệp sinh nhật ⭐
│
└── 📖 DOCUMENTATION (4 files)
    ├── INVITATION_DESIGN_GUIDE.md      13.4 KB - Hướng dẫn thiết kế thiệp
    ├── TEMPLATES_SUMMARY.md            10.4 KB - Tổng hợp templates
    ├── ADD_BACKGROUND_GUIDE.md          9.8 KB - Hướng dẫn thêm hình nền ⭐
    └── README.md                        3.5 KB - README cơ bản
```

⭐ = Created today

---

## 🎨 Templates Chi Tiết

### 1. 📋 **Hợp Đồng Lao Động** (hop_dong_lao_dong.docx)

**Thông tin:**
- Loại: Business contract
- Style: Professional, formal
- Colors: Blue (#2E75B6)
- Size: A4 (21×29.7cm)
- Pages: Multiple

**Features:**
- ✅ Viền trang xanh dương
- ✅ Header CHXHCNVN chuẩn
- ✅ Bảng thông tin công ty/nhân viên
- ✅ Loops: Tasks và Benefits
- ✅ Signature section 2 bên
- ✅ Font: Times New Roman

**Variables:**
```json
{
  "contractNumber": "HĐLĐ-2024-001",
  "signDate": "01/12/2024",
  "company": { name, address, phone, taxId, representative },
  "employee": { fullName, birthDate, idNumber, address, phone, email },
  "position": { title, department, startDate, contractType },
  "salary": { base, allowance, total },
  "tasks": [{ name, description }],
  "benefits": [...]
}
```

**Use cases:**
- Hợp đồng lao động chính thức
- Phụ lục hợp đồng
- Hợp đồng cộng tác viên

---

### 2. 🏢 **Thiệp Khai Trương** (thiep_khai_truong.docx) ⭐ NEW

**Thông tin:**
- Loại: Grand opening invitation
- Style: Elegant, luxurious
- Colors: Red (#C41E3A) + Gold (#FFD700)
- Size: A5 (14.8×21cm)
- Pages: 1

**Design highlights:**
- ✅ **Double border** màu đỏ sang trọng (width: 36pt)
- ✅ **Logo space** ở top center
- ✅ **Gold decorations**: ✦ ✦ ✦, ❈ ❈ ❈
- ✅ **Red shading box** cho tiêu đề "TRÂN TRỌNG KÍNH MỜI"
- ✅ **Gold shading box** cho chương trình
- ✅ Icons: 🏛️ (địa điểm), 📅 (thời gian), 🎁 (chương trình)
- ✅ Font: Times New Roman
- ✅ Guest personalization (name + title)

**Layout:**
```
[LOGO SPACE]
✦ ✦ ✦ ✦ ✦
╔════════════════════════╗
║ TRÂN TRỌNG KÍNH MỜI   ║ <-- Red background
╚════════════════════════╝
═══════════════════════    <-- Gold line

Quý khách: [Name] (Red color, bold)
[Title] (Gray, italic)

Tham dự buổi lễ khai trương
[Business Name] (Red, bold)

❈ ❈ ❈

🏛️ Địa điểm: [Address]
📅 Thời gian: [DateTime]

┌──────────────────────┐
│ 🎁 CHƯƠNG TRÌNH     │ <-- Gold background
│ • Cắt băng          │
│ • Buffet            │
│ • Tham quan         │
└──────────────────────┘

📞 [Phone] | 📧 [Email]

✦ ✦ ✦ ✦ ✦
[Slogan]
```

**Variables:**
```json
{
  "guest": { "name": "Ông Nguyễn Văn A", "title": "Giám Đốc..." },
  "business": { "name": "SHOWROOM...", "slogan": "Uy tín..." },
  "venue": { "address": "Số 123..." },
  "event": { "datetime": "08:00, Thứ Bảy..." },
  "contact": { "phone": "0912...", "email": "..." }
}
```

**Use cases:**
- Khai trương cửa hàng, showroom
- Ra mắt sản phẩm mới
- Khai trương văn phòng, chi nhánh
- Opening ceremony

**Customization:**
- Change colors: Modify RGB values in script
- Add logo: Insert in [LOGO SPACE] position
- Add background: Design → Watermark → Red curtain image
- Change program: Edit static text or convert to loop

---

### 3. 🎂 **Thiệp Sinh Nhật** (thiep_sinh_nhat.docx) ⭐ NEW

**Thông tin:**
- Loại: Birthday invitation
- Style: Fun, playful, vibrant
- Colors: Hot Pink (#FF69B4) + Gold (#FFD700)
- Size: A5 (14.8×21cm)
- Pages: 1

**Design highlights:**
- ✅ **Triple border** màu hồng vui nhộn (width: 24pt)
- ✅ **Emoji decorations**: 🎈 🎉 🎂 🎁 🎊
- ✅ **Comic Sans MS** font (fun, playful)
- ✅ **Gold shading box** cho "BIRTHDAY CELEBRATION"
- ✅ **Age display** lớn và nổi bật
- ✅ Icons cho date/time/venue
- ✅ RSVP section rõ ràng
- ✅ Colorful text (pink, gold, gray)

**Layout:**
```
🎈 🎉 🎂 🎁 🎊

YOU'RE INVITED! (Pink, 24pt, Comic Sans)

┌──────────────────────────┐
│ 🎂 BIRTHDAY CELEBRATION 🎂│ <-- Gold background
└──────────────────────────┘

for (Gray, italic)
[Celebrant Name] (Pink, 22pt, bold)
Turning [Age]! (Gold age number)

🎈 🎈 🎈 🎈 🎈

📅 Date: [Date] (Pink)
🕐 Time: [Time] (Pink)
📍 Venue: [Venue] (Pink)

Please join us to make
this day special!

RSVP (Pink, bold)
📞 [Phone]
📧 [Email]

🎊 🎁 🎂 🎉 🎈
```

**Variables:**
```json
{
  "celebrant": { "name": "Bé Minh An", "age": "5" },
  "event": {
    "date": "Saturday, December 15th, 2024",
    "time": "2:00 PM - 5:00 PM",
    "venue": "KidZania Aeon Mall..."
  },
  "contact": { "phone": "0987...", "email": "..." }
}
```

**Use cases:**
- Sinh nhật trẻ em
- Sinh nhật người lớn (casual)
- Birthday party invitation
- Kids party

**Customization:**
- Change theme color: Modify pink to blue/purple/etc
- Change age style: Modify font size/color
- Add photo: Insert picture of celebrant
- Add background: Balloons pattern image

---

## 🛠️ Python Scripts

### **create_template.py**
- Tạo hợp đồng lao động
- Uses python-docx library
- Features: Tables, borders, page styling

### **create_invitation_grand_opening.py** ⭐
- Tạo thiệp khai trương
- Advanced: Double border, shading, decorations
- Color scheme: Red + Gold

### **create_invitation_birthday.py** ⭐
- Tạo thiệp sinh nhật
- Features: Triple border, emojis, fun fonts
- Color scheme: Pink + Gold

**Run scripts:**
```bash
cd d:\thang\utility-server\templates
python create_template.py
python create_invitation_grand_opening.py
python create_invitation_birthday.py
```

---

## 📖 Documentation Files

### **1. INVITATION_DESIGN_GUIDE.md** (13.4 KB)
**Nội dung:**
- 📋 Phương pháp tạo thiệp (Word, Python, HTML)
- 🎨 Thiết kế 4 loại thiệp:
  - Sinh nhật (Birthday)
  - Khai trương (Grand Opening)
  - Lễ kỷ niệm (Anniversary)
  - Đại hội (Conference)
- 🌈 Color schemes chuyên nghiệp
- 💡 Best practices
- 📦 Free resources
- 🎯 Implementation plan

**Đọc khi:** Muốn hiểu cách thiết kế thiệp chuyên nghiệp

---

### **2. TEMPLATES_SUMMARY.md** (10.4 KB)
**Nội dung:**
- ✅ Danh sách 3 templates đã tạo
- 📊 Comparison table
- 🎯 Design highlights với ASCII art
- 💡 Tips cho từng loại thiệp
- 🚀 Cách sử dụng với API
- 📥 Files location

**Đọc khi:** Muốn overview nhanh tất cả templates

---

### **3. ADD_BACKGROUND_GUIDE.md** (9.8 KB) ⭐ NEW
**Nội dung:**
- 🖼️ 3 methods thêm hình nền vào Word
- 🏢 Cách thêm logo
- 💦 Watermark text
- 🌈 Gradient background
- 📦 Free resources (Unsplash, Freepik, etc.)
- 💡 Pro tips
- 🛠️ Complete workflow example

**Đọc khi:** Muốn thêm hình nền/logo vào template có sẵn

---

### **4. README.md** (3.5 KB)
**Nội dung:**
- 📋 Quick overview hợp đồng lao động
- 🚀 Cách sử dụng
- 📝 Variables
- 🎨 Format tips

**Đọc khi:** Quick start với hợp đồng lao động

---

## 🚀 Quick Start Guide

### **Scenario 1: Tạo thiệp khai trương nhanh**

```bash
# Step 1: Open template
start d:\thang\utility-server\templates\thiep_khai_truong.docx

# Step 2: (Optional) Add background
# In Word: Design → Watermark → Picture → Choose fireworks image

# Step 3: (Optional) Add logo
# Double-click header → Insert → Pictures → Choose logo

# Step 4: Test with API
# POST /api/v1/pdf/document-generation
# Files: thiep_khai_truong.docx + thiep_khai_truong.json

# Step 5: Receive beautiful PDF! 🎉
```

---

### **Scenario 2: Customize thiệp sinh nhật**

```bash
# Step 1: Edit JSON data
notepad thiep_sinh_nhat.json
# Change: name, age, date, venue

# Step 2: (Optional) Change colors in Word
start thiep_sinh_nhat.docx
# Change pink to blue, gold to silver, etc.

# Step 3: Add balloon background
# Design → Watermark → Picture → balloons.jpg

# Step 4: Generate PDF via API
# Result: Personalized birthday invitation! 🎂
```

---

### **Scenario 3: Tạo loại thiệp mới**

```bash
# Step 1: Copy existing script
copy create_invitation_birthday.py create_invitation_wedding.py

# Step 2: Modify script
# Change colors: Pink → White/Gold
# Change fonts: Comic Sans → Script fonts
# Change decorations: Balloons → Hearts/Flowers

# Step 3: Run script
python create_invitation_wedding.py

# Step 4: Create JSON data
# Define wedding-specific variables

# Step 5: Test! 💒
```

---

## 🎨 Color Reference

### **Thiệp Khai Trương:**
- **Primary:** `#C41E3A` (Cardinal Red) - RGB(196, 30, 58)
- **Accent:** `#FFD700` (Gold) - RGB(255, 215, 0)
- **Text:** `#000000` (Black) + `#FFFFFF` (White)
- **Gray:** `#646464` (Dim gray) - RGB(100, 100, 100)

### **Thiệp Sinh Nhật:**
- **Primary:** `#FF69B4` (Hot Pink) - RGB(255, 105, 180)
- **Accent:** `#FFD700` (Gold) - RGB(255, 215, 0)
- **Light:** `#FFF5EE` (Seashell) - RGB(255, 245, 238)
- **Gray:** `#646464` (Dim gray) - RGB(100, 100, 100)

### **Hợp Đồng:**
- **Primary:** `#2E75B6` (Blue) - RGB(46, 117, 182)
- **Text:** `#000000` (Black)
- **Red:** `#C00000` (Dark red) - RGB(192, 0, 0)

---

## 📊 Statistics

### **Templates by Type:**
- Business documents: 1 (Hợp đồng)
- Invitations: 2 (Khai trương, Sinh nhật)
- **Total:** 3 templates

### **Features:**
- Borders: 3/3 (100%)
- Colors: 3/3 (100%)
- Icons/Emojis: 2/3 (67%)
- Tables: 1/3 (33%)
- Loops: 2/3 (67%)
- Shading boxes: 2/3 (67%)

### **Languages:**
- Vietnamese: 2 templates
- English: 1 template
- Mixed: 0 templates

---

## 🎯 Next Steps

### **Recommended additions:**

1. **Thiệp Lễ Kỷ Niệm** (Anniversary)
   - Style: Elegant, sophisticated
   - Colors: Burgundy + Silver/Gold
   - Use: Company/wedding anniversary

2. **Thiệp Hội Nghị** (Conference)
   - Style: Modern, professional
   - Colors: Blue + Green
   - Use: Seminar, convention, workshop

3. **Thiệp Cưới** (Wedding)
   - Style: Romantic, elegant
   - Colors: White + Rose gold
   - Use: Wedding invitation

4. **Thiệp Tốt Nghiệp** (Graduation)
   - Style: Academic, formal
   - Colors: Navy + Gold
   - Use: Graduation ceremony

5. **Phiếu Lương** (Payslip)
   - Style: Professional, clean
   - Colors: Blue/Gray
   - Use: Monthly payroll

---

## 💡 Tips & Tricks

### **For Print:**
- Resolution: 300 DPI minimum
- Color mode: CMYK
- Bleed: 3mm on all sides
- Save as: PDF/X-1a

### **For Digital:**
- Resolution: 150 DPI
- Color mode: RGB
- File format: PDF
- File size: Compress <1MB

### **For Batch Generation:**
```python
# Loop through multiple guests
guests = [
    {"name": "Guest 1", ...},
    {"name": "Guest 2", ...},
]

for guest in guests:
    # Generate individual invitation
    # Save as: invitation_guest1.pdf
```

---

## 📞 Support

**Cần giúp gì?**
- ❓ Tạo thêm loại thiệp mới
- 🎨 Customize design
- 🖼️ Thêm hình nền/logo
- 🐛 Debug issues
- 📚 More documentation

**Contact:** GitHub Issues hoặc email support

---

**Last Updated:** November 26, 2025
**Version:** 1.0
**Status:** ✅ Production Ready

🎉 **Happy Creating!** 🎨
