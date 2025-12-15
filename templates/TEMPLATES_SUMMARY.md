# 🎨 THIỆP MỜI CHUYÊN NGHIỆP - ĐÃ TẠO XONG

## ✅ Đã có 3 templates:

### 1️⃣ **Hợp đồng Lao động** (hop_dong_lao_dong.docx)
- 📋 Loại: Business document
- 🎨 Style: Professional, formal
- 🌈 Colors: Blue (#2E75B6), Black
- 📏 Features:
  - ✅ Viền trang xanh dương
  - ✅ Bảng thông tin rõ ràng
  - ✅ Loops cho tasks và benefits
  - ✅ Signature section
- 📄 JSON: hop_dong_lao_dong.json

---

### 2️⃣ **Thiệp Khai Trương** (thiep_khai_truong.docx) ⭐ MỚI
- 📋 Loại: Grand Opening Invitation
- 🎨 Style: Elegant, luxurious
- 🌈 Colors: 
  - Primary: Cardinal Red (#C41E3A)
  - Accent: Gold (#FFD700)
  - Text: White/Black
- 📏 Features:
  - ✅ **Double border** màu đỏ sang trọng
  - ✅ **Gold decorations** (✦, ❈)
  - ✅ Logo space ở top
  - ✅ Guest personalization (name + title)
  - ✅ Event details với icons (🏛️, 📅, 🎁)
  - ✅ Program section
  - ✅ Red/Gold shading boxes
  - ✅ Business slogan footer
- 📄 JSON: thiep_khai_truong.json
- 📐 Size: A5 (14.8×21cm)

**Use case:**
- Khai trương cửa hàng, showroom
- Ra mắt sản phẩm mới
- Khai trương văn phòng, chi nhánh

---

### 3️⃣ **Thiệp Sinh Nhật** (thiep_sinh_nhat.docx) ⭐ MỚI
- 📋 Loại: Birthday Invitation
- 🎨 Style: Fun, playful, vibrant
- 🌈 Colors:
  - Primary: Hot Pink (#FF69B4)
  - Accent: Gold (#FFD700)
  - Background: Light yellow tint
- 📏 Features:
  - ✅ **Triple border** màu hồng vui nhộn
  - ✅ **Emoji decorations** (🎈🎉🎂🎁🎊)
  - ✅ Comic Sans MS font (fun!)
  - ✅ Age display prominent
  - ✅ Event details với icons
  - ✅ RSVP section
  - ✅ Colorful shading boxes
- 📄 JSON: thiep_sinh_nhat.json
- 📐 Size: A5 (14.8×21cm)

**Use case:**
- Sinh nhật trẻ em
- Sinh nhật người lớn (casual style)
- Party invitations

---

## 🚀 Cách sử dụng:

### **Test với Document Generation API:**

**1. Thiệp Khai Trương:**
```bash
POST /api/v1/pdf/document-generation
Files:
  - template: thiep_khai_truong.docx
  - data: thiep_khai_truong.json
  - output_format: PDF
```

**2. Thiệp Sinh Nhật:**
```bash
POST /api/v1/pdf/document-generation
Files:
  - template: thiep_sinh_nhat.docx
  - data: thiep_sinh_nhat.json
  - output_format: PDF
```

### **Xem preview:**
```bash
start thiep_khai_truong.docx
start thiep_sinh_nhat.docx
```

---

## 📊 Comparison Table

| Feature | Hợp Đồng | Khai Trương | Sinh Nhật |
|---------|----------|-------------|-----------|
| **Màu chủ đạo** | Xanh dương | Đỏ + Vàng | Hồng + Vàng |
| **Style** | Professional | Elegant | Fun |
| **Font** | Times New Roman | Times New Roman | Comic Sans MS |
| **Border** | Single blue | Double red | Triple pink |
| **Icons** | ✅ Minimal | ✦ ❈ 🏛️ 📅 | 🎈 🎉 🎂 🎁 |
| **Target** | Business | Business/Formal | Personal/Casual |
| **Pages** | Multiple | 1 page | 1 page |
| **Size** | A4 | A5 | A5 |

---

## 🎯 Thiết kế nổi bật:

### **Thiệp Khai Trương:**
```
┌─══════════════════════════════════════──┐
│         [LOGO CÔNG TY]                   │
│                                          │
│           ✦ ✦ ✦ ✦ ✦                      │
│                                          │
│    ╔═══════════════════════════╗        │
│    ║  TRÂN TRỌNG KÍNH MỜI      ║  <-- Red box
│    ╚═══════════════════════════╝        │
│                                          │
│      ═══════════════════════  <-- Gold line
│                                          │
│  Quý khách: Ông Nguyễn Văn A            │
│  Giám Đốc Công ty ABC                   │
│                                          │
│  Tham dự buổi lễ khai trương            │
│   SHOWROOM ĐIỆN MÁY XANH PLUS           │
│                                          │
│          ❈ ❈ ❈                          │
│                                          │
│  🏛️ Địa điểm: 123 Đường Láng            │
│  📅 Thời gian: 08:00, 30/11/2024        │
│                                          │
│    ┌─────────────────────────┐          │
│    │  🎁  CHƯƠNG TRÌNH       │  <-- Gold box
│    │  • Cắt băng khai trương │          │
│    │  • Tiệc buffet          │          │
│    │  • Tham quan showroom   │          │
│    └─────────────────────────┘          │
│                                          │
│  📞 0912 345 678                        │
│                                          │
│           ✦ ✦ ✦ ✦ ✦                      │
│   Uy tín - Chất lượng - Giá tốt        │
└─══════════════════════════════════════──┘
```

### **Thiệp Sinh Nhật:**
```
┌─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━──┐
│                                          │
│        🎈 🎉 🎂 🎁 🎊                    │
│                                          │
│       YOU'RE INVITED!                    │
│                                          │
│    ┌──────────────────────────┐         │
│    │ 🎂 BIRTHDAY CELEBRATION 🎂│ <-- Gold
│    └──────────────────────────┘         │
│                                          │
│              for                         │
│         Bé Minh An                       │
│          Turning 5!                      │
│                                          │
│        🎈 🎈 🎈 🎈 🎈                    │
│                                          │
│  📅 Date: Saturday, Dec 15, 2024        │
│  🕐 Time: 2:00 PM - 5:00 PM             │
│  📍 Venue: KidZania Aeon Mall           │
│                                          │
│  Please join us to make                 │
│      this day special!                  │
│                                          │
│           RSVP                           │
│      📞 0987 654 321                    │
│      📧 chuminhan@gmail.com             │
│                                          │
│        🎊 🎁 🎂 🎉 🎈                    │
└─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━──┘
```

---

## 💡 Các loại thiệp CÒN có thể tạo:

### **Thiệp Lễ Kỷ Niệm:**
- 🎖️ Style: Elegant, sophisticated
- 🌹 Colors: Burgundy + Silver/Gold
- 💎 Fonts: Garamond, Baskerville
- 🥂 Use: Company anniversary, wedding anniversary

### **Thiệp Hội Nghị/Đại Hội:**
- 📊 Style: Modern, professional
- 💻 Colors: Blue + Green (corporate)
- 🎯 Fonts: Arial, Helvetica, Roboto
- 📋 Use: Conference, seminar, convention

### **Thiệp Cưới:**
- 💕 Style: Romantic, elegant
- 🌸 Colors: White + Gold/Rose gold
- 💍 Fonts: Script fonts, serif elegant
- 👰 Use: Wedding invitation

### **Thiệp Tốt Nghiệp:**
- 🎓 Style: Academic, formal
- 📚 Colors: Navy + Gold
- 🏆 Fonts: Traditional serif
- 🎉 Use: Graduation ceremony

---

## 🎨 Design Tips Áp Dụng:

### **1. Color Psychology:**
- 🔴 **Red:** Power, celebration (khai trương)
- 💛 **Gold:** Luxury, prosperity (khai trương, kỷ niệm)
- 💗 **Pink:** Fun, youthful (sinh nhật, baby shower)
- 🔵 **Blue:** Trust, professional (hội nghị, business)
- 💚 **Green:** Growth, fresh start (khai trương, tân gia)

### **2. Border Styles:**
- **Single:** Clean, minimal (business)
- **Double:** Elegant, important (grand opening)
- **Triple:** Playful, festive (birthday, party)
- **Art borders:** Themed decorations

### **3. Typography:**
- **Serif** (Times, Garamond): Formal, traditional
- **Sans-serif** (Arial, Helvetica): Modern, clean
- **Display** (Comic Sans, Pacifico): Fun, casual
- **Script** (Dancing Script): Elegant, romantic

### **4. Layout:**
- **Centered:** Formal invitations
- **Asymmetric:** Modern, creative
- **Grid-based:** Structured information

---

## 📥 Files Location

```
d:\thang\utility-server\templates\
├── hop_dong_lao_dong.docx
├── hop_dong_lao_dong.json
├── thiep_khai_truong.docx ⭐ NEW
├── thiep_khai_truong.json ⭐ NEW
├── thiep_sinh_nhat.docx ⭐ NEW
├── thiep_sinh_nhat.json ⭐ NEW
├── create_template.py
├── create_invitation_grand_opening.py ⭐ NEW
├── create_invitation_birthday.py ⭐ NEW
├── README.md
└── INVITATION_DESIGN_GUIDE.md ⭐ NEW
```

---

## 🚀 Next Steps:

### **1. Test thiệp mời với API:**
- Upload thiep_khai_truong.docx + JSON
- Generate PDF
- Kiểm tra màu sắc, layout

### **2. Thêm hình nền thực:**
- Download background images từ Unsplash/Freepik
- Thêm vào Word template (Design → Watermark)
- Hoặc Insert → Pictures → Behind Text

### **3. Thêm logo thực:**
- Chuẩn bị logo PNG (transparent background)
- Insert vào vị trí [LOGO]
- Set position fixed

### **4. Customize cho nhu cầu riêng:**
- Sửa colors trong script
- Thay đổi layout
- Thêm/bớt fields trong JSON

---

## 📞 Support

Cần tạo thêm loại thiệp nào? Inbox:
- 💝 Thiệp cưới
- 🎓 Thiệp tốt nghiệp  
- 📊 Thiệp hội nghị
- 🏡 Thiệp tân gia
- 🎄 Thiệp Giáng Sinh/Tết

**Happy Designing!** 🎨✨
