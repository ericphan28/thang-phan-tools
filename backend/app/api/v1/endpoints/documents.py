"""
Modern Document Conversion API Endpoints (2025)
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import List, Optional
from pathlib import Path

from app.services.document_service import DocumentService

router = APIRouter(tags=["Document Conversion"])

# Initialize service
doc_service = DocumentService()


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
        
        # Return file
        return FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=output_path.name,
            background=None  # Don't delete file yet
        )
        
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
):
    """
    Convert PDF to Word document
    
    - Uses **pdf2docx** (pure Python, cross-platform)
    - Can convert specific page ranges
    - Preserves formatting, images, tables
    """
    # Save uploaded file
    input_path = await doc_service.save_upload_file(file)
    
    try:
        # Convert
        output_path = await doc_service.pdf_to_word(
            input_path,
            start_page=start_page,
            end_page=end_page
        )
        
        # Return file
        return FileResponse(
            path=output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=output_path.name
        )
        
    except Exception as e:
        await doc_service.cleanup_file(input_path)
        raise e


@router.post("/convert/pdf-to-excel")
async def convert_pdf_to_excel(
    file: UploadFile = File(..., description="PDF file with tables"),
):
    """
    Convert PDF to Excel (.xlsx)
    
    - Extracts **tables** from PDF using pdfplumber
    - Creates separate sheets for each page with tables
    - Auto-formats with headers, column widths
    - Falls back to text extraction if no tables found
    """
    # Save uploaded file
    input_path = await doc_service.save_upload_file(file)
    
    try:
        # Convert
        output_path = await doc_service.pdf_to_excel(input_path)
        
        # Return file
        return FileResponse(
            path=output_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=output_path.name
        )
        
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


@router.post("/pdf/split")
async def split_pdf(
    file: UploadFile = File(..., description="PDF file"),
    page_ranges: str = Form(..., description="Page ranges, e.g., '1-3,5-7,10'"),
    output_prefix: str = Form("split", description="Output files prefix"),
):
    """
    Split PDF into multiple files by page ranges
    
    **Examples:**
    - `page_ranges="1-3,5-7"` → Creates 2 files (pages 1-3, pages 5-7)
    - `page_ranges="1,3,5"` → Creates 3 files (page 1, page 3, page 5)
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
        # Split
        output_paths = await doc_service.split_pdf(input_path, ranges, output_prefix)
        
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
    Compress PDF file to reduce size
    
    - **quality**: 
      - low = ebook quality (72dpi, smallest file)
      - medium = balanced (150dpi, recommended)
      - high = prepress quality (300dpi, larger file)
    
    Returns compressed PDF file
    """
    input_path = await doc_service.save_upload_file(file)
    
    try:
        # Get original size
        original_size = input_path.stat().st_size
        
        # Compress
        output_path = await doc_service.compress_pdf(input_path, quality)
        
        # Get compressed size
        compressed_size = output_path.stat().st_size
        compression_ratio = ((original_size - compressed_size) / original_size * 100)
        
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_path.name,
            headers={
                "X-Original-Size": str(original_size),
                "X-Compressed-Size": str(compressed_size),
                "X-Compression-Ratio": f"{compression_ratio:.1f}%"
            }
        )
        
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


@router.post("/pdf/watermark")
async def add_watermark(
    file: UploadFile = File(..., description="PDF file"),
    watermark_text: str = Form(..., description="Watermark text"),
    position: str = Form("center", description="Position: center, top-left, top-right, bottom-left, bottom-right"),
    opacity: float = Form(0.3, description="Opacity (0.0 to 1.0)"),
):
    """
    Add text watermark to PDF
    
    - **watermark_text**: Text to display as watermark
    - **position**: Where to place watermark
    - **opacity**: Transparency level (0.0 = transparent, 1.0 = opaque)
    """
    input_path = await doc_service.save_upload_file(file)
    
    try:
        output_path = await doc_service.add_watermark_to_pdf(
            input_path, watermark_text, position, opacity
        )
        
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=output_path.name
        )
        
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
