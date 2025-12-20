"""
OCR Comparison API - Compare Adobe, Tesseract, and Gemini OCR engines
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import time
from typing import Dict, Any
from loguru import logger

from app.core.config import settings
from app.services.ocr_service import OCRService
from app.services.document_service import DocumentService
from app.services.ai_usage_service import get_api_key, get_primary_key, log_usage, check_budget_limit
from app.core.database import SessionLocal

router = APIRouter(prefix="/ocr-compare", tags=["🔍 OCR Comparison"])

# Initialize services
ocr_service = OCRService()
document_service = DocumentService()


@router.post("/compare-engines")
async def compare_ocr_engines(
    file: UploadFile = File(...),
    language: str = "vi"
):
    """
    Compare OCR results from Adobe, Tesseract, and Gemini
    
    Args:
        file: Image file to OCR
        language: Language code (vi, en, etc.)
    
    Returns:
        Comparison results from all available engines
    """
    try:
        # Save uploaded file
        temp_dir = Path(settings.TEMP_DIR)
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        temp_file = temp_dir / f"ocr_compare_{int(time.time())}_{file.filename}"
        with open(temp_file, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"📄 Comparing OCR engines for: {file.filename}")
        
        results = {
            "filename": file.filename,
            "file_size": len(content),
            "language": language,
            "engines": {}
        }
        
        # Run all engines
        tasks = []
        
        # 1. Adobe OCR (if available)
        async def run_adobe():
            try:
                # Skip Adobe for Vietnamese - not supported
                if language == "vi" or language == "vi+en":
                    return {
                        "engine": "adobe",
                        "available": False,
                        "reason": "⚠️ Adobe OCR không hỗ trợ tiếng Việt. Chỉ hỗ trợ: English, German, French, Spanish, Italian, Portuguese",
                        "processing_time": 0,
                        "warning": "Vietnamese language not supported by Adobe OCR"
                    }
                
                if not settings.USE_ADOBE_PDF_API:
                    return {
                        "engine": "adobe",
                        "available": False,
                        "reason": "Adobe PDF Services chưa được config. Set USE_ADOBE_PDF_API=true và thêm credentials vào .env",
                        "processing_time": 0
                    }
                
                start = time.time()
                
                # Check Adobe SDK availability
                try:
                    from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
                    from adobe.pdfservices.operation.pdf_services import PDFServices
                    from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
                    from adobe.pdfservices.operation.pdfjobs.jobs.export_pdf_job import ExportPDFJob
                    from adobe.pdfservices.operation.pdfjobs.params.export_pdf.export_pdf_params import ExportPDFParams
                    from adobe.pdfservices.operation.pdfjobs.params.export_pdf.export_pdf_target_format import ExportPDFTargetFormat
                    from adobe.pdfservices.operation.pdfjobs.params.export_pdf.export_ocr_locale import ExportOCRLocale
                    from adobe.pdfservices.operation.pdfjobs.result.export_pdf_result import ExportPDFResult
                    from adobe.pdfservices.operation.io.stream_asset import StreamAsset
                except ImportError as e:
                    return {
                        "engine": "adobe",
                        "available": False,
                        "error": f"Adobe SDK not installed: {e}. Run: pip install pdfservices-sdk",
                        "processing_time": 0
                    }
                
                # Convert image to PDF first
                import img2pdf
                pdf_path = temp_file.parent / f"{temp_file.stem}_adobe.pdf"
                
                with open(temp_file, "rb") as img_file:
                    pdf_bytes = img2pdf.convert(img_file.read())
                    with open(pdf_path, "wb") as pdf_file:
                        pdf_file.write(pdf_bytes)
                
                logger.info(f"Converted to PDF: {pdf_path}")
                
                # Initialize Adobe credentials
                credentials = ServicePrincipalCredentials(
                    client_id=settings.PDF_SERVICES_CLIENT_ID,
                    client_secret=settings.PDF_SERVICES_CLIENT_SECRET
                )
                
                pdf_services = PDFServices(credentials=credentials)
                
                # Upload PDF
                with open(pdf_path, 'rb') as f:
                    input_asset = pdf_services.upload(
                        input_stream=f,
                        mime_type=PDFServicesMediaType.PDF
                    )
                
                # Create export job (PDF → DOCX with embedded OCR)
                export_pdf_params = ExportPDFParams(
                    target_format=ExportPDFTargetFormat.DOCX
                )
                
                export_pdf_job = ExportPDFJob(
                    input_asset=input_asset,
                    export_pdf_params=export_pdf_params
                )
                
                # Execute job
                location = pdf_services.submit(export_pdf_job)
                pdf_services_response = pdf_services.get_job_result(
                    location,
                    ExportPDFResult
                )
                
                # Download result
                result_asset = pdf_services_response.get_result().get_asset()
                stream_asset = pdf_services.get_content(result_asset)
                
                # Save DOCX
                docx_path = temp_file.parent / f"{temp_file.stem}_adobe.docx"
                with open(docx_path, "wb") as f:
                    f.write(stream_asset.get_input_stream())
                
                # Extract text from DOCX
                from docx import Document
                doc = Document(docx_path)
                text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
                
                elapsed = time.time() - start
                
                # Cleanup temp files
                pdf_path.unlink(missing_ok=True)
                docx_path.unlink(missing_ok=True)
                
                return {
                    "engine": "adobe",
                    "available": True,
                    "text": text,
                    "confidence": 0.98,  # Adobe typically high quality
                    "char_count": len(text),
                    "word_count": len(text.split()),
                    "processing_time": round(elapsed, 2),
                    "success": True,
                    "note": "Adobe OCR không hỗ trợ tiếng Việt - kết quả có thể kém chính xác"
                }
                
            except Exception as e:
                logger.error(f"Adobe OCR error: {e}")
                return {
                    "engine": "adobe",
                    "available": False,
                    "error": str(e),
                    "processing_time": 0
                }
        tasks.append(("adobe", run_adobe()))
        
        # 2. Tesseract OCR
        async def run_tesseract():
            try:
                start = time.time()
                result = await ocr_service.extract_text(temp_file, languages=[language])
                elapsed = time.time() - start
                
                return {
                    "engine": "tesseract",
                    "available": True,
                    "text": result.get("text", ""),
                    "confidence": result.get("confidence", 0),
                    "char_count": len(result.get("text", "")),
                    "word_count": len(result.get("text", "").split()),
                    "processing_time": round(elapsed, 2),
                    "success": True,
                    "ocr_engine": result.get("ocr_engine", "tesseract")
                }
            except Exception as e:
                return {
                    "engine": "tesseract",
                    "available": False,
                    "error": str(e),
                    "processing_time": 0
                }
        tasks.append(("tesseract", run_tesseract()))
        
        # 3. Gemini Vision AI
        logger.info(f"Gemini check: use_gemini={document_service.use_gemini}, api_key_exists={bool(document_service.gemini_api_key)}")
        if document_service.use_gemini:
            async def run_gemini():
                try:
                    start = time.time()
                    
                    # Use PIL to load image for Gemini
                    from PIL import Image
                    image = Image.open(temp_file)
                    
                    # Gemini OCR prompt
                    prompt = f"""Trích xuất TOÀN BỘ văn bản trong ảnh này.

YÊU CẦU:
- Giữ chính xác 100% ký tự Tiếng Việt (ă, â, ê, ô, ơ, ư, đ, dấu thanh)
- Giữ nguyên cấu trúc, xuống dòng như trong ảnh
- Chỉ trả về văn bản, KHÔNG thêm giải thích, KHÔNG thêm markdown

Trả về văn bản:"""
                    
                    # Call Gemini API
                    response = document_service.gemini_model.generate_content([prompt, image])
                    text = response.text.strip()
                    
                    elapsed = time.time() - start
                    
                    # Extract usage metadata from response
                    usage_metadata = {
                        "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                        "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                        "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                    }
                    
                    # Log usage to database
                    try:
                        db = SessionLocal()
                        log_usage(
                            db=db,
                            provider="gemini",
                            model=document_service.gemini_model_name,
                            endpoint="ocr_compare",
                            input_tokens=usage_metadata["prompt_tokens"],
                            output_tokens=usage_metadata["completion_tokens"],
                            status="success",
                            processing_time=elapsed,
                            request_metadata={"language": language, "file_size": file.size}
                        )
                        db.close()
                    except Exception as log_err:
                        logger.warning(f"Failed to log Gemini usage: {log_err}")
                    
                    return {
                        "engine": "gemini",
                        "available": True,
                        "text": text,
                        "confidence": 0.95,  # Gemini doesn't provide confidence score
                        "char_count": len(text),
                        "word_count": len(text.split()),
                        "processing_time": round(elapsed, 2),
                        "success": True,
                        "model": document_service.gemini_model_name,
                        "usage": usage_metadata
                    }
                except Exception as e:
                    logger.error(f"Gemini OCR failed: {e}")
                    return {
                        "engine": "gemini",
                        "available": False,
                        "error": str(e),
                        "processing_time": 0
                    }
            tasks.append(("gemini", run_gemini()))
        
        # 4. Claude Vision AI
        async def run_claude():
            try:
                # Try to get API key from database first, fallback to settings
                db = SessionLocal()
                claude_api_key = get_api_key("claude", db)
                db.close()
                
                if not claude_api_key:
                    # Fallback to .env settings
                    if settings.USE_CLAUDE_API and settings.ANTHROPIC_API_KEY:
                        claude_api_key = settings.ANTHROPIC_API_KEY
                    else:
                        return {
                            "engine": "claude",
                            "available": False,
                            "reason": "Claude API chưa được config. Thêm API key trong Admin hoặc set USE_CLAUDE_API=true và ANTHROPIC_API_KEY vào .env",
                            "processing_time": 0
                        }
                
                start = time.time()
                
                # Check Anthropic SDK
                try:
                    import anthropic
                    import base64
                except ImportError as e:
                    return {
                        "engine": "claude",
                        "available": False,
                        "error": f"Anthropic SDK not installed: {e}. Run: pip install anthropic",
                        "processing_time": 0
                    }
                
                # Read and encode image
                with open(temp_file, "rb") as img_file:
                    image_data = base64.standard_b64encode(img_file.read()).decode("utf-8")
                
                # Detect media type
                import mimetypes
                media_type = mimetypes.guess_type(str(temp_file))[0] or "image/png"
                
                # Initialize Claude client
                client = anthropic.Anthropic(api_key=claude_api_key)
                
                # Claude OCR prompt
                prompt = """Trích xuất TOÀN BỘ văn bản trong ảnh này.

YÊU CẦU:
- Giữ chính xác 100% ký tự Tiếng Việt (ă, â, ê, ô, ơ, ư, đ, dấu thanh)
- Giữ nguyên cấu trúc, xuống dòng như trong ảnh
- Chỉ trả về văn bản, KHÔNG thêm giải thích, KHÔNG thêm markdown

Trả về văn bản:"""
                
                # Call Claude API
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1024,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": image_data,
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ],
                        }
                    ],
                )
                
                text = message.content[0].text.strip()
                elapsed = time.time() - start
                
                # Extract usage from Claude response
                usage_metadata = {
                    "input_tokens": message.usage.input_tokens if hasattr(message, 'usage') else 0,
                    "output_tokens": message.usage.output_tokens if hasattr(message, 'usage') else 0,
                    "total_tokens": (message.usage.input_tokens + message.usage.output_tokens) if hasattr(message, 'usage') else 0,
                }
                
                # Log usage to database
                try:
                    db = SessionLocal()
                    log_usage(
                        db=db,
                        provider="claude",
                        model="claude-sonnet-4-20250514",
                        endpoint="ocr_compare",
                        input_tokens=usage_metadata["input_tokens"],
                        output_tokens=usage_metadata["output_tokens"],
                        status="success",
                        processing_time=elapsed,
                        request_metadata={"language": language, "file_size": file.size}
                    )
                    db.close()
                except Exception as log_err:
                    logger.warning(f"Failed to log Claude usage: {log_err}")
                
                return {
                    "engine": "claude",
                    "available": True,
                    "text": text,
                    "confidence": 0.97,
                    "char_count": len(text),
                    "word_count": len(text.split()),
                    "processing_time": round(elapsed, 2),
                    "success": True,
                    "model": "claude-sonnet-4-20250514",
                    "usage": usage_metadata
                }
                
            except Exception as e:
                logger.error(f"Claude OCR error: {e}")
                return {
                    "engine": "claude",
                    "available": False,
                    "error": str(e),
                    "processing_time": 0
                }
        tasks.append(("claude", run_claude()))
        
        # Execute all tasks
        for engine_name, task in tasks:
            result = await task
            results["engines"][engine_name] = result
        
        # Calculate comparison metrics
        available_engines = [
            name for name, data in results["engines"].items() 
            if data.get("available", False) and data.get("success", False)
        ]
        
        if len(available_engines) >= 2:
            lengths = {name: results["engines"][name].get("char_count", 0) for name in available_engines}
            times = {name: results["engines"][name].get("processing_time", 0) for name in available_engines}
            
            fastest = min(times, key=times.get) if times else None
            most_detailed = max(lengths, key=lengths.get) if lengths else None
            
            results["comparison"] = {
                "available_engines": available_engines,
                "fastest_engine": fastest,
                "fastest_time": times.get(fastest, 0) if fastest else 0,
                "most_detailed_engine": most_detailed,
                "most_text": lengths.get(most_detailed, 0) if most_detailed else 0,
                "char_counts": lengths,
                "processing_times": times
            }
        else:
            results["comparison"] = {
                "available_engines": available_engines,
                "note": "Need at least 2 engines to compare"
            }
        
        # Cleanup
        try:
            temp_file.unlink()
        except:
            pass
        
        logger.info(f"✅ OCR comparison complete: {len(available_engines)} engines")
        return results
        
    except Exception as e:
        logger.error(f"❌ OCR comparison failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/smart-ocr")
async def smart_ocr(file: UploadFile = File(...), language: str = "vi"):
    """Smart OCR with Gemini - Coming soon"""
    try:
        if not document_service.use_gemini:
            raise HTTPException(status_code=400, detail="Gemini API not configured")
        
        return {
            "status": "coming_soon",
            "message": "Smart OCR with Gemini Vision under development",
            "gemini_model": document_service.gemini_model_name
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify-document")
async def classify_document(file: UploadFile = File(...)):
    """Document classification with Gemini - Coming soon"""
    try:
        if not document_service.use_gemini:
            raise HTTPException(status_code=400, detail="Gemini API not configured")
        
        return {
            "status": "coming_soon",
            "message": "Document classification with Gemini under development",
            "gemini_model": document_service.gemini_model_name
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-data")
async def extract_structured_data(file: UploadFile = File(...), document_type: str = "AUTO"):
    """Structured data extraction with Gemini - Coming soon"""
    try:
        if not document_service.use_gemini:
            raise HTTPException(status_code=400, detail="Gemini API not configured")
        
        return {
            "status": "coming_soon",
            "message": "Data extraction with Gemini under development",
            "document_type": document_type,
            "gemini_model": document_service.gemini_model_name
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
