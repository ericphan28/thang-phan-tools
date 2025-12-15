# 🎉 HƯỚNG DẪN TẠO THIỆP MỜI CHUYÊN NGHIỆP

## 📋 Mục lục
1. [Phương pháp tạo thiệp mời](#phương-pháp)
2. [Thiết kế template Word với hình nền và màu sắc](#thiết-kế-word)
3. [Sử dụng Adobe Document Generation](#adobe-solution)
4. [Ví dụ thực tế](#ví-dụ)

---

## 🎯 Phương pháp tạo thiệp mời chuyên nghiệp

### **Option 1: Word Template + Adobe Document Generation** ⭐ (RECOMMENDED)
**Ưu điểm:**
- ✅ Control hoàn toàn design (màu sắc, font, layout)
- ✅ Hỗ trợ hình nền, logo, watermark
- ✅ Variable thay đổi linh hoạt (tên khách, ngày giờ, địa điểm)
- ✅ Export PDF chất lượng cao
- ✅ Dễ customize cho từng event

**Nhược điểm:**
- ⚠️ Phải thiết kế template trước
- ⚠️ Cần basic Word skills

### **Option 2: Python docx-template + PIL/Pillow**
**Ưu điểm:**
- ✅ Tạo động 100% từ code
- ✅ Thêm hình ảnh, QR code dễ dàng
- ✅ Batch generate nhiều thiệp cùng lúc

**Nhược điểm:**
- ⚠️ Khó control chi tiết design
- ⚠️ Layout phức tạp khó code

### **Option 3: HTML + CSS + WeasyPrint/Playwright**
**Ưu điểm:**
- ✅ Design cực đẹp với CSS modern
- ✅ Responsive, effects, animations
- ✅ Web designer dễ làm

**Nhược điểm:**
- ⚠️ PDF conversion đôi khi có vấn đề fonts
- ⚠️ Cần setup thêm dependencies

---

## 🎨 Thiết kế Word Template Chuyên Nghiệp

### **A. Thiệp Sinh Nhật (Birthday Invitation)**

**Đặc điểm:**
- 🎈 Màu sắc: Pastel, bright colors (hồng, xanh mint, vàng)
- 🎂 Hình nền: Balloons, confetti, cake patterns
- 🎉 Font: Playful, fun (Comic Sans MS, Arial Rounded)
- ⭐ Layout: Center-aligned, festive

**Elements:**
```
┌─────────────────────────────────────┐
│       [LOGO COMPANY/PERSONAL]        │
│                                      │
│        🎉 YOU'RE INVITED! 🎉         │
│                                      │
│     [Hình nền: Balloons pattern]    │
│                                      │
│     Birthday Celebration for:       │
│        {{celebrant.name}}           │
│                                      │
│   📅 Date: {{event.date}}           │
│   🕐 Time: {{event.time}}           │
│   📍 Venue: {{event.venue}}         │
│                                      │
│      Please join us to make         │
│       this day special! 🎂          │
│                                      │
│    RSVP: {{contact.phone}}          │
└─────────────────────────────────────┘
```

### **B. Thiệp Khai Trương (Grand Opening)**

**Đặc điểm:**
- 🏆 Màu sắc: Gold, red, royal blue (sang trọng)
- 🎊 Hình nền: Fireworks, ribbons, prosperity patterns
- 💼 Font: Professional (Times New Roman, Garamond, Helvetica)
- 🏢 Layout: Formal, elegant

**Elements:**
```
┌─────────────────────────────────────┐
│         [LOGO CỰC LỚN ĐẸP]          │
│                                      │
│  ═══════════════════════════════     │
│     TRÂN TRỌNG KÍNH MỜI              │
│  ═══════════════════════════════     │
│                                      │
│  [Gold/Red decorative border]       │
│                                      │
│  Quý khách: {{guest.name}}          │
│  Chức vụ: {{guest.title}}           │
│                                      │
│  Tham dự buổi lễ khai trương:       │
│   {{business.name}}                 │
│                                      │
│  🏛️ Địa chỉ: {{venue.address}}      │
│  📅 Thời gian: {{event.datetime}}   │
│                                      │
│  🎁 Chương trình:                   │
│    • Cắt băng khai trương           │
│    • Tiệc buffet                    │
│    • Tham quan showroom             │
│                                      │
│  Liên hệ: {{contact.phone}}        │
│                                      │
│  [Company Footer với slogan]        │
└─────────────────────────────────────┘
```

### **C. Thiệp Lễ Kỷ Niệm (Anniversary)**

**Đặc điểm:**
- 💝 Màu sắc: Elegant (burgundy, navy, silver, gold)
- 🎖️ Hình nền: Subtle patterns, floral, elegant borders
- 💎 Font: Sophisticated (Garamond, Baskerville, Didot)
- 🌹 Layout: Classic, timeless

**Elements:**
```
┌─────────────────────────────────────┐
│    [Elegant Logo + Border Design]   │
│                                      │
│         ✨ Celebrating ✨            │
│      {{anniversary.years}} YEARS    │
│                                      │
│    [Hình nền: Subtle gold pattern]  │
│                                      │
│   {{company.name}}                  │
│   cordially invites you to          │
│                                      │
│  Our {{anniversary.event}} Anniversary │
│         Gala Dinner                 │
│                                      │
│  📅 {{event.date}}                  │
│  🕖 {{event.time}}                  │
│  🏨 {{event.venue}}                 │
│                                      │
│  Dress Code: {{event.dressCode}}    │
│                                      │
│  RSVP by {{rsvp.deadline}}          │
│  {{contact.email}} | {{contact.phone}} │
│                                      │
│  [Elegant footer decoration]        │
└─────────────────────────────────────┘
```

### **D. Thiệp Đại Hội (Conference/Convention)**

**Đặc điểm:**
- 🎯 Màu sắc: Corporate (blue, green, professional)
- 📊 Hình nền: Modern, tech-inspired, geometric
- 💻 Font: Modern sans-serif (Arial, Helvetica, Roboto)
- 📋 Layout: Clean, informative

**Elements:**
```
┌─────────────────────────────────────┐
│  [Company Logo] [Event Logo]        │
│                                      │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓         │
│                                      │
│    INVITATION TO ATTEND              │
│   {{event.name}}                    │
│                                      │
│  Theme: {{event.theme}}             │
│                                      │
│  Dear {{guest.name}},               │
│  {{guest.title}}                    │
│  {{guest.organization}}             │
│                                      │
│  📅 Date: {{event.dates}}           │
│  📍 Venue: {{event.venue}}          │
│                                      │
│  📋 AGENDA:                         │
│  {% for session in agenda %}        │
│    • {{session.time}}: {{session.title}} │
│  {% endfor %}                       │
│                                      │
│  🎤 Keynote Speakers:               │
│  {% for speaker in speakers %}      │
│    • {{speaker.name}} - {{speaker.title}} │
│  {% endfor %}                       │
│                                      │
│  Register: {{registration.url}}     │
│  Contact: {{contact.email}}         │
│                                      │
│  [Sponsor logos]                    │
└─────────────────────────────────────┘
```

---

## 🛠️ Technical Implementation

### **1. Word Template với Hình Nền và Logo**

**Cách thêm hình nền vào Word:**
```
1. Design → Watermark → Custom Watermark → Picture Watermark
   - Chọn hình nền đẹp (balloons, confetti, patterns)
   - Điều chỉnh Scale: 100-200%
   - ✅ Washout (để text dễ đọc)

2. Insert → Picture → Place in Background
   - Right-click → Wrap Text → Behind Text
   - Resize to cover page

3. Design → Page Color
   - Chọn màu nền gradient hoặc solid color
```

**Cách thêm Logo:**
```
1. Insert → Picture → From File
   - Chọn logo công ty (PNG with transparent background)
   - Resize: 3-5cm width
   - Position: Top center hoặc top left

2. Format Picture:
   - Wrap Text: In Front of Text
   - Position: Fixed position
```

**Cách thêm Border đẹp:**
```
1. Design → Page Borders
   - Art: Chọn pattern phù hợp event
   - Color: Match với theme color
   - Width: 20-31pt
   
2. Hoặc Insert → Shapes → Rectangle
   - Tạo frame border custom
   - Format: No Fill, Colored Outline
```

### **2. Variables cho Adobe Document Generation**

**Template syntax:**
```
Single value: {{variable.name}}
Loop: {% for item in list %} ... {% endfor %}
Conditional: {% if condition %} ... {% endif %}
```

**JSON data structure:**
```json
{
  "event": {
    "type": "birthday|grand_opening|anniversary|conference",
    "title": "Event Title",
    "date": "DD/MM/YYYY",
    "time": "HH:MM",
    "venue": "Address"
  },
  "guest": {
    "name": "Guest Full Name",
    "title": "Position/Title",
    "organization": "Company Name"
  },
  "host": {
    "name": "Host Name",
    "logo": "path/to/logo.png",
    "contact": {
      "phone": "0123456789",
      "email": "email@example.com"
    }
  },
  "details": {
    "agenda": [...],
    "speakers": [...],
    "sponsors": [...]
  }
}
```

### **3. Color Schemes Chuyên Nghiệp**

**Birthday:**
- Primary: `#FF69B4` (Hot Pink)
- Secondary: `#87CEEB` (Sky Blue)
- Accent: `#FFD700` (Gold)
- Background: `#FFF5EE` (Seashell)

**Grand Opening:**
- Primary: `#C41E3A` (Cardinal Red)
- Secondary: `#FFD700` (Gold)
- Accent: `#FFFFFF` (White)
- Background: `#FFF8DC` (Cornsilk)

**Anniversary:**
- Primary: `#800020` (Burgundy)
- Secondary: `#C0C0C0` (Silver)
- Accent: `#FFD700` (Gold)
- Background: `#F5F5DC` (Beige)

**Conference:**
- Primary: `#003366` (Navy Blue)
- Secondary: `#00A86B` (Jade Green)
- Accent: `#FF6600` (Orange)
- Background: `#F0F8FF` (Alice Blue)

---

## 📦 Free Resources

### **Hình nền miễn phí:**
- Unsplash.com - High quality background images
- Freepik.com - Patterns, textures, decorative elements
- Pexels.com - Free stock photos
- Pixabay.com - Royalty-free images

### **Icon & Decorations:**
- Flaticon.com - Icons for events
- Noun Project - Simple, elegant icons
- Iconfinder.com - Premium and free icons

### **Fonts đẹp:**
- Google Fonts (miễn phí):
  - **Elegant:** Playfair Display, Cormorant, Cinzel
  - **Modern:** Montserrat, Raleway, Lato
  - **Fun:** Pacifico, Lobster, Dancing Script
  - **Professional:** Roboto, Open Sans, Source Sans Pro

---

## 💡 Best Practices

### **1. Design Principles:**
- ✅ **Contrast:** Text phải đọc được rõ trên background
- ✅ **Hierarchy:** Title > Subtitle > Body > Footer
- ✅ **White Space:** Đừng nhồi nhét quá nhiều info
- ✅ **Alignment:** Căn chỉnh đều đặn (center/left)
- ✅ **Consistency:** Dùng 2-3 fonts max, 3-4 colors max

### **2. Content Structure:**
```
1. HEADER (20%)
   - Logo + Event name
   - Eye-catching title

2. BODY (60%)
   - Guest name (personalized)
   - Event details (date, time, venue)
   - Special notes/agenda
   - Call-to-action (RSVP)

3. FOOTER (20%)
   - Contact info
   - Decorative elements
   - Company slogan/tagline
```

### **3. Print Specifications:**
- **Size:** A5 (148×210mm) hoặc A6 (105×148mm)
- **Orientation:** Portrait hoặc Landscape
- **Resolution:** 300 DPI minimum
- **Bleed:** 3mm extra on all sides
- **Color Mode:** CMYK (for print), RGB (for digital)

---

## 🎯 Implementation Plan

### **Phase 1: Design Template**
1. Chọn event type (birthday, grand opening, etc.)
2. Pick color scheme
3. Find/create background image
4. Design layout in Word
5. Add placeholders {{variables}}

### **Phase 2: Create JSON Schema**
1. Define all variables needed
2. Create sample data
3. Test with Adobe Document Generation API

### **Phase 3: Generate & Test**
1. Upload template.docx
2. Send JSON data
3. Generate PDF
4. Review quality
5. Iterate design if needed

---

**Next Step:** Bạn muốn tôi tạo template thực tế cho loại thiệp nào? 🎨
- 🎂 Sinh nhật
- 🏢 Khai trương
- 💝 Lễ kỷ niệm
- 📊 Đại hội/Hội nghị
