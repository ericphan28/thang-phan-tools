# 🚀 VĂN BẢN PROCESSING ROADMAP - Priority Features

## 📋 CONTEXT

**Mục tiêu:** Tập trung vào xử lý văn bản cho cán bộ nhà nước
**Payment:** Manual admin subscription (skip payment gateway)
**Target Users:** 500k+ cán bộ các cơ quan nhà nước

---

## ✅ COMPLETED

- ✅ **Quota System** - Limit AI usage by tier
- ✅ **Admin Subscription Tool** - Manual user/subscription management
- ✅ **OCR Basic** - Tesseract, Gemini, Claude comparison

---

## 🔴 PHASE 1: OCR TIẾNG VIỆT PRODUCTION (PRIORITY: CRITICAL)

**Timeline:** 3-4 days  
**Objective:** OCR scan tài liệu tiếng Việt → Word chất lượng cao

### **Pain Point:**
Cán bộ nhận văn bản scan/fax → Phải đánh máy lại (2-3 giờ/văn bản 10 trang)

### **Solution:**
```
Input: PDF scan hoặc ảnh (công văn, quyết định, báo cáo)
       ↓
   Gemini 2.0 Flash Vision OCR (98% accuracy Vietnamese)
       ↓
Output: Word file (.docx) chỉnh sửa được
```

### **Implementation:**

#### 1. **Backend Endpoint** (`/documents/ocr-to-word`)
```python
@router.post("/ocr-to-word")
async def ocr_to_word(
    file: UploadFile,  # PDF scan hoặc ảnh
    preserve_layout: bool = True,  # Giữ nguyên layout
    output_format: str = "docx",  # docx hoặc txt
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check quota
    QuotaService.check_ai_quota(current_user, db)
    
    # OCR with Gemini
    text = await gemini_ocr(file, language="vi")
    
    # Format to Word with layout
    docx_path = create_word_with_layout(text, preserve_layout)
    
    db.commit()  # Commit quota usage
    return FileResponse(docx_path)
```

#### 2. **Frontend Page** (`OCRToWordPage.tsx`)
```tsx
Features:
- Drag & drop multi-file upload (hàng loạt scan)
- Real-time preview (PDF → extracted text)
- Layout preservation toggle
- Batch processing (10 files → 10 Word files)
- Progress bar
- Download zip with all results
```

#### 3. **Gemini Optimization**
```python
# Prompt engineering for Vietnamese OCR
prompt = f"""
Bạn là chuyên gia OCR tiếng Việt. Hãy trích xuất CHÍNH XÁC toàn bộ văn bản từ ảnh.

YÊU CẦU:
- Giữ NGUYÊN định dạng (tiêu đề, đoạn văn, bullet points)
- Sửa lỗi dấu thanh tiếng Việt (nếu có)
- Bảng biểu: Format Markdown table
- Chữ ký/con dấu: Ghi [CHỮ KÝ], [CON DẤU]

OUTPUT: Chỉ văn bản đã OCR, KHÔNG giải thích.
"""
```

**Deliverables:**
- ✅ Endpoint `/ocr-to-word` with quota check
- ✅ Frontend page với batch upload
- ✅ Word export với layout preservation
- ✅ Error handling (file quá mờ, không phải scan)

**Success Metrics:**
- ⏱️ <30s per page
- ✅ 95%+ accuracy (Vietnamese text)
- 📊 90%+ layout preservation

---

## 🔴 PHASE 2: FORMAL WRITING OPTIMIZATION (PRIORITY: CRITICAL)

**Timeline:** 2-3 days  
**Objective:** Tự động sửa văn phong văn bản hành chính chuẩn

### **Pain Point:**
Chuyên viên mới viết văn bản không chuẩn → Trưởng phòng sửa 3-5 lần (20 giờ/tháng)

### **Solution:**
```
Input: Văn bản nháp (informal)
       ↓
   Gemini 2.5 Flash (formal style transfer)
       ↓
Output: Văn bản chuẩn hành chính (track changes)
```

### **Implementation:**

#### 1. **Backend Service** (`formal_writing_service.py`)
```python
class FormalWritingService:
    TONE_TEMPLATES = {
        "cong_van": "Văn phong công văn hành chính (Thông tư 01/2011/TT-BNV)",
        "quyet_dinh": "Văn phong quyết định (chính thức, pháp lý)",
        "bao_cao": "Văn phong báo cáo (chính xác, khách quan)",
        "to_trinh": "Văn phong tờ trình (đề xuất, thuyết phục)"
    }
    
    async def optimize(self, text: str, doc_type: str) -> dict:
        prompt = f"""
Bạn là chuyên gia văn bản hành chính Việt Nam.

NHIỆM VỤ: Chỉnh sửa văn bản sau theo chuẩn {self.TONE_TEMPLATES[doc_type]}

YÊU CẦU:
1. Sửa lỗi chính tả, ngữ pháp
2. Chuẩn hóa thuật ngữ hành chính
3. Đảm bảo cấu trúc: Kính gửi → Nội dung → Đề nghị → Nơi nhận
4. Loại bỏ thông tin không cần thiết

INPUT:
{text}

OUTPUT JSON:
{{
    "optimized_text": "...",
    "changes": [
        {{"line": 5, "old": "...", "new": "...", "reason": "Sửa lỗi chính tả"}},
        ...
    ],
    "warnings": ["Thiếu số ký hiệu văn bản", ...]
}}
"""
        
        response = await gemini.generate_content(prompt)
        return json.loads(response.text)
```

#### 2. **Frontend Component** (`FormalWritingEditor.tsx`)
```tsx
Features:
- Side-by-side editor (Before | After)
- Track changes highlighting
- Accept/Reject individual changes
- Document type selector (công văn, quyết định, báo cáo)
- Export to Word with track changes
```

**Deliverables:**
- ✅ 4 document type templates
- ✅ Change tracking system
- ✅ Side-by-side comparison UI
- ✅ Export with Word track changes

**Success Metrics:**
- ⏱️ <10s per document
- ✅ 90%+ acceptance rate (changes approved by users)
- 📉 80% reduction in revision cycles

---

## 🟠 PHASE 3: DATA CONFLICT DETECTION (PRIORITY: HIGH)

**Timeline:** 3-4 days  
**Objective:** Tự động phát hiện mâu thuẫn số liệu trong báo cáo tổng hợp

### **Pain Point:**
Phòng A báo 125 tỷ, Phòng B báo 132 tỷ cùng 1 chỉ tiêu → Lãnh đạo phát hiện trong họp

### **Solution:**
```
Input: Multi-source reports (Word, Excel, PDF)
       ↓
   Gemini 2.5 Pro (semantic analysis + cross-check)
       ↓
Output: Conflict report với highlight mismatches
```

### **Implementation:**

#### 1. **Backend Service** (`conflict_detection_service.py`)
```python
async def detect_conflicts(files: List[UploadFile]) -> dict:
    # Extract all data points
    all_data = {}
    for file in files:
        data = await extract_structured_data(file)  # Tables, numbers, dates
        all_data[file.filename] = data
    
    # Cross-check with Gemini
    prompt = f"""
Phân tích các báo cáo sau và tìm MÂU THUẪN về số liệu:

{json.dumps(all_data, ensure_ascii=False, indent=2)}

Tìm các mâu thuẫn:
- Cùng chỉ tiêu nhưng khác số liệu
- Tổng số không khớp với chi tiết
- Ngày tháng không logic

OUTPUT JSON:
{{
    "conflicts": [
        {{
            "metric": "Tổng vốn đầu tư",
            "sources": [
                {{"file": "phong_a.docx", "value": "125 tỷ", "line": 15}},
                {{"file": "phong_b.docx", "value": "132 tỷ", "line": 23}}
            ],
            "severity": "high",
            "suggestion": "Liên hệ Phòng A, Phòng B để đối chiếu"
        }}
    ],
    "summary": {{
        "total_conflicts": 3,
        "high_severity": 1,
        "medium_severity": 2
    }}
}}
"""
    
    response = await gemini.generate_content(prompt, model="gemini-2.5-pro")
    return json.loads(response.text)
```

#### 2. **Frontend Component** (`ConflictDashboard.tsx`)
```tsx
Features:
- Upload multiple files (drag & drop)
- Conflict table with severity colors
- Click to jump to source location
- Side-by-side file comparison
- Export conflict report (Excel)
```

**Deliverables:**
- ✅ Multi-file analysis engine
- ✅ Conflict severity classification
- ✅ Interactive dashboard
- ✅ Export conflict report

**Success Metrics:**
- ⏱️ <2 minutes for 10 files
- ✅ 95%+ conflict detection accuracy
- 📉 50% reduction in meeting time (pre-checked)

---

## 🟡 PHASE 4: AUTO CHART GENERATION (PRIORITY: MEDIUM)

**Timeline:** 2-3 days  
**Objective:** Tự động tạo biểu đồ từ bảng số liệu

### **Pain Point:**
Cán bộ không biết Excel → Copy số vào PowerPoint thủ công (60 giờ/tháng)

### **Solution:**
```
Input: Table (Word/Excel/PDF)
       ↓
   Extract data + Gemini suggest chart type
       ↓
Output: Beautiful charts (PNG, PowerPoint)
```

### **Implementation:**

#### 1. **Backend Service** (`chart_generation_service.py`)
```python
async def generate_chart(data: dict, user_preference: str = "auto") -> bytes:
    # Gemini suggests best chart type
    prompt = f"""
Dữ liệu:
{json.dumps(data)}

Gợi ý loại biểu đồ tốt nhất (bar, line, pie, combo) và lý do.
"""
    
    suggestion = await gemini.generate_content(prompt)
    chart_type = extract_chart_type(suggestion)
    
    # Generate with plotly/matplotlib
    fig = create_chart(data, chart_type, style="professional")
    
    # Export
    return fig.to_image(format="png", width=1200, height=800)
```

#### 2. **Frontend Component** (`ChartGenerator.tsx`)
```tsx
Features:
- Upload file with table → Auto-detect tables
- Chart type selector (with AI suggestion)
- Live preview
- Style customization (colors, fonts)
- Export: PNG, PowerPoint, Excel chart
```

**Deliverables:**
- ✅ Auto table detection
- ✅ 5 chart types (bar, line, pie, combo, scatter)
- ✅ Professional styling
- ✅ Multi-format export

**Success Metrics:**
- ⏱️ <15s per chart
- ✅ 85%+ chart type suggestion accuracy
- 📊 80% time saved vs manual Excel

---

## 🟢 PHASE 5: AI REPORT ASSISTANT (PRIORITY: LOW)

**Timeline:** 4-5 days  
**Objective:** Hỗ trợ viết báo cáo 6 tháng/năm từ dữ liệu thô

### **Solution:**
```
Input: Raw data + Outline
       ↓
   Gemini 2.5 Pro (long-form writing)
       ↓
Output: Draft report (20+ pages)
```

**Features:**
- Auto outline generation
- Section-by-section writing
- Insert charts automatically
- Citation management

*(Chi tiết implement sau khi Phase 1-4 done)*

---

## 📊 IMPLEMENTATION PRIORITY

| Phase | Feature | Priority | Effort | Impact | Timeline |
|-------|---------|----------|--------|--------|----------|
| **1** | 🔍 **OCR Vietnamese** | 🔴 Critical | Medium | 🔴 Huge | **3-4 days** |
| **2** | ✍️ **Formal Writing** | 🔴 Critical | Low | 🔴 Huge | **2-3 days** |
| **3** | 🔎 **Conflict Detection** | 🟠 High | Medium | 🟠 High | **3-4 days** |
| **4** | 📊 **Chart Generation** | 🟡 Medium | Low | 🟡 Medium | **2-3 days** |
| **5** | 📝 **Report Assistant** | 🟢 Low | High | 🟡 Medium | **4-5 days** |

**Total:** 14-19 days (3-4 weeks)

---

## ⏭️ NEXT IMMEDIATE ACTIONS

**TODAY:**
1. ✅ Test admin subscription tool
   ```bash
   python admin_subscription.py create canbo@test.com canbo1 Pass123! "Test User" PRO
   python admin_subscription.py list
   ```

2. 🚀 Start Phase 1: OCR Vietnamese
   - Create `/documents/ocr-to-word` endpoint
   - Implement Gemini OCR with Vietnamese prompt
   - Build OCRToWordPage.tsx

**WEEK 1:** Phase 1 + Phase 2 (OCR + Formal Writing)  
**WEEK 2:** Phase 3 (Conflict Detection)  
**WEEK 3:** Phase 4 (Chart Generation)

---

Ready to start Phase 1 (OCR Vietnamese)?
