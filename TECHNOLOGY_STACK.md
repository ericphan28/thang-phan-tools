# 🔧 Technology Stack - Document Conversion

**Last Updated:** November 22, 2025

---

## 📊 Current Technology Usage

### 1️⃣ Office → PDF (Word, Excel, PowerPoint → PDF)

#### **Primary Technology: Gotenberg 8**
- **Library:** Gotenberg REST API + LibreOffice Headless
- **Method:** `word_to_pdf()`, `excel_to_pdf()`, `powerpoint_to_pdf()`
- **Quality:** ⭐⭐⭐⭐⭐ 9/10
- **Speed:** Fast (2-5 seconds)
- **Cost:** FREE
- **Status:** ✅ Production

**How it works:**
```python
async def word_to_pdf(input_file: Path) -> Path:
    # Call Gotenberg API
    response = await client.post(
        f"{gotenberg_url}/forms/libreoffice/convert",
        files={'files': file_content}
    )
```

**Advantages:**
- ✅ Perfect format preservation (fonts, colors, tables, images)
- ✅ Docker microservice (no LibreOffice installation needed)
- ✅ Modern REST API
- ✅ Supports: DOC, DOCX, XLS, XLSX, PPT, PPTX, ODT, ODS, ODP
- ✅ Production-ready, stable

**Environment:**
```bash
GOTENBERG_URL=http://gotenberg:3000
```

---

### 2️⃣ PDF → Word

#### **Primary Technology: Adobe PDF Services API** ⭐ NEW!
- **Library:** `pdfservices-sdk` (Python)
- **Method:** `_pdf_to_word_adobe()`
- **Quality:** ⭐⭐⭐⭐⭐ 10/10
- **Speed:** Medium (5-10 seconds, cloud API)
- **Cost:** FREE (500 conversions/month)
- **Status:** ✅ Production (with fallback)

**How it works:**
```python
async def _pdf_to_word_adobe(input_file: Path, output_path: Path) -> Path:
    # 1. Upload PDF to Adobe cloud
    # 2. Submit export job (PDF → DOCX)
    # 3. Wait for completion (SDK auto-polls)
    # 4. Download result
    # 5. Save to local file
```

**Advantages:**
- ✅ **AI-powered** layout analysis
- ✅ **95%+ accuracy** on fonts, colors, tables, images
- ✅ Best-in-class format preservation
- ✅ Official Adobe API (enterprise-grade)

**Environment:**
```bash
USE_ADOBE_PDF_API=true
PDF_SERVICES_CLIENT_ID=your_client_id
PDF_SERVICES_CLIENT_SECRET=your_client_secret
ADOBE_ORG_ID=your_org_id
```

#### **Fallback Technology: pdf2docx**
- **Library:** `pdf2docx` (Python)
- **Method:** `_pdf_to_word_local()`
- **Quality:** ⭐⭐⭐⭐ 7/10
- **Speed:** Fast (2-3 seconds)
- **Cost:** FREE
- **Status:** ✅ Production (automatic fallback)

**How it works:**
```python
async def _pdf_to_word_local(input_file: Path) -> Path:
    cv = PDFToWordConverter(str(input_file))
    cv.convert(str(output_path))
    cv.close()
```

**Advantages:**
- ✅ Pure Python (no external dependencies)
- ✅ Works offline
- ✅ Fast processing
- ✅ Good quality for simple documents

**Conversion Strategy:**
```
PDF → Word Request
    ↓
[1] Try Adobe PDF Services (if enabled)
    ├─ Success → Return high-quality DOCX (10/10)
    └─ Failed/Disabled → [2] Use pdf2docx (7/10)
```

---

### 3️⃣ PDF → Excel

#### **Technology: pdfplumber**
- **Library:** `pdfplumber` (Python)
- **Method:** `pdf_to_excel()`
- **Quality:** ⭐⭐⭐⭐ 8/10 (for table extraction)
- **Speed:** Fast (3-5 seconds)
- **Cost:** FREE
- **Status:** ✅ Production

**How it works:**
```python
async def pdf_to_excel(input_file: Path) -> Path:
    with pdfplumber.open(input_file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            # Write to Excel using openpyxl
```

**Advantages:**
- ✅ Excellent table detection
- ✅ Preserves table structure
- ✅ Handles multi-page PDFs
- ✅ Clean Excel output with formatting

---

### 4️⃣ Excel → PDF

#### **Technology: Gotenberg 8**
- Same as Word → PDF
- **Method:** `excel_to_pdf()`
- **Quality:** ⭐⭐⭐⭐⭐ 9/10
- **Speed:** Fast (2-5 seconds)
- **Cost:** FREE
- **Status:** ✅ Production

---

## 📋 Complete Technology Matrix

| Conversion | Primary Tech | Fallback | Quality | Speed | Cost |
|------------|-------------|----------|---------|-------|------|
| **Word → PDF** | Gotenberg (LibreOffice) | - | 9/10 | 2-5s | FREE |
| **Excel → PDF** | Gotenberg (LibreOffice) | - | 9/10 | 2-5s | FREE |
| **PowerPoint → PDF** | Gotenberg (LibreOffice) | - | 9/10 | 2-5s | FREE |
| **PDF → Word** | Adobe PDF Services ⭐ | pdf2docx | 10/10 → 7/10 | 5-10s → 2-3s | FREE (500/mo) |
| **PDF → Excel** | pdfplumber | - | 8/10 | 3-5s | FREE |

---

## 🎨 UI Badge Display Recommendation

### Display Technology on Frontend

Add technology badges to show users which engine is processing their files:

#### **Example UI Implementation:**

```typescript
// frontend/src/components/ConversionStatus.tsx

interface ConversionTech {
  conversion: string;
  primaryTech: string;
  fallbackTech?: string;
  badge: {
    color: string;
    icon: string;
  };
}

const CONVERSION_TECH: ConversionTech[] = [
  {
    conversion: "word-to-pdf",
    primaryTech: "Gotenberg (LibreOffice)",
    badge: { color: "blue", icon: "⚡" }
  },
  {
    conversion: "pdf-to-word",
    primaryTech: "Adobe PDF Services",
    fallbackTech: "pdf2docx",
    badge: { color: "red", icon: "🔥" }
  },
  {
    conversion: "pdf-to-excel",
    primaryTech: "pdfplumber",
    badge: { color: "green", icon: "📊" }
  }
];

// Display during conversion
<div className="conversion-status">
  <Badge color="red">
    🔥 Adobe PDF Services
  </Badge>
  <span>Converting with AI-powered engine...</span>
</div>

// On completion
<div className="conversion-result">
  <Badge color="green">✅ Success</Badge>
  <Badge color="gray">
    Powered by Adobe PDF Services
  </Badge>
  <span className="quality-indicator">
    Quality: 10/10 ⭐⭐⭐⭐⭐
  </span>
</div>
```

#### **API Response Enhancement:**

Modify backend to return technology info:

```python
# backend/app/api/endpoints/documents.py

@router.post("/convert/pdf-to-word")
async def convert_pdf_to_word(file: UploadFile):
    result = await document_service.pdf_to_word(input_path)
    
    return {
        "filename": output_file.name,
        "size": output_file.stat().st_size,
        "technology": {
            "engine": "Adobe PDF Services" if used_adobe else "pdf2docx",
            "quality": "10/10" if used_adobe else "7/10",
            "type": "cloud" if used_adobe else "local"
        },
        "download_url": f"/api/documents/download/{output_file.name}"
    }
```

#### **UI Component Example:**

```jsx
// Display conversion options with technology info
<Select>
  <Option value="pdf-to-word">
    <div>
      <span>PDF → Word</span>
      <Badge color="red">🔥 Adobe AI</Badge>
      <Badge color="gray">Fallback: pdf2docx</Badge>
    </div>
    <small>Quality: 10/10 ⭐⭐⭐⭐⭐</small>
  </Option>
  
  <Option value="word-to-pdf">
    <div>
      <span>Word → PDF</span>
      <Badge color="blue">⚡ Gotenberg</Badge>
    </div>
    <small>Quality: 9/10 ⭐⭐⭐⭐</small>
  </Option>
  
  <Option value="pdf-to-excel">
    <div>
      <span>PDF → Excel</span>
      <Badge color="green">📊 pdfplumber</Badge>
    </div>
    <small>Quality: 8/10 ⭐⭐⭐⭐</small>
  </Option>
</Select>
```

---

## 🎯 Recommended UI/UX Implementation

### 1. **Conversion Selection Screen**

Show technology badges on conversion type cards:

```
┌─────────────────────────────────────┐
│  📄 PDF to Word                     │
│  ├─ 🔥 Adobe PDF Services (Primary) │
│  └─ 📦 pdf2docx (Fallback)          │
│                                     │
│  Quality: ⭐⭐⭐⭐⭐ 10/10            │
│  Speed: 5-10 seconds                │
│  [Select this conversion]           │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  📄 Word to PDF                     │
│  └─ ⚡ Gotenberg (LibreOffice)      │
│                                     │
│  Quality: ⭐⭐⭐⭐ 9/10               │
│  Speed: 2-5 seconds                 │
│  [Select this conversion]           │
└─────────────────────────────────────┘
```

### 2. **Progress Display**

Show which engine is processing:

```
Converting your file...
┌─────────────────────────────────────┐
│  📤 Uploading to Adobe Cloud        │
│  ⏳ Processing with AI Engine       │
│  ⚙️  Analyzing layout & formatting  │
│  ⬇️  Downloading result             │
└─────────────────────────────────────┘

Using: 🔥 Adobe PDF Services
Quality: 10/10 ⭐⭐⭐⭐⭐
```

### 3. **Completion Screen**

```
✅ Conversion Complete!

Your file: document.docx (45 KB)

Technology used:
├─ Engine: 🔥 Adobe PDF Services
├─ Quality: 10/10 ⭐⭐⭐⭐⭐
├─ Processing time: 8.2 seconds
└─ Quota remaining: 498/500

[Download File]  [Convert Another]
```

### 4. **Settings Panel**

Allow users to see/configure technology preferences:

```
⚙️ Conversion Settings

PDF to Word Engine:
  ○ Auto (Try Adobe, fallback to pdf2docx)
  ○ Adobe PDF Services only
  ○ pdf2docx only (offline mode)

Current Status:
  ├─ Adobe: ✅ Enabled (498/500 remaining)
  └─ Fallback: ✅ Available

Quality Comparison:
  • Adobe PDF Services: 10/10 ⭐⭐⭐⭐⭐
  • pdf2docx:          7/10 ⭐⭐⭐⭐
```

---

## 🔍 Technology Detection API

Add endpoint to check available technologies:

```python
# backend/app/api/endpoints/system.py

@router.get("/technologies")
async def get_available_technologies():
    return {
        "conversions": {
            "word_to_pdf": {
                "engine": "gotenberg",
                "version": "8.x",
                "quality": "9/10",
                "available": True
            },
            "pdf_to_word": {
                "engines": [
                    {
                        "name": "adobe",
                        "quality": "10/10",
                        "available": document_service.use_adobe,
                        "quota": "498/500"
                    },
                    {
                        "name": "pdf2docx",
                        "quality": "7/10",
                        "available": True,
                        "quota": "unlimited"
                    }
                ],
                "strategy": "adobe_with_fallback"
            },
            "pdf_to_excel": {
                "engine": "pdfplumber",
                "quality": "8/10",
                "available": True
            }
        }
    }
```

Frontend can call this to display real-time technology status.

---

## 📦 Technology Dependencies

```python
# Current requirements.txt

# Office → PDF
# Gotenberg (External Docker service)

# PDF → Word (Primary)
pdfservices-sdk>=4.0.0          # Adobe PDF Services

# PDF → Word (Fallback)
pdf2docx==0.5.6                 # Pure Python

# PDF → Excel
pdfplumber==0.10.3              # Table extraction

# Supporting libraries
python-docx==1.1.0              # Word manipulation
openpyxl==3.1.2                 # Excel manipulation
pypdf==4.0.0                    # PDF utilities
```

---

## 🎉 Summary

### Current Stack (Production-Ready):
1. **Office → PDF:** Gotenberg 8 (9/10 quality)
2. **PDF → Word:** Adobe PDF Services with pdf2docx fallback (10/10 → 7/10)
3. **PDF → Excel:** pdfplumber (8/10 quality)

### UI Recommendation:
- Show technology badges on conversion cards
- Display engine status during processing
- Add quality indicators (star ratings)
- Show quota remaining for Adobe
- Allow fallback preference in settings

Anh muốn implement UI badges như thế nào? Tôi có thể tạo React components mẫu!
