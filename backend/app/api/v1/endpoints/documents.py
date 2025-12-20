"""
Modern Document Conversion API Endpoints (2025)
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, Depends
from fastapi.responses import FileResponse, StreamingResponse, Response
from typing import List, Optional
from pathlib import Path
from urllib.parse import quote
from datetime import datetime
import zipfile
import io
import asyncio
import aiofiles
import logging
import time

from app.services.document_service import DocumentService
from pathlib import Path

router = APIRouter(tags=["Document Conversion"])

# Initialize global service
upload_dir = Path("./uploads/documents")
doc_service = DocumentService(upload_dir=str(upload_dir))

# Setup logger
logger = logging.getLogger(__name__)


def encode_filename(filename: str) -> str:
    """Encode filename for Content-Disposition header (RFC 2231)"""
    return quote(filename)


@router.get("/gemini/models")
async def get_gemini_models():
    """
    Get all available Gemini models with metadata
    
    Returns:
        List of available Gemini models with:
        - name: Display name
        - model_id: Model identifier for API calls
        - series: Model generation (2.5, 3.0, etc.)
        - description: Brief description
        - features: List of key features
        - use_cases: Recommended use cases
        - quality: Quality rating (1-10)
        - speed: Speed rating (1-10)
        - pricing: Input/output costs per 1M tokens
        - status: stable/preview/experimental/legacy
        - badge: Special badge if any
        - recommended_for: Tags for filtering
    """
    from app.services.document_service import GEMINI_MODELS, DEFAULT_GEMINI_MODEL
    
    # Transform models dict to list with model_id
    models_list = []
    for model_id, model_info in GEMINI_MODELS.items():
        model_data = {
            "model_id": model_id,
            "is_default": model_id == DEFAULT_GEMINI_MODEL,
            **model_info
        }
        models_list.append(model_data)
    
    # Sort by quality (highest first), then by series (newest first)
    models_list.sort(
        key=lambda x: (
            -x.get("quality", 0),  # Higher quality first
            -float(x.get("series", "0"))  # Newer series first
        )
    )
    
    return {
        "models": models_list,
        "default_model": DEFAULT_GEMINI_MODEL,
        "total_count": len(models_list),
        "categories": {
            "recommended": [m for m in models_list if m.get("badge") or m.get("is_default")],
            "stable": [m for m in models_list if m.get("status") == "stable"],
            "preview": [m for m in models_list if m.get("status") == "preview"],
            "budget": [m for m in models_list if "budget" in m.get("recommended_for", [])],
        }
    }


def get_document_service():
    """Dependency to get DocumentService instance"""
    return doc_service


@router.post("/convert/word-to-pdf")
async def convert_word_to_pdf(
    file: UploadFile = File(..., description="Word file (.docx, .doc)"),
):
    """
    Chuyển đổi Word sang PDF bằng **Gotenberg** (Giải pháp hiện đại 2025)
    
    **Gotenberg** là Docker microservice sử dụng LibreOffice headless:
    - ⚡ Nhanh, ổn định, production-ready
    - 🐳 Chạy trong Docker container riêng
    - 🎯 Không cần cài LibreOffice trên host machine
    - ✅ Giữ nguyên formatting, hình ảnh, bảng biểu
    - 📦 Support: .docx, .doc, .xls, .xlsx, .ppt, .pptx, .odt...
    
    **Fallback**: Nếu Gotenberg không khả dụng, tự động dùng LibreOffice local (dev only)
    """
    # Save uploaded file
    input_path = await doc_service.save_upload_file(file)
    
    try:
        # Convert
        output_path = await doc_service.word_to_pdf(input_path)
        
        # Return file with technology metadata in headers
        response = FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=output_path.name,
            background=None  # Don't delete file yet
        )
        
        # Add technology metadata to response headers (no emojis - HTTP headers only support Latin-1)
        response.headers["X-Technology-Engine"] = "gotenberg"
        response.headers["X-Technology-Name"] = "Gotenberg"
        response.headers["X-Technology-Quality"] = "9/10"
        response.headers["X-Technology-Type"] = "local"
        
        return response
        
    except Exception as e:
        # Cleanup on error
        await doc_service.cleanup_file(input_path)
        raise e


@router.post("/convert/excel-to-pdf")
async def convert_excel_to_pdf(
    file: UploadFile = File(..., description="Excel file (.xlsx, .xls)"),
):
    """
    Chuyển đổi Excel sang PDF bằng Gotenberg
    
    - Support: .xlsx, .xls
    - Giữ nguyên formatting, charts, formulas
    - Powered by LibreOffice headless
    """
    input_path = await doc_service.save_upload_file(file)
    
    try:
        output_path = await doc_service.office_to_pdf(input_path)
        
        return FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=output_path.name,
            background=None
        )
    except Exception as e:
        await doc_service.cleanup_file(input_path)
        raise e


@router.post("/convert/powerpoint-to-pdf")
async def convert_powerpoint_to_pdf(
    file: UploadFile = File(..., description="PowerPoint file (.pptx, .ppt)"),
):
    """
    Chuyển đổi PowerPoint sang PDF bằng Gotenberg
    
    - Support: .pptx, .ppt
    - Mỗi slide thành 1 trang PDF
    - Giữ nguyên animations, transitions thành static images
    """
    input_path = await doc_service.save_upload_file(file)
    
    try:
        output_path = await doc_service.office_to_pdf(input_path)
        
        return FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=output_path.name,
            background=None
        )
    except Exception as e:
        await doc_service.cleanup_file(input_path)
        raise e


@router.post("/convert/pdf-to-word")
async def convert_pdf_to_word(
    file: UploadFile = File(..., description="PDF file"),
    start_page: int = Form(0, description="Start page (0-indexed)"),
    end_page: Optional[int] = Form(None, description="End page (None = all)"),
    enable_ocr: bool = Form(False, description="Enable OCR for scanned PDFs"),
    ocr_language: str = Form("vi-VN", description="OCR language (vi-VN, en-US, fr-FR, etc.)"),
    auto_detect_scanned: bool = Form(True, description="Auto-detect scanned PDFs and enable OCR"),
    use_gemini: bool = Form(False, description="Use Gemini API (best for Vietnamese + tables)"),
    gemini_model: Optional[str] = Form(None, description="Gemini model to use (e.g., gemini-2.5-flash)"),
):
    """
    Convert PDF to Word document
    
    - **Gemini API:** 9-10/10 quality, 100+ languages, multiple models, best for Vietnamese + tables
    - **Adobe PDF Services:** 10/10 quality, AI-powered BUT NO Vietnamese support  
    - **pdf2docx:** 7/10 quality, pure Python fallback
    - Can convert specific page ranges
    - Preserves formatting, images, tables
    
    **Gemini API (NEW - December 2025):**
    - `use_gemini`: Use Gemini API instead of Adobe (default: False)
    - `gemini_model`: Choose specific model (default: gemini-2.5-flash)
      - gemini-2.5-flash: ⭐ Best price-performance (recommended)
      - gemini-2.5-flash-lite: 💰 Cheapest (80% off)
      - gemini-2.5-pro: 🎯 Highest quality (advanced reasoning)
      - gemini-3-pro-preview: 🚀 Cutting edge (world's best)
    - Supports 100+ languages including Vietnamese
    - Native PDF understanding (no OCR preprocessing needed)
    - Best for tables, layout, complex documents
    - Quality: 9-10/10 depending on model
    - FREE tier: 1,500 requests/day
    
    **OCR Support (Adobe only):**
    - `enable_ocr`: Manually enable OCR for scanned PDFs
    - `ocr_language`: Language for OCR (default: vi-VN for Vietnamese)
    - `auto_detect_scanned`: Auto-detect if PDF is scanned and enable OCR
    
    **Supported OCR Languages (Adobe):**
    - vi-VN (Vietnamese) - NOT SUPPORTED BY ADOBE! Use Gemini instead
    - en-US (English), fr-FR (French), de-DE (German)
    - es-ES (Spanish), it-IT (Italian), pt-BR (Portuguese), ja-JP (Japanese)
    - ko-KR (Korean), zh-CN (Chinese Simplified), zh-TW (Chinese Traditional)
    - and 40+ more languages
    
    **How it works:**
    1. If `use_gemini=True`, use Gemini API (supports Vietnamese)
    2. Else if `auto_detect_scanned=True` (default), automatically detects scanned PDFs
    3. Scanned PDFs are converted with OCR enabled automatically
    4. Or manually set `enable_ocr=True` to force OCR
    5. Adobe performs OCR during conversion (one-step, no intermediate files)
    """
    # Save uploaded file
    input_path = await doc_service.save_upload_file(file)
    
    try:
        # Track which technology was used
        used_adobe = False
        used_gemini = False
        used_ocr = False
        
        # Convert (priority: Gemini > Adobe > pdf2docx)
        output_path = await doc_service.pdf_to_word(
            input_path,
            start_page=start_page,
            end_page=end_page,
            enable_ocr=enable_ocr,
            ocr_language=ocr_language,
            auto_detect_scanned=auto_detect_scanned,
            use_gemini=use_gemini,
            gemini_model=gemini_model
        )
        
        # Check which technology was actually used
        if use_gemini and doc_service.gemini_model:
            used_gemini = True
            # Get actual model name used
            actual_model = gemini_model or doc_service.gemini_model_name
        elif doc_service.use_adobe and doc_service.adobe_credentials:
            used_adobe = True
            # Check if OCR was enabled (either manually or auto-detected)
            from app.services.document_service import is_pdf_scanned
            if enable_ocr or (auto_detect_scanned and is_pdf_scanned(input_path)):
                used_ocr = True
        
        # Return file with technology metadata
        response = FileResponse(
            path=output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=output_path.name
        )
        
        # Add technology metadata to response headers (no emojis - HTTP headers only support Latin-1)
        if used_gemini:
            from app.services.document_service import GEMINI_MODELS
            model_info = GEMINI_MODELS.get(actual_model, {})
            
            response.headers["X-Technology-Engine"] = "gemini"
            response.headers["X-Technology-Name"] = model_info.get("name", "Google Gemini API")
            response.headers["X-Technology-Model"] = actual_model
            response.headers["X-Technology-Quality"] = f"{model_info.get('quality', 9)}/10"
            response.headers["X-Technology-Speed"] = f"{model_info.get('speed', 9)}/10"
            response.headers["X-Technology-Type"] = "cloud"
            response.headers["X-Technology-Series"] = model_info.get("series", "2.5")
            response.headers["X-Technology-Status"] = model_info.get("status", "stable")
            response.headers["X-Technology-Languages"] = "100+ including Vietnamese"
            
            # Cost information
            pricing = model_info.get("pricing", {})
            if pricing:
                response.headers["X-Technology-Price-Input"] = f"${pricing.get('input', 0.50)} per 1M tokens"
                response.headers["X-Technology-Price-Output"] = f"${pricing.get('output', 2.00)} per 1M tokens"
            
            response.headers["X-Technology-Features"] = "Native PDF understanding, best for tables"
        elif used_adobe:
            response.headers["X-Technology-Engine"] = "adobe"
            response.headers["X-Technology-Name"] = "Adobe PDF Services"
            response.headers["X-Technology-Quality"] = "10/10"
            response.headers["X-Technology-Type"] = "cloud"
            response.headers["X-Technology-OCR"] = "true" if used_ocr else "false"
            response.headers["X-Technology-OCR-Language"] = ocr_language if used_ocr else "none"
            # TODO: Add quota tracking
            # response.headers["X-Adobe-Quota-Remaining"] = "498/500"
        else:
            response.headers["X-Technology-Engine"] = "pdf2docx"
            response.headers["X-Technology-Name"] = "pdf2docx"
            response.headers["X-Technology-Quality"] = "7/10"
            response.headers["X-Technology-Type"] = "local"
            response.headers["X-Technology-OCR"] = "false"
        
        return response
        
    except Exception as e:
        await doc_service.cleanup_file(input_path)
        raise e


@router.post("/convert/pdf-to-excel")
async def convert_pdf_to_excel(
    file: UploadFile = File(..., description="PDF file with tables"),
):
    """
    Convert PDF to Excel (.xlsx)
    
    - Extracts **tables** from PDF using **pdfplumber** (8/10 quality)
    - Creates separate sheets for each page with tables
    - Auto-formats with headers, column widths
    - Falls back to text extraction if no tables found
    """
    # Save uploaded file
    input_path = await doc_service.save_upload_file(file)
    
    try:
        # Convert
        output_path = await doc_service.pdf_to_excel(input_path)
        
        # Return file with technology metadata
        response = FileResponse(
            path=output_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=output_path.name
        )
        
        # Add technology metadata to response headers (no emojis - HTTP headers only support Latin-1)
        response.headers["X-Technology-Engine"] = "pdfplumber"
        response.headers["X-Technology-Name"] = "pdfplumber"
        response.headers["X-Technology-Quality"] = "8/10"
        response.headers["X-Technology-Type"] = "local"
        
        return response
        
    except Exception as e:
        await doc_service.cleanup_file(input_path)
        raise e


@router.post("/pdf/merge")
async def merge_pdfs(
    files: List[UploadFile] = File(..., description="Multiple PDF files"),
    output_filename: str = Form("merged.pdf", description="Output filename"),
):
    """
    Merge multiple PDF files into one
    
    - Preserves all pages from all files
    - Files are merged in the order provided
    """
    if len(files) < 2:
        raise HTTPException(400, "Need at least 2 PDF files to merge")
    
    # Save all uploaded files
    input_paths = []
    for file in files:
        path = await doc_service.save_upload_file(file)
        input_paths.append(path)
    
    try:
        # Merge
        output_path = await doc_service.merge_pdfs(input_paths, output_filename)
        
        # Return file
        return FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=output_path.name
        )
        
    finally:
        # Cleanup input files
        for path in input_paths:
            await doc_service.cleanup_file(path)


@router.post("/pdf/split-pypdf")
async def split_pdf_pypdf(
    file: UploadFile = File(..., description="PDF file"),
    page_ranges: str = Form(..., description="Page ranges, e.g., '1-3,5-7,10'"),
    output_prefix: str = Form("split", description="Output files prefix"),
):
    """
    Split PDF into multiple files by page ranges (OLD pypdf method)
    
    **Examples:**
    - `page_ranges="1-3,5-7"` → Creates 2 files (pages 1-3, pages 5-7)
    - `page_ranges="1,3,5"` → Creates 3 files (page 1, page 3, page 5)
    
    **NOTE:** This is the old pypdf implementation. Use `/pdf/split` for Adobe quality.
    """
    # Parse page ranges
    ranges = []
    for part in page_ranges.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            ranges.append((int(start), int(end)))
        else:
            page = int(part)
            ranges.append((page, page))
    
    # Save uploaded file
    input_path = await doc_service.save_upload_file(file)
    
    try:
        # Split PDF - convert ranges to string format like ["1-3", "4-6"]
        range_strings = [f"{start}-{end}" for start, end in ranges]
        output_paths = await doc_service.split_pdf(input_path, range_strings)
        
        # For now, return first file (in real app, zip all files)
        if output_paths:
            return FileResponse(
                path=output_paths[0],
                media_type="application/pdf",
                filename=output_paths[0].name
            )
        else:
            raise HTTPException(500, "No output files generated")
            
    except Exception as e:
        await doc_service.cleanup_file(input_path)
        raise e


@router.post("/pdf/extract-text")
async def extract_pdf_text(
    file: UploadFile = File(..., description="PDF file"),
):
    """
    Extract all text from PDF
    
    - Returns plain text content
    - Useful for text analysis, search, etc.
    """
    # Save uploaded file
    input_path = await doc_service.save_upload_file(file)
    
    try:
        # Extract text
        text = await doc_service.extract_pdf_text(input_path)
        
        return {
            "filename": file.filename,
            "text": text,
            "char_count": len(text),
            "word_count": len(text.split())
        }
        
    finally:
        await doc_service.cleanup_file(input_path)


@router.post("/pdf/rotate")
async def rotate_pdf(
    file: UploadFile = File(..., description="PDF file"),
    rotation: int = Form(90, description="Rotation angle (90, 180, 270)"),
    pages: Optional[str] = Form(None, description="Comma-separated page numbers (None = all)"),
):
    """
    Rotate PDF pages
    
    - **rotation**: 90, 180, or 270 degrees clockwise
    - **pages**: Specific pages to rotate (e.g., "1,3,5" or None for all)
    """
    # Parse pages
    page_list = None
    if pages:
        page_list = [int(p.strip()) for p in pages.split(',')]
    
    # Save uploaded file
    input_path = await doc_service.save_upload_file(file)
    
    try:
        # Rotate
        output_path = await doc_service.rotate_pdf_pages(
            input_path,
            rotation=rotation,
            pages=page_list
        )
        
        # Return file
        return FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=output_path.name
        )
        
    finally:
        await doc_service.cleanup_file(input_path)


@router.post("/info/pdf")
async def get_pdf_info(
    file: UploadFile = File(..., description="PDF file"),
):
    """
    Get PDF file information
    
    Returns:
    - Number of pages
    - Metadata (title, author, etc.)
    - Encryption status
    - Page sizes
    """
    input_path = await doc_service.save_upload_file(file)
    
    try:
        info = await doc_service.get_pdf_info(input_path)
        return {"filename": file.filename, **info}
    finally:
        await doc_service.cleanup_file(input_path)


@router.post("/info/word")
async def get_word_info(
    file: UploadFile = File(..., description="Word file (.docx)"),
):
    """
    Get Word document information
    
    Returns:
    - Number of paragraphs
    - Number of tables
    - Number of images
    - Word count
    - Character count
    """
    input_path = await doc_service.save_upload_file(file)
    
    try:
        info = await doc_service.get_word_info(input_path)
        return {"filename": file.filename, **info}
    finally:
        await doc_service.cleanup_file(input_path)


@router.post("/info/excel")
async def get_excel_info(
    file: UploadFile = File(..., description="Excel file (.xlsx)"),
):
    """
    Get Excel workbook information
    
    Returns:
    - Number of sheets
    - Sheet names
    - Active sheet
    """
    input_path = await doc_service.save_upload_file(file)
    
    try:
        info = await doc_service.get_excel_info(input_path)
        return {"filename": file.filename, **info}
    finally:
        await doc_service.cleanup_file(input_path)


@router.post("/info/powerpoint")
async def get_powerpoint_info(
    file: UploadFile = File(..., description="PowerPoint file (.pptx)"),
):
    """
    Get PowerPoint presentation information
    
    Returns:
    - Number of slides
    - Slide dimensions
    """
    input_path = await doc_service.save_upload_file(file)
    
    try:
        info = await doc_service.get_powerpoint_info(input_path)
        return {"filename": file.filename, **info}
    finally:
        await doc_service.cleanup_file(input_path)


@router.post("/pdf/compress")
async def compress_pdf(
    file: UploadFile = File(..., description="PDF file to compress"),
    quality: str = Form("medium", description="Compression quality: low, medium, high"),
):
    """
    📦 Compress PDF file to reduce size - HYBRID (Adobe AI or pypdf)
    
    **Quality Levels:**
    - `low`: Maximum compression (smallest file)
      - Adobe: 50-80% reduction (10/10 quality)
      - pypdf: 30-50% reduction (7/10 quality)
    - `medium`: Balanced (recommended)
      - Adobe: 40-60% reduction (10/10 quality)
      - pypdf: 20-40% reduction (7/10 quality)
    - `high`: Light compression (preserve quality)
      - Adobe: 20-40% reduction (10/10 quality)
      - pypdf: 10-30% reduction (7/10 quality)
    
    **Technology Used:**
    - Tries Adobe PDF Services first (AI-powered, best quality)
    - Falls back to pypdf if Adobe unavailable
    - Returns which technology was used in headers
    
    **Headers:**
    - `X-Technology-Engine`: adobe or pypdf
    - `X-Technology-Quality`: 10/10 or 7/10
    - `X-Compression-Ratio`: Percentage reduced
    """
    input_path = await doc_service.save_upload_file(file)
    
    try:
        # Get original size
        original_size = input_path.stat().st_size
        
        # Compress (returns tuple: output_path, technology_used)
        output_path, technology = await doc_service.compress_pdf(input_path, quality)
        
        # Get compressed size
        compressed_size = output_path.stat().st_size
        compression_ratio = ((original_size - compressed_size) / original_size * 100)
        
        # Dynamic headers based on technology used
        response = FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_path.name
        )
        
        # Technology metadata headers
        if technology == "adobe":
            response.headers["X-Technology-Engine"] = "adobe"
            response.headers["X-Technology-Name"] = "Adobe Compress PDF"
            response.headers["X-Technology-Quality"] = "10/10"
            response.headers["X-Technology-Type"] = "cloud"
        else:  # pypdf
            response.headers["X-Technology-Engine"] = "pypdf"
            response.headers["X-Technology-Name"] = "pypdf"
            response.headers["X-Technology-Quality"] = "7/10"
            response.headers["X-Technology-Type"] = "local"
        
        # Compression info headers
        response.headers["X-Original-Size"] = str(original_size)
        response.headers["X-Compressed-Size"] = str(compressed_size)
        response.headers["X-Compression-Ratio"] = f"{compression_ratio:.1f}%"
        
        return response
        
    finally:
        await doc_service.cleanup_file(input_path)


@router.post("/convert/image-to-pdf")
async def image_to_pdf(
    file: UploadFile = File(..., description="Image file (JPG, PNG, etc.)"),
):
    """
    Convert image to PDF
    
    Supported formats: JPG, JPEG, PNG, GIF, BMP, WebP, HEIC
    
    - Automatically handles transparency (PNG)
    - Converts to RGB color space
    - Maintains original resolution
    - High quality output (95%)
    """
    input_path = await doc_service.save_upload_file(file)
    
    try:
        output_path = await doc_service.image_to_pdf(input_path)
        
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_path.name
        )
        
    finally:
        await doc_service.cleanup_file(input_path)


# OLD TEXT WATERMARK - Moved to /pdf/watermark-text to avoid conflict
@router.post("/pdf/watermark-text")
async def add_watermark(
    file: UploadFile = File(..., description="PDF file"),
    watermark_text: str = Form(..., description="Watermark text"),
    position: str = Form("center", description="Position: center, top-left, top-right, bottom-left, bottom-right"),
    opacity: float = Form(0.3, description="Opacity (0.0 to 1.0)"),
):
    """
    💧 Add text watermark to PDF - HYBRID (Adobe or pypdf)
    
    **Parameters:**
    - `watermark_text`: Text to display as watermark
    - `position`: Where to place watermark (center, top-left, top-right, bottom-left, bottom-right)
    - `opacity`: Transparency level (0.0 = fully transparent, 1.0 = fully opaque)
    
    **Technology Used:**
    - Tries Adobe PDF Services first (advanced watermark, 10/10 quality)
    - Falls back to reportlab+pypdf (basic watermark, 8/10 quality)
    - Returns which technology was used in headers
    
    **Note:** Adobe Watermark API may not be available yet in SDK, will fallback to pypdf
    """
    input_path = await doc_service.save_upload_file(file)
    
    try:
        # Add watermark (returns tuple: output_path, technology_used)
        output_path, technology = await doc_service.add_watermark_to_pdf(
            input_path, watermark_text, position, opacity
        )
        
        # Dynamic headers based on technology used
        response = FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_path.name
        )
        
        # Technology metadata headers
        if technology == "adobe":
            response.headers["X-Technology-Engine"] = "adobe"
            response.headers["X-Technology-Name"] = "Adobe Watermark"
            response.headers["X-Technology-Quality"] = "10/10"
            response.headers["X-Technology-Type"] = "cloud"
        else:  # pypdf
            response.headers["X-Technology-Engine"] = "pypdf"
            response.headers["X-Technology-Name"] = "reportlab+pypdf"
            response.headers["X-Technology-Quality"] = "8/10"
            response.headers["X-Technology-Type"] = "local"
        
        return response
        
    finally:
        await doc_service.cleanup_file(input_path)


@router.post("/pdf/protect")
async def protect_pdf(
    file: UploadFile = File(..., description="PDF file"),
    password: str = Form(..., description="Password to protect PDF"),
):
    """
    Protect PDF with password
    
    - **password**: Password required to open the PDF
    - User can open with password
    - Allows printing
    """
    input_path = await doc_service.save_upload_file(file)
    
    try:
        output_path = await doc_service.protect_pdf_with_password(input_path, password)
        
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_path.name
        )
        
    finally:
        await doc_service.cleanup_file(input_path)


@router.post("/pdf/unlock")
async def unlock_pdf(
    file: UploadFile = File(..., description="Encrypted PDF file"),
    password: str = Form(..., description="Password to unlock PDF"),
):
    """
    Remove password protection from PDF
    
    - **password**: Current password of the PDF
    - Returns unprotected PDF
    """
    input_path = await doc_service.save_upload_file(file)
    
    try:
        output_path = await doc_service.unlock_pdf(input_path, password)
        
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_path.name
        )
        
    finally:
        await doc_service.cleanup_file(input_path)


# ==================== NEW: ADOBE-ONLY FEATURES ====================

@router.post("/pdf/ocr")
async def ocr_pdf(
    file: UploadFile = File(..., description="Scanned PDF file"),
    language: str = Form("vi-VN", description="Language code (vi-VN, en-US, fr-FR, etc.)"),
):
    """
    🔍 OCR - Convert scanned PDF to searchable PDF
    
    **Technology Priority:**
    1. **Adobe OCR (10/10)** - Best quality, 50+ languages, perfect layout
    2. **Tesseract OCR (7/10)** - Free fallback, basic OCR
    
    **Features:**
    - Extract text from scanned PDFs
    - Support Vietnamese ✅ (vi-VN)
    - 50+ languages supported (Adobe) / 100+ languages (Tesseract)
    - Make scanned PDFs searchable
    
    **Supported Languages:**
    - `vi-VN`: Vietnamese (tiếng Việt) ✅
    - `en-US`: English
    - `fr-FR`: French
    - `de-DE`: German
    - `es-ES`: Spanish
    - `it-IT`: Italian
    - `ja-JP`: Japanese
    - `ko-KR`: Korean
    - `zh-CN`: Chinese Simplified
    - ... and many more
    
    **Use Cases:**
    - Scan tài liệu giấy → searchable PDF
    - Digitize old documents
    - Make scanned contracts searchable
    - Process scanned invoices
    
    **Setup:**
    - For Adobe: Set `USE_ADOBE_PDF_API=true` in .env + configure credentials
    - For Tesseract: Install Tesseract-OCR binary (free)
    
    **Returns:** Searchable PDF with text layer
    """
    input_path = await doc_service.save_upload_file(file)
    
    try:
        # OCR PDF (Adobe preferred, Tesseract fallback)
        output_path = await doc_service.ocr_pdf(input_path, language)
        
        response = FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_path.name
        )
        
        # Detect which technology was used based on filename
        if "tesseract" in output_path.name.lower():
            response.headers["X-Technology-Engine"] = "tesseract"
            response.headers["X-Technology-Name"] = "Tesseract OCR"
            response.headers["X-Technology-Quality"] = "7/10"
            response.headers["X-Technology-Type"] = "local"
        else:
            response.headers["X-Technology-Engine"] = "adobe"
            response.headers["X-Technology-Name"] = "Adobe OCR"
            response.headers["X-Technology-Quality"] = "10/10"
            response.headers["X-Technology-Type"] = "cloud"
        
        response.headers["X-OCR-Language"] = language
        
        return response
        
    except HTTPException:
        raise
    finally:
        await doc_service.cleanup_file(input_path)


@router.post("/pdf/ocr-smart")
async def smart_pdf_ocr(
    file: UploadFile = File(..., description="PDF file"),
    ai_engine: str = Form("gemini", description="AI engine: gemini or claude"),
    language: str = Form("vi", description="Language for OCR: vi, en")
):
    """
    🤖 Smart PDF OCR - AI-powered text extraction for scanned PDFs
    
    **Smart Detection:**
    - Automatically detects if PDF is scanned (image-based)
    - Uses direct text extraction for text-based PDFs (fast & free)
    - Uses AI OCR (Gemini/Claude) only for scanned PDFs
    
    **AI Engines:**
    - `gemini`: Fast & cost-effective (~$0.000031/page)
    - `claude`: Highest accuracy (~$0.001464/page)
    
    **Languages:**
    - `vi`: Tiếng Việt (recommended for Vietnamese docs)
    - `en`: English
    
    **Use Cases:**
    - Extract text from scanned documents
    - OCR old paper documents converted to PDF
    - Process image-based PDFs with high accuracy
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, "File must be a PDF")
    
    # Save uploaded file
    input_path = await doc_service.save_upload_file(file)
    
    try:
        # Smart OCR processing
        result = await doc_service.smart_pdf_ocr(
            input_path, 
            ai_engine=ai_engine,
            language=language
        )
        
        return {
            "success": True,
            "filename": file.filename,
            **result
        }
        
    except HTTPException:
        raise
    finally:
        await doc_service.cleanup_file(input_path)


@router.post("/generate-report")
async def generate_ai_report(
    text_input: str = Form(..., description="Text content to analyze"),
    report_title: str = Form(None, description="Custom report title (optional)"),
    language: str = Form("vi", description="Language: vi or en"),
):
    """
    🤖 AI Report Generator - Create beautiful Word reports from text
    
    **How it works:**
    1. AI analyzes your text and structures it logically
    2. Creates comparison tables, sections, bullet points
    3. Generates professional Word document with colors and formatting
    
    **Features:**
    - 📊 Comparison tables with styled headers
    - 🎨 Blue headings and colored elements
    - 📝 Organized sections with bullet points
    - ✨ Professional spacing and layout
    - 🌍 Vietnamese & English support
    
    **Example use cases:**
    - Compare technologies/products/methods
    - Analyze data and create reports
    - Structure meeting notes into formal reports
    - Convert chat discussions into documents
    
    **Cost:** ~$0.001-0.005 per report
    """
    try:
        from app.services.ai_report_generator import AIReportGenerator
        
        # Create generator
        output_dir = Path("./temp_outputs")
        output_dir.mkdir(exist_ok=True)
        generator = AIReportGenerator(output_dir=output_dir)
        
        # Generate report
        output_path = await generator.generate_comparison_report(
            text_input=text_input,
            title=report_title,
            language=language
        )
        
        # Return Word file
        if not output_path.exists():
            raise HTTPException(404, "Report file not generated")
        
        return FileResponse(
            str(output_path),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"AI_Report_{int(time.time())}.docx",
            headers={
                "X-Technology-Engine": "gemini",
                "X-Technology-Model": "gemini-2.0-flash-exp",
                "X-Technology-Type": "cloud",
                "X-Technology-Feature": "AI Report Generator"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Report generation failed: {str(e)}")


@router.post("/pdf/extract-content")
async def extract_pdf_content(
    file: UploadFile = File(..., description="PDF file"),
    extract_type: str = Form("all", description="What to extract: all, text, tables, images"),
):
    """
    🔬 Extract PDF Content - AI-powered extraction (Adobe)
    
    **Adobe Extract Features:**
    - Extract tables → Structured data (CSV/Excel format)
    - Extract images → PNG files with metadata
    - Extract text with font information (bold, italic, size, family)
    - AI-powered reading order detection
    - Character bounding boxes (precise position)
    - Document structure detection (headings, paragraphs, lists)
    
    **Extract Types:**
    - `all`: Extract everything (text, tables, images)
    - `text`: Text only with font information
    - `tables`: Tables only
    - `images`: Images only
    
    **Use Cases:**
    - Extract tables from financial reports → Excel
    - Extract images from catalogs → PNG files
    - Data mining from PDF documents
    - Convert PDF reports to database records
    - Analyze document structure
    
    **Requirements:**
    - Adobe PDF Services API must be enabled
    - Set `USE_ADOBE_PDF_API=true` in .env
    - Configure Adobe credentials
    
    **Pricing:** 1 transaction per PDF file
    
    **Returns:** JSON with extracted content:
    ```json
    {
        "text": [{"text": "...", "font": {...}, "bounds": [...]}],
        "tables": [{"cells": [...], "data": [[...]]}],
        "images": [{"path": "...", "width": 800, "height": 600}],
        "structure": {"headings": [...], "paragraphs": [...]}
    }
    ```
    """
    input_path = await doc_service.save_upload_file(file)
    
    try:
        # Extract content (Adobe-only, no fallback)
        result = await doc_service.extract_pdf_content(input_path, extract_type)
        
        return {
            "success": True,
            "data": result,
            "technology": {
                "engine": "adobe",
                "name": "Adobe Extract API",
                "quality": "10/10",
                "type": "cloud"
            },
            "extract_type": extract_type,
            "summary": {
                "text_elements": len(result.get("text", [])),
                "tables": len(result.get("tables", [])),
                "images": len(result.get("images", []))
            }
        }
        
    except HTTPException:
        raise
    finally:
        await doc_service.cleanup_file(input_path)


@router.post("/convert/html-to-pdf")
async def html_to_pdf(
    html_content: str = Form(..., description="HTML content or URL"),
    page_size: str = Form("A4", description="Page size: A4, Letter, Legal, A3"),
    orientation: str = Form("portrait", description="Orientation: portrait or landscape"),
):
    """
    🌐 HTML to PDF - Perfect HTML rendering (Adobe)
    
    **Adobe HTML to PDF Features:**
    - Perfect rendering (same as Chrome browser)
    - Full CSS3 support
    - JavaScript execution
    - Custom page size (A4, Letter, Legal, A3)
    - Portrait/Landscape orientation
    - Header/Footer support
    - Margin control
    
    **Page Sizes:**
    - `A4`: 210mm × 297mm (default)
    - `Letter`: 8.5in × 11in
    - `Legal`: 8.5in × 14in
    - `A3`: 297mm × 420mm
    
    **Orientation:**
    - `portrait`: Vertical (default)
    - `landscape`: Horizontal
    
    **Use Cases:**
    - Generate invoices from HTML templates
    - Create reports from web dashboards
    - Convert web pages to PDF
    - Generate certificates/diplomas
    - Export data visualizations
    
    **Requirements:**
    - Adobe PDF Services API must be enabled
    - Set `USE_ADOBE_PDF_API=true` in .env
    - Configure Adobe credentials
    
    **Pricing:** 1 transaction per conversion
    
    **Example HTML:**
    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial; }
            .header { background: #333; color: white; padding: 20px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>My Report</h1>
        </div>
        <p>Content here...</p>
    </body>
    </html>
    ```
    
    **Returns:** Generated PDF file
    """
    try:
        # Convert HTML to PDF (Adobe-only, no fallback)
        output_path = await doc_service.html_to_pdf(
            html_content=html_content,
            page_size=page_size,
            orientation=orientation,
            output_filename=f"document_{page_size}_{orientation}.pdf"
        )
        
        response = FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_path.name
        )
        
        # Technology metadata headers
        response.headers["X-Technology-Engine"] = "adobe"
        response.headers["X-Technology-Name"] = "Adobe CreatePDF"
        response.headers["X-Technology-Quality"] = "10/10"
        response.headers["X-Technology-Type"] = "cloud"
        response.headers["X-Page-Size"] = page_size
        response.headers["X-Orientation"] = orientation
        
        return response
        
    except HTTPException:
        raise


# ==================== END: ADOBE-ONLY FEATURES ====================


@router.post("/pdf/to-images")
async def pdf_to_images(
    file: UploadFile = File(..., description="PDF file"),
    format: str = Form("png", description="Image format: png or jpg"),
    dpi: int = Form(200, description="Resolution in DPI (default: 200)"),
):
    """
    Convert PDF pages to images
    
    - **format**: Output image format (png or jpg)
    - **dpi**: Resolution (higher = better quality, larger file)
    - Returns ZIP file containing all page images
    """
    input_path = await doc_service.save_upload_file(file)
    
    try:
        output_paths = await doc_service.pdf_to_images(input_path, format, dpi)
        
        # Create ZIP file
        import zipfile
        from pathlib import Path
        
        zip_path = doc_service.output_dir / f"{input_path.stem}_images.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for img_path in output_paths:
                zipf.write(img_path, img_path.name)
                await doc_service.cleanup_file(img_path)
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=zip_path.name
        )
        
    finally:
        await doc_service.cleanup_file(input_path)


@router.post("/pdf/add-page-numbers")
async def add_page_numbers(
    file: UploadFile = File(..., description="PDF file"),
    position: str = Form("bottom-center", description="Position: bottom-center, bottom-right, bottom-left"),
    format: str = Form("Page {page}", description="Format: {page}, Page {page} of {total}, etc."),
):
    """
    Add page numbers to PDF
    
    - **position**: Where to place page numbers
    - **format**: Page number format ({page} = current page, {total} = total pages)
    """
    input_path = await doc_service.save_upload_file(file)
    
    try:
        output_path = await doc_service.add_page_numbers(input_path, position, format)
        
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_path.name
        )
        
    finally:
        await doc_service.cleanup_file(input_path)


@router.delete("/cleanup")
async def cleanup_old_files(
    max_age_hours: int = 24
):
    """
    Delete old uploaded/output files
    
    - **max_age_hours**: Delete files older than this (default: 24 hours)
    """
    count = await doc_service.cleanup_old_files(max_age_hours)
    return {
        "deleted_files": count,
        "message": f"Deleted {count} files older than {max_age_hours} hours"
    }


# ==================== BATCH CONVERSION ENDPOINTS ====================

@router.post("/batch/word-to-pdf")
async def batch_convert_word_to_pdf(
    files: List[UploadFile] = File(..., description="Multiple Word files"),
):
    """
    **Batch Convert** nhiều file Word sang PDF cùng lúc
    
    - Upload nhiều file .docx, .doc
    - Tự động convert tất cả
    - Download kết quả dưới dạng ZIP
    
    **Use case:**
    - Convert hàng loạt báo cáo, tài liệu
    - Xử lý nhiều file cùng lúc tiết kiệm thời gian
    """
    if not files or len(files) == 0:
        raise HTTPException(400, "No files uploaded")
    
    output_files = []
    errors = []
    
    try:
        # Process each file
        for idx, file in enumerate(files, 1):
            try:
                print(f"[Batch Word→PDF] Processing file {idx}/{len(files)}: {file.filename}")
                input_path = await doc_service.save_upload_file(file)
                output_path = await doc_service.word_to_pdf(input_path)
                output_files.append(output_path)
                await doc_service.cleanup_file(input_path)
                print(f"[Batch Word→PDF] ✓ Success: {file.filename} → {output_path.name}")
            except Exception as e:
                error_msg = str(e)
                print(f"[Batch Word→PDF] ✗ Error: {file.filename} - {error_msg}")
                errors.append({"file": file.filename, "error": error_msg})
                # Cleanup input file even on error
                try:
                    if 'input_path' in locals():
                        await doc_service.cleanup_file(input_path)
                except:
                    pass
        
        if not output_files:
            raise HTTPException(500, f"All conversions failed. Errors: {errors}")
        
        print(f"[Batch Word→PDF] Creating ZIP with {len(output_files)} files...")
        
        # Create ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for idx, output_path in enumerate(output_files, 1):
                # Check if file still exists
                if not output_path.exists():
                    print(f"[Batch Word→PDF] ⚠ Warning: File not found: {output_path}")
                    continue
                
                # Handle duplicate filenames in ZIP by adding index
                zip_filename = output_path.name
                if list(output_files).count(output_path) > 1 or any(
                    f.name == output_path.name for f in output_files if f != output_path
                ):
                    # Add index to filename for duplicates
                    stem = output_path.stem
                    suffix = output_path.suffix
                    zip_filename = f"{stem}_{idx}{suffix}"
                
                zip_file.write(output_path, zip_filename)
                
                # Cleanup after adding to ZIP
                try:
                    await doc_service.cleanup_file(output_path)
                except Exception as e:
                    print(f"[Batch Word→PDF] ⚠ Cleanup warning: {e}")
        
        zip_buffer.seek(0)
        
        print(f"[Batch Word→PDF] ✓ ZIP created! Size: {len(zip_buffer.getvalue())} bytes")
        
        if errors:
            print(f"[Batch Word→PDF] ⚠ Completed with {len(errors)} errors: {errors}")
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=converted_pdfs_{len(output_files)}_files.zip"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Batch Word→PDF] ✗ Fatal error: {str(e)}")
        for output_path in output_files:
            try:
                await doc_service.cleanup_file(output_path)
            except:
                pass
        raise HTTPException(500, f"Batch conversion failed: {str(e)}")


@router.post("/batch/merge-word-to-pdf")
async def merge_word_files_to_pdf(
    files: List[UploadFile] = File(..., description="Multiple Word files to merge"),
):
    """
    **Merge & Convert** nhiều file Word thành 1 PDF duy nhất
    
    - Upload nhiều file Word (.docx, .doc)
    - Files sẽ được merge theo thứ tự upload
    - Convert thành 1 file PDF duy nhất
    - Hỗ trợ sắp xếp lại thứ tự trước khi merge
    
    **Use case:**
    - Gộp nhiều chương thành 1 tài liệu PDF
    - Merge nhiều báo cáo thành 1 file
    - Tạo PDF từ nhiều phần khác nhau
    """
    if not files or len(files) == 0:
        raise HTTPException(400, "No files uploaded")
    
    temp_pdf_files = []
    errors = []
    
    try:
        print(f"[Merge Word→PDF] Starting merge of {len(files)} Word files")
        
        # Step 1: Convert each Word to PDF
        for idx, file in enumerate(files, 1):
            try:
                print(f"[Merge Word→PDF] Converting file {idx}/{len(files)}: {file.filename}")
                input_path = await doc_service.save_upload_file(file)
                pdf_path = await doc_service.word_to_pdf(input_path)
                temp_pdf_files.append(pdf_path)
                await doc_service.cleanup_file(input_path)
                print(f"[Merge Word→PDF] ✓ Converted: {file.filename} → {pdf_path.name}")
            except Exception as e:
                error_msg = str(e)
                print(f"[Merge Word→PDF] ✗ Error converting {file.filename}: {error_msg}")
                errors.append({"file": file.filename, "error": error_msg})
        
        if not temp_pdf_files:
            raise HTTPException(500, f"All conversions failed. Errors: {errors}")
        
        if len(temp_pdf_files) < len(files):
            print(f"[Merge Word→PDF] ⚠ Warning: Only {len(temp_pdf_files)}/{len(files)} files converted successfully")
        
        # Step 2: Merge all PDFs into one
        print(f"[Merge Word→PDF] Merging {len(temp_pdf_files)} PDF files...")
        
        from pypdf import PdfMerger
        
        merger = PdfMerger()
        for pdf_path in temp_pdf_files:
            if pdf_path.exists():
                merger.append(str(pdf_path))
            else:
                print(f"[Merge Word→PDF] ⚠ Warning: PDF not found: {pdf_path}")
        
        # Save merged PDF
        output_path = doc_service.output_dir / f"merged_{len(temp_pdf_files)}_files.pdf"
        merger.write(str(output_path))
        merger.close()
        
        print(f"[Merge Word→PDF] ✓ Merged PDF created: {output_path.name}")
        
        # Cleanup temp PDFs
        for pdf_path in temp_pdf_files:
            try:
                await doc_service.cleanup_file(pdf_path)
            except:
                pass
        
        # Return merged PDF
        if errors:
            print(f"[Merge Word→PDF] ⚠ Completed with {len(errors)} errors: {errors}")
        
        return FileResponse(
            path=str(output_path),
            media_type="application/pdf",
            filename=f"merged_{len(files)}_documents.pdf",
            background=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Merge Word→PDF] ✗ Fatal error: {str(e)}")
        # Cleanup temp files
        for pdf_path in temp_pdf_files:
            try:
                await doc_service.cleanup_file(pdf_path)
            except:
                pass
        raise HTTPException(500, f"Merge and conversion failed: {str(e)}")


@router.post("/batch/pdf-to-word")
async def batch_convert_pdf_to_word(
    files: List[UploadFile] = File(..., description="Multiple PDF files"),
):
    """
    **Batch Convert** nhiều file PDF sang Word cùng lúc
    
    - Upload nhiều file PDF
    - Tự động convert tất cả sang .docx
    - Download kết quả dưới dạng ZIP
    """
    if not files or len(files) == 0:
        raise HTTPException(400, "No files uploaded")
    
    output_files = []
    errors = []
    
    try:
        for idx, file in enumerate(files, 1):
            try:
                print(f"[Batch PDF→Word] Processing file {idx}/{len(files)}: {file.filename}")
                input_path = await doc_service.save_upload_file(file)
                output_path = await doc_service.pdf_to_word(input_path)
                output_files.append(output_path)
                await doc_service.cleanup_file(input_path)
                print(f"[Batch PDF→Word] ✓ Success: {file.filename} → {output_path.name}")
            except Exception as e:
                error_msg = str(e)
                print(f"[Batch PDF→Word] ✗ Error: {file.filename} - {error_msg}")
                errors.append({"file": file.filename, "error": error_msg})
                try:
                    if 'input_path' in locals():
                        await doc_service.cleanup_file(input_path)
                except:
                    pass
        
        if not output_files:
            raise HTTPException(500, f"All conversions failed. Errors: {errors}")
        
        print(f"[Batch PDF→Word] Creating ZIP with {len(output_files)} files...")
        
        # Create ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for output_path in output_files:
                zip_file.write(output_path, output_path.name)
                await doc_service.cleanup_file(output_path)
        
        zip_buffer.seek(0)
        
        print(f"[Batch PDF→Word] ✓ ZIP created! Size: {len(zip_buffer.getvalue())} bytes")
        
        if errors:
            print(f"[Batch PDF→Word] ⚠ Completed with {len(errors)} errors: {errors}")
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=converted_word_{len(output_files)}_files.zip"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Batch PDF→Word] ✗ Fatal error: {str(e)}")
        for output_path in output_files:
            try:
                await doc_service.cleanup_file(output_path)
            except:
                pass
        raise HTTPException(500, f"Batch conversion failed: {str(e)}")


@router.post("/batch/excel-to-pdf")
async def batch_convert_excel_to_pdf(
    files: List[UploadFile] = File(..., description="Multiple Excel files"),
):
    """
    **Batch Convert** nhiều file Excel sang PDF cùng lúc
    
    - Upload nhiều file .xlsx, .xls
    - Tự động convert tất cả
    - Download kết quả dưới dạng ZIP
    """
    if not files or len(files) == 0:
        raise HTTPException(400, "No files uploaded")
    
    output_files = []
    errors = []
    
    try:
        for idx, file in enumerate(files, 1):
            try:
                print(f"[Batch Excel→PDF] Processing file {idx}/{len(files)}: {file.filename}")
                input_path = await doc_service.save_upload_file(file)
                output_path = await doc_service.office_to_pdf(input_path)
                output_files.append(output_path)
                await doc_service.cleanup_file(input_path)
                print(f"[Batch Excel→PDF] ✓ Success: {file.filename} → {output_path.name}")
            except Exception as e:
                error_msg = str(e)
                print(f"[Batch Excel→PDF] ✗ Error: {file.filename} - {error_msg}")
                errors.append({"file": file.filename, "error": error_msg})
                try:
                    if 'input_path' in locals():
                        await doc_service.cleanup_file(input_path)
                except:
                    pass
        
        if not output_files:
            raise HTTPException(500, f"All conversions failed. Errors: {errors}")
        
        print(f"[Batch Excel→PDF] Creating ZIP with {len(output_files)} files...")
        
        # Create ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for output_path in output_files:
                zip_file.write(output_path, output_path.name)
                await doc_service.cleanup_file(output_path)
        
        zip_buffer.seek(0)
        
        print(f"[Batch Excel→PDF] ✓ ZIP created! Size: {len(zip_buffer.getvalue())} bytes")
        
        if errors:
            print(f"[Batch Excel→PDF] ⚠ Completed with {len(errors)} errors: {errors}")
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=converted_excel_pdf_{len(output_files)}_files.zip"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Batch Excel→PDF] ✗ Fatal error: {str(e)}")
        for output_path in output_files:
            try:
                await doc_service.cleanup_file(output_path)
            except:
                pass
        raise HTTPException(500, f"Batch conversion failed: {str(e)}")


@router.post("/batch/image-to-pdf")
async def batch_convert_image_to_pdf(
    files: List[UploadFile] = File(..., description="Multiple image files"),
):
    """
    **Batch Convert** nhiều ảnh sang PDF cùng lúc
    
    - Upload nhiều file ảnh (JPG, PNG, etc.)
    - Mỗi ảnh thành 1 file PDF riêng
    - Download kết quả dưới dạng ZIP
    """
    if not files or len(files) == 0:
        raise HTTPException(400, "No files uploaded")
    
    output_files = []
    errors = []
    
    try:
        for idx, file in enumerate(files, 1):
            try:
                print(f"[Batch Image→PDF] Processing file {idx}/{len(files)}: {file.filename}")
                input_path = await doc_service.save_upload_file(file)
                output_path = await doc_service.image_to_pdf(input_path)
                output_files.append(output_path)
                await doc_service.cleanup_file(input_path)
                print(f"[Batch Image→PDF] ✓ Success: {file.filename} → {output_path.name}")
            except Exception as e:
                error_msg = str(e)
                print(f"[Batch Image→PDF] ✗ Error: {file.filename} - {error_msg}")
                errors.append({"file": file.filename, "error": error_msg})
                try:
                    if 'input_path' in locals():
                        await doc_service.cleanup_file(input_path)
                except:
                    pass
        
        if not output_files:
            raise HTTPException(500, f"All conversions failed. Errors: {errors}")
        
        print(f"[Batch Image→PDF] Creating ZIP with {len(output_files)} files...")
        
        # Create ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for output_path in output_files:
                zip_file.write(output_path, output_path.name)
                await doc_service.cleanup_file(output_path)
        
        zip_buffer.seek(0)
        
        print(f"[Batch Image→PDF] ✓ ZIP created! Size: {len(zip_buffer.getvalue())} bytes")
        
        if errors:
            print(f"[Batch Image→PDF] ⚠ Completed with {len(errors)} errors: {errors}")
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=images_to_pdf_{len(output_files)}_files.zip"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Batch Image→PDF] ✗ Fatal error: {str(e)}")
        for output_path in output_files:
            try:
                await doc_service.cleanup_file(output_path)
            except:
                pass
        raise HTTPException(500, f"Batch conversion failed: {str(e)}")


@router.post("/batch/compress-pdf")
async def batch_compress_pdf(
    files: List[UploadFile] = File(..., description="Multiple PDF files"),
    quality: str = Form("medium", description="Compression quality: low, medium, high"),
):
    """
    **Batch Compress** nhiều file PDF cùng lúc
    
    - Upload nhiều file PDF
    - Nén tất cả với cùng mức chất lượng
    - Download kết quả dưới dạng ZIP
    """
    if not files or len(files) == 0:
        raise HTTPException(400, "No files uploaded")
    
    output_files = []
    errors = []
    
    try:
        for idx, file in enumerate(files, 1):
            try:
                print(f"[Batch Compress PDF] Processing file {idx}/{len(files)}: {file.filename}")
                input_path = await doc_service.save_upload_file(file)
                output_path, technology = await doc_service.compress_pdf(input_path, quality)
                output_files.append(output_path)
                await doc_service.cleanup_file(input_path)
                print(f"[Batch Compress PDF] ✓ Success: {file.filename} → {output_path.name} ({technology})")
            except Exception as e:
                error_msg = str(e)
                print(f"[Batch Compress PDF] ✗ Error: {file.filename} - {error_msg}")
                errors.append({"file": file.filename, "error": error_msg})
                try:
                    if 'input_path' in locals():
                        await doc_service.cleanup_file(input_path)
                except:
                    pass
        
        if not output_files:
            raise HTTPException(500, f"All compressions failed. Errors: {errors}")
        
        print(f"[Batch Compress PDF] Creating ZIP with {len(output_files)} files...")
        
        # Create ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for output_path in output_files:
                zip_file.write(output_path, output_path.name)
                await doc_service.cleanup_file(output_path)
        
        zip_buffer.seek(0)
        
        print(f"[Batch Compress PDF] ✓ ZIP created! Size: {len(zip_buffer.getvalue())} bytes")
        
        if errors:
            print(f"[Batch Compress PDF] ⚠ Completed with {len(errors)} errors: {errors}")
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=compressed_pdfs_{len(output_files)}_files.zip"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Batch Compress PDF] ✗ Fatal error: {str(e)}")
        for output_path in output_files:
            try:
                await doc_service.cleanup_file(output_path)
            except:
                pass
        raise HTTPException(500, f"Batch compression failed: {str(e)}")


@router.post("/batch/pdf-to-multiple")
async def batch_convert_pdf_to_multiple(
    files: List[UploadFile] = File(...),
    format: str = Query(..., description="Target format: word, excel, or image")
):
    """
    Bulk Convert: Chuyển đổi nhiều PDF sang định dạng mong muốn (Word/Excel/Image)
    
    - **files**: Danh sách PDF files cần convert
    - **format**: Định dạng đích - "word", "excel", hoặc "image"
    - Returns: ZIP file chứa tất cả files đã convert
    
    Examples:
    - Convert 5 PDFs → 5 Word files
    - Convert 3 PDFs → 3 Excel files  
    - Convert 10 PDFs → 10 Image folders (mỗi PDF thành nhiều ảnh)
    """
    output_files = []
    errors = []
    
    try:
        # Validate format
        valid_formats = ["word", "excel", "image"]
        if format.lower() not in valid_formats:
            raise HTTPException(400, f"Invalid format. Must be one of: {valid_formats}")
        
        format = format.lower()
        format_display = {"word": "Word", "excel": "Excel", "image": "Images"}[format]
        
        print(f"[Bulk PDF→{format_display}] Starting conversion of {len(files)} PDF(s)")
        
        for idx, file in enumerate(files, 1):
            try:
                # Validate PDF file
                if not file.filename.lower().endswith('.pdf'):
                    errors.append({"file": file.filename, "error": "Not a PDF file"})
                    continue
                
                print(f"[Bulk PDF→{format_display}] Processing file {idx}/{len(files)}: {file.filename}")
                
                input_path = await doc_service.save_upload_file(file)
                
                # Convert based on format
                if format == "word":
                    output_path = await doc_service.pdf_to_word(input_path)
                    output_files.append(output_path)
                    print(f"[Bulk PDF→Word] ✓ Success: {file.filename} → {output_path.name}")
                    
                elif format == "excel":
                    output_path = await doc_service.pdf_to_excel(input_path)
                    output_files.append(output_path)
                    print(f"[Bulk PDF→Excel] ✓ Success: {file.filename} → {output_path.name}")
                    
                elif format == "image":
                    # PDF to images returns list of image paths
                    image_paths = await doc_service.pdf_to_images(input_path)
                    output_files.extend(image_paths)
                    print(f"[Bulk PDF→Images] ✓ Success: {file.filename} → {len(image_paths)} image(s)")
                
                await doc_service.cleanup_file(input_path)
                
            except Exception as e:
                error_msg = str(e)
                print(f"[Bulk PDF→{format_display}] ✗ Error: {file.filename} - {error_msg}")
                errors.append({"file": file.filename, "error": error_msg})
                try:
                    if 'input_path' in locals():
                        await doc_service.cleanup_file(input_path)
                except:
                    pass
        
        if not output_files:
            raise HTTPException(500, f"All conversions failed. Errors: {errors}")
        
        print(f"[Bulk PDF→{format_display}] Creating ZIP with {len(output_files)} file(s)...")
        
        # Create ZIP with all converted files
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for output_path in output_files:
                # For images, preserve folder structure
                if format == "image":
                    # Get relative path (e.g., "filename/page_1.png")
                    relative_path = output_path.relative_to(output_path.parent.parent)
                    zip_file.write(output_path, str(relative_path))
                else:
                    zip_file.write(output_path, output_path.name)
                
                await doc_service.cleanup_file(output_path)
        
        zip_buffer.seek(0)
        
        print(f"[Bulk PDF→{format_display}] ✓ ZIP created! Size: {len(zip_buffer.getvalue())} bytes")
        
        if errors:
            print(f"[Bulk PDF→{format_display}] ⚠ Completed with {len(errors)} errors: {errors}")
        
        # Determine filename based on format
        format_names = {
            "word": "docx",
            "excel": "xlsx", 
            "image": "images"
        }
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=bulk_pdf_to_{format_names[format]}_{len(files)}_files.zip"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Bulk PDF→{format_display}] ✗ Fatal error: {str(e)}")
        for output_path in output_files:
            try:
                await doc_service.cleanup_file(output_path)
            except:
                pass
        raise HTTPException(500, f"Bulk PDF conversion failed: {str(e)}")
    except Exception as e:
        for output_path in output_files:
            await doc_service.cleanup_file(output_path)
        raise HTTPException(500, f"Bulk PDF conversion failed: {str(e)}")


# ==================== NEW ADOBE PDF SERVICES FEATURES ====================

@router.post("/pdf/watermark")
async def watermark_pdf(
    pdf_file: UploadFile = File(..., description="File PDF gốc"),
    watermark_file: UploadFile = File(..., description="File PDF dấu mờ"),
):
    """
    Đóng dấu mờ lên PDF bằng Adobe PDF Services
    
    - Upload file PDF gốc + file PDF dấu mờ
    - Adobe sẽ overlay dấu mờ lên tất cả các trang
    - Dấu mờ có thể là text hoặc image (đã convert sang PDF)
    - Chất lượng: 10/10 (Adobe grade)
    """
    pdf_path = await doc_service.save_upload_file(pdf_file)
    watermark_path = await doc_service.save_upload_file(watermark_file)
    
    try:
        output_path = await doc_service.watermark_pdf(pdf_path, watermark_path)
        
        response = FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=f"watermarked_{pdf_file.filename}",
            background=None
        )
        
        response.headers["X-Technology-Engine"] = "adobe"
        response.headers["X-Technology-Name"] = "Adobe Watermark"
        response.headers["X-Technology-Quality"] = "10/10"
        response.headers["X-Technology-Type"] = "cloud"
        
        return response
        
    except Exception as e:
        await doc_service.cleanup_file(pdf_path)
        await doc_service.cleanup_file(watermark_path)
        raise e


@router.post("/pdf/combine")
async def combine_pdfs(
    files: List[UploadFile] = File(..., description="Các file PDF cần gộp"),
    page_ranges: Optional[str] = Form(None, description="Page ranges (comma separated): all,1-3,all")
):
    """
    Gộp nhiều PDF thành một file bằng Adobe PDF Services
    
    - Upload nhiều file PDF
    - Tùy chọn chọn trang cụ thể từ mỗi file
    - Format page_ranges: "all,1-3,5-10" (cách nhau bởi dấu phẩy)
    - Chất lượng: 10/10 (Adobe grade, tốt hơn pypdf)
    """
    pdf_paths = []
    
    try:
        # Save all files
        for file in files:
            path = await doc_service.save_upload_file(file)
            pdf_paths.append(path)
        
        # Parse page ranges
        ranges = None
        if page_ranges:
            ranges = [r.strip() for r in page_ranges.split(',')]
        
        # Combine
        output_path = await doc_service.combine_pdfs(pdf_paths, ranges)
        
        response = FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename="combined.pdf",
            background=None
        )
        
        response.headers["X-Technology-Engine"] = "adobe"
        response.headers["X-Technology-Name"] = "Adobe Combine"
        response.headers["X-Technology-Quality"] = "10/10"
        response.headers["X-Technology-Type"] = "cloud"
        
        return response
        
    except Exception as e:
        for path in pdf_paths:
            await doc_service.cleanup_file(path)
        raise e


@router.post("/pdf/split")
async def split_pdf(
    file: UploadFile = File(..., description="File PDF cần tách"),
    page_ranges: str = Form(..., description="Page ranges (comma separated): 1-3,4-6,7-10")
):
    """
    Tách PDF thành nhiều file bằng Adobe PDF Services
    
    - Upload file PDF
    - Chỉ định các khoảng trang cần tách
    - Format: "1-3,4-6,7-10" (mỗi khoảng sẽ tạo 1 file riêng)
    - Output: ZIP chứa tất cả các file PDF đã tách
    """
    pdf_path = await doc_service.save_upload_file(file)
    output_paths = []
    
    try:
        # Parse page ranges
        ranges = [r.strip() for r in page_ranges.split(',')]
        
        # Split
        output_paths = await doc_service.split_pdf(pdf_path, ranges)
        logger.info(f"🔍 Split returned {len(output_paths)} file paths")
        
        # Log each file size BEFORE adding to ZIP
        for idx, output_path in enumerate(output_paths):
            file_size = output_path.stat().st_size
            logger.info(f"📦 File {idx+1} before ZIP: {output_path.name} = {file_size} bytes")
        
        # Create ZIP - DON'T cleanup files until ZIP is fully created!
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for idx, output_path in enumerate(output_paths):
                # Verify file exists
                if not output_path.exists():
                    logger.error(f"❌ ERROR: File {output_path} does NOT exist before adding to ZIP!")
                    continue
                
                file_size = output_path.stat().st_size
                logger.info(f"📥 Adding to ZIP: {output_path.name} ({file_size} bytes)")
                
                # Add file to ZIP with FORWARD SLASH (/) for cross-platform compatibility
                # Use only filename (not full path) to avoid path issues
                arcname = output_path.name  # Just filename, no path separators
                zip_file.write(output_path, arcname=arcname)
                logger.info(f"✅ Added to ZIP: {arcname}")
        
        # Get the bytes BEFORE closing buffer
        zip_bytes = zip_buffer.getvalue()
        zip_size = len(zip_bytes)
        logger.info(f"📦 ZIP created: Total size = {zip_size} bytes")
        zip_buffer.close()
        
        if zip_size == 0:
            logger.error(f"❌ CRITICAL ERROR: ZIP file is EMPTY (0 bytes)!")
        
        # NOW we can cleanup all files (after ZIP is complete)
        await doc_service.cleanup_file(pdf_path)
        for output_path in output_paths:
            await doc_service.cleanup_file(output_path)
        
        logger.info(f"🚀 Returning ZIP response: {zip_size} bytes, filename=split_{file.filename}.zip")
        
        # Encode filename for non-ASCII characters (RFC 2231)
        encoded_filename = encode_filename(f"split_{file.filename}.zip")
        
        # Return as bytes response
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "X-Technology-Engine": "adobe",
                "X-Technology-Name": "Adobe Split",
                "X-Technology-Quality": "10/10",
                "Content-Length": str(zip_size)
            }
        )
        
    except Exception as e:
        await doc_service.cleanup_file(pdf_path)
        for path in output_paths:
            await doc_service.cleanup_file(path)
        raise e


@router.post("/pdf/protect")
async def protect_pdf(
    file: UploadFile = File(..., description="File PDF cần bảo vệ"),
    user_password: str = Form(..., description="Mật khẩu để mở file"),
    owner_password: Optional[str] = Form(None, description="Mật khẩu chủ sở hữu (optional)"),
    permissions: Optional[str] = Form(None, description="Quyền hạn: print,copy,edit (comma separated)")
):
    """
    Bảo vệ PDF bằng mật khẩu và phân quyền - Adobe PDF Services
    
    - Đặt mật khẩu để mở file (user_password)
    - Tùy chọn: Mật khẩu chủ sở hữu để thay đổi permissions
    - Quyền hạn: print, copy, edit, fill_forms, etc.
    - Mã hóa AES-256 (chuẩn enterprise)
    """
    pdf_path = await doc_service.save_upload_file(file)
    
    try:
        # Parse permissions
        perm_list = None
        if permissions:
            perm_list = [p.strip() for p in permissions.split(',')]
        
        # Protect
        output_path = await doc_service.protect_pdf(
            pdf_path, 
            user_password,
            owner_password,
            perm_list
        )
        
        response = FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=f"protected_{file.filename}",
            background=None
        )
        
        response.headers["X-Technology-Engine"] = "adobe"
        response.headers["X-Technology-Name"] = "Adobe Protect"
        response.headers["X-Technology-Quality"] = "10/10"
        response.headers["X-Technology-Type"] = "cloud"
        response.headers["X-Encryption"] = "AES-256"
        
        return response
        
    except Exception as e:
        await doc_service.cleanup_file(pdf_path)
        raise e


@router.post("/pdf/linearize")
async def linearize_pdf(
    file: UploadFile = File(..., description="File PDF cần tối ưu"),
):
    """
    Tối ưu hóa PDF cho web (Fast Web Viewing) - Adobe PDF Services
    
    - Tối ưu cấu trúc PDF để xem nhanh trên web
    - Page-by-page loading (không cần đợi tải hết file)
    - Giảm thời gian First Byte
    - Lý tưởng cho: Website, catalog online, tài liệu lớn
    """
    pdf_path = await doc_service.save_upload_file(file)
    
    try:
        original_size = pdf_path.stat().st_size
        
        output_path = await doc_service.linearize_pdf(pdf_path)
        optimized_size = output_path.stat().st_size
        
        response = FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=f"web_optimized_{file.filename}",
            background=None
        )
        
        response.headers["X-Technology-Engine"] = "adobe"
        response.headers["X-Technology-Name"] = "Adobe Linearize"
        response.headers["X-Technology-Quality"] = "10/10"
        response.headers["X-Technology-Type"] = "cloud"
        response.headers["X-Original-Size"] = str(original_size)
        response.headers["X-Optimized-Size"] = str(optimized_size)
        
        return response
        
    except Exception as e:
        await doc_service.cleanup_file(pdf_path)
        raise e


@router.post("/pdf/autotag")
async def autotag_pdf(
    file: UploadFile = File(..., description="File PDF cần gắn thẻ"),
    generate_report: bool = Form(True, description="Tạo báo cáo accessibility")
):
    """
    Tự động gắn thẻ PDF cho Accessibility - Adobe PDF Services
    
    - AI tự động phát hiện cấu trúc tài liệu
    - Thêm thẻ cho headings, paragraphs, tables, lists
    - Tạo PDF có thể đọc bằng screen reader
    - Tuân thủ WCAG, Section 508
    - Tùy chọn: Tạo báo cáo accessibility (Excel)
    """
    pdf_path = await doc_service.save_upload_file(file)
    
    try:
        output_path, report_path = await doc_service.autotag_pdf(pdf_path, generate_report)
        
        # If report exists, return ZIP with both files
        if report_path:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.write(output_path, f"tagged_{file.filename}")
                zip_file.write(report_path, report_path.name)
                
                await doc_service.cleanup_file(output_path)
                await doc_service.cleanup_file(report_path)
            
            zip_buffer.seek(0)
            await doc_service.cleanup_file(pdf_path)
            
            # Encode filename for non-ASCII characters
            encoded_filename = encode_filename(f"tagged_{file.filename}.zip")
            
            return StreamingResponse(
                zip_buffer,
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                    "X-Technology-Engine": "adobe",
                    "X-Technology-Name": "Adobe Auto-Tag",
                    "X-Technology-Quality": "10/10",
                    "X-Accessibility": "WCAG-compliant"
                }
            )
        else:
            # Just return tagged PDF
            response = FileResponse(
                path=output_path,
                media_type="application/pdf",
                filename=f"tagged_{file.filename}",
                background=None
            )
            
            response.headers["X-Technology-Engine"] = "adobe"
            response.headers["X-Technology-Name"] = "Adobe Auto-Tag"
            response.headers["X-Technology-Quality"] = "10/10"
            response.headers["X-Accessibility"] = "WCAG-compliant"
            
            return response
        
    except Exception as e:
        await doc_service.cleanup_file(pdf_path)
        raise e


@router.post("/pdf/generate", summary="Generate document from template (Adobe)")
async def generate_document(
    template_file: UploadFile = File(..., description="Word template (.docx)"),
    json_data: str = Form(..., description="JSON data as string"),
    output_format: str = Form("pdf", description="Output format: pdf or docx"),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Generate PDF/DOCX from Word template + JSON data (Adobe Document Generation).
    
    **Template Format:**
    - Use {{variable}} for simple variables
    - Use {{#array}}...{{/array}} for loops
    - Use {{#condition}}...{{/condition}} for conditionals
    
    **Example JSON:**
    ```json
    {
        "name": "John Doe",
        "company": "ACME Corp",
        "items": [
            {"product": "Widget", "price": 100},
            {"product": "Gadget", "price": 200}
        ]
    }
    ```
    
    **Returns:** Generated PDF or DOCX file
    
    **Adobe API:** Document Generation API (500 free/month)
    """
    import json
    
    # Validate file extension
    if not template_file.filename.endswith('.docx'):
        raise HTTPException(400, "Template must be .docx file")
    
    # Validate output format
    if output_format.lower() not in ['pdf', 'docx']:
        raise HTTPException(400, "Output format must be 'pdf' or 'docx'")
    
    # Parse JSON data
    try:
        data_dict = json.loads(json_data)
    except json.JSONDecodeError as e:
        raise HTTPException(400, f"Invalid JSON data: {str(e)}")
    
    # Save template file
    template_path = doc_service.upload_dir / f"template_{template_file.filename}"
    
    try:
        async with aiofiles.open(template_path, 'wb') as f:
            content = await template_file.read()
            await f.write(content)
        
        # Generate document
        output_path = await doc_service.generate_document(
            template_path=template_path,
            json_data=data_dict,
            output_format=output_format
        )
        
        # Determine media type
        media_type = "application/pdf" if output_format.lower() == "pdf" else \
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        # Return file
        response = FileResponse(
            path=output_path,
            media_type=media_type,
            filename=f"generated_{template_file.filename.replace('.docx', f'.{output_format.lower()}')}",
            background=None
        )
        
        response.headers["X-Technology-Engine"] = "adobe"
        response.headers["X-Technology-Name"] = "Adobe Document Generation"
        response.headers["X-Technology-Quality"] = "10/10"
        response.headers["X-Template-Processing"] = "Mustache-based"
        
        
        # Cleanup template file
        await doc_service.cleanup_file(template_path)
        
        return response
        
    except Exception as e:
        await doc_service.cleanup_file(template_path)
        raise e


@router.post("/pdf/generate-batch", summary="Generate multiple documents from template (Adobe)")
async def generate_documents_batch(
    template_file: UploadFile = File(..., description="Word template (.docx)"),
    json_data: str = Form(..., description="JSON array with multiple data objects"),
    output_format: str = Form("pdf", description="Output format: pdf or docx"),
    merge_output: bool = Form(False, description="True: merge into 1 PDF, False: return ZIP with multiple files"),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Generate multiple documents from one template + array of JSON data.
    
    **Input:**
    - `template_file`: Word template (.docx)
    - `json_data`: JSON array with multiple objects
    - `output_format`: "pdf" or "docx"
    - `merge_output`: 
      - `true` = Merge all into 1 PDF file
      - `false` = Return ZIP containing separate files
    
    **Example JSON Array:**
    ```json
    [
        {"name": "John Doe", "company": "ACME"},
        {"name": "Jane Smith", "company": "TechCorp"},
        {"name": "Bob Wilson", "company": "StartupXYZ"}
    ]
    ```
    
    **Output:**
    - If `merge_output=true`: Single merged PDF
    - If `merge_output=false`: ZIP file with multiple PDFs/DOCX
    
    **Use Cases:**
    - Batch invitations (thiệp mời hàng loạt)
    - Multiple contracts (nhiều hợp đồng)
    - Personalized certificates (giấy chứng nhận cá nhân hóa)
    
    **Adobe API:** Document Generation + CombinePDF (if merge)
    """
    import json
    import io
    import zipfile
    from pathlib import Path
    
    # Validate file extension
    if not template_file.filename.endswith('.docx'):
        raise HTTPException(400, "Template must be .docx file")
    
    # Validate output format
    if output_format.lower() not in ['pdf', 'docx']:
        raise HTTPException(400, "Output format must be 'pdf' or 'docx'")
    
    # Parse JSON data - expect array
    try:
        data_array = json.loads(json_data)
        if not isinstance(data_array, list):
            raise ValueError("JSON must be an array of objects")
        if len(data_array) == 0:
            raise ValueError("JSON array cannot be empty")
        if len(data_array) > 100:
            raise ValueError("Maximum 100 items per batch")
    except json.JSONDecodeError as e:
        raise HTTPException(400, f"Invalid JSON data: {str(e)}")
    except ValueError as e:
        raise HTTPException(400, str(e))
    
    # Save template file
    template_path = doc_service.upload_dir / f"template_{template_file.filename}"
    generated_files = []
    
    try:
        async with aiofiles.open(template_path, 'wb') as f:
            content = await template_file.read()
            await f.write(content)
        
        logger.info(f"🔄 Batch generation: {len(data_array)} items, merge={merge_output}")
        
        # Generate document for each data item
        for idx, data_dict in enumerate(data_array, 1):
            logger.info(f"📄 Generating document {idx}/{len(data_array)}")
            
            output_path = await doc_service.generate_document(
                template_path=template_path,
                json_data=data_dict,
                output_format=output_format
            )
            
            generated_files.append(output_path)
            logger.info(f"✅ Generated: {output_path.name} ({output_path.stat().st_size} bytes)")
        
        logger.info(f"✅ All {len(generated_files)} documents generated")
        
        # OPTION 1: Merge into single PDF
        if merge_output and output_format.lower() == "pdf":
            logger.info("🔗 Merging all PDFs into one...")
            
            # Use CombinePDF to merge
            merged_path = await doc_service.combine_pdfs(
                pdf_paths=generated_files,
                page_ranges=None  # All pages from all files
            )
            
            logger.info(f"✅ Merged PDF: {merged_path.name} ({merged_path.stat().st_size} bytes)")
            
            # Cleanup individual files
            for file_path in generated_files:
                await doc_service.cleanup_file(file_path)
            
            # Return merged PDF
            response = FileResponse(
                path=merged_path,
                media_type="application/pdf",
                filename=f"batch_{len(data_array)}_merged.pdf",
                background=None
            )
            
            response.headers["X-Technology-Engine"] = "adobe"
            response.headers["X-Technology-Name"] = "Adobe Document Generation + CombinePDF"
            response.headers["X-Batch-Count"] = str(len(data_array))
            response.headers["X-Output-Type"] = "merged"
            
            # Cleanup template and merged file after response
            await doc_service.cleanup_file(template_path)
            
            return response
        
        # OPTION 2: Return ZIP with separate files
        else:
            logger.info(f"📦 Creating ZIP with {len(generated_files)} files...")
            
            # Create ZIP in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for idx, file_path in enumerate(generated_files, 1):
                    # Generate filename based on index or data
                    arcname = f"document_{idx:03d}.{output_format.lower()}"
                    
                    # Try to get a better name from first field in data
                    try:
                        first_value = str(list(data_array[idx-1].values())[0])
                        # Sanitize filename
                        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in first_value)
                        safe_name = safe_name[:50]  # Limit length
                        arcname = f"{safe_name}_{idx:03d}.{output_format.lower()}"
                    except:
                        pass
                    
                    logger.info(f"📥 Adding to ZIP: {arcname} ({file_path.stat().st_size} bytes)")
                    zip_file.write(file_path, arcname=arcname)
            
            # Get ZIP bytes
            zip_bytes = zip_buffer.getvalue()
            zip_size = len(zip_bytes)
            zip_buffer.close()
            
            logger.info(f"📦 ZIP created: {zip_size} bytes with {len(generated_files)} files")
            
            # Cleanup all generated files
            for file_path in generated_files:
                await doc_service.cleanup_file(file_path)
            await doc_service.cleanup_file(template_path)
            
            # Return ZIP
            return Response(
                content=zip_bytes,
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename=batch_{len(data_array)}_files.zip",
                    "X-Technology-Engine": "adobe",
                    "X-Technology-Name": "Adobe Document Generation",
                    "X-Batch-Count": str(len(data_array)),
                    "X-Output-Type": "zip",
                    "Content-Length": str(zip_size)
                }
            )
        
    except Exception as e:
        # Cleanup on error
        await doc_service.cleanup_file(template_path)
        for file_path in generated_files:
            await doc_service.cleanup_file(file_path)
        
        logger.error(f"❌ Batch generation error: {e}")
        raise HTTPException(500, f"Batch generation failed: {str(e)}")


@router.post("/pdf/seal", summary="Apply electronic seal to PDF (Adobe)")
async def electronic_seal_pdf(
    pdf_file: UploadFile = File(..., description="PDF file to seal"),
    seal_image: Optional[UploadFile] = File(None, description="Seal image (PNG/JPG, optional)"),
    provider_name: str = Form(..., description="TSP provider name"),
    access_token: str = Form(..., description="TSP access token"),
    credential_id: str = Form(..., description="TSP credential ID"),
    pin: str = Form(..., description="TSP PIN"),
    seal_field_name: str = Form("Signature1", description="Signature field name"),
    page_number: int = Form(1, description="Page number (1-based)"),
    visible: bool = Form(True, description="Seal visibility"),
    field_x: int = Form(150, description="Field X position"),
    field_y: int = Form(250, description="Field Y position"),
    field_width: int = Form(350, description="Field width"),
    field_height: int = Form(200, description="Field height"),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Apply electronic seal (digital signature) to PDF using Adobe E-Seal API.
    
    **Requirements:**
    - PDF file to seal
    - TSP (Trust Service Provider) credentials
    - Optional: Seal image (company logo, etc.)
    
    **TSP Credentials:**
    You need to register with a TSP provider to get:
    - Provider name (e.g., "GlobalSign", "DigiCert")
    - Access token
    - Credential ID
    - PIN
    
    **Seal Position:**
    - field_x, field_y: Top-left corner position
    - field_width, field_height: Seal size
    
    **Returns:** Sealed PDF with digital signature
    
    **Adobe API:** E-Seal API (500 free/month)
    
    **Note:** This is enterprise-grade digital signature, not just visual stamp.
    """
    # Validate PDF
    if not pdf_file.filename.endswith('.pdf'):
        raise HTTPException(400, "File must be PDF")
    
    # Validate seal image if provided
    if seal_image:
        ext = seal_image.filename.lower().split('.')[-1]
        if ext not in ['png', 'jpg', 'jpeg']:
            raise HTTPException(400, "Seal image must be PNG or JPEG")
    
    # Save PDF
    pdf_path = doc_service.upload_dir / f"seal_input_{pdf_file.filename}"
    
    # Save seal image if provided
    seal_image_path = None
    if seal_image:
        seal_image_path = doc_service.upload_dir / f"seal_image_{seal_image.filename}"
    
    try:
        # Save PDF
        async with aiofiles.open(pdf_path, 'wb') as f:
            content = await pdf_file.read()
            await f.write(content)
        
        # Save seal image
        if seal_image and seal_image_path:
            async with aiofiles.open(seal_image_path, 'wb') as f:
                img_content = await seal_image.read()
                await f.write(img_content)
        
        # Apply electronic seal
        output_path = await doc_service.electronic_seal_pdf(
            pdf_path=pdf_path,
            seal_image_path=seal_image_path,
            provider_name=provider_name,
            access_token=access_token,
            credential_id=credential_id,
            pin=pin,
            seal_field_name=seal_field_name,
            page_number=page_number,
            visible=visible,
            field_x=field_x,
            field_y=field_y,
            field_width=field_width,
            field_height=field_height
        )
        
        # Return sealed PDF
        response = FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=f"sealed_{pdf_file.filename}",
            background=None
        )
        
        response.headers["X-Technology-Engine"] = "adobe"
        response.headers["X-Technology-Name"] = "Adobe E-Seal"
        response.headers["X-Technology-Quality"] = "10/10"
        response.headers["X-Signature-Type"] = "Digital-Signature"
        response.headers["X-Compliance"] = "eIDAS-compliant"
        
        # Cleanup input files
        await doc_service.cleanup_file(pdf_path)
        if seal_image_path:
            await doc_service.cleanup_file(seal_image_path)
        
        return response
        
    except Exception as e:
        await doc_service.cleanup_file(pdf_path)
        if seal_image_path:
            await doc_service.cleanup_file(seal_image_path)
        raise e


# ==================== TEXT TO WORD (MHTML) ====================

@router.post("/text-to-word-smart")
async def text_to_word_smart(
    text: str = Form(..., description="Plain text input"),
    provider: str = Form("gemini", description="AI provider: 'gemini' or 'claude'"),
    model: Optional[str] = Form(None, description="Specific model name (optional)"),
    language: str = Form("vi", description="Language code: 'vi', 'en', etc."),
):
    """
    🎨 Convert plain text to beautifully formatted Word document using AI
    
    **Technology:** DOCX format (python-docx) - 100% Microsoft Word compatible
    **AI Providers:** Gemini or Claude for intelligent text structuring
    
    **How it works:**
    1. AI analyzes your text and creates structured sections
    2. Automatically identifies headings, paragraphs, lists
    3. Highlights important names, terms, and info boxes
    4. Generates professional DOCX with perfect formatting
    
    **Features:**
    - ✅ Smart section detection (H1, H2, H3)
    - ✅ Auto-detect important information → info boxes
    - ✅ Auto-detect conclusions → highlight boxes
    - ✅ Proper Vietnamese formatting (thụt đầu dòng 1cm)
    - ✅ A4 page size with standard margins (2.5cm top/bottom, 2cm left/right)
    - ✅ Times New Roman 13pt (chuẩn công văn)
    - ✅ Beautiful colors and professional styling
    - ✅ Perfect Word compatibility (no more HTML encoding issues!)
    
    **Supported Providers:**
    - **Gemini** (Google): Fast, cost-effective, great for Vietnamese
    - **Claude** (Anthropic): High quality, best reasoning
    
    **Output:** `.docx` file (OpenXML format) - 100% compatible with:
    - Microsoft Word 2007+
    - Google Docs
    - LibreOffice Writer
    - WPS Office
    - Apple Pages
    
    **Example Input:**
    ```
    Báo cáo dự án ABC
    
    Giới thiệu: Dự án ABC được khởi động...
    
    Mục tiêu chính:
    - Tăng hiệu quả 30%
    - Giảm chi phí 20%
    
    Kết luận: Dự án hoàn thành đúng tiến độ.
    ```
    
    **AI Auto-detects:**
    - Title: "Báo cáo dự án ABC"
    - Sections: "Giới thiệu", "Mục tiêu chính", "Kết luận"
    - Lists: Bullet points
    - Highlight boxes: Conclusion section
    """
    try:
        # Log incoming request
        logger.info(f"🎨 Text-to-Word request: provider={provider}, model={model}, language={language}, text_length={len(text) if text else 0}")
        
        # Validate inputs
        if not text or len(text.strip()) < 10:
            raise HTTPException(400, "Text must be at least 10 characters")
        
        if provider not in ["gemini", "claude"]:
            raise HTTPException(400, "Provider must be 'gemini' or 'claude'")
        
        if language not in ["vi", "en", "zh", "ja", "ko", "fr", "de", "es"]:
            raise HTTPException(400, "Unsupported language code")
        
        # Generate DOCX (using python-docx, not MHTML)
        docx_bytes, ai_usage = await doc_service.text_to_word_mhtml(
            text=text,
            provider=provider,
            model=model,
            language=language
        )
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"document_{timestamp}.docx"
        
        # Return as downloadable file
        response = Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="{encode_filename(filename)}"'
            }
        )
        
        # Add metadata headers
        response.headers["X-Technology-Engine"] = provider
        response.headers["X-Technology-Name"] = f"{provider.title()} AI"
        response.headers["X-Technology-Model"] = ai_usage.get("model", "unknown")
        response.headers["X-Technology-Quality"] = "10/10"  # DOCX quality (perfect compatibility)
        response.headers["X-Technology-Type"] = "ai-docx"
        response.headers["X-Input-Tokens"] = str(ai_usage.get("input_tokens", 0))
        response.headers["X-Output-Tokens"] = str(ai_usage.get("output_tokens", 0))
        response.headers["X-Processing-Time-Ms"] = str(int(ai_usage.get("processing_time_ms", 0)))
        
        return response
        
    except HTTPException as he:
        logger.error(f"❌ HTTPException in text-to-word: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ Text to Word error: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"Failed to generate Word document: {str(e)}")


@router.get("/ai-providers")
async def get_ai_providers():
    """
    Get available AI providers for text-to-word conversion
    
    Returns list of providers with their models and pricing
    """
    from app.services.document_service import GEMINI_MODELS
    
    return {
        "providers": [
            {
                "id": "gemini",
                "name": "Google Gemini",
                "description": "Fast, cost-effective, great for Vietnamese",
                "status": "available",
                "models": [
                    {
                        "id": model_id,
                        **model_info
                    }
                    for model_id, model_info in GEMINI_MODELS.items()
                    if model_info.get("series") in ["3.0", "2.5"]  # Only 3.0 and 2.5+
                ],
                "recommended": True
            },
            {
                "id": "claude",
                "name": "Anthropic Claude",
                "description": "High quality reasoning and formatting",
                "status": "available",
                "models": [
                    {
                        "id": "claude-sonnet-4-20250514",
                        "name": "Claude Sonnet 4.0 (Latest)",
                        "quality": 10,
                        "speed": 8,
                        "pricing": {"input": 3.00, "output": 15.00}
                    },
                    {
                        "id": "claude-3-7-sonnet-20250219",
                        "name": "Claude 3.7 Sonnet",
                        "quality": 9.8,
                        "speed": 8,
                        "pricing": {"input": 3.00, "output": 15.00}
                    }
                ],
                "recommended": False
            }
        ]
    }



