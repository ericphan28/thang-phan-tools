# 🏢 UTILITY SERVER - PROJECT CONTEXT

## 📋 PROJECT OVERVIEW

**Project Name:** Utility Server  
**Type:** Full-stack Web Application  
**Purpose:** Multi-purpose utility server for Vietnamese government document processing and PDF operations  
**Tech Stack:** FastAPI (Backend) + React + TypeScript (Frontend)  
**Target Users:** Vietnamese government officials and general users needing document/PDF tools

---

## 🎯 CORE BUSINESS DOMAINS

### 1. 📄 Adobe PDF Services Integration (`/adobe-pdf`)
**Business Purpose:** Professional PDF manipulation using Adobe PDF Services API

**Key Features:**
- **Combine PDF** - Merge multiple PDFs into one document
- **Protect PDF** - Add password protection with encryption
- **Split PDF** - Extract specific pages or ranges
- **Watermark PDF** - Add watermark images to PDFs
- **Linearize PDF** - Optimize PDFs for fast web viewing
- **PDF to Word/Excel/PPT** - Convert PDFs to editable Office formats
- **Word/Excel/PPT to PDF** - Convert Office docs to PDF
- **Compress PDF** - Reduce file size
- **OCR PDF** - Extract text from scanned documents
- **Extract PDF** - Get text, images, tables from PDFs
- **Delete Pages** - Remove specific pages from PDF
- **Rotate Pages** - Change page orientation
- **Reorder Pages** - Rearrange page order
- **Replace Pages** - Swap pages between PDFs
- **Insert Pages** - Add pages from another PDF
- **AutoTag PDF** - Add accessibility tags
- **Document Generation** - Create PDFs from JSON templates
- **Electronic Seal** - Add digital seals/signatures

**Technical Architecture:**
```
Frontend (React) → Backend (FastAPI) → Adobe PDF Services API
                 ↓
              File Storage (temp uploads/downloads)
```

**Authentication:**
- Uses Adobe OAuth credentials (client_id, client_secret)
- Stored in `.env`: `ADOBE_CLIENT_ID`, `ADOBE_CLIENT_SECRET`
- Located in: `backend/app/routers/adobe_pdf_services.py`

**Error Handling:**
- Friendly Vietnamese error messages
- User-friendly explanations for technical errors
- Automatic cleanup of temp files

**File Flow:**
1. User uploads file(s) via frontend
2. Backend receives and validates files
3. Files stored temporarily in `backend/temp_uploads/`
4. Adobe API processes files
5. Result downloaded to `backend/temp_downloads/`
6. Frontend downloads result file
7. Temp files auto-cleaned after 1 hour

---

### 2. 📝 Vietnamese Government Forms (`/mau-2c`)
**Business Purpose:** Digitize and automate Vietnamese government personnel forms (Mẫu 2C - Sơ yếu lý lịch cán bộ)

**What is Mẫu 2C?**
- Official resume/CV form for Vietnamese government officials
- Used for: hiring, promotion, annual reviews, party membership
- Contains: personal info, education, work history, family details, salary progression
- Must follow strict government formatting standards

**Key Features:**
1. **Form Input** - Web form with 116+ fields organized in sections:
   - Personal Information (name, DOB, gender, ethnicity, religion)
   - Contact Details (address, phone, email)
   - Education History (degrees, certifications, training)
   - Work History (positions, departments, dates)
   - Family Information (parents, spouse, children)
   - Spouse Family (in-laws)
   - Salary Progression (pay grades over time)
   - Party Membership (Communist Party details)
   - Awards & Recognition
   - Languages & Skills

2. **Sample Templates** - Pre-filled realistic examples:
   - `can_bo_tre` - Young specialist (27 years, 5 years experience, single)
   - `can_bo_chinh` - Mid-level manager (38 years, Deputy Head, married)
   - `can_bo_cao_cap` - Senior manager (48 years, Department Head, many awards)

3. **Document Generation** - Creates `.docx` file with proper formatting
   - Uses `python-docx` library
   - Matches official government template layout
   - Auto-fills all fields from form data
   - Handles dynamic arrays (education, work history, family)

**Data Structure:**
```typescript
interface Mau2CData {
  // 50+ simple fields
  ho_ten: string;
  gioi_tinh: 'Nam' | 'Nữ';
  ngay: string; // birth day
  thang: string; // birth month
  nam: string; // birth year
  // ... 40+ more fields
  
  // 5 array fields
  dao_tao: Array<{
    tu_nam: string;
    den_nam: string;
    truong: string;
    chuyen_nganh: string;
    trinh_do: string;
  }>;
  
  cong_tac: Array<{
    tu_thang: string;
    den_thang: string;
    chuc_vu: string;
    don_vi: string;
  }>;
  
  gia_dinh: Array<{
    moi_quan_he: string;
    ho_ten: string;
    nam_sinh: string;
    que_quan: string;
    nghe_nghiep: string;
    chuc_danh: string;
  }>;
  
  gia_dinh_vo_chong: Array<{...}>; // same as gia_dinh
  
  luong: Array<{
    tu_ngay: string;
    he_so: string;
    bac_luong: string;
  }>;
}
```

**API Endpoints:**
- `GET /api/mau-2c/sample-templates` - List 3 template options
- `GET /api/mau-2c/sample-data/{template_id}` - Get full template data
- `POST /api/mau-2c/generate-and-download` - Generate Word document

**Vietnamese Context:**
- **Tinh/Huyen/Xa** - Province/District/Ward administrative divisions
- **UBND** - People's Committee (government agency)
- **Dang vien** - Communist Party member
- **Chi bo/Chi uy** - Party cell/committee
- **Bang khen** - Certificate of Merit
- **Chien si thi dua** - Emulation Fighter (honorary title)
- **Huan chuong** - Medal/Order
- **Liet si** - Martyr (fallen soldier)

---

## 🏗️ TECHNICAL ARCHITECTURE

### Backend Structure
```
backend/
├── app/
│   ├── main_simple.py          # Main FastAPI app
│   ├── routers/
│   │   ├── adobe_pdf_services.py  # Adobe PDF endpoints (18 operations)
│   │   └── mau_2c.py              # Mẫu 2C endpoints (3 endpoints)
│   └── utils/
│       └── adobe_credentials.py   # Adobe auth helper
├── temp_uploads/               # User uploaded files (auto-clean)
├── temp_downloads/             # Generated files (auto-clean)
└── templates/                  # Word document templates
    └── mau_2c_template.docx
```

### Frontend Structure
```
frontend/
├── src/
│   ├── pages/
│   │   ├── ToolsPage.tsx       # Adobe PDF tools UI
│   │   └── Mau2CPage.tsx       # Mẫu 2C form UI
│   ├── components/
│   │   ├── adobe/
│   │   │   ├── CombinePDF.tsx
│   │   │   ├── ProtectPDF.tsx
│   │   │   └── ... (18 total components)
│   │   └── layout/
│   │       └── Sidebar.tsx
│   └── config.ts               # API base URL config
```

### API URL Architecture
**IMPORTANT:** Different routers use different URL patterns!

**Legacy endpoints** (auth, users, roles):
```
Frontend: /api/v1/auth/login
Backend:  /api/v1/auth/login
```

**Adobe PDF Services:**
```
Frontend: http://localhost:8000/api/adobe-pdf/combine
Backend:  /api/adobe-pdf/combine
Router:   app.include_router(adobe_router, prefix="/api/adobe-pdf")
```

**Mẫu 2C:**
```
Frontend: http://localhost:8000/api/mau-2c/sample-templates
Backend:  /api/mau-2c/sample-templates
Router:   app.include_router(mau_2c_router, prefix="/api/mau-2c")
```

**Why different?**
- Legacy endpoints designed for nginx proxy in production
- New routers (Adobe, Mẫu 2C) use direct backend calls
- Frontend must use absolute URLs for new routers to avoid `/api/v1` prefix

---

## 🔧 COMMON ISSUES & SOLUTIONS

### Issue 1: URL Path Duplication (404 Errors)
**Symptom:** Frontend gets 404 when calling new routers
```
Error: GET http://localhost:8000/api/v1/api/mau-2c/sample-templates 404
```

**Root Cause:** Using `API_BASE_URL` (which is `/api/v1`) for new routers
```typescript
// ❌ WRONG
const API_BASE = API_BASE_URL; // '/api/v1'
axios.get(`${API_BASE}/api/mau-2c/...`); // → /api/v1/api/mau-2c/...

// ✅ CORRECT
axios.get('http://localhost:8000/api/mau-2c/...');
```

**Solution:** Use absolute URLs for Adobe PDF and Mẫu 2C endpoints

### Issue 2: Browser Cache Not Updating
**Symptom:** Code changes don't take effect in browser
**Solution:**
1. Hard refresh: Ctrl + Shift + R (Windows) or Cmd + Shift + R (Mac)
2. Or: Open DevTools (F12) → Right-click reload → "Empty Cache and Hard Reload"
3. Or: Close browser tab completely, open new tab

### Issue 3: Adobe API Credentials Missing
**Symptom:** Adobe PDF operations fail with authentication error
**Solution:** Add to `backend/.env`:
```
ADOBE_CLIENT_ID=your_client_id
ADOBE_CLIENT_SECRET=your_client_secret
```

### Issue 4: Python Cache Issues
**Symptom:** Backend server keeps reloading with errors
**Solution:**
```powershell
Stop-Process -Name python -Force
Remove-Item backend\app\routers\__pycache__\* -Force
cd backend
python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000
```

---

## 🚀 DEVELOPMENT WORKFLOW

### Start Development Servers
```powershell
# Backend (Terminal 1)
cd backend
python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000

# Frontend (Terminal 2)
cd frontend
npm run dev
```

### Access URLs
- Frontend: http://localhost:5173
- Backend API Docs: http://localhost:8000/docs
- Adobe PDF Tools: http://localhost:5173/adobe-pdf
- Mẫu 2C Form: http://localhost:5173/mau-2c

### Testing Flow
1. **Test Adobe PDF:**
   - Go to `/adobe-pdf`
   - Select operation (e.g., Combine PDF)
   - Upload test files
   - Click "Thực hiện" (Execute)
   - Download result
   - Check friendly error messages

2. **Test Mẫu 2C:**
   - Go to `/mau-2c`
   - Click "Chọn mẫu dữ liệu" (Select sample data)
   - Choose template (e.g., "Cán bộ trẻ")
   - Click "Tải dữ liệu mẫu" (Load sample data)
   - Verify all fields populated
   - Click "Tạo tài liệu Mẫu 2C" (Generate document)
   - Download and open `.docx` file
   - Verify formatting and data

---

## 📚 KEY VIETNAMESE TERMINOLOGY

**Government/Administrative:**
- **Cán bộ** - Government official/cadre
- **Sơ yếu lý lịch** - Resume/biographical record
- **UBND** - Ủy ban Nhân dân (People's Committee)
- **Phường/Xã** - Ward/Commune
- **Quận/Huyện** - District
- **Tỉnh/Thành phố** - Province/City

**Party/Political:**
- **Đảng viên** - Party member
- **Chi bộ** - Party cell
- **Chi ủy** - Party cell committee
- **Đảng Cộng sản Việt Nam** - Communist Party of Vietnam

**Education:**
- **Trình độ** - Education level
- **Cử nhân** - Bachelor's degree
- **Thạc sĩ** - Master's degree
- **Tiến sĩ** - Doctorate
- **Trung cấp** - Vocational school
- **Cao đẳng** - College diploma
- **Chuyên ngành** - Major/specialization

**Career:**
- **Chức vụ** - Position/title
- **Chuyên viên** - Specialist
- **Phó Trưởng phòng** - Deputy Department Head
- **Trưởng phòng** - Department Head
- **Kinh nghiệm** - Experience
- **Hệ số lương** - Salary coefficient
- **Bậc lương** - Salary grade

**Awards:**
- **Bằng khen** - Certificate of Merit
- **Huân chương** - Medal/Order
- **Chiến sĩ thi đua** - Emulation Fighter
- **Lao động tiên tiến** - Advanced Worker

---

## 🎯 USER STORIES

### Story 1: Government Official Creates Resume
**Actor:** 35-year-old government official in Hanoi

**Goal:** Create official Mẫu 2C document for annual review

**Flow:**
1. Opens `/mau-2c` page
2. Sees empty form with many fields
3. Clicks "Chọn mẫu dữ liệu" to see examples
4. Selects "Cán bộ chính - Phó Phòng" (similar to their role)
5. Clicks "Tải dữ liệu mẫu" to auto-fill
6. Edits fields to match their actual information
7. Adds/removes education entries as needed
8. Updates work history with their positions
9. Fills in family members
10. Clicks "Tạo tài liệu Mẫu 2C"
11. Downloads `.docx` file
12. Opens in Microsoft Word, makes final edits
13. Prints and signs for submission

### Story 2: Office Administrator Combines Documents
**Actor:** Administrative staff member

**Goal:** Merge multiple PDF reports into one file

**Flow:**
1. Opens `/adobe-pdf` page
2. Clicks on "Combine PDF" card
3. Clicks "Chọn files" and selects 5 PDFs
4. Sees list of files with preview
5. Drags to reorder if needed
6. Clicks "Thực hiện" (Execute)
7. Sees loading indicator
8. Downloads combined PDF automatically
9. Verifies all pages are in correct order

---

## 🔐 SECURITY CONSIDERATIONS

**File Upload Security:**
- File size limits enforced
- File type validation (PDF, DOCX, XLSX, PPTX only)
- Temporary files auto-deleted after 1 hour
- Files stored in isolated temp directories

**API Authentication:**
- Adobe credentials stored in `.env` (not committed)
- Backend validates all requests
- CORS configured for localhost development

**Production Deployment:**
- Use environment variables for all secrets
- Enable HTTPS
- Configure nginx reverse proxy
- Set up proper CORS origins
- Enable rate limiting

---

## 📦 DEPLOYMENT CHECKLIST

**Environment Variables:**
```bash
# Backend .env
ADOBE_CLIENT_ID=...
ADOBE_CLIENT_SECRET=...
DATABASE_URL=...  # if using database
SECRET_KEY=...    # for JWT tokens
```

**Frontend Build:**
```bash
cd frontend
npm run build
# Output: dist/ folder
```

**Backend Production:**
```bash
cd backend
pip install -r requirements.txt
gunicorn app.main_simple:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Docker (if used):**
```bash
docker-compose up -d
```

---

## 🆘 TROUBLESHOOTING GUIDE

**Problem:** "Adobe credentials not found"
```bash
# Check .env file exists
ls backend/.env

# Verify credentials loaded
cd backend
python -c "from app.utils.adobe_credentials import AdobeCredentials; print(AdobeCredentials.get_credentials())"
```

**Problem:** Templates not loading in Mẫu 2C
```bash
# Check backend logs
# Should see: INFO: GET /api/mau-2c/sample-templates 200 OK

# Test endpoint directly
curl http://localhost:8000/api/mau-2c/sample-templates

# Check frontend console for errors
# Should NOT see /api/v1 in URL
```

**Problem:** Document generation fails
```bash
# Check template exists
ls backend/templates/mau_2c_template.docx

# Test python-docx installation
cd backend
python -c "from docx import Document; print('OK')"

# Check backend logs for detailed error
```

**Problem:** Frontend not updating
```bash
# Clear Vite cache
cd frontend
rm -rf .vite
rm -rf node_modules/.vite

# Rebuild
npm run dev
```

---

## 📖 CODE CONVENTIONS

**Backend (Python):**
- Use `snake_case` for variables and functions
- Use `PascalCase` for classes
- Type hints for all functions
- Async functions for I/O operations
- Exception handling with try/except

**Frontend (TypeScript):**
- Use `camelCase` for variables and functions
- Use `PascalCase` for components and interfaces
- Explicit types for all props and state
- Use functional components with hooks
- Toast notifications for user feedback

**API Responses:**
```typescript
// Success
{
  "message": "Success message",
  "data": { ... }
}

// Error
{
  "detail": "Error message in Vietnamese"
}

// File download: Blob with Content-Disposition header
```

---

## 🎓 LEARNING RESOURCES

**Adobe PDF Services API:**
- Official Docs: https://developer.adobe.com/document-services/docs/
- Python SDK: https://github.com/adobe/pdfservices-python-sdk

**Vietnamese Government Forms:**
- Mẫu 2C is standardized across all government agencies
- Based on Communist Party personnel management regulations
- Must match exact formatting for official use

**FastAPI:**
- Docs: https://fastapi.tiangolo.com/
- File uploads: https://fastapi.tiangolo.com/tutorial/request-files/

**React + TypeScript:**
- React Docs: https://react.dev/
- TypeScript: https://www.typescriptlang.org/docs/

---

## 🎯 FUTURE ENHANCEMENTS

**Phase 1 (Completed):**
- ✅ Adobe PDF Services integration (18 operations)
- ✅ Mẫu 2C form with sample templates
- ✅ Document generation

**Phase 2 (Planned):**
- [ ] User authentication and saved forms
- [ ] Database storage for form drafts
- [ ] More government forms (Mẫu 1A, 2A, etc.)
- [ ] Batch document generation
- [ ] Email notifications

**Phase 3 (Future):**
- [ ] Mobile responsive design
- [ ] E-signature integration
- [ ] Document versioning
- [ ] Audit trail
- [ ] Multi-language support

---

## 📞 QUICK REFERENCE

**Start Both Servers:**
```powershell
# Use VS Code tasks or manual:
cd backend; python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000
cd frontend; npm run dev
```

**Test Adobe PDF:**
```bash
curl -X POST http://localhost:8000/api/adobe-pdf/compress \
  -F "file=@test.pdf" \
  --output compressed.pdf
```

**Test Mẫu 2C:**
```bash
curl http://localhost:8000/api/mau-2c/sample-templates
curl http://localhost:8000/api/mau-2c/sample-data/can_bo_tre
```

**Check Logs:**
```bash
# Backend logs show in terminal
# Frontend logs in browser console (F12)
```

---

## 📋 **3. Tools Page - Document Processing Hub** (`/tools`)

**Mục đích**: Trung tâm xử lý file toàn diện với 50+ tính năng chuyển đổi và xử lý tài liệu/hình ảnh.

### **3 Tabs Chính**:

#### **A. Documents Tab** 📄
**Chuyển đổi Office ↔ PDF**:
- **Word ↔ PDF**: 
  - Word → PDF (Gotenberg - LibreOffice headless, 9/10 quality)
  - PDF → Word (Adobe 10/10 → fallback pdf2docx 7/10)
  - Batch: Nhiều Word → PDF cùng lúc
  - Merge: Gộp nhiều Word → 1 PDF duy nhất
- **Excel ↔ PDF**:
  - Excel → PDF (Gotenberg)
  - PDF → Excel (pdfplumber - extract tables, 8/10 quality)
  - Batch: Nhiều Excel → PDF
- **PowerPoint ↔ PDF**:
  - PPT → PDF (Gotenberg)
  - Batch conversion

**16 Tính năng PDF Tools**:
1. **Compress PDF** - Nén file (Adobe 10/10 → fallback pypdf 7/10)
2. **Merge PDFs** - Gộp nhiều PDF (drag-drop để sắp xếp)
3. **Split PDF** - Tách theo page ranges (VD: "1-3,5-7")
4. **Rotate PDF** - Xoay 90°/180°/270° (all pages hoặc specific)
5. **Watermark** - Thêm text watermark (position, opacity)
6. **Protect PDF** - Mã hóa password (AES-256)
7. **Unlock PDF** - Mở khóa PDF đã bảo vệ
8. **PDF → Images** - Chuyển từng trang thành PNG/JPG (ZIP)
9. **Add Page Numbers** - Thêm số trang (format customizable)
10. **Extract Text** - Trích xuất text từ PDF
11. **PDF Info** - Xem metadata (pages, author, encryption, page sizes)

**Adobe AI-Powered Features** (Cloud, 500 free/month):
1. **OCR PDF** (🔍) - Convert scanned PDF → searchable (50+ languages, Vietnamese AI)
2. **Extract Content** (🔬) - AI trích xuất:
   - Tables → Excel data
   - Images → PNG files với metadata
   - Text với font information (bold, italic, size, family)
   - Document structure (headings, paragraphs, lists)
3. **HTML → PDF** (�) - Perfect Chrome-quality rendering
   - Page size: A4/Letter/Legal/A3
   - Orientation: Portrait/Landscape
   - Full CSS3 + JavaScript support

**Bulk/Batch Operations**:
- **Bulk PDF Conversion** (🔀): Convert nhiều PDF → Word/Excel/Images cùng lúc
- **Batch Word → PDF**: Convert hàng loạt Word files
- **Batch PDF → Word**: Convert hàng loạt PDF files
- **Batch Compress**: Nén nhiều PDF
- **Batch Image → PDF**: Convert nhiều ảnh thành PDF

#### **B. Images Tab** 🖼️
**Xử lý ảnh**:
- **Resize** - Thay đổi kích thước (keep aspect ratio)
- **Remove Background** - AI xóa nền (10-30s, rembg library)
- **Image → PDF** - Chuyển ảnh sang PDF
- **Batch Image → PDF** - Nhiều ảnh → nhiều PDF hoặc 1 PDF

**Định dạng hỗ trợ**: JPG, PNG, GIF, WebP, BMP, HEIC

#### **C. OCR Tab** 🔍
**Trích xuất text từ ảnh**:
- **Languages**: Vietnamese + English + 80+ ngôn ngữ (Tesseract)
- **Output**: Text + confidence scores + bounding boxes
- **Use cases**: CMND/CCCD, passport, table detection

### **Technology Stack Backend**:

| Feature | Primary Tech | Fallback | Quality |
|---------|--------------|----------|---------|
| **Word → PDF** | Gotenberg (LibreOffice) | - | 9/10 |
| **PDF → Word** | Adobe PDF Services | pdf2docx | 10/10 → 7/10 |
| **PDF → Excel** | pdfplumber | - | 8/10 |
| **Office → PDF** | Gotenberg | - | 9/10 |
| **Compress PDF** | Adobe | pypdf | 10/10 → 7/10 |
| **Watermark PDF** | Adobe | pypdf + reportlab | 10/10 → 8/10 |
| **OCR PDF** | Adobe Sensei AI | - | 10/10 (50+ languages) |
| **Extract Content** | Adobe AI | - | 10/10 (smart structure) |
| **HTML → PDF** | Adobe CreatePDF | - | 10/10 (Chrome quality) |
| **Remove BG** | rembg (ML) | - | 9/10 |
| **OCR Images** | Tesseract | - | 8/10 |

### **API Endpoints Structure**:
```
/api/v1/documents/
├── convert/
│   ├── word-to-pdf
│   ├── pdf-to-word (start_page, end_page)
│   ├── excel-to-pdf
│   ├── powerpoint-to-pdf
│   ├── pdf-to-excel
│   ├── image-to-pdf
│   └── html-to-pdf (Adobe)
├── pdf/
│   ├── compress (quality: low/medium/high)
│   ├── merge (files[])
│   ├── split (page_ranges)
│   ├── rotate (rotation: 90/180/270, pages)
│   ├── watermark (watermark_text, position, opacity)
│   ├── protect (password)
│   ├── unlock (password)
│   ├── to-images (format: png/jpg, dpi)
│   ├── add-page-numbers (position, format)
│   ├── extract-text
│   ├── ocr (language: vi-VN/en-US/...) [Adobe]
│   └── extract-content (extract_type: all/text/tables/images) [Adobe]
├── info/
│   └── pdf (metadata, pages, encryption)
└── batch/
    ├── word-to-pdf (files[])
    ├── pdf-to-word (files[])
    ├── excel-to-pdf (files[])
    ├── image-to-pdf (files[])
    ├── compress-pdf (files[], quality)
    ├── pdf-to-multiple (files[], format: word/excel/image)
    └── merge-word-to-pdf (files[]) → 1 merged PDF

/api/v1/images/
├── resize (width, height, keep_aspect_ratio)
├── remove-background (output_format)
└── compress

/api/v1/ocr/
└── extract (languages: vi,en, detail)
```

### **Frontend Features**:

**Smart File Detection**:
- Upload file → Auto-detect type (Word/Excel/PDF/Image)
- Show **relevant actions only** cho file type đó
- Color-coded UI theo file type (Blue: Word, Green: Excel, Red: PDF, Purple: Image)

**Drag & Drop**:
- Single file: Click hoặc drag file
- Multi-file: 
  - Merge PDFs: Drag-drop để sắp xếp thứ tự, nút ↑↓
  - Batch mode: Ctrl+Click nhiều files cùng lúc

**Batch Mode**:
- Toggle "📦 Batch Mode" button
- Upload nhiều files cùng loại
- Drag-drop reorder
- Visual feedback (purple gradient)
- Output: ZIP file hoặc merged PDF

**Progress Tracking**:
- Upload progress (0-100%)
- Processing progress với animation
- Real-time timer (X.Xs)
- Technology badge hiển thị (Adobe/Gotenberg/pdf2docx/...)
- Cancel button (abort operation)

**Result Display**:
- Success banner với stats:
  - Original file size
  - Output file size
  - Compression ratio
  - Processing time
  - Technology used + quality score
- Adobe quota display (X/500 remaining)
- Download button + "Convert Another" button

**Error Handling**:
- Friendly Vietnamese error messages
- Validation before submit:
  - File type check
  - File size limit (max 50MB)
  - Required fields
- Toast notifications (success/error/info)
- Disabled button states với reason tooltip

### **Settings Panel** ⚙️:
**Technology Priority Configuration**:
- **Compress**: Adobe-first → pypdf fallback
- **Watermark**: Adobe-first → pypdf fallback
- **PDF Info**: Adobe-first → pypdf fallback
- Runtime toggle: Switch priorities on-the-fly
- View quota usage: X/500 Adobe transactions
- Reset to defaults button

### **Use Cases**:

**1. Office Worker - Daily Documents**:
- Upload `hop-dong.docx` → Convert to PDF → Download
- Upload 10 Word files → Batch convert → Download ZIP
- Time saved: 10 minutes → 30 seconds

**2. Legal Department - Sensitive PDFs**:
- Upload `tai-lieu-mat.pdf`
- Click "Protect PDF" → Enter password
- Download encrypted file
- Share via email safely

**3. HR - Employee Records**:
- Upload 50 PDF applications
- Bulk convert → Word for editing
- Edit details → Merge → 1 final PDF
- Archive

**4. Marketing - Multilingual Content**:
- Upload scanned brochure (Vietnamese + English)
- OCR PDF with "vi-VN" language
- Get searchable PDF
- Extract text → Translate

**5. Student - Research Papers**:
- Upload `paper-scan.pdf` (scanned)
- OCR → Searchable PDF
- Extract Text → Copy to Word
- Edit citations → Convert back to PDF

### **Performance Metrics**:

| Operation | Speed | Quality | Technology |
|-----------|-------|---------|------------|
| Word → PDF | 2-5s | 9/10 | Gotenberg |
| PDF → Word (Adobe) | 5-10s | 10/10 | Adobe AI |
| PDF → Word (local) | 3-7s | 7/10 | pdf2docx |
| PDF → Excel | 5-15s | 8/10 | pdfplumber |
| Compress (Adobe) | 5-10s | 10/10 | Adobe |
| Compress (local) | 2-5s | 7/10 | pypdf |
| OCR PDF | 10-30s | 10/10 | Adobe AI |
| Extract Content | 10-30s | 10/10 | Adobe AI |
| Remove BG | 10-30s | 9/10 | rembg ML |
| Merge 10 PDFs | 5-10s | 10/10 | pypdf |

### **Gotenberg Architecture**:
```
Frontend → Backend (FastAPI) → Gotenberg (Docker)
                             → LibreOffice Headless
                             → Return PDF
```
- **Gotenberg**: Microservice chạy trong Docker
- **Port**: 3000 (internal)
- **Advantages**:
  - No LibreOffice installation on host
  - Consistent output quality
  - Scalable (horizontal scaling)
  - Production-ready

### **Adobe PDF Services Integration**:
```
Frontend → Backend → Adobe PDF Services API (Cloud)
                  ↓
                Local Fallback (if quota exceeded)
```
- **Free Tier**: 500 transactions/month
- **Quota Tracking**: X-Adobe-Quota-Remaining header
- **Fallback Strategy**: Adobe → Local automatically
- **Quality**: 10/10 (AI-powered Sensei)

---

## �🏁 GETTING STARTED (New Developer)

1. **Clone and install:**
   ```bash
   git clone <repo>
   cd utility-server
   
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   ```

2. **Configure environment:**
   ```bash
   # Create backend/.env
   ADOBE_CLIENT_ID=your_id
   ADOBE_CLIENT_SECRET=your_secret
   ```

3. **Start servers:**
   ```bash
   # Terminal 1
   cd backend
   python -m uvicorn app.main_simple:app --reload
   
   # Terminal 2
   cd frontend
   npm run dev
   ```

4. **Test basic flow:**
   - **Adobe PDF**: http://localhost:5173/adobe-pdf → Try "Combine PDF"
   - **Mẫu 2C**: http://localhost:5173/mau-2c → Generate document
   - **Tools**: http://localhost:5173/tools → Upload Word → Convert to PDF

5. **Read this document** for deep understanding!

---

**Last Updated:** November 28, 2025  
**Version:** 2.0  
**Maintained by:** Development Team

