"""
Settings & Configuration API Endpoints
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Optional
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(tags=["Settings"])


class TechnologyPriorityUpdate(BaseModel):
    """Model for updating technology priority"""
    operation: str  # compress, watermark, pdf_info
    priority: str   # e.g., "adobe,pypdf" or "pypdf,adobe"


class SettingsResponse(BaseModel):
    """Current settings response"""
    adobe_enabled: bool
    technology_priorities: Dict[str, list]
    adobe_quota_info: Optional[Dict] = None


@router.get("", response_model=SettingsResponse)
async def get_settings():
    """
    📊 Xem cấu hình hiện tại
    
    Hiển thị:
    - Trạng thái Adobe API (enabled/disabled)
    - Thứ tự công nghệ cho mỗi operation
    - Quota Adobe (nếu có)
    """
    return {
        "adobe_enabled": settings.USE_ADOBE_PDF_API,
        "technology_priorities": {
            "compress": settings.get_technology_priority("compress"),
            "watermark": settings.get_technology_priority("watermark"),
            "pdf_info": settings.get_technology_priority("pdf_info"),
        },
        "adobe_quota_info": {
            "monthly_limit": 500,
            "note": "Check Adobe console for real-time usage: https://developer.adobe.com/console"
        } if settings.USE_ADOBE_PDF_API else None
    }


@router.post("/technology-priority")
async def update_technology_priority(
    update: TechnologyPriorityUpdate = Body(...)
):
    """
    ⚙️ Cập nhật thứ tự công nghệ cho operation
    
    **Request Body:**
    ```json
    {
        "operation": "compress",
        "priority": "adobe,pypdf"
    }
    ```
    
    **Operations:**
    - `compress`: PDF compression
    - `watermark`: Add watermark to PDF
    - `pdf_info`: Get PDF properties
    
    **Technologies:**
    - `adobe`: Adobe PDF Services API (10/10 quality, cloud, 500 free/month)
    - `pypdf`: pypdf library (7/10 quality, local, unlimited)
    
    **Examples:**
    - `"adobe,pypdf"`: Try Adobe first, fallback to pypdf
    - `"pypdf,adobe"`: Try pypdf first, fallback to Adobe
    - `"pypdf"`: Use pypdf only (no fallback)
    - `"adobe"`: Use Adobe only (no fallback)
    """
    # Validate operation
    valid_operations = ["compress", "watermark", "pdf_info"]
    if update.operation not in valid_operations:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid operation. Must be one of: {', '.join(valid_operations)}"
        )
    
    # Validate technologies
    valid_technologies = ["adobe", "pypdf", "reportlab"]
    technologies = [t.strip().lower() for t in update.priority.split(",")]
    
    for tech in technologies:
        if tech not in valid_technologies:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid technology '{tech}'. Must be one of: {', '.join(valid_technologies)}"
            )
    
    # Update settings (runtime only - not persistent)
    if update.operation == "compress":
        settings.COMPRESS_PRIORITY = update.priority
    elif update.operation == "watermark":
        settings.WATERMARK_PRIORITY = update.priority
    elif update.operation == "pdf_info":
        settings.PDF_INFO_PRIORITY = update.priority
    
    return {
        "success": True,
        "message": f"Updated {update.operation} priority to: {update.priority}",
        "note": "This change is runtime only. To make it permanent, update .env file",
        "new_priority": settings.get_technology_priority(update.operation)
    }


@router.get("/available-technologies")
async def get_available_technologies():
    """
    🔧 Xem danh sách công nghệ khả dụng
    
    Hiển thị tất cả công nghệ có thể dùng và khả năng của chúng
    """
    return {
        "technologies": {
            "adobe": {
                "name": "Adobe PDF Services API",
                "quality": "10/10",
                "type": "cloud",
                "cost": "500 free transactions/month",
                "enabled": settings.USE_ADOBE_PDF_API,
                "operations": [
                    "pdf_to_word",      # ✅ Already using
                    "compress_pdf",     # Can upgrade
                    "add_watermark",    # Can upgrade
                    "get_pdf_info",     # Can upgrade
                    "ocr_pdf",          # New - Adobe only
                    "extract_content",  # New - Adobe only
                    "html_to_pdf"       # New - Adobe only
                ],
                "unique_features": [
                    "AI-powered compression (50-80% size reduction)",
                    "OCR with 50+ languages including Vietnamese",
                    "Smart content extraction (tables, images, fonts)",
                    "HTML to PDF with perfect rendering",
                    "Rich PDF metadata"
                ]
            },
            "pypdf": {
                "name": "pypdf (Python library)",
                "quality": "7/10",
                "type": "local",
                "cost": "Free, unlimited",
                "enabled": True,  # Always available
                "operations": [
                    "compress_pdf",     # ✅ Already using
                    "add_watermark",    # ✅ Already using (with reportlab)
                    "protect_pdf",      # ✅ Already using
                    "unlock_pdf",       # ✅ Already using
                    "merge_pdf",        # ✅ Already using
                    "split_pdf",        # ✅ Already using
                    "rotate_pdf",       # ✅ Already using
                    "extract_text",     # ✅ Already using
                    "get_pdf_info"      # ✅ Already using
                ],
                "notes": [
                    "Good for basic operations",
                    "No internet required",
                    "Faster for simple tasks",
                    "Lower compression quality than Adobe"
                ]
            },
            "gotenberg": {
                "name": "Gotenberg (LibreOffice headless)",
                "quality": "9/10",
                "type": "local (Docker)",
                "cost": "Free, unlimited",
                "enabled": True,  # Assuming Gotenberg is running
                "operations": [
                    "word_to_pdf",      # ✅ Already using
                    "excel_to_pdf",     # ✅ Already using
                    "powerpoint_to_pdf" # ✅ Already using
                ],
                "notes": [
                    "Excellent Office to PDF conversion",
                    "Preserves formatting perfectly",
                    "Requires Docker container running"
                ]
            },
            "pdf2docx": {
                "name": "pdf2docx (Python library)",
                "quality": "7/10",
                "type": "local",
                "cost": "Free, unlimited",
                "enabled": True,
                "operations": [
                    "pdf_to_word"  # ✅ Already using as fallback
                ],
                "notes": [
                    "Fallback for PDF to Word when Adobe unavailable",
                    "Pure Python, cross-platform",
                    "Good for simple PDFs"
                ]
            },
            "pdfplumber": {
                "name": "pdfplumber (Python library)",
                "quality": "8/10",
                "type": "local",
                "cost": "Free, unlimited",
                "enabled": True,
                "operations": [
                    "pdf_to_excel"  # ✅ Already using
                ],
                "notes": [
                    "Excellent for table extraction",
                    "Good text extraction with layout info"
                ]
            }
        },
        "recommendations": {
            "best_quality": "Use Adobe for all operations (if quota allows)",
            "balanced": "Adobe for conversions, pypdf for manipulations",
            "cost_effective": "pypdf for everything, Adobe only for critical tasks",
            "no_internet": "pypdf + gotenberg + pdfplumber only"
        }
    }


@router.post("/reset-priorities")
async def reset_priorities():
    """
    🔄 Reset về cấu hình mặc định
    
    Reset tất cả technology priorities về default:
    - compress: adobe,pypdf
    - watermark: adobe,pypdf
    - pdf_info: adobe,pypdf
    """
    settings.COMPRESS_PRIORITY = "adobe,pypdf"
    settings.WATERMARK_PRIORITY = "adobe,pypdf"
    settings.PDF_INFO_PRIORITY = "adobe,pypdf"
    
    return {
        "success": True,
        "message": "All priorities reset to default (Adobe first)",
        "priorities": {
            "compress": settings.get_technology_priority("compress"),
            "watermark": settings.get_technology_priority("watermark"),
            "pdf_info": settings.get_technology_priority("pdf_info"),
        }
    }
