"""
Modern Document Conversion API Endpoints (2025)
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Optional
from pathlib import Path
import zipfile
import io
import asyncio

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
                output_path = await doc_service.compress_pdf(input_path, quality)
                output_files.append(output_path)
                await doc_service.cleanup_file(input_path)
                print(f"[Batch Compress PDF] ✓ Success: {file.filename} → {output_path.name}")
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


