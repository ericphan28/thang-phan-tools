# 📚 Adobe PDF Services API - Complete Guide & All Samples

## 🎯 YOU ALREADY HAVE CREDENTIALS! ✅

**Credentials File**: `public/adobe/pdfservices-api-credentials.json`

```json
{
  "client_credentials": {
    "client_id": "d46f7e349fe44f7ca933c216eaa9bd48",
    "client_secret": "p8e-Bg7-Ce-gj80zF62wXyhY-rqjbVmDHgzz"
  },
  "service_principal_credentials": {
    "organization_id": "491221D76920D5EB0A495C5D@AdobeOrg"
  }
}
```

---

## ⚡ Quick Setup (30 giây)

### **Step 1: Update `backend/.env`**

```env
USE_ADOBE_PDF_API=true
PDF_SERVICES_CLIENT_ID="d46f7e349fe44f7ca933c216eaa9bd48"
PDF_SERVICES_CLIENT_SECRET="p8e-Bg7-Ce-gj80zF62wXyhY-rqjbVmDHgzz"
ADOBE_ORG_ID="491221D76920D5EB0A495C5D@AdobeOrg"
```

### **Step 2: Test**

```bash
python test_adobe_credentials.py
# Expected: ✅ SUCCESS!
```

### **Step 3: Done!** 🎉

Restart backend → Try OCR từ frontend!

---

## 📦 All Available Adobe APIs

### ✅ ALREADY IMPLEMENTED (Ready to use!)

| API | Path | Backend Status | Quality | Frontend |
|-----|------|---------------|---------|----------|
| **OCR PDF** | `src/ocrpdf/` | ✅ DONE | 10/10 | ✅ Button |
| **Extract Content** | `src/extractpdf/` | ✅ DONE | 10/10 | ✅ Button |
| **PDF to Word** | `src/exportpdf/` | ✅ DONE | 10/10 | ✅ Button |
| **HTML to PDF** | `src/htmltopdf/` | ✅ DONE | 10/10 | ✅ Button |
| **Compress PDF** | `src/compresspdf/` | ✅ DONE | 10/10 | ✅ Button |

### 📋 TODO (Samples available, not integrated yet)

| API | Path | Complexity | Priority |
|-----|------|-----------|----------|
| **Watermark** | `src/pdfwatermark/` | Easy | MEDIUM |
| **Combine PDF** | `src/combinepdf/` | Easy | MEDIUM |
| **Split PDF** | `src/splitpdf/` | Easy | LOW |
| **Rotate Pages** | `src/rotatepages/` | Easy | LOW |
| **Delete Pages** | `src/deletepages/` | Easy | LOW |
| **Insert Pages** | `src/insertpages/` | Easy | LOW |
| **Replace Pages** | `src/replacepages/` | Easy | LOW |
| **Reorder Pages** | `src/reorderpages/` | Easy | LOW |
| **Protect PDF** | `src/protectpdf/` | Medium | LOW |
| **Remove Protection** | `src/removeprotection/` | Medium | LOW |
| **Linearize** | `src/linearizepdf/` | Medium | LOW |
| **PDF Properties** | `src/pdfproperties/` | Easy | LOW |
| **Auto-Tag PDF** | `src/autotagpdf/` | Hard | LOW |
| **Electronic Seal** | `src/electronicseal/` | Hard | LOW |
| **Document Merge** | `src/documentmerge/` | Medium | LOW |
| **Export to Images** | `src/exportpdftoimages/` | Easy | MEDIUM |

---

## 🔥 Quick Sample Reference

### 1️⃣ **OCR PDF** - Vietnamese Text Recognition

**Sample**: `public/adobe/adobe-dc-pdf-services-sdk-python/src/ocrpdf/ocr_pdf_with_options.py`

```python
from adobe.pdfservices.operation.pdfjobs.params.ocr_pdf.ocr_params import OCRParams
from adobe.pdfservices.operation.pdfjobs.params.ocr_pdf.ocr_supported_locale import OCRSupportedLocale
from adobe.pdfservices.operation.pdfjobs.params.ocr_pdf.ocr_supported_type import OCRSupportedType

# OCR with Vietnamese
ocr_params = OCRParams(
    ocr_locale=OCRSupportedLocale.VI_VN,  # 🇻🇳 Vietnamese!
    ocr_type=OCRSupportedType.SEARCHABLE_IMAGE  # Keep original look
)

ocr_job = OCRPDFJob(input_asset=input_asset, ocr_pdf_params=ocr_params)
location = pdf_services.submit(ocr_job)
response = pdf_services.get_job_result(location, OCRPDFResult)
```

**Supported Languages**: 50+
- `VI_VN` 🇻🇳 Vietnamese
- `EN_US` 🇺🇸 English
- `FR_FR` 🇫🇷 French
- `DE_DE` 🇩🇪 German
- `ES_ES` 🇪🇸 Spanish
- `JA_JP` 🇯🇵 Japanese
- `KO_KR` 🇰🇷 Korean
- `ZH_HANS` 🇨🇳 Chinese

---

### 2️⃣ **Extract PDF** - AI Table & Image Extraction

**Sample**: `src/extractpdf/extract_text_table_info_from_pdf.py`

```python
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType

# Extract everything
extract_params = ExtractPDFParams(
    elements_to_extract=[
        ExtractElementType.TEXT,      # Text with formatting
        ExtractElementType.TABLES,    # Tables → CSV
        ExtractElementType.IMAGES     # Images → PNG
    ],
    get_char_info=True,           # Character positions
    get_styling_info=True,        # Font, size, bold, italic
    get_table_structure_format=True  # Table structure
)

extract_job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=extract_params)
```

**Output**: ZIP file with:
- `structuredData.json` - All extracted data
- `images/*.png` - Extracted images
- `tables/*.csv` - Extracted tables

---

### 3️⃣ **PDF to Word** - Perfect Format Preservation

**Sample**: `src/exportpdf/export_pdf_to_docx.py`

```python
from adobe.pdfservices.operation.pdfjobs.params.export_pdf.export_pdf_target_format import ExportPDFTargetFormat

# Export to Word with perfect formatting
export_params = ExportPDFParams(target_format=ExportPDFTargetFormat.DOCX)
export_job = ExportPDFJob(input_asset=input_asset, export_pdf_params=export_params)
```

**Supported Formats**:
- `DOCX` - Word (best)
- `XLSX` - Excel
- `PPTX` - PowerPoint
- `RTF` - Rich Text
- `JPEG` - Images

---

### 4️⃣ **HTML to PDF** - Perfect Web Page Capture

**Sample**: `src/htmltopdf/html_to_pdf_from_url.py`

```python
from adobe.pdfservices.operation.pdfjobs.params.html_to_pdf.page_layout import PageLayout

# Convert URL to PDF (Chrome quality!)
page_layout = PageLayout(page_height=25, page_width=20)  # inches
html_params = HTMLtoPDFParams(
    page_layout=page_layout,
    include_header_footer=True
)

html_job = HTMLtoPDFJob(
    input_url="https://example.com",
    html_to_pdf_params=html_params
)
```

**Use Cases**:
- Capture web pages
- Generate reports from HTML
- Convert invoices/receipts
- Archive web content

---

### 5️⃣ **Compress PDF** - Smart AI Compression

**Sample**: `src/compresspdf/compress_pdf_with_options.py`

```python
from adobe.pdfservices.operation.pdfjobs.params.compress_pdf.compress_pdf_params import CompressPDFParams
from adobe.pdfservices.operation.pdfjobs.params.compress_pdf.compression_level import CompressionLevel

# Compress with AI optimization
compress_params = CompressPDFParams(
    compression_level=CompressionLevel.HIGH  # 40-60% reduction
)
compress_job = CompressPDFJob(input_asset=input_asset, compress_pdf_params=compress_params)
```

**Compression Levels**:
- `LOW` - 5-10% (best quality)
- `MEDIUM` - 20-30% (balanced) ← default
- `HIGH` - 40-60% (max compression)

---

### 6️⃣ **Combine PDF** - Merge Multiple PDFs

**Sample**: `src/combinepdf/combine_pdf_with_page_ranges.py`

```python
# Combine multiple PDFs with page ranges
combine_job = CombinePDFJob()
combine_job.add_input(asset1, page_ranges=[PageRanges(1, 3)])  # Pages 1-3
combine_job.add_input(asset2)  # All pages
combine_job.add_input(asset3, page_ranges=[PageRanges(5, 10)])  # Pages 5-10

location = pdf_services.submit(combine_job)
```

---

### 7️⃣ **Split PDF** - Split into Multiple Files

**Sample**: `src/splitpdf/`

```python
# Split by page number
split_params = SplitPDFParams(page_count=5)  # Every 5 pages
split_job = SplitPDFJob(input_asset=input_asset, split_pdf_params=split_params)
```

---

### 8️⃣ **Watermark PDF** - Add Text/Image Watermark

**Sample**: `src/pdfwatermark/`

```python
# Add watermark to all pages
watermark_asset = pdf_services.upload(watermark_stream, PDFServicesMediaType.PDF)
watermark_job = PDFWatermarkJob(
    input_asset=input_asset,
    watermark_asset=watermark_asset
)
```

---

## 🧪 Test Any Sample

All samples in `public/adobe/adobe-dc-pdf-services-sdk-python/src/` are ready:

```bash
cd public/adobe/adobe-dc-pdf-services-sdk-python

# Set credentials (Windows PowerShell)
$env:PDF_SERVICES_CLIENT_ID="d46f7e349fe44f7ca933c216eaa9bd48"
$env:PDF_SERVICES_CLIENT_SECRET="p8e-Bg7-Ce-gj80zF62wXyhY-rqjbVmDHgzz"

# Run any sample
python src/ocrpdf/ocr_pdf.py
python src/extractpdf/extract_text_table_info_from_pdf.py
python src/exportpdf/export_pdf_to_docx.py
python src/htmltopdf/html_to_pdf_from_url.py
python src/compresspdf/compress_pdf.py
```

---

## 📊 Usage & Quota

**Your Account**:
- Organization: `491221D76920D5EB0A495C5D@AdobeOrg`
- **Free tier**: 500 transactions/month
- Resets: First day of each month

**Transaction Costs**:
| Operation | Cost |
|-----------|------|
| OCR | 1 per PDF |
| Extract | 1 per PDF |
| Export (PDF→Word) | 1 per PDF |
| HTML→PDF | 1 per URL |
| Compress | 1 per PDF |
| Combine | 1 per operation |
| Split | 1 per PDF |
| Watermark | 1 per PDF |

**Check Usage**: https://developer.adobe.com/console → Insights

---

## 🔧 Common Code Pattern

All Adobe APIs follow this pattern:

```python
# 1. Setup credentials
credentials = ServicePrincipalCredentials(
    client_id="d46f7e349fe44f7ca933c216eaa9bd48",
    client_secret="p8e-Bg7-Ce-gj80zF62wXyhY-rqjbVmDHgzz"
)

# 2. Create PDF Services
pdf_services = PDFServices(credentials=credentials)

# 3. Upload file
input_asset = pdf_services.upload(
    input_stream=file_bytes,
    mime_type=PDFServicesMediaType.PDF
)

# 4. Create job
job = SomeJob(input_asset=input_asset, params=params)

# 5. Submit & get result
location = pdf_services.submit(job)
response = pdf_services.get_job_result(location, SomeResult)

# 6. Download
result_asset = response.get_result().get_asset()
stream_asset = pdf_services.get_content(result_asset)

# 7. Save
with open(output_path, "wb") as f:
    f.write(stream_asset.get_input_stream())
```

---

## 🎯 Backend Integration Guide

Want to add more Adobe APIs? Follow this pattern:

### **Example: Add Watermark**

1. **Add method to `document_service.py`**:
```python
async def watermark_pdf_adobe(
    self,
    input_file: Path,
    watermark_file: Path
) -> Path:
    """Add watermark using Adobe"""
    # Read files
    async with aiofiles.open(input_file, 'rb') as f:
        input_stream = await f.read()
    async with aiofiles.open(watermark_file, 'rb') as f:
        watermark_stream = await f.read()
    
    # Adobe API
    pdf_services = PDFServices(credentials=self.adobe_credentials)
    input_asset = pdf_services.upload(input_stream, PDFServicesMediaType.PDF)
    watermark_asset = pdf_services.upload(watermark_stream, PDFServicesMediaType.PDF)
    
    watermark_job = PDFWatermarkJob(
        input_asset=input_asset,
        watermark_asset=watermark_asset
    )
    
    location = pdf_services.submit(watermark_job)
    response = pdf_services.get_job_result(location, PDFWatermarkResult)
    
    # Download result
    result_asset = response.get_result().get_asset()
    stream_asset = pdf_services.get_content(result_asset)
    
    # Save
    output_path = self.output_dir / f"{input_file.stem}_watermarked.pdf"
    async with aiofiles.open(output_path, 'wb') as f:
        await f.write(stream_asset.get_input_stream())
    
    return output_path
```

2. **Add endpoint to `documents.py`**:
```python
@router.post("/pdf/watermark")
async def watermark_pdf(
    file: UploadFile = File(...),
    watermark: UploadFile = File(...)
):
    input_path = await doc_service.save_upload_file(file)
    watermark_path = await doc_service.save_upload_file(watermark)
    
    output_path = await doc_service.watermark_pdf_adobe(input_path, watermark_path)
    
    return FileResponse(output_path, media_type="application/pdf")
```

3. **Add frontend button** - Easy! ✅

---

## 📚 Full Sample List

### Text & OCR
- ✅ `ocrpdf/ocr_pdf.py` - Basic OCR
- ✅ `ocrpdf/ocr_pdf_with_options.py` - OCR with language
- ✅ `extractpdf/extract_text_info_from_pdf.py` - Extract text
- ✅ `extractpdf/extract_text_table_info_from_pdf.py` - Extract text + tables
- ✅ `extractpdf/extract_text_table_info_with_renditions_from_pdf.py` - Extract with images

### Conversion
- ✅ `exportpdf/export_pdf_to_docx.py` - PDF → Word
- ✅ `exportpdf/export_pdf_to_docx_with_ocr_option.py` - PDF → Word with OCR
- ✅ `htmltopdf/html_to_pdf_from_url.py` - URL → PDF
- ✅ `htmltopdf/static_html_to_pdf.py` - HTML file → PDF
- ✅ `createpdf/create_pdf_from_docx.py` - Word → PDF

### Manipulation
- `combinepdf/combine_pdf.py` - Merge PDFs
- `splitpdf/` - Split PDF
- `deletepages/delete_pdf_pages.py` - Delete pages
- `insertpages/` - Insert pages
- `replacepages/` - Replace pages
- `reorderpages/` - Reorder pages
- `rotatepages/` - Rotate pages

### Optimization
- ✅ `compresspdf/compress_pdf.py` - Compress
- ✅ `compresspdf/compress_pdf_with_options.py` - Compress with options
- `linearizepdf/` - Optimize for web

### Security
- `protectpdf/` - Add password
- `removeprotection/` - Remove password

### Design
- `pdfwatermark/` - Add watermark
- `autotagpdf/` - Accessibility tags
- `electronicseal/` - Digital signature

---

## 🚀 Next Steps

### **Right Now**:
1. ✅ Update `backend/.env` with credentials
2. ✅ Run: `python test_adobe_credentials.py`
3. ✅ Restart backend
4. ✅ Try OCR from frontend → Should work!

### **Future**:
- Add Watermark API (samples ready!)
- Add Combine PDF (samples ready!)
- Add Split PDF (samples ready!)
- Add more features as needed

---

## 📖 Resources

- 📘 **Full Docs**: https://developer.adobe.com/document-services/docs/
- 🔧 **API Ref**: https://developer.adobe.com/document-services/apis/pdf-services/
- 💻 **Python SDK**: https://github.com/adobe/pdfservices-python-sdk
- 🎓 **Tutorials**: https://developer.adobe.com/document-services/docs/overview/pdf-services-api/howtos/
- 🔗 **Console**: https://developer.adobe.com/console

---

## ✅ Summary

🎉 **You're all set!**

- ✅ **Credentials**: Ready in `public/adobe/`
- ✅ **Backend**: Already integrated (OCR, Extract, Export, HTML→PDF, Compress)
- ✅ **Samples**: 50+ examples in `public/adobe/.../src/`
- ✅ **Free tier**: 500 transactions/month

**Just update `.env` and start using Adobe AI!** 🚀
