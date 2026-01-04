"""
Modern Document Conversion API Endpoints (2025)
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, Depends, Header
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
from sqlalchemy.orm import Session
from app.core.database import get_db

from app.services.document_service import DocumentService
from app.services.quota_service import QuotaService
from app.api.dependencies import get_current_user, get_current_user_optional
from app.models.auth_models import User
from pathlib import Path

router = APIRouter(tags=["Document Conversion"])

# Initialize global service
upload_dir = Path("./uploads/documents")
doc_service = DocumentService(upload_dir=str(upload_dir))

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # CRITICAL: Enable INFO logs

# Add console handler if not exists
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s:     %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


@router.get("/test-auth")
async def test_auth_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Test endpoint to verify optional auth works"""
    # Manually get user from header
    user = None
    if authorization:
        try:
            from app.api.dependencies import get_current_user_optional
            # Simpler: just decode token manually
            from app.core.security import decode_access_token
            if authorization.startswith("Bearer "):
                token = authorization.replace("Bearer ", "")
                payload = decode_access_token(token)
                user_id = payload.get("user_id")
                if user_id:
                    from app.models.auth_models import User
                    user = db.query(User).filter(User.id == user_id).first()
        except:
            pass  # Ignore errors - demo mode
    
    if user:
        return {"status": "authenticated", "user_id": user.id, "username": user.username}
    else:
        return {"status": "demo_mode", "message": "No authentication provided"}


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
    logger.info(f"📥 Received Word file: {file.filename} (content_type: {file.content_type})")
    
    # Save uploaded file
    input_path = await doc_service.save_upload_file(file)
    logger.info(f"💾 Saved to: {input_path} (size: {input_path.stat().st_size} bytes)")
    
    try:
        # Convert
        output_path = await doc_service.word_to_pdf(input_path)
        
        # Verify output is PDF
        logger.info(f"✅ Conversion completed: {output_path} (size: {output_path.stat().st_size} bytes)")
        
        if not output_path.suffix.lower() == '.pdf':
            logger.error(f"❌ Output file is not PDF: {output_path.suffix}")
            raise HTTPException(500, f"Output file has wrong extension: {output_path.suffix}")
        
        # Read first bytes to verify PDF magic number
        with open(output_path, 'rb') as f:
            magic = f.read(4)
            logger.info(f"🔍 File magic bytes: {magic}")
            if not magic.startswith(b'%PDF'):
                logger.error(f"❌ File is not a valid PDF (magic: {magic})")
                raise HTTPException(500, "Generated file is not a valid PDF")
        
        # Return file with technology metadata in headers
        response = FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=output_path.name,
            background=None  # Don't delete file yet
        )
        
        # Add technology metadata to response headers (no emojis - HTTP headers only support Latin-1)
        response.headers["X-Technology-Engine"] = "libreoffice"
        response.headers["X-Technology-Name"] = "LibreOffice"
        response.headers["X-Technology-Quality"] = "8/10"
        response.headers["X-Technology-Type"] = "local"
        
        logger.info(f"📤 Sending PDF response: {output_path.name}")
        return response
        
    except Exception as e:
        # Log full traceback for debugging
        import traceback
        logger.error(f"❌ Word→PDF conversion error: {str(e)}")
        logger.error(traceback.format_exc())
        
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
    db: Session = Depends(get_db)
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
    import logging
    logger = logging.getLogger(__name__)
    
    # Save uploaded file
    logger.info("")
    logger.info("="*80)
    logger.info("🌐 API ENDPOINT: /api/v1/documents/convert/pdf-to-word")
    logger.info(f"   File: {file.filename}")
    logger.info(f"   Content-Type: {file.content_type}")
    logger.info(f"   Size: {file.size if hasattr(file, 'size') else 'unknown'}")
    logger.info(f"   Parameters:")
    logger.info(f"      use_gemini={use_gemini}")
    logger.info(f"      enable_ocr={enable_ocr}")
    logger.info(f"      auto_detect_scanned={auto_detect_scanned}")
    logger.info(f"      ocr_language={ocr_language}")
    logger.info(f"      gemini_model={gemini_model}")
    logger.info("="*80)
    logger.info("")
    
    input_path = await doc_service.save_upload_file(file)
    
    try:
        # Track which technology was used
        used_adobe = False
        used_gemini = False
        used_ocr = False
        
        logger.info("📞 Calling doc_service.pdf_to_word()...")
        
        # Convert (priority: Gemini > Adobe > pdf2docx)
        output_path = await doc_service.pdf_to_word(
            input_path,
            start_page=start_page,
            end_page=end_page,
            enable_ocr=enable_ocr,
            ocr_language=ocr_language,
            auto_detect_scanned=auto_detect_scanned,
            use_gemini=use_gemini,
            gemini_model=gemini_model,
            db=db
        )
        
        logger.info("")
        logger.info(f"📨 Returned from pdf_to_word(): {output_path}")
        logger.info(f"   Output file exists: {output_path.exists()}")
        logger.info(f"   Output size: {output_path.stat().st_size if output_path.exists() else 0} bytes")
        logger.info("")
        
        # Check which technology was actually used
        if use_gemini and doc_service.use_gemini:
            used_gemini = True
            # Get actual model name used
            actual_model = gemini_model or doc_service.gemini_model_name
            logger.info(f"✅ Technology used: GEMINI ({actual_model})")
        elif doc_service.use_adobe and doc_service.adobe_credentials:
            used_adobe = True
            # Check if OCR was enabled (either manually or auto-detected)
            from app.services.document_service import is_pdf_scanned
            if enable_ocr or (auto_detect_scanned and is_pdf_scanned(input_path)):
                used_ocr = True
            logger.info(f"✅ Technology used: ADOBE (OCR: {used_ocr})")
        else:
            logger.warning("⚠️  Technology used: UNKNOWN or pdf2docx")
        
        logger.info("")
        
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
        
        logger.info("="*80)
        logger.info("✅ API RESPONSE: 200 OK")
        logger.info(f"   Technology: {response.headers.get('X-Technology-Engine', 'unknown')}")
        logger.info(f"   File: {output_path.name}")
        logger.info(f"   Size: {output_path.stat().st_size} bytes")
        logger.info("="*80)
        logger.info("")
        
        return response
        
    except Exception as e:
        logger.error("")
        logger.error("="*80)
        logger.error("❌ API ERROR")
        logger.error(f"   Exception: {type(e).__name__}")
        logger.error(f"   Message: {str(e)}")
        logger.error("="*80)
        logger.error("")
        
        await doc_service.cleanup_file(input_path)
        raise e


@router.post("/convert/pdf-to-word-adobe-only")
async def convert_pdf_to_word_adobe_only(
    file: UploadFile = File(..., description="PDF file"),
    enable_ocr: bool = Form(False, description="Enable OCR for scanned PDFs"),
    ocr_language: str = Form("en-US", description="OCR language (en-US, fr-FR, de-DE, etc. - NO Vietnamese)")
):
    """
    🔵 Adobe PDF Services ONLY - Pure Adobe API Test
    
    - **Direct Adobe API call** - No Gemini, no pdf2docx, no fallback
    - **10/10 quality** - AI-powered layout preservation
    - **50+ languages OCR** - BUT NO Vietnamese support
    - **Purpose:** Debug and verify Adobe PDF Services is working
    
    ⚠️ NOTE: This endpoint will FAIL if Adobe is not configured properly
    ⚠️ Vietnamese OCR NOT supported - use en-US, fr-FR, de-DE, etc.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Check if Adobe is available
    if not doc_service.use_adobe or not doc_service.adobe_credentials:
        raise HTTPException(
            503,
            "Adobe PDF Services not configured. Please set USE_ADOBE_PDF_API=true and add credentials."
        )
    
    # Save uploaded file
    logger.info("")
    logger.info("="*80)
    logger.info("🔵 ADOBE-ONLY ENDPOINT: /api/v1/documents/convert/pdf-to-word-adobe-only")
    logger.info(f"   File: {file.filename}")
    logger.info(f"   Size: {file.size if hasattr(file, 'size') else 'unknown'}")
    logger.info(f"   Enable OCR: {enable_ocr}")
    logger.info(f"   OCR Language: {ocr_language}")
    logger.info("="*80)
    logger.info("")
    
    input_path = await doc_service.save_upload_file(file)
    
    try:
        output_filename = input_path.stem + ".docx"
        output_path = doc_service.output_dir / output_filename
        
        logger.info("📞 Calling _pdf_to_word_adobe() directly (no fallback)...")
        logger.info("")
        
        # Call Adobe directly - no fallback, no other tech
        result = await doc_service._pdf_to_word_adobe(
            input_path,
            output_path,
            enable_ocr=enable_ocr,
            ocr_language=ocr_language
        )
        
        logger.info("")
        logger.info(f"✅ Adobe returned: {result}")
        logger.info(f"   File exists: {result.exists()}")
        logger.info(f"   Size: {result.stat().st_size if result.exists() else 0} bytes")
        logger.info("")
        
        # Return file
        response = FileResponse(
            path=result,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=result.name
        )
        
        # Add metadata headers
        response.headers["X-Technology-Engine"] = "adobe-only"
        response.headers["X-Technology-Name"] = "Adobe PDF Services (Direct)"
        response.headers["X-Technology-Quality"] = "10/10"
        response.headers["X-Technology-Type"] = "cloud"
        response.headers["X-Technology-OCR"] = "true" if enable_ocr else "false"
        response.headers["X-Technology-OCR-Language"] = ocr_language if enable_ocr else "none"
        
        logger.info("="*80)
        logger.info("✅ ADOBE-ONLY RESPONSE: 200 OK")
        logger.info(f"   File: {result.name}")
        logger.info(f"   Size: {result.stat().st_size} bytes")
        logger.info("="*80)
        logger.info("")
        
        return response
        
    except Exception as e:
        logger.error("")
        logger.error("="*80)
        logger.error("❌ ADOBE-ONLY ERROR")
        logger.error(f"   Exception: {type(e).__name__}")
        logger.error(f"   Message: {str(e)}")
        logger.error("="*80)
        logger.error("")
        
        # Log full traceback
        import traceback
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        
        await doc_service.cleanup_file(input_path)
        raise HTTPException(
            500,
            f"Adobe PDF Services conversion failed: {str(e)}"
        )


@router.post("/convert/pdf-to-word-pdf2docx-only")
async def convert_pdf_to_word_pdf2docx_only(
    file: UploadFile = File(..., description="PDF file to convert"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🟢 PDF2DOCX Library ONLY - Pure Python Local Test
    
    - **Pure Python library** - No cloud APIs, 100% local processing
    - **7/10 quality** - Good for simple text PDFs
    - **Free & fast** - No API costs, instant conversion
    - **NO OCR support** - Cannot handle scanned PDFs
    - **Purpose:** Debug and verify pdf2docx library is working
    
    ⚠️ NOTE: pdf2docx is disabled by default (reduces Docker image by 230MB)
    ⚠️ To enable: Install opencv-python, PyMuPDF, pdf2docx in requirements.txt
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("")
    logger.info("="*80)
    logger.info("🟢 PDF2DOCX-ONLY ENDPOINT: /api/v1/documents/convert/pdf-to-word-pdf2docx-only")
    logger.info(f"   File: {file.filename}")
    logger.info(f"   Size: {file.size if hasattr(file, 'size') else 'unknown'}")
    logger.info("="*80)
    logger.info("")
    
    # Check if pdf2docx is available
    try:
        from pdf2docx import Converter
        logger.info("✅ pdf2docx library found")
    except ImportError:
        logger.error("❌ pdf2docx not installed")
        raise HTTPException(
            503,
            "pdf2docx library not installed. Install: pip install pdf2docx opencv-python PyMuPDF"
        )
    
    # Save uploaded file
    input_path = await doc_service.save_upload_file(file)
    
    try:
        output_filename = input_path.stem + ".docx"
        output_path = doc_service.output_dir / output_filename
        
        logger.info("🔄 Starting pdf2docx conversion...")
        logger.info(f"   Input: {input_path}")
        logger.info(f"   Output: {output_path}")
        logger.info("")
        
        # Use pdf2docx directly
        import time
        start = time.time()
        
        cv = Converter(str(input_path))
        cv.convert(str(output_path), start=0, end=None)
        cv.close()
        
        elapsed = time.time() - start
        
        logger.info("")
        logger.info(f"✅ pdf2docx conversion completed in {elapsed:.2f}s")
        logger.info(f"   Output file: {output_path}")
        logger.info(f"   File exists: {output_path.exists()}")
        logger.info(f"   Size: {output_path.stat().st_size if output_path.exists() else 0} bytes")
        logger.info("")
        
        if not output_path.exists():
            raise FileNotFoundError(f"Output file not created: {output_path}")
        
        # Return file
        response = FileResponse(
            path=output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=output_path.name
        )
        
        # Add metadata headers
        response.headers["X-Technology-Engine"] = "pdf2docx"
        response.headers["X-Technology-Name"] = "pdf2docx (Python Library)"
        response.headers["X-Technology-Quality"] = "7/10"
        response.headers["X-Technology-Type"] = "local"
        response.headers["X-Technology-OCR"] = "false"
        response.headers["X-Processing-Time"] = f"{elapsed:.2f}s"
        
        logger.info("="*80)
        logger.info("✅ PDF2DOCX-ONLY RESPONSE: 200 OK")
        logger.info(f"   File: {output_path.name}")
        logger.info(f"   Size: {output_path.stat().st_size} bytes")
        logger.info(f"   Time: {elapsed:.2f}s")
        logger.info("="*80)
        logger.info("")
        
        return response
        
    except Exception as e:
        logger.error("")
        logger.error("="*80)
        logger.error("❌ PDF2DOCX-ONLY ERROR")
        logger.error(f"   Exception: {type(e).__name__}")
        logger.error(f"   Message: {str(e)}")
        logger.error("="*80)
        logger.error("")
        
        # Log full traceback
        import traceback
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        
        await doc_service.cleanup_file(input_path)
        raise HTTPException(
            500,
            f"pdf2docx conversion failed: {str(e)}"
        )


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


@router.post("/convert/pdf-to-word-hybrid-vietnamese", response_class=FileResponse)
async def convert_pdf_to_word_hybrid_vietnamese(
    file: UploadFile = File(..., description="PDF file to convert"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🌟 HYBRID APPROACH: Gemini OCR + Adobe Layout (Vietnamese scanned PDFs)
    
    **Best solution for Vietnamese scanned PDFs:**
    - **Gemini AI**: Extracts Vietnamese text with 98% accuracy
    - **Adobe PDF Services**: Preserves images and layout at 10/10 quality
    - **Result**: Perfect Vietnamese text + Perfect images/layout = Best of both worlds!
    
    **Why hybrid:**
    - Adobe: NO Vietnamese OCR support (50+ languages but not Vietnamese)
    - Gemini: Excellent Vietnamese OCR but loses images/layout when generating Word
    - Hybrid: Combines Gemini text accuracy with Adobe layout preservation
    
    **When to use:**
    - ✅ Scanned Vietnamese documents with images/photos
    - ✅ Vietnamese forms with handwritten content
    - ✅ Vietnamese PDFs with complex layouts
    
    **Processing steps (logged in detail):**
    1. Gemini OCR → Extract Vietnamese text (98% accuracy)
    2. Adobe OCR (EN_US) → Preserve images/layout (100%)
    3. Combine → Word document with Vietnamese text + images
    
    **Quality:**
    - Text: 98% (Gemini Vietnamese OCR)
    - Images: 100% preserved (Adobe SEARCHABLE_IMAGE_EXACT)
    - Layout: 10/10 (Adobe AI)
    
    **Technical details:**
    - Uses Gemini 2.0 Flash Vision for Vietnamese OCR
    - Uses Adobe ExportPDF with SEARCHABLE_IMAGE_EXACT for layout
    - Detailed logging at each step shows which technology is active
    
    **Returns:** Word document (.docx) with Vietnamese text + images
    """
    doc_service = DocumentService()
    
    # Save uploaded file
    input_path = await doc_service.save_upload_file(file)
    
    try:
        logger.info("")
        logger.info("="*80)
        logger.info("🌟 API ENDPOINT: /convert/pdf-to-word-hybrid-vietnamese")
        logger.info(f"   User: {current_user.email}")
        logger.info(f"   File: {file.filename}")
        logger.info(f"   Size: {input_path.stat().st_size / 1024:.2f} KB")
        logger.info("="*80)
        logger.info("")
        
        # Check if Gemini and Adobe are both available
        if not doc_service.use_gemini:
            logger.error("❌ Gemini API not configured")
            raise HTTPException(500, "Gemini API not configured. Please set GEMINI_API_KEY in .env")
        
        if not (doc_service.use_adobe and doc_service.adobe_credentials):
            logger.error("❌ Adobe PDF Services not configured")
            raise HTTPException(500, "Adobe PDF Services not configured. Please check .env credentials")
        
        # Convert using hybrid approach
        output_path = await doc_service._pdf_to_word_hybrid_vietnamese(
            input_path,
            doc_service.output_dir / f"hybrid_{file.filename.rsplit('.', 1)[0]}.docx",
            db=db
        )
        
        # Return file
        response = FileResponse(
            path=output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=output_path.name
        )
        
        # Add metadata headers
        response.headers["X-Technology-Engine"] = "hybrid"
        response.headers["X-Technology-Name"] = "Gemini + Adobe"
        response.headers["X-Technology-Quality"] = "10/10"
        response.headers["X-Technology-Type"] = "cloud"
        response.headers["X-OCR-Language"] = "Vietnamese"
        response.headers["X-Text-Source"] = "Gemini OCR"
        response.headers["X-Layout-Source"] = "Adobe"
        
        logger.info("")
        logger.info("="*80)
        logger.info("✅ API RESPONSE: FileResponse sent to client")
        logger.info(f"   Output: {output_path.name}")
        logger.info(f"   Size: {output_path.stat().st_size / 1024:.2f} KB")
        logger.info("="*80)
        logger.info("")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Hybrid conversion failed: {e}")
        await doc_service.cleanup_file(input_path)
        raise HTTPException(500, f"Hybrid conversion failed: {str(e)}")


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
    files: List[UploadFile] = File(..., description="Image files (JPG, PNG, etc.)"),
):
    """
    Convert multiple images to PDF (combined into one PDF)
    
    Supported formats: JPG, JPEG, PNG, GIF, BMP, WebP, HEIC
    
    - Automatically handles transparency (PNG)
    - Converts to RGB color space
    - Maintains original resolution
    - High quality output (95%)
    - Multiple images → Pages in single PDF
    """
    if not files:
        raise HTTPException(400, "No files uploaded")
    
    input_paths = []
    try:
        # Save all uploaded files
        for file in files:
            input_path = await doc_service.save_upload_file(file)
            input_paths.append(input_path)
        
        # Convert all images to one PDF
        if len(input_paths) == 1:
            # Single image
            output_path = await doc_service.image_to_pdf(input_paths[0])
        else:
            # Multiple images → combine into one PDF
            output_path = await doc_service.images_to_pdf(input_paths)
        
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=f"images_to_pdf_{len(files)}_pages.pdf"
        )
        
    finally:
        # Cleanup all input files
        for path in input_paths:
            await doc_service.cleanup_file(path)


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
    language: str = Form("vi", description="Language for OCR: vi, en"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ← NEW: Require authentication
):
    """
    🤖 Smart PDF OCR - AI-powered text extraction for scanned PDFs
    
    **⚠️ REQUIRES AUTHENTICATION + AI QUOTA**
    
    **Smart Detection:**
    - Automatically detects if PDF is scanned (image-based)
    - Uses direct text extraction for text-based PDFs (fast & free, no quota)
    - Uses AI OCR (Gemini/Claude) only for scanned PDFs (uses quota)
    
    **AI Engines:**
    - `gemini`: Fast & cost-effective (~$0.000031/page)
    - `claude`: Highest accuracy (~$0.001464/page)
    
    **Quota System:**
    - FREE tier: 3 AI requests/month
    - PRO tier: 100 AI requests/month
    - If quota exceeded, returns 403 with upgrade prompt
    
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
        # ✅ CHECK QUOTA FIRST (only if scanned PDF detected)
        from app.services.document_service import is_pdf_scanned
        is_scanned = is_pdf_scanned(input_path)
        
        if is_scanned:
            # Check quota trước khi gọi AI
            quota_info = QuotaService.check_ai_quota(current_user, db)
            logger.info(f"User {current_user.email} using AI OCR. Quota: {quota_info}")
        
        # Smart OCR processing
        try:
            result = await doc_service.smart_pdf_ocr(
                input_path, 
                ai_engine=ai_engine,
                language=language,
                db=db
            )
            
            # ✅ COMMIT quota increment (AI call thành công)
            if is_scanned:
                db.commit()
            
            return {
                "success": True,
                "filename": file.filename,
                "quota_used": quota_info if is_scanned else None,
                **result
            }
            
        except Exception as e:
            # ❌ ROLLBACK quota nếu AI call thất bại
            if is_scanned:
                QuotaService.rollback_quota_increment(current_user, db)
            raise e
        
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
        logger.info(f"🔄 [Merge Word→PDF] Starting merge of {len(files)} Word files")
        logger.info(f"📁 Files: {[f.filename for f in files]}")
        
        # Step 1: Convert each Word to PDF
        for idx, file in enumerate(files, 1):
            try:
                logger.info(f"📝 [{idx}/{len(files)}] Converting: {file.filename}")
                input_path = await doc_service.save_upload_file(file)
                logger.info(f"💾 Saved to: {input_path}")
                
                pdf_path = await doc_service.word_to_pdf(input_path)
                logger.info(f"✅ Converted to PDF: {pdf_path}")
                
                temp_pdf_files.append(pdf_path)
                await doc_service.cleanup_file(input_path)
                logger.info(f"🗑️ Cleaned up input file: {input_path}")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ Error converting {file.filename}: {error_msg}", exc_info=True)
                errors.append({"file": file.filename, "error": error_msg})
        
        if not temp_pdf_files:
            error_details = "\n".join([f"- {e['file']}: {e['error']}" for e in errors])
            raise HTTPException(500, f"All conversions failed:\n{error_details}")
        
        if len(temp_pdf_files) < len(files):
            logger.warning(f"⚠️ Only {len(temp_pdf_files)}/{len(files)} files converted successfully")
        
        # Step 2: Merge all PDFs into one
        logger.info(f"🔗 Merging {len(temp_pdf_files)} PDF files...")
        
        import pypdf
        
        merger = pypdf.PdfWriter()
        for pdf_path in temp_pdf_files:
            if pdf_path.exists():
                logger.info(f"➕ Adding to merge: {pdf_path.name}")
                with open(pdf_path, 'rb') as f:
                    pdf_reader = pypdf.PdfReader(f)
                    for page in pdf_reader.pages:
                        merger.add_page(page)
            else:
                logger.warning(f"⚠️ PDF not found: {pdf_path}")
        
        # Save merged PDF
        output_path = doc_service.output_dir / f"merged_{len(temp_pdf_files)}_files.pdf"
        logger.info(f"💾 Writing merged PDF to: {output_path}")
        
        with open(output_path, 'wb') as output_file:
            merger.write(output_file)
        
        logger.info(f"✅ Merged PDF created: {output_path.name} ({output_path.stat().st_size} bytes)")
        
        # Cleanup temp PDFs
        for pdf_path in temp_pdf_files:
            try:
                await doc_service.cleanup_file(pdf_path)
            except Exception as cleanup_err:
                logger.warning(f"⚠️ Failed to cleanup {pdf_path}: {cleanup_err}")
        
        # Return merged PDF
        if errors:
            logger.warning(f"⚠️ Completed with {len(errors)} errors: {errors}")
        
        return FileResponse(
            path=str(output_path),
            media_type="application/pdf",
            filename=f"merged_{len(files)}_documents.pdf",
            background=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fatal error in merge operation: {str(e)}", exc_info=True)
        # Cleanup temp files
        for pdf_path in temp_pdf_files:
            try:
                await doc_service.cleanup_file(pdf_path)
            except Exception as cleanup_err:
                logger.warning(f"⚠️ Failed to cleanup {pdf_path}: {cleanup_err}")
        raise HTTPException(500, f"Merge and conversion failed: {str(e)}")


@router.post("/batch/pdf-to-word")
async def batch_convert_pdf_to_word(
    files: List[UploadFile] = File(..., description="Multiple PDF files"),
    db: Session = Depends(get_db)
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
                output_path = await doc_service.pdf_to_word(input_path, db=db)
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
    format: str = Query(..., description="Target format: word, excel, or image"),
    db: Session = Depends(get_db)
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
                    output_path = await doc_service.pdf_to_word(input_path, db=db)
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
    Tách PDF thành nhiều file bằng PyPDF2 (đơn giản, nhanh, miễn phí)

    - Upload file PDF
    - Chỉ định các khoảng trang cần tách
    - Format: "1-3,4-6,7-10" (mỗi khoảng sẽ tạo 1 file riêng)
    - Output: ZIP chứa tất cả các file PDF đã tách
    - Công nghệ: PyPDF2 (không dùng Adobe API để tiết kiệm quota)
    """
    # DEBUG: Log received parameters
    logger.info(f"🔍 Split PDF received: file={file.filename}, page_ranges={page_ranges}")
    
    pdf_path = await doc_service.save_upload_file(file)
    output_paths = []
    
    try:
        # Parse page ranges - remove ALL whitespace
        ranges = [r.strip().replace(' ', '') for r in page_ranges.split(',')]
        logger.info(f"📝 Parsed ranges: {ranges}")
        
        # Validate ranges against PDF page count
        import pypdf
        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                total_pages = len(pdf_reader.pages)
                logger.info(f"📖 PDF has {total_pages} pages")
                
                # Validate each range
                for range_str in ranges:
                    if '-' in range_str:
                        start, end = map(int, range_str.split('-'))
                        if start > total_pages or end > total_pages:
                            error_msg = (
                                f"⚠️ Khoảng trang '{range_str}' vượt quá số trang của PDF!\n\n"
                                f"📖 PDF của bạn chỉ có {total_pages} trang.\n"
                                f"💡 Vui lòng nhập khoảng trang từ 1 đến {total_pages}.\n\n"
                                f"Ví dụ hợp lệ: 1-{min(3, total_pages)},{min(2, total_pages)}-{total_pages}"
                            )
                            logger.error(f"❌ Validation failed: {error_msg}")
                            raise HTTPException(status_code=400, detail=error_msg)
                    else:
                        page_num = int(range_str)
                        if page_num > total_pages:
                            error_msg = (
                                f"⚠️ Trang {page_num} không tồn tại trong PDF!\n\n"
                                f"📖 PDF của bạn chỉ có {total_pages} trang.\n"
                                f"💡 Vui lòng chọn trang từ 1 đến {total_pages}."
                            )
                            logger.error(f"❌ Validation failed: {error_msg}")
                            raise HTTPException(status_code=400, detail=error_msg)
        except HTTPException:
            raise  # Re-raise validation errors
        except Exception as e:
            logger.warning(f"⚠️ Cannot validate page count: {e}. Continuing...")
        
        # Use PyPDF2 for splitting (simple, fast, free)
        # Adobe API reserved for complex operations like PDF-to-Word conversion
        output_paths = await doc_service.split_pdf_pypdf(pdf_path, ranges)
        engine_used = "pypdf2"
        logger.info(f"✅ PyPDF2 split returned {len(output_paths)} file paths")
        
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
        
        # Set headers based on engine used
        tech_engine = "Adobe PDF Services" if engine_used == "adobe" else "PyPDF2 (Fallback)"
        tech_quality = "10/10" if engine_used == "adobe" else "8/10"
        
        # Return as bytes response
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "X-Technology-Engine": engine_used,
                "X-Technology-Name": tech_engine,
                "X-Technology-Quality": tech_quality,
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


@router.post("/generate-visualization")
async def generate_visualization(
    text_input: str = Form(..., description="Text content with data to visualize"),
    document_title: Optional[str] = Form(None, description="Custom document title (optional)"),
    language: str = Form("vi", description="Language: vi or en"),
    provider: str = Form("gemini", description="AI provider: 'gemini' or 'claude'"),
    model: Optional[str] = Form(None, description="Specific model name (optional)"),
):
    """
    📊 AI Data Visualization - Create Word documents with charts from text data
    
    **How it works:**
    1. AI analyzes your text and detects numerical data
    2. Automatically selects appropriate chart types (bar, line, pie, scatter)
    3. Generates beautiful matplotlib charts
    4. Embeds charts into formatted Word document with descriptions
    
    **Features:**
    - 🎨 Auto-detect data patterns and choose chart types
    - 📊 Multiple chart types: bar, line, pie, scatter
    - 🖼️ High-quality PNG charts (200 DPI)
    - 📄 Professional Word document formatting
    - 🌍 Vietnamese & English support
    - 🤖 Powered by Gemini AI + matplotlib
    
    **Example input:**
    ```
    Báo cáo doanh thu Q4/2024
    
    Doanh thu các tháng:
    - Tháng 10: 500 triệu
    - Tháng 11: 650 triệu
    - Tháng 12: 720 triệu
    
    Phân tích sản phẩm:
    - Sản phẩm A: 45%
    - Sản phẩm B: 30%
    - Sản phẩm C: 25%
    ```
    
    **AI will create:**
    - Bar chart: Monthly revenue
    - Pie chart: Product distribution
    - Formatted sections with analysis
    
    **Cost:** ~$0.00001-0.0001 per request (very cheap)
    """
    try:
        # Log incoming request
        logger.info(f"📊 Visualization request: provider={provider}, model={model}, language={language}, text_length={len(text_input) if text_input else 0}")
        
        # Validate inputs
        if not text_input or len(text_input.strip()) < 10:
            raise HTTPException(400, "Text must be at least 10 characters")
        
        if provider not in ["gemini", "claude"]:
            raise HTTPException(400, "Provider must be 'gemini' or 'claude'")
        
        if language not in ["vi", "en", "zh", "ja", "ko", "fr", "de", "es"]:
            raise HTTPException(400, "Unsupported language code")
        
        # Generate DOCX with charts (using text_to_word_mhtml which supports visualization)
        docx_bytes, ai_usage = await doc_service.text_to_word_mhtml(
            text=text_input,
            provider=provider,
            model=model,
            language=language
        )
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        title_slug = document_title.replace(" ", "_") if document_title else "visualization"
        filename = f"{title_slug}_{timestamp}.docx"
        
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
        response.headers["X-Technology-Feature"] = "Data Visualization + matplotlib"
        response.headers["X-Technology-Quality"] = "10/10"
        response.headers["X-Technology-Type"] = "ai-visualization"
        response.headers["X-Input-Tokens"] = str(ai_usage.get("input_tokens", 0))
        response.headers["X-Output-Tokens"] = str(ai_usage.get("output_tokens", 0))
        response.headers["X-Processing-Time-Ms"] = str(int(ai_usage.get("processing_time_ms", 0)))
        
        logger.info(f"✅ Visualization created successfully: {filename}")
        return response
        
    except HTTPException as he:
        logger.error(f"❌ HTTPException in generate-visualization: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ Visualization generation error: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"Failed to generate visualization: {str(e)}")


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


# ============================================
# OCR TO WORD ENDPOINT (Vietnamese AI-First)
# ============================================

@router.post("/ocr-to-word-demo", dependencies=[])
async def ocr_to_word_demo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Public demo OCR: always skip auth/quota and don't track usage."""
    return await ocr_to_word(file=file, authorization=None, db=db)

@router.post("/ocr-to-word", dependencies=[])
async def ocr_to_word(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    🇻🇳 Trích xuất văn bản từ PDF → Word (Gemini 2.5 Flash - Perfect Vietnamese)
    
    Features:
    - Auto-detect: Text-based hay Scanned PDF (for analytics only)
    - Gemini 2.5 Flash PDF Upload: LUÔN LUÔN dùng cho TẤT CẢ PDF
    - 98% accuracy cho tiếng Việt (perfect diacritics)
    - Upload trực tiếp PDF (không convert image)
    - Quota tracking: Tích hợp hệ thống quota
    - Analytics logging: Track user behavior
    - PUBLIC DEMO: Cho phép dùng thử không cần đăng nhập
    
    Why Gemini for ALL PDFs?
    - PyMuPDF/PyPDF2: SAI DẤU tiếng Việt (tr ngày → từ ngày, quân trj → quản trị)
    - Gemini: PERFECT Vietnamese diacritics, understands layout/tables
    - Cost: $0.10-0.20/doc → Worth it for quality!
    - Speed: 10-20s for 12 pages (upload entire PDF, not page-by-page)
    
    Process:
    1. Upload PDF
    2. Detect type (analytics only, không ảnh hưởng xử lý)
    3. Upload PDF lên Gemini 2.5 Flash
    4. Gemini processes all pages at once
    5. Generate Word file with formatting
    6. Log analytics
    7. Return Word file
    
    Returns:
        Word file (.docx) with PERFECT Vietnamese text extraction
    """
    temp_pdf_path = None
    temp_word_path = None
    start_time = time.time()
    
    # Get current user from header (optional)
    current_user = None
    if authorization:
        try:
            from app.core.security import decode_access_token
            if authorization.startswith("Bearer "):
                token = authorization.replace("Bearer ", "")
                payload = decode_access_token(token)
                user_id = payload.get("user_id")
                if user_id:
                    current_user = db.query(User).filter(User.id == user_id).first()
        except:
            pass  # Ignore errors - demo mode
    
    is_demo_user = current_user is None  # Public demo mode
    
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(400, "Chỉ hỗ trợ file PDF. Vui lòng chọn file PDF.")

        # NOTE: Do NOT check/increment quota yet.
        # Only scanned PDFs that require AI OCR should consume quota.
        logger.info("ℹ️ Quota will be checked only if AI OCR is needed")
        
        # Log user action: processing_start (only for authenticated users)
        if not is_demo_user:
            from app.services.ocr_analytics_service import OCRAnalyticsService
            import uuid
            session_id = str(uuid.uuid4())
            
            OCRAnalyticsService.log_user_action(
                db=db,
                user_id=current_user.id,
                session_id=session_id,
                action_type="processing_start",
                action_metadata={"filename": file.filename},
                page_url="/ocr-to-word"
            )
        
        # Save uploaded file
        logger.info(f"📥 Saving uploaded file: {file.filename}")
        upload_dir = Path("uploads/ocr")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # IMPORTANT: Never use user-provided filename for filesystem paths.
        # Some filenames (Vietnamese, special chars, path separators) can break Windows paths.
        import uuid
        temp_pdf_path = upload_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}.pdf"
        
        async with aiofiles.open(temp_pdf_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        # Early sanity checks for problematic PDFs (encrypted/corrupt)
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(str(temp_pdf_path))
            if getattr(pdf_reader, "is_encrypted", False):
                raise HTTPException(
                    400,
                    "🔒 File PDF đang được đặt mật khẩu/mã hóa. Vui lòng gỡ mật khẩu (Unlock) rồi thử lại."
                )
            # Touch pages to surface some structural errors early
            _ = len(getattr(pdf_reader, "pages", []))
        except HTTPException:
            raise
        except Exception as e:
            msg = str(e).lower()
            if any(k in msg for k in ["encrypted", "password", "decrypt"]):
                raise HTTPException(
                    400,
                    "🔒 File PDF đang được đặt mật khẩu/mã hóa. Vui lòng gỡ mật khẩu (Unlock) rồi thử lại."
                )
            if any(k in msg for k in ["pdfreaderror", "invalid", "corrupt", "broken", "xref", "eof"]):
                raise HTTPException(
                    400,
                    "📄 File PDF có thể bị lỗi/corrupt hoặc không đúng định dạng. Vui lòng thử tải lại file hoặc xuất (Export) PDF lại rồi thử lại."
                )
            # Otherwise: continue; OCRService may still handle it via PyMuPDF
        
        file_size_bytes = temp_pdf_path.stat().st_size
        logger.info(f"✅ File saved: {file_size_bytes} bytes")
        
        # Initialize OCR service with Gemini
        from app.services.gemini_service import GeminiService
        from app.services.ocr_service import OCRService
        
        user_id = current_user.id if current_user else None
        gemini = GeminiService(db, user_id=user_id)
        ocr_service = OCRService(gemini)
        
        # Step 1: Detect PDF type (avoid AI calls until quota is confirmed)
        logger.info("🔍 Detecting PDF type...")
        metadata = {"total_pages": 0, "extracted_text_length": 0, "images_found": 0, "confidence": "low"}

        # Method 1 (fast): text extraction on first 3 pages
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(str(temp_pdf_path))
            metadata["total_pages"] = len(pdf_reader.pages)
            extracted_preview = ""
            for page in pdf_reader.pages[:3]:
                extracted_preview += (page.extract_text() or "")
            metadata["extracted_text_length"] = len(extracted_preview.strip())
        except Exception:
            # We'll fall back to image ratio
            pass

        if metadata.get("extracted_text_length", 0) > OCRService.TEXT_LENGTH_THRESHOLD:
            is_scanned = False
            detection_method = "text_extraction"
            metadata["confidence"] = "high"
        else:
            # Method 2: image ratio
            images_found = ocr_service._count_images_in_pdf(temp_pdf_path)
            metadata["images_found"] = images_found
            total_pages = max(1, int(metadata.get("total_pages") or 1))
            image_ratio = images_found / total_pages
            if image_ratio > OCRService.IMAGE_RATIO_THRESHOLD:
                is_scanned = True
                detection_method = "image_ratio"
                metadata["confidence"] = "medium"
            else:
                # Ambiguous → treat as scanned (safer) but this will require quota for authenticated users
                is_scanned = True
                detection_method = "ambiguous_fallback"
                metadata["confidence"] = "low"
        
        logger.info(f"📊 Detection result: {'SCANNED' if is_scanned else 'TEXT-BASED'} (method: {detection_method})")

        # ALWAYS use Gemini AI - Even text-based PDFs need it for perfect Vietnamese
        # PyMuPDF/PyPDF2 fail miserably with Vietnamese diacritics
        quota_incremented = False
        if not is_demo_user:
            logger.info(f"🔍 Checking AI quota for user {current_user.id} (using Gemini for perfect Vietnamese)...")
            quota_info_checked = QuotaService.check_ai_quota(current_user, db)
            quota_incremented = True
        else:
            logger.info("🎭 Demo mode - skipping quota check")
        
        # Step 2: Extract text
        logger.info("📝 Extracting text...")
        try:
            extracted_text = ocr_service.extract_text_from_pdf(temp_pdf_path, is_scanned)
        except Exception:
            # Roll back quota increment if AI OCR failed
            if not is_demo_user and 'quota_incremented' in locals() and quota_incremented:
                try:
                    QuotaService.rollback_quota_increment(current_user, db)
                except Exception:
                    pass
            raise
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            raise HTTPException(400, "Không thể trích xuất văn bản từ file này. Vui lòng thử file khác.")
        
        # Step 3: Create Word document
        logger.info("📄 Creating Word document...")
        temp_word_path = upload_dir / f"OCR_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        
        ocr_service.create_word_document(
            text=extracted_text,
            output_path=temp_word_path,
            title=f"Trích xuất văn bản - {file.filename}"
        )
        
        processing_time = time.time() - start_time
        logger.info(f"✅ Processing completed in {processing_time:.2f}s")
        
        # Log analytics (success) - only for authenticated users
        if not is_demo_user:
            OCRAnalyticsService.log_ocr_usage(
                db=db,
                user_id=current_user.id,
                file_name=file.filename,
                file_size_bytes=file_size_bytes,
                file_type="application/pdf",
                total_pages=metadata.get("total_pages", 1),
                detection_method=detection_method,
                is_scanned=is_scanned,
                processing_time_seconds=processing_time,
                gemini_model_used="gemini-2.5-flash",  # Always use Gemini
                success=True,
                downloaded=False  # Will be updated when user downloads
            )
        
        # Commit quota increment after successful AI extraction
        if not is_demo_user and 'quota_incremented' in locals() and quota_incremented:
            db.commit()

        # Refetch quota (updated after use) - only for authenticated users
        if not is_demo_user:
            quota_info = QuotaService.get_user_quota_info(current_user)
        else:
            quota_info = {"ai_usage_this_month": 0, "ai_quota_monthly": 0}
        
        # Return Word file
        original_stem = Path(file.filename).stem
        output_filename_utf8 = f"OCR_{original_stem}.docx"

        # Create an ASCII-safe fallback filename for legacy clients
        import re
        import unicodedata
        ascii_stem = (
            unicodedata.normalize("NFKD", original_stem)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        ascii_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", ascii_stem).strip("_")
        if not ascii_stem:
            ascii_stem = "document"
        output_filename_ascii = f"OCR_{ascii_stem}.docx"

        encoded_filename = encode_filename(output_filename_utf8)

        return FileResponse(
            path=str(temp_word_path),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "X-Quota-Used": str(quota_info.get("usage_this_month", 0) if isinstance(quota_info, dict) else 0),
                "X-Quota-Total": str(quota_info.get("quota_monthly", 0) if isinstance(quota_info, dict) else 0),
                "X-Processing-Time": f"{processing_time:.2f}s",
                "X-Is-Scanned": str(is_scanned).lower(),
                "X-Detection-Method": detection_method,
                "X-Total-Pages": str(metadata.get("total_pages", 0)),
                "X-Text-Length": str(len(extracted_text)),
                "X-Confidence": metadata.get("confidence", "low"),
                "X-AI-Used": str(is_scanned).lower(),
                "Content-Disposition": (
                    f'attachment; filename="{output_filename_ascii}"; '
                    f"filename*=UTF-8''{encoded_filename}"
                ),
            },
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        import uuid
        import traceback
        error_id = uuid.uuid4().hex[:10]
        logger.error(f"❌ OCR error [{error_id}]: {e}", exc_info=True)

        # Persist traceback to a local log file for file-specific debugging
        try:
            logs_dir = Path("logs")
            logs_dir.mkdir(parents=True, exist_ok=True)
            log_path = logs_dir / "ocr_errors.log"
            with open(log_path, "a", encoding="utf-8") as f:
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"time={datetime.now().isoformat()} error_id={error_id}\n")
                f.write(f"filename={getattr(file, 'filename', None)}\n")
                if 'file_size_bytes' in locals():
                    f.write(f"file_size_bytes={file_size_bytes}\n")
                if temp_pdf_path:
                    f.write(f"temp_pdf_path={temp_pdf_path}\n")
                if 'detection_method' in locals():
                    f.write(f"detection_method={detection_method}\n")
                if 'is_scanned' in locals():
                    f.write(f"is_scanned={is_scanned}\n")
                f.write(f"exception={type(e).__name__}: {e}\n")
                f.write(traceback.format_exc())
        except Exception:
            pass
        
        # Log analytics (error) - only for authenticated users
        if not is_demo_user:
            try:
                from app.services.ocr_analytics_service import OCRAnalyticsService
                OCRAnalyticsService.log_ocr_usage(
                    db=db,
                    user_id=current_user.id,
                    file_name=file.filename if file else "unknown",
                    file_size_bytes=file_size_bytes if 'file_size_bytes' in locals() else 0,
                    file_type="application/pdf",
                    success=False,
                    error_message=str(e),
                    error_type=type(e).__name__
                )
            except:
                pass  # Don't fail if analytics fails

        # Roll back quota increment if we consumed quota but failed later
        if not is_demo_user and 'quota_incremented' in locals() and quota_incremented:
            try:
                QuotaService.rollback_quota_increment(current_user, db)
            except Exception:
                pass
        
        # Friendly error message (classify common PDF issues)
        msg = str(e).lower()
        if any(k in msg for k in ["encrypted", "password", "decrypt"]):
            raise HTTPException(
                400,
                "🔒 File PDF đang được đặt mật khẩu/mã hóa. Vui lòng gỡ mật khẩu (Unlock) rồi thử lại."
            )
        if any(k in msg for k in ["pdfreaderror", "invalid", "corrupt", "broken", "xref", "eof", "cannot open broken document"]):
            raise HTTPException(
                400,
                "📄 File PDF có thể bị lỗi/corrupt hoặc không đúng định dạng. Vui lòng thử tải lại file hoặc xuất (Export) PDF lại rồi thử lại."
            )
        if "quota" in msg:
            raise HTTPException(403, "❌ Bạn đã hết quota. Vui lòng nâng cấp gói.")
        if "memory" in msg:
            raise HTTPException(400, "🧠 File quá lớn. Vui lòng thử file nhỏ hơn hoặc tách file ra.")

        raise HTTPException(500, f"😔 Không thể xử lý file này (Mã lỗi: {error_id}). Vui lòng thử lại sau.")
        
    finally:
        # Cleanup temporary files (keep Word for download, delete PDF)
        if temp_pdf_path and temp_pdf_path.exists():
            try:
                temp_pdf_path.unlink()
                logger.info(f"🗑️ Cleaned up temp PDF: {temp_pdf_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup PDF: {e}")
