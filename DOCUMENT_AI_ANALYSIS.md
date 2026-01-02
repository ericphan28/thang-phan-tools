# 📄 PHÂN TÍCH NGHIỆP VỤ HỆ THỐNG XỬ LÝ VĂN BẢN BẰNG AI

## 🎯 TỔNG QUAN NGHIỆP VỤ

Dựa trên bộ câu hỏi hỗ trợ soạn thảo báo cáo, hệ thống cần xây dựng **3 nhóm chức năng chính**:

### I. NHÓM XỬ LÝ DỮ LIỆU ĐẦU VÀO (Input Processing)
- Trích xuất & phân tích văn bản
- Xử lý số liệu thống kê
- So sánh & đánh giá dữ liệu
- Tổng hợp & phân loại thông tin

### II. NHÓM XÂY DỰNG NỘI DUNG (Content Generation)
- Đề xuất bố cục báo cáo
- Viết phần đánh giá kết quả
- Viết phần hạn chế/khó khăn
- Viết phần kiến nghị/đề xuất

### III. NHÓM HOÀN THIỆN VĂN BẢN (Document Refinement)
- Chỉnh sửa văn phong hành chính
- Tạo tóm tắt (Abstract)
- Kiểm tra độ chính xác

---

## 🏗️ KIẾN TRÚC HỆ THỐNG

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND UI                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Upload Docs  │  │ AI Assistant │  │ Export Result│      │
│  │ & Data       │  │ (Chat)       │  │ (Word/PDF)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND API                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │              Document Processing Flow              │     │
│  │                                                     │     │
│  │  1. Upload → 2. Extract → 3. Analyze → 4. Generate│     │
│  │             ↓                 ↓           ↓         │     │
│  │         OCR/Parse         Gemini AI   Template    │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    AI PROVIDER (Gemini)                      │
│  - Text Analysis & Extraction                                │
│  - Statistical Analysis                                      │
│  - Content Generation                                        │
│  - Style & Grammar Check                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 DATABASE SCHEMA

### 1. Documents Table (Văn bản nguồn)
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    project_id INTEGER REFERENCES projects(id),
    title VARCHAR(500),
    file_type VARCHAR(50), -- pdf, docx, txt, image
    file_path VARCHAR(500),
    file_size INTEGER,
    extracted_text TEXT,
    metadata JSONB, -- {pages: 10, word_count: 5000, ...}
    status VARCHAR(50), -- uploaded, processing, extracted, error
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 2. Projects Table (Dự án báo cáo)
```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(500),
    description TEXT,
    report_type VARCHAR(100), -- periodic, special, summary, proposal
    department VARCHAR(200),
    period VARCHAR(100), -- "Tháng 12/2025", "Quý IV/2025", "Năm 2025"
    status VARCHAR(50), -- draft, in_progress, review, completed
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 3. AI Tasks Table (Các tác vụ AI)
```sql
CREATE TABLE ai_tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    user_id INTEGER REFERENCES users(id),
    task_type VARCHAR(100), -- extract, analyze, compare, generate, refine
    task_group VARCHAR(50), -- group_1, group_2, group_3
    input_data JSONB, -- {documents: [...], parameters: {...}}
    prompt TEXT,
    ai_response TEXT,
    tokens_used INTEGER,
    cost_vnd DECIMAL(10,2),
    status VARCHAR(50), -- pending, processing, completed, error
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

### 4. Report Sections Table (Các phần của báo cáo)
```sql
CREATE TABLE report_sections (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    section_type VARCHAR(100), -- introduction, overview, statistics, 
                                -- evaluation, challenges, recommendations, conclusion
    section_order INTEGER,
    title VARCHAR(500),
    content TEXT,
    ai_generated BOOLEAN DEFAULT false,
    reviewed BOOLEAN DEFAULT false,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 5. Statistical Data Table (Dữ liệu thống kê)
```sql
CREATE TABLE statistical_data (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    data_type VARCHAR(100), -- table, chart, number, percentage
    label VARCHAR(500),
    data_json JSONB, -- {headers: [...], rows: [...]} or {labels: [...], values: [...]}
    source VARCHAR(500), -- "Phòng KH-TC", "Sở XYZ"
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6. Templates Table (Mẫu báo cáo)
```sql
CREATE TABLE report_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500),
    report_type VARCHAR(100),
    department_type VARCHAR(200),
    structure JSONB, -- [{section: "Phần 1", subsections: [...]}, ...]
    sample_content TEXT,
    is_active BOOLEAN DEFAULT true,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔄 WORKFLOW LOGIC

### PHASE 1: Chuẩn bị dữ liệu (Data Preparation)

```
User → Tạo Project mới
     → Upload văn bản nguồn (PDF, Word, Image)
     → Nhập/Import số liệu thống kê (Excel, CSV)
     → Chọn loại báo cáo & mẫu template
```

**API Endpoints:**
```
POST   /api/v1/projects                 # Tạo project
POST   /api/v1/projects/{id}/documents  # Upload tài liệu
POST   /api/v1/projects/{id}/statistics # Import số liệu
GET    /api/v1/templates                # Lấy danh sách mẫu
```

---

### PHASE 2: Xử lý với AI - Group 1 (Input Processing)

#### Task 1: Trích xuất văn bản & Tài liệu
```python
PROMPT_TEMPLATE = """
Bạn là trợ lý AI chuyên nghiệp phục vụ cơ quan Nhà nước Việt Nam.

Nhiệm vụ: Phân tích văn bản sau và trích xuất thông tin theo yêu cầu.

Văn bản nguồn:
{document_text}

Yêu cầu:
1. Xác định loại văn bản (Công văn, Quyết định, Thông báo, Báo cáo, Tờ trình...)
2. Trích xuất: Số/ký hiệu, Ngày, Người ký, Cơ quan ban hành
3. Tóm tắt nội dung chính (3-5 câu)
4. Liệt kê các yêu cầu/chỉ đạo quan trọng (nếu có)

Trả lời dưới dạng JSON:
{
  "document_type": "...",
  "number": "...",
  "date": "...",
  "signer": "...",
  "agency": "...",
  "summary": "...",
  "key_requirements": [...]
}
"""
```

#### Task 2: Phân tích số liệu thống kê
```python
PROMPT_TEMPLATE = """
Phân tích bảng số liệu sau và đánh giá xu hướng:

Dữ liệu:
{statistical_data_json}

Yêu cầu:
1. Xác định xu hướng tăng/giảm của các chỉ tiêu
2. Tìm các điểm bất thường (outliers)
3. Tính tỷ lệ hoàn thành so với kế hoạch (nếu có)
4. Đánh giá tổng thể: Tích cực/Tiêu cực/Trung bình

Trả lời dưới dạng JSON có cấu trúc rõ ràng.
"""
```

#### Task 3: So sánh & Đánh giá
```python
PROMPT_TEMPLATE = """
So sánh kết quả giữa các đơn vị/thời kỳ sau:

Dữ liệu:
{comparison_data}

Yêu cầu:
1. So sánh kết quả giữa [Đơn vị A] và [Đơn vị B]
2. Tính bình chung của các chỉ tiêu
3. Xác định đơn vị xuất sắc nhất/cần cải thiện
4. Phân tích nguyên nhân khác biệt (dựa trên dữ liệu)

Trả lời bằng văn phong chuyên nghiệp, có số liệu minh chứng.
"""
```

#### Task 4: Tổng hợp & Phân loại
```python
PROMPT_TEMPLATE = """
Đã cung cấp: {num_documents} văn bản và {num_reports} báo cáo.

Yêu cầu:
1. Tổng hợp và phân loại theo nhóm vấn đề:
   - Nhóm 1: Thể chế/Chính sách
   - Nhóm 2: Nguồn lực (nhân lực, tài chính, vật chất)
   - Nhóm 3: Phối hợp liên ngành
   - Nhóm 4: Khác

2. Đối với mỗi nhóm:
   - Liệt kê khó khăn/vướng mắc cụ thể
   - Đánh giá mức độ tác động: Cao/Trung bình/Thấp
   - Gợi ý nguyên nhân

Trả lời dưới dạng có cấu trúc, dễ chuyển thành nội dung báo cáo.
"""
```

---

### PHASE 3: Xử lý với AI - Group 2 (Content Generation)

#### Task 5: Đề xuất Bố cục Chung
```python
PROMPT_TEMPLATE = """
Dựa trên dữ liệu đã phân tích, đề xuất bố cục chi tiết cho báo cáo:

Loại báo cáo: {report_type}
Phạm vi: {scope}
Thời gian: {period}

Yêu cầu:
- Đề xuất bố cục chuẩn mẫu hành chính Việt Nam
- Bao gồm các phần: Mở đầu, Nội dung chính (I, II, III...), Kết luận/Kiến nghị
- Mỗi phần có mục đích rõ ràng

Trả lời:
{
  "title": "...",
  "sections": [
    {
      "number": "I",
      "title": "...",
      "purpose": "...",
      "subsections": [...]
    },
    ...
  ]
}
"""
```

#### Task 6: Viết Phần Đánh giá Kết quả
```python
PROMPT_TEMPLATE = """
Viết phần "Đánh giá kết quả đạt được" cho báo cáo.

Dữ liệu:
{achievements_data}

Yêu cầu:
- Sử dụng số liệu minh chứng quan trọng nhất
- Văn phong: Nghiêm túc, khách quan, chuyên nghiệp
- Cấu trúc: Thành tựu chung → Chi tiết từng lĩnh vực → Điểm nổi bật
- Độ dài: Khoảng {target_length} từ

Viết thành văn bản hoàn chỉnh, sẵn sàng paste vào báo cáo.
"""
```

#### Task 7: Viết Phần Hạn chế/Khó khăn
```python
PROMPT_TEMPLATE = """
Viết phần "Hạn chế, tồn tại" cho báo cáo.

Dữ liệu:
{challenges_data}

Yêu cầu:
- Tổng hợp theo nhóm nguyên nhân (như đã phân loại trước đó)
- Đánh giá tác động của từng hạn chế
- Văn phong: Thẳng thắn, có tính xây dựng
- Tránh đùn đẩy trách nhiệm, tập trung vào giải pháp

Viết thành văn bản hoàn chỉnh.
"""
```

#### Task 8: Viết Phần Kiến nghị
```python
PROMPT_TEMPLATE = """
Viết phần "Kiến nghị" cho báo cáo.

Dữ liệu hạn chế:
{challenges_data}

Yêu cầu:
- Đề xuất giải pháp/kiến nghị cụ thể và khả thi
- Gửi đến: {target_agencies} (Cơ quan cấp trên/Đơn vị liên quan)
- Mỗi kiến nghị cần rõ ràng về:
  * Đối tượng thực hiện
  * Nội dung công việc cụ thể
  * Thời hạn (nếu có)

Viết thành văn bản hoàn chỉnh, có tính chất chỉ đạo.
"""
```

---

### PHASE 4: Xử lý với AI - Group 3 (Document Refinement)

#### Task 9: Chỉnh sửa Văn phong Hành chính
```python
PROMPT_TEMPLATE = """
Chỉnh sửa toàn bộ bản nháp báo cáo sau để đảm bảo văn phong hành chính chuẩn mực:

Bản nháp:
{draft_content}

Yêu cầu:
- Văn phong: Chính luận, trang trọng, nghiêm túc
- Sử dụng đúng thuật ngữ chuyên ngành của {department}
- Sử dụng đúng từ xưng hô, kính ngữ (Kính gửi, Kính báo cáo...)
- Cấu trúc câu rõ ràng, logic
- Tránh lặp từ, diễn đạt dài dòng

Trả về văn bản đã chỉnh sửa hoàn chỉnh.
"""
```

#### Task 10: Tạo Tóm tắt (Abstract)
```python
PROMPT_TEMPLATE = """
Soạn thảo phần "Tóm tắt" (Abstract) cho báo cáo.

Nội dung báo cáo đầy đủ:
{full_report_content}

Yêu cầu:
- Độ dài: Không quá 1/3 trang A4 (khoảng 150-200 từ)
- Bao gồm: 
  * Mục tiêu báo cáo
  * Kết quả chính (2-3 điểm quan trọng nhất)
  * Kiến nghị quan trọng nhất (1-2 điểm)
- Văn phong: Súc tích, rõ ràng, đầy đủ

Viết thành văn bản hoàn chỉnh.
"""
```

#### Task 11: Kiểm tra Độ chính xác
```python
PROMPT_TEMPLATE = """
Rà soát lại toàn bộ báo cáo và kiểm tra các lỗi:

Báo cáo:
{report_content}

Yêu cầu kiểm tra:
1. Lỗi chính tả, lỗi ngữ pháp
2. Lỗi định dạng số liệu (dấu phẩy, dấu chấm, đơn vị)
3. Mâu thuẫn giữa các phần (số liệu không khớp)
4. Tính nhất quán về thuật ngữ, tên riêng

Trả về:
{
  "errors_found": [
    {
      "type": "spelling/grammar/data/consistency",
      "location": "...",
      "description": "...",
      "suggestion": "..."
    }
  ],
  "corrected_content": "..." // Nếu có lỗi
}
"""
```

---

## 🎨 UI/UX WORKFLOW

### Màn hình chính: Document AI Assistant

```
┌────────────────────────────────────────────────────────────┐
│  📁 Dự án: Báo cáo tháng 12/2025 - Phòng KH-TC            │
│  ├── 📄 Văn bản đã upload (5)                              │
│  ├── 📊 Số liệu thống kê (3 bảng)                          │
│  └── 🤖 Trợ lý AI (11 tác vụ)                              │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  💬 Chat với AI Assistant                           │  │
│  │                                                      │  │
│  │  [User]: Hãy phân tích văn bản số 123/CV-ABC       │  │
│  │                                                      │  │
│  │  [AI]: ✓ Đã phân tích văn bản:                      │  │
│  │     - Loại: Công văn                                │  │
│  │     - Nội dung: V/v thanh tra tài chính...          │  │
│  │     - Yêu cầu: [1] Báo cáo trước 25/12...           │  │
│  │                                                      │  │
│  │  [User]: Tạo bố cục báo cáo cho tôi                │  │
│  │                                                      │  │
│  │  [AI]: ✓ Đề xuất bố cục:                            │  │
│  │     I. Tổng quan tình hình                          │  │
│  │     II. Kết quả đạt được                            │  │
│  │     III. Hạn chế, tồn tại                           │  │
│  │     IV. Phương hướng, giải pháp                     │  │
│  │                                                      │  │
│  │     [Áp dụng bố cục này] [Chỉnh sửa]               │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  📝 Soạn thảo nội dung                               │  │
│  │                                                      │  │
│  │  I. TỔNG QUAN TÌNH HÌNH                             │  │
│  │  [Nội dung AI đã tạo... Click để chỉnh sửa]         │  │
│  │                                                      │  │
│  │  II. KẾT QUẢ ĐẠT ĐƯỢC                               │  │
│  │  [🤖 Nhấn để AI viết phần này]                      │  │
│  │                                                      │  │
│  │  [💾 Lưu nháp] [📤 Xuất Word] [🔍 Kiểm tra AI]      │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### Sidebar: Quick Actions

```
🎯 Tác vụ nhanh:
├── 📥 1. Trích xuất văn bản
├── 📊 2. Phân tích số liệu
├── ⚖️  3. So sánh dữ liệu
├── 📑 4. Tổng hợp & phân loại
├── 🏗️  5. Tạo bố cục
├── ✍️  6. Viết phần đánh giá
├── ⚠️  7. Viết phần hạn chế
├── 💡 8. Viết phần kiến nghị
├── 🎨 9. Chỉnh văn phong
├── 📝 10. Tạo tóm tắt
└── ✅ 11. Kiểm tra lỗi
```

---

## 🔧 API IMPLEMENTATION

### Base Endpoint Pattern
```
POST /api/v1/ai/tasks
```

**Request Body:**
```json
{
  "project_id": 123,
  "task_type": "extract_document", // hoặc các task khác
  "task_group": "group_1",
  "input_data": {
    "document_ids": [1, 2, 3],
    "statistical_data_ids": [10, 11],
    "parameters": {
      "report_type": "periodic",
      "target_length": 500,
      "department": "Phòng Kế hoạch - Tài chính"
    }
  },
  "use_history": true // Có sử dụng context từ các task trước không
}
```

**Response:**
```json
{
  "task_id": 456,
  "status": "completed",
  "ai_response": {
    "type": "json" | "text",
    "content": "...",
    "suggestions": ["Gợi ý 1", "Gợi ý 2"]
  },
  "tokens_used": 1500,
  "cost_vnd": 3000,
  "completed_at": "2025-12-26T10:30:00Z"
}
```

---

## 💰 COST OPTIMIZATION

### 1. Sử dụng Context thông minh
- Lưu kết quả của các task trước
- Khi task mới cần context, chỉ gửi tóm tắt (summary) thay vì toàn bộ

### 2. Caching
- Cache các phân tích phổ biến (template, mẫu câu)
- Cache kết quả của các văn bản tương tự

### 3. Batch Processing
- Gộp nhiều task nhỏ thành 1 request lớn
- VD: Phân tích 5 văn bản cùng lúc thay vì 5 lần riêng

### 4. Token Limit
```python
# Ước tính tokens trước khi gửi
def estimate_tokens(text: str) -> int:
    # 1 token ≈ 4 characters (Vietnamese)
    return len(text) // 4

# Truncate nếu quá dài
MAX_TOKENS_PER_REQUEST = 30000  # Gemini 1.5 Pro limit
if estimate_tokens(prompt) > MAX_TOKENS_PER_REQUEST:
    prompt = truncate_smartly(prompt, MAX_TOKENS_PER_REQUEST)
```

---

## 📦 EXPORT FEATURES

### 1. Export to Word (.docx)
```python
from docx import Document

def export_to_word(report_data: dict) -> bytes:
    doc = Document()
    
    # Header
    doc.add_heading(report_data['title'], 0)
    
    # Sections
    for section in report_data['sections']:
        doc.add_heading(section['title'], level=1)
        doc.add_paragraph(section['content'])
        
        # Statistics tables
        if section.get('tables'):
            for table_data in section['tables']:
                add_table(doc, table_data)
    
    # Footer
    add_signature(doc, report_data['signature'])
    
    return save_to_bytes(doc)
```

### 2. Export to PDF
```python
from docx2pdf import convert

def export_to_pdf(word_bytes: bytes) -> bytes:
    # Save word temporarily
    temp_word = save_temp(word_bytes)
    temp_pdf = temp_word.replace('.docx', '.pdf')
    
    # Convert
    convert(temp_word, temp_pdf)
    
    # Read PDF
    with open(temp_pdf, 'rb') as f:
        pdf_bytes = f.read()
    
    # Cleanup
    cleanup_temp([temp_word, temp_pdf])
    
    return pdf_bytes
```

---

## 🚀 DEPLOYMENT PLAN

### Phase 1: MVP (2-3 tuần)
- ✅ Tạo project & upload tài liệu
- ✅ Task 1-4: Nhóm xử lý dữ liệu đầu vào
- ✅ Chat interface với AI
- ✅ Export to Word (basic)

### Phase 2: Core Features (3-4 tuần)
- ✅ Task 5-8: Nhóm xây dựng nội dung
- ✅ Template system
- ✅ Statistical data import/visualization
- ✅ Rich text editor cho soạn thảo

### Phase 3: Advanced (2-3 tuần)
- ✅ Task 9-11: Nhóm hoàn thiện văn bản
- ✅ Version control cho báo cáo
- ✅ Collaboration features
- ✅ Export to PDF với formatting đẹp

---

## 🎯 SUCCESS METRICS

1. **Hiệu quả:**
   - Giảm 70% thời gian soạn thảo báo cáo
   - Tăng 50% chất lượng nội dung (đo bằng số lần chỉnh sửa)

2. **Chi phí:**
   - Trung bình 10,000 - 30,000 VNĐ/báo cáo (tùy độ phức tạp)
   - < 50,000 VNĐ cho báo cáo phức tạp nhất

3. **Trải nghiệm:**
   - User satisfaction > 4.5/5
   - Completion rate > 80%

---

## 📌 LƯU Ý KỸ THUẬT

### 1. Prompt Engineering
- Luôn cung cấp context đầy đủ (loại báo cáo, phạm vi, thời gian)
- Sử dụng few-shot examples cho kết quả tốt hơn
- Yêu cầu output dạng JSON cho dễ parse

### 2. Error Handling
- Retry với exponential backoff khi API rate limit
- Fallback sang model khác nếu Gemini unavailable
- Lưu state để có thể resume nếu bị ngắt

### 3. Security
- Sanitize user input trước khi gửi AI
- Không gửi thông tin nhạy cảm (số CMND, mật khẩu...)
- Encrypt data at rest

---

**Tài liệu này sẵn sàng để triển khai thực tế!**

*Cập nhật lần cuối: 26/12/2025*
