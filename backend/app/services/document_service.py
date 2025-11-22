"""
Modern Document Conversion Service (2025)
Sử dụng các công nghệ mới nhất để convert documents
Tích hợp Adobe PDF Services API cho PDF → Word chất lượng cao
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List
import aiofiles
import httpx
from fastapi import UploadFile, HTTPException
import logging

# Document libraries
from docx import Document
import pypdf
from pdf2docx import Converter as PDFToWordConverter
from pptx import Presentation
from openpyxl import load_workbook
import pypdfium2 as pdfium

# Adobe PDF Services (optional)
try:
    from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
    from adobe.pdfservices.operation.pdf_services import PDFServices
    from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
    from adobe.pdfservices.operation.pdfjobs.jobs.export_pdf_job import ExportPDFJob
    from adobe.pdfservices.operation.pdfjobs.params.export_pdf.export_pdf_params import ExportPDFParams
    from adobe.pdfservices.operation.pdfjobs.params.export_pdf.export_pdf_target_format import ExportPDFTargetFormat
    from adobe.pdfservices.operation.pdfjobs.result.export_pdf_result import ExportPDFResult
    from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
    from adobe.pdfservices.operation.io.stream_asset import StreamAsset
    ADOBE_AVAILABLE = True
except ImportError:
    ADOBE_AVAILABLE = False

logger = logging.getLogger(__name__)


class DocumentService:
    """Modern document processing service sử dụng Gotenberg + Adobe PDF Services"""
    
    def __init__(
        self, 
        upload_dir: str = "uploads/documents",
        gotenberg_url: str = None
    ):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Output directories
        self.output_dir = Path("uploads/outputs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Gotenberg URL - auto-detect environment
        if gotenberg_url:
            self.gotenberg_url = gotenberg_url
        else:
            # Production: Gotenberg container, Dev: có thể dùng local LibreOffice
            self.gotenberg_url = os.getenv("GOTENBERG_URL", "http://gotenberg:3000")
        
        # Adobe PDF Services - optional but recommended for better quality
        self.use_adobe = os.getenv("USE_ADOBE_PDF_API", "false").lower() == "true"
        self.adobe_credentials = None
        
        if self.use_adobe and ADOBE_AVAILABLE:
            client_id = os.getenv("PDF_SERVICES_CLIENT_ID")
            client_secret = os.getenv("PDF_SERVICES_CLIENT_SECRET")
            
            if client_id and client_secret:
                try:
                    self.adobe_credentials = ServicePrincipalCredentials(
                        client_id=client_id,
                        client_secret=client_secret
                    )
                    logger.info("Adobe PDF Services enabled - High quality PDF to Word conversion available")
                except Exception as e:
                    logger.warning(f"Failed to initialize Adobe credentials: {e}")
                    self.use_adobe = False
            else:
                logger.warning("USE_ADOBE_PDF_API=true but credentials not found in env")
                self.use_adobe = False
        elif self.use_adobe and not ADOBE_AVAILABLE:
            logger.warning("USE_ADOBE_PDF_API=true but pdfservices-sdk not installed")
            self.use_adobe = False
        
    async def save_upload_file(self, upload_file: UploadFile) -> Path:
        """Save uploaded file async"""
        file_path = self.upload_dir / upload_file.filename
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await upload_file.read()
            await out_file.write(content)
            
        return file_path
    
    # ==================== Word → PDF (Gotenberg) ====================
    
    async def word_to_pdf(
        self,
        input_file: Path,
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Convert Word (.docx/.doc) sang PDF bằng Gotenberg API
        
        Gotenberg là Docker microservice hiện đại, sử dụng LibreOffice headless
        - Không cần cài LibreOffice trên host machine
        - REST API đơn giản, nhanh, ổn định
        - Support: DOC, DOCX, XLS, XLSX, PPT, PPTX, ODT...
        """
        if not input_file.suffix.lower() in ['.docx', '.doc']:
            raise HTTPException(400, "File phải là .docx hoặc .doc")
        
        output_filename = output_filename or input_file.stem + ".pdf"
        output_path = self.output_dir / output_filename
        
        try:
            # Gọi Gotenberg API để convert
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Đọc file Word
                async with aiofiles.open(input_file, 'rb') as f:
                    file_content = await f.read()
                
                # POST đến Gotenberg LibreOffice endpoint
                files = {
                    'files': (input_file.name, file_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                }
                
                response = await client.post(
                    f"{self.gotenberg_url}/forms/libreoffice/convert",
                    files=files
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        500,
                        f"Gotenberg conversion failed: {response.status_code} - {response.text}"
                    )
                
                # Lưu PDF output
                async with aiofiles.open(output_path, 'wb') as f:
                    await f.write(response.content)
                
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise HTTPException(500, "File PDF không được tạo ra hoặc rỗng")
                
            return output_path
            
        except httpx.ConnectError:
            # Gotenberg không khả dụng - fallback to LibreOffice local (dev only)
            return await self._word_to_pdf_libreoffice_fallback(input_file, output_filename)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Lỗi chuyển đổi Word sang PDF: {str(e)}")
    
    async def _word_to_pdf_libreoffice_fallback(
        self,
        input_file: Path,
        output_filename: str
    ) -> Path:
        """
        Fallback method: Dùng LibreOffice local nếu Gotenberg không có
        (Chỉ dùng cho development/testing)
        """
        output_path = self.output_dir / output_filename
        
        # Tìm LibreOffice
        libreoffice_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            "/usr/bin/libreoffice",
            "/usr/bin/soffice",
            "soffice",
        ]
        
        soffice_path = None
        for path in libreoffice_paths:
            if os.path.exists(path) or path == "soffice":
                soffice_path = path
                break
        
        if not soffice_path:
            raise HTTPException(
                503,
                "Gotenberg service không khả dụng và LibreOffice chưa được cài đặt. "
                "Vui lòng đảm bảo Gotenberg container đang chạy."
            )
        
        try:
            cmd = [
                soffice_path,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", str(self.output_dir),
                str(input_file)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                raise HTTPException(500, f"LibreOffice conversion failed: {result.stderr}")
            
            generated_pdf = self.output_dir / (input_file.stem + ".pdf")
            if generated_pdf != output_path:
                generated_pdf.rename(output_path)
            
            return output_path
            
        except subprocess.TimeoutExpired:
            raise HTTPException(500, "Conversion timeout")
        except Exception as e:
            raise HTTPException(500, f"Fallback conversion failed: {str(e)}")
    
    # ==================== Generic Office → PDF (Excel, PowerPoint) ====================
    
    async def office_to_pdf(
        self,
        input_file: Path,
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Convert any Office file (Excel, PowerPoint) to PDF using Gotenberg
        
        Supports: .xlsx, .xls, .pptx, .ppt, .odt, .ods, .odp
        """
        supported_extensions = ['.xlsx', '.xls', '.pptx', '.ppt', '.odt', '.ods', '.odp']
        if input_file.suffix.lower() not in supported_extensions:
            raise HTTPException(400, f"File phải là Office file: {', '.join(supported_extensions)}")
        
        output_filename = output_filename or input_file.stem + ".pdf"
        output_path = self.output_dir / output_filename
        
        try:
            # Gọi Gotenberg API
            async with httpx.AsyncClient(timeout=120.0) as client:  # Excel/PPT có thể mất thời gian hơn
                async with aiofiles.open(input_file, 'rb') as f:
                    file_content = await f.read()
                
                # Determine MIME type
                mime_types = {
                    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    '.xls': 'application/vnd.ms-excel',
                    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    '.ppt': 'application/vnd.ms-powerpoint',
                    '.odt': 'application/vnd.oasis.opendocument.text',
                    '.ods': 'application/vnd.oasis.opendocument.spreadsheet',
                    '.odp': 'application/vnd.oasis.opendocument.presentation'
                }
                mime_type = mime_types.get(input_file.suffix.lower(), 'application/octet-stream')
                
                files = {
                    'files': (input_file.name, file_content, mime_type)
                }
                
                response = await client.post(
                    f"{self.gotenberg_url}/forms/libreoffice/convert",
                    files=files
                )
                
                if response.status_code != 200:
                    raise HTTPException(500, f"Gotenberg conversion failed: {response.status_code}")
                
                async with aiofiles.open(output_path, 'wb') as f:
                    await f.write(response.content)
                
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise HTTPException(500, "File PDF không được tạo ra hoặc rỗng")
                
            return output_path
            
        except httpx.ConnectError:
            # Fallback to LibreOffice local
            return await self._office_to_pdf_libreoffice_fallback(input_file, output_filename)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Lỗi chuyển đổi Office sang PDF: {str(e)}")
    
    async def _office_to_pdf_libreoffice_fallback(
        self,
        input_file: Path,
        output_filename: str
    ) -> Path:
        """Fallback: Use LibreOffice for Office files"""
        return await self._word_to_pdf_libreoffice_fallback(input_file, output_filename)

    # ==================== PDF → Word ====================
    
    async def pdf_to_word(
        self,
        input_file: Path,
        output_filename: Optional[str] = None,
        start_page: int = 0,
        end_page: Optional[int] = None
    ) -> Path:
        """
        Convert PDF to Word (.docx)
        
        Strategy:
        1. Try Adobe PDF Services (if enabled) - Best quality
        2. Fallback to pdf2docx - Good quality, free
        """
        if input_file.suffix.lower() != '.pdf':
            raise HTTPException(400, "File must be .pdf")
        
        output_filename = output_filename or input_file.stem + ".docx"
        output_path = self.output_dir / output_filename
        
        # Try Adobe first if enabled (best quality)
        if self.use_adobe and self.adobe_credentials:
            try:
                logger.info(f"Using Adobe PDF Services for {input_file.name}")
                return await self._pdf_to_word_adobe(input_file, output_path)
            except Exception as e:
                logger.warning(f"Adobe PDF conversion failed: {e}, falling back to pdf2docx")
        
        # Fallback to pdf2docx (good quality, free)
        logger.info(f"Using pdf2docx for {input_file.name}")
        return await self._pdf_to_word_local(input_file, output_path, start_page, end_page)
    
    async def _pdf_to_word_adobe(self, input_file: Path, output_path: Path) -> Path:
        """
        Convert PDF to Word using Adobe PDF Services API
        High quality conversion with AI-powered layout preservation
        """
        try:
            # Read input file
            async with aiofiles.open(input_file, 'rb') as f:
                input_stream = await f.read()
            
            # Create PDF Services instance
            pdf_services = PDFServices(credentials=self.adobe_credentials)
            
            # Upload file to Adobe
            input_asset = pdf_services.upload(
                input_stream=input_stream,
                mime_type=PDFServicesMediaType.PDF
            )
            
            # Create export parameters
            export_pdf_params = ExportPDFParams(
                target_format=ExportPDFTargetFormat.DOCX
            )
            
            # Create and submit job
            export_pdf_job = ExportPDFJob(
                input_asset=input_asset,
                export_pdf_params=export_pdf_params
            )
            
            location = pdf_services.submit(export_pdf_job)
            
            # Get result (polling handled by SDK)
            pdf_services_response = pdf_services.get_job_result(location, ExportPDFResult)
            
            # Download result
            result_asset: CloudAsset = pdf_services_response.get_result().get_asset()
            stream_asset: StreamAsset = pdf_services.get_content(result_asset)
            
            # Save to file
            async with aiofiles.open(output_path, "wb") as f:
                await f.write(stream_asset.get_input_stream())
            
            logger.info(f"Adobe conversion successful: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Adobe PDF Services error: {e}")
            raise
    
    async def _pdf_to_word_local(
        self,
        input_file: Path,
        output_path: Path,
        start_page: int = 0,
        end_page: Optional[int] = None
    ) -> Path:
        """
        Convert PDF to Word using pdf2docx (fallback)
        Good quality, pure Python, free
        """
        try:
            # pdf2docx is pure Python, works cross-platform
            cv = PDFToWordConverter(str(input_file))
            cv.convert(str(output_path), start=start_page, end=end_page)
            cv.close()
            
            logger.info(f"pdf2docx conversion successful: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"pdf2docx conversion error: {e}")
            raise HTTPException(500, f"PDF to Word conversion failed: {str(e)}")
    
    async def pdf_to_excel(
        self,
        input_file: Path,
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Convert PDF to Excel (.xlsx)
        Extracts tables from PDF using pdfplumber
        """
        if input_file.suffix.lower() != '.pdf':
            raise HTTPException(400, "File must be .pdf")
        
        output_filename = output_filename or input_file.stem + ".xlsx"
        output_path = self.output_dir / output_filename
        
        try:
            import pdfplumber
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
            
            # Create Excel workbook
            wb = Workbook()
            wb.remove(wb.active)  # Remove default sheet
            
            # Open PDF
            with pdfplumber.open(input_file) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    # Extract tables from page
                    tables = page.extract_tables()
                    
                    if tables:
                        # Create sheet for each page with tables
                        ws = wb.create_sheet(title=f"Page {page_num}")
                        
                        # Write all tables from this page
                        current_row = 1
                        for table_num, table in enumerate(tables, start=1):
                            # Add table header
                            if len(tables) > 1:
                                header_cell = ws.cell(row=current_row, column=1, value=f"Table {table_num}")
                                header_cell.font = Font(bold=True, size=12)
                                header_cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
                                current_row += 1
                            
                            # Write table data
                            for row_data in table:
                                for col_num, cell_value in enumerate(row_data, start=1):
                                    cell = ws.cell(row=current_row, column=col_num, value=cell_value)
                                    cell.alignment = Alignment(wrap_text=True, vertical='top')
                                    
                                    # Bold first row (header)
                                    if current_row == 1 or (len(tables) > 1 and current_row == 2):
                                        cell.font = Font(bold=True)
                                        cell.fill = PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid")
                                
                                current_row += 1
                            
                            # Add spacing between tables
                            current_row += 1
                        
                        # Auto-adjust column widths
                        for column in ws.columns:
                            max_length = 0
                            column_letter = column[0].column_letter
                            for cell in column:
                                try:
                                    if cell.value:
                                        max_length = max(max_length, len(str(cell.value)))
                                except:
                                    pass
                            adjusted_width = min(max_length + 2, 50)
                            ws.column_dimensions[column_letter].width = adjusted_width
                    else:
                        # No tables found, extract text
                        text = page.extract_text()
                        if text and text.strip():
                            ws = wb.create_sheet(title=f"Page {page_num} (Text)")
                            ws.cell(row=1, column=1, value=text)
                            ws.column_dimensions['A'].width = 100
            
            # If no content was extracted at all
            if len(wb.sheetnames) == 0:
                ws = wb.create_sheet(title="No Data")
                ws.cell(row=1, column=1, value="No tables or text found in PDF")
            
            # Save workbook
            wb.save(output_path)
            
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"PDF to Excel conversion failed: {str(e)}")
    
    # ==================== PDF Operations ====================
    
    async def merge_pdfs(
        self,
        input_files: List[Path],
        output_filename: str = "merged.pdf"
    ) -> Path:
        """Merge multiple PDFs into one (using modern pypdf)"""
        output_path = self.output_dir / output_filename
        
        try:
            merger = pypdf.PdfWriter()
            
            for pdf_file in input_files:
                if pdf_file.suffix.lower() != '.pdf':
                    continue
                    
                with open(pdf_file, 'rb') as f:
                    pdf_reader = pypdf.PdfReader(f)
                    for page in pdf_reader.pages:
                        merger.add_page(page)
            
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
                
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"PDF merge failed: {str(e)}")
    
    async def split_pdf(
        self,
        input_file: Path,
        page_ranges: List[tuple],  # [(1,3), (5,7)] means pages 1-3 and 5-7
        output_prefix: str = "split"
    ) -> List[Path]:
        """Split PDF into multiple files by page ranges"""
        if input_file.suffix.lower() != '.pdf':
            raise HTTPException(400, "File must be .pdf")
        
        try:
            output_files = []
            
            with open(input_file, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                
                for idx, (start, end) in enumerate(page_ranges):
                    pdf_writer = pypdf.PdfWriter()
                    
                    for page_num in range(start - 1, end):  # Convert to 0-indexed
                        if page_num < len(pdf_reader.pages):
                            pdf_writer.add_page(pdf_reader.pages[page_num])
                    
                    output_path = self.output_dir / f"{output_prefix}_{idx+1}.pdf"
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)
                    
                    output_files.append(output_path)
                    
            return output_files
            
        except Exception as e:
            raise HTTPException(500, f"PDF split failed: {str(e)}")
    
    async def extract_pdf_text(self, input_file: Path) -> str:
        """Extract all text from PDF"""
        if input_file.suffix.lower() != '.pdf':
            raise HTTPException(400, "File must be .pdf")
        
        try:
            with open(input_file, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n\n"
                    
            return text.strip()
            
        except Exception as e:
            raise HTTPException(500, f"PDF text extraction failed: {str(e)}")
    
    async def rotate_pdf_pages(
        self,
        input_file: Path,
        rotation: int = 90,  # 90, 180, 270
        pages: Optional[List[int]] = None,  # None = all pages
        output_filename: Optional[str] = None
    ) -> Path:
        """Rotate PDF pages"""
        if input_file.suffix.lower() != '.pdf':
            raise HTTPException(400, "File must be .pdf")
        
        if rotation not in [90, 180, 270, -90]:
            raise HTTPException(400, "Rotation must be 90, 180, or 270 degrees")
        
        output_filename = output_filename or input_file.stem + "_rotated.pdf"
        output_path = self.output_dir / output_filename
        
        try:
            with open(input_file, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                pdf_writer = pypdf.PdfWriter()
                
                for page_num, page in enumerate(pdf_reader.pages):
                    if pages is None or (page_num + 1) in pages:
                        page.rotate(rotation)
                    pdf_writer.add_page(page)
                
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                    
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"PDF rotation failed: {str(e)}")
    
    # ==================== PDF Info ====================
    
    async def get_pdf_info(self, input_file: Path) -> dict:
        """Get PDF metadata and information"""
        if input_file.suffix.lower() != '.pdf':
            raise HTTPException(400, "File must be .pdf")
        
        try:
            with open(input_file, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                
                info = {
                    "num_pages": len(pdf_reader.pages),
                    "metadata": pdf_reader.metadata.__dict__ if pdf_reader.metadata else {},
                    "is_encrypted": pdf_reader.is_encrypted,
                    "page_sizes": []
                }
                
                # Get page sizes
                for page in pdf_reader.pages[:5]:  # First 5 pages
                    box = page.mediabox
                    info["page_sizes"].append({
                        "width": float(box.width),
                        "height": float(box.height)
                    })
                    
            return info
            
        except Exception as e:
            raise HTTPException(500, f"PDF info extraction failed: {str(e)}")
    
    # ==================== Word Operations ====================
    
    async def get_word_info(self, input_file: Path) -> dict:
        """Get Word document information"""
        if input_file.suffix.lower() != '.docx':
            raise HTTPException(400, "File must be .docx")
        
        try:
            doc = Document(str(input_file))
            
            info = {
                "num_paragraphs": len(doc.paragraphs),
                "num_tables": len(doc.tables),
                "num_images": len([r for p in doc.paragraphs for r in p.runs if r._element.xml.find('pic') > 0]),
                "word_count": sum(len(p.text.split()) for p in doc.paragraphs),
                "char_count": sum(len(p.text) for p in doc.paragraphs),
            }
            
            return info
            
        except Exception as e:
            raise HTTPException(500, f"Word info extraction failed: {str(e)}")
    
    # ==================== Excel Operations ====================
    
    async def get_excel_info(self, input_file: Path) -> dict:
        """Get Excel workbook information"""
        if input_file.suffix.lower() not in ['.xlsx', '.xlsm']:
            raise HTTPException(400, "File must be .xlsx or .xlsm")
        
        try:
            wb = load_workbook(str(input_file), read_only=True)
            
            info = {
                "num_sheets": len(wb.sheetnames),
                "sheet_names": wb.sheetnames,
                "active_sheet": wb.active.title,
            }
            
            wb.close()
            return info
            
        except Exception as e:
            raise HTTPException(500, f"Excel info extraction failed: {str(e)}")
    
    # ==================== PowerPoint Operations ====================
    
    async def get_powerpoint_info(self, input_file: Path) -> dict:
        """Get PowerPoint presentation information"""
        if input_file.suffix.lower() not in ['.pptx']:
            raise HTTPException(400, "File must be .pptx")
        
        try:
            prs = Presentation(str(input_file))
            
            info = {
                "num_slides": len(prs.slides),
                "slide_width": prs.slide_width,
                "slide_height": prs.slide_height,
            }
            
            return info
            
        except Exception as e:
            raise HTTPException(500, f"PowerPoint info extraction failed: {str(e)}")
    
    # ==================== Cleanup ====================
    
    # ==================== PDF Compression ====================
    
    async def compress_pdf(
        self,
        input_file: Path,
        quality: str = "medium",  # low, medium, high
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Compress PDF using Ghostscript settings
        quality: low = ebook (72dpi), medium = default (150dpi), high = prepress (300dpi)
        """
        if input_file.suffix.lower() != '.pdf':
            raise HTTPException(400, "File must be .pdf")
        
        output_filename = output_filename or input_file.stem + "_compressed.pdf"
        output_path = self.output_dir / output_filename
        
        # Quality settings for pypdf compression
        quality_map = {
            "low": 4,      # More compression
            "medium": 2,   # Balanced
            "high": 0      # Less compression
        }
        
        compression_level = quality_map.get(quality, 2)
        
        try:
            with open(input_file, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                pdf_writer = pypdf.PdfWriter()
                
                # Copy all pages
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
                
                # Compress images
                for page in pdf_writer.pages:
                    page.compress_content_streams(level=compression_level)
                
                # Write compressed PDF
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                    
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"PDF compression failed: {str(e)}")
    
    # ==================== Image to PDF ====================
    
    async def image_to_pdf(
        self,
        input_file: Path,
        output_filename: Optional[str] = None
    ) -> Path:
        """Convert image (JPG, PNG, etc.) to PDF"""
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic']
        
        if input_file.suffix.lower() not in allowed_extensions:
            raise HTTPException(400, f"File must be one of: {', '.join(allowed_extensions)}")
        
        output_filename = output_filename or input_file.stem + ".pdf"
        output_path = self.output_dir / output_filename
        
        try:
            # Use Pillow to convert image to PDF
            from PIL import Image
            
            # Open and convert image
            img = Image.open(input_file)
            
            # Convert RGBA to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save as PDF
            img.save(output_path, 'PDF', resolution=100.0, quality=95)
            
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"Image to PDF conversion failed: {str(e)}")
    
    # ==================== PDF Watermark ====================
    
    async def add_watermark_to_pdf(
        self,
        input_file: Path,
        watermark_text: str,
        position: str = "center",  # center, top-left, top-right, bottom-left, bottom-right
        opacity: float = 0.3,
        output_filename: Optional[str] = None
    ) -> Path:
        """Add text watermark to PDF"""
        if input_file.suffix.lower() != '.pdf':
            raise HTTPException(400, "File must be .pdf")
        
        output_filename = output_filename or input_file.stem + "_watermarked.pdf"
        output_path = self.output_dir / output_filename
        
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.colors import Color
            import io
            
            # Read input PDF
            with open(input_file, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                pdf_writer = pypdf.PdfWriter()
                
                # Create watermark
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                
                # Position mapping
                positions = {
                    'center': (300, 400),
                    'top-left': (50, 750),
                    'top-right': (450, 750),
                    'bottom-left': (50, 50),
                    'bottom-right': (450, 50)
                }
                x, y = positions.get(position, (300, 400))
                
                # Set watermark properties
                can.setFillColor(Color(0, 0, 0, alpha=opacity))
                can.setFont("Helvetica", 40)
                can.drawString(x, y, watermark_text)
                can.save()
                
                # Move to beginning of BytesIO
                packet.seek(0)
                watermark_pdf = pypdf.PdfReader(packet)
                watermark_page = watermark_pdf.pages[0]
                
                # Apply watermark to all pages
                for page in pdf_reader.pages:
                    page.merge_page(watermark_page)
                    pdf_writer.add_page(page)
                
                # Write output
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                    
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"Add watermark failed: {str(e)}")
    
    # ==================== PDF Password Protection ====================
    
    async def protect_pdf_with_password(
        self,
        input_file: Path,
        user_password: str,
        owner_password: Optional[str] = None,
        output_filename: Optional[str] = None
    ) -> Path:
        """Protect PDF with password"""
        if input_file.suffix.lower() != '.pdf':
            raise HTTPException(400, "File must be .pdf")
        
        output_filename = output_filename or input_file.stem + "_protected.pdf"
        output_path = self.output_dir / output_filename
        
        if not owner_password:
            owner_password = user_password + "_owner"
        
        try:
            with open(input_file, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                pdf_writer = pypdf.PdfWriter()
                
                # Copy all pages
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
                
                # Encrypt with password
                pdf_writer.encrypt(
                    user_password=user_password,
                    owner_password=owner_password,
                    permissions_flag=0b0100  # Allow printing
                )
                
                # Write encrypted PDF
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                    
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"PDF password protection failed: {str(e)}")
    
    async def unlock_pdf(
        self,
        input_file: Path,
        password: str,
        output_filename: Optional[str] = None
    ) -> Path:
        """Remove password from PDF"""
        if input_file.suffix.lower() != '.pdf':
            raise HTTPException(400, "File must be .pdf")
        
        output_filename = output_filename or input_file.stem + "_unlocked.pdf"
        output_path = self.output_dir / output_filename
        
        try:
            with open(input_file, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                
                # Check if encrypted
                if not pdf_reader.is_encrypted:
                    raise HTTPException(400, "PDF is not encrypted")
                
                # Decrypt
                if not pdf_reader.decrypt(password):
                    raise HTTPException(401, "Incorrect password")
                
                pdf_writer = pypdf.PdfWriter()
                
                # Copy all pages (now decrypted)
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
                
                # Write unencrypted PDF
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                    
            return output_path
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"PDF unlock failed: {str(e)}")
    
    # ==================== PDF to Images ====================
    
    async def pdf_to_images(
        self,
        input_file: Path,
        format: str = "png",  # png, jpg
        dpi: int = 200,
        output_prefix: str = "page"
    ) -> List[Path]:
        """Convert PDF pages to images using pdf2image"""
        if input_file.suffix.lower() != '.pdf':
            raise HTTPException(400, "File must be .pdf")
        
        try:
            from pdf2image import convert_from_path
            
            output_files = []
            
            # Convert PDF to images
            images = convert_from_path(input_file, dpi=dpi)
            
            # Save each page
            for page_num, image in enumerate(images, start=1):
                output_filename = f"{output_prefix}_{page_num}.{format}"
                output_path = self.output_dir / output_filename
                image.save(output_path, format.upper())
                output_files.append(output_path)
            
            return output_files
            
        except Exception as e:
            raise HTTPException(500, f"PDF to images conversion failed: {str(e)}")
    
    # ==================== Add Page Numbers ====================
    
    async def add_page_numbers(
        self,
        input_file: Path,
        position: str = "bottom-center",  # bottom-center, bottom-right, bottom-left
        format: str = "Page {page}",  # {page}, {page} of {total}, etc.
        output_filename: Optional[str] = None
    ) -> Path:
        """Add page numbers to PDF"""
        if input_file.suffix.lower() != '.pdf':
            raise HTTPException(400, "File must be .pdf")
        
        output_filename = output_filename or input_file.stem + "_numbered.pdf"
        output_path = self.output_dir / output_filename
        
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            import io
            
            with open(input_file, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                pdf_writer = pypdf.PdfWriter()
                total_pages = len(pdf_reader.pages)
                
                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    # Create page number overlay
                    packet = io.BytesIO()
                    can = canvas.Canvas(packet, pagesize=letter)
                    
                    # Position mapping
                    positions = {
                        'bottom-center': (300, 30),
                        'bottom-right': (520, 30),
                        'bottom-left': (80, 30)
                    }
                    x, y = positions.get(position, (300, 30))
                    
                    # Format page number text
                    page_text = format.replace('{page}', str(page_num))
                    page_text = page_text.replace('{total}', str(total_pages))
                    
                    can.setFont("Helvetica", 10)
                    can.drawString(x, y, page_text)
                    can.save()
                    
                    # Merge with original page
                    packet.seek(0)
                    overlay_pdf = pypdf.PdfReader(packet)
                    page.merge_page(overlay_pdf.pages[0])
                    pdf_writer.add_page(page)
                
                # Write output
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                    
            return output_path
            
        except Exception as e:
            raise HTTPException(500, f"Add page numbers failed: {str(e)}")
    
    # ==================== Cleanup ====================
    
    async def cleanup_file(self, file_path: Path) -> None:
        """Delete a file"""
        if file_path.exists():
            file_path.unlink()
    
    async def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """Delete files older than max_age_hours"""
        import time
        
        count = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for dir_path in [self.upload_dir, self.output_dir]:
            for file_path in dir_path.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        count += 1
                        
        return count
