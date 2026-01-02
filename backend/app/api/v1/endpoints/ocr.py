"""
Modern OCR API Endpoints (2025)
Extract text from images using deep learning
"""

from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import List
from sqlalchemy.orm import Session

from app.services.ocr_service import OCRService
from app.services.gemini_service import GeminiService
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.auth_models import User

router = APIRouter(tags=["OCR - Text Recognition"])


def get_ocr_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> OCRService:
    """Dependency to get OCRService with GeminiService"""
    gemini_service = GeminiService(db=db, user_id=current_user.id)
    return OCRService(gemini_service=gemini_service)


@router.post("/extract")
async def extract_text(
    file: UploadFile = File(..., description="Image file with text"),
    languages: str = Form("vi,en", description="Comma-separated language codes (e.g., 'vi,en')"),
    detail: int = Form(1, ge=0, le=1, description="0=text only, 1=text+confidence+bounding boxes"),
    paragraph: bool = Form(False, description="Group text into paragraphs"),
    gpu: bool = Form(False, description="Use GPU acceleration (requires CUDA)"),
    ocr_service: OCRService = Depends(get_ocr_service),
):
    """
    Extract text from image using AI-powered OCR
    
    **Supported Languages:**
    - `vi`: Vietnamese (tiếng Việt)
    - `en`: English
    - `ch_sim`: Chinese Simplified (简体中文)
    - `ch_tra`: Chinese Traditional (繁體中文)
    - `ja`: Japanese (日本語)
    - `ko`: Korean (한국어)
    - `th`: Thai (ภาษาไทย)
    - And 70+ more languages!
    
    **Examples:**
    - `languages=vi,en` → Detect Vietnamese and English
    - `languages=vi` → Vietnamese only
    - `languages=en` → English only
    - `languages=vi,en,ch_sim` → Vietnamese, English, Chinese
    
    **Detail levels:**
    - `0`: Returns plain text only (faster)
    - `1`: Returns text + confidence + bounding box coordinates (recommended)
    
    **Use cases:**
    - Digitize printed documents
    - Extract text from photos
    - Process receipts, invoices
    - Read street signs, menus
    - Convert handwritten notes (limited support)
    """
    input_path = await ocr_service.save_upload_file(file)
    
    try:
        # Parse languages
        lang_list = [lang.strip() for lang in languages.split(',')]
        
        # Extract text
        result = await ocr_service.extract_text(
            input_path,
            languages=lang_list,
            detail=detail,
            paragraph=paragraph,
            gpu=gpu
        )
        
        return {
            "filename": file.filename,
            **result
        }
        
    finally:
        await ocr_service.cleanup_file(input_path)


@router.post("/vietnamese")
async def extract_vietnamese(
    file: UploadFile = File(..., description="Image with Vietnamese text"),
    include_english: bool = Form(True, description="Also detect English text"),
    gpu: bool = Form(False, description="Use GPU acceleration"),
    ocr_service: OCRService = Depends(get_ocr_service),
):
    """
    Extract Vietnamese text (optimized for Vietnamese)
    
    - Optimized model for Vietnamese characters
    - Handles Vietnamese diacritics (dấu) accurately
    - Can detect mixed Vietnamese/English text
    
    **Perfect for:**
    - Vietnamese documents (CCCD, CMND, giấy tờ)
    - Vietnamese receipts (hóa đơn)
    - Vietnamese books (sách, tài liệu)
    - Vietnamese street signs (biển báo)
    """
    input_path = await ocr_service.save_upload_file(file)
    
    try:
        result = await ocr_service.extract_vietnamese_text(
            input_path,
            include_english=include_english,
            gpu=gpu
        )
        
        return {
            "filename": file.filename,
            **result
        }
        
    finally:
        await ocr_service.cleanup_file(input_path)


@router.post("/auto-detect")
async def auto_detect_and_extract(
    file: UploadFile = File(..., description="Image with text (any language)"),
    gpu: bool = Form(False, description="Use GPU acceleration"),
    ocr_service: OCRService = Depends(get_ocr_service),
):
    """
    Auto-detect language and extract text
    
    - Automatically detects the language in the image
    - Tries common language combinations
    - Returns best result
    
    **Detection priority:**
    1. Vietnamese + English
    2. English only
    3. Vietnamese + English (fallback)
    
    **When to use:**
    - Unknown language in image
    - Mixed language documents
    - Quick OCR without language specification
    """
    input_path = await ocr_service.save_upload_file(file)
    
    try:
        result = await ocr_service.detect_language_and_extract(
            input_path,
            gpu=gpu
        )
        
        return {
            "filename": file.filename,
            **result
        }
        
    finally:
        await ocr_service.cleanup_file(input_path)
