"""
Batch Word to PDF Converter
Chuyển đổi tất cả file Word (.docx, .doc) trong thư mục thành PDF
"""

import os
import sys
from pathlib import Path
import logging
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BatchWordToPDFConverter:
    def __init__(self, target_directory: str):
        self.target_dir = Path(target_directory)
        self.success_count = 0
        self.error_count = 0
        self.errors = []
        
        if not self.target_dir.exists():
            raise FileNotFoundError(f"Directory not found: {target_directory}")
    
    def find_word_files(self) -> List[Path]:
        """Tìm tất cả file Word trong thư mục"""
        word_extensions = ['.docx', '.doc']
        word_files = []
        
        for ext in word_extensions:
            for file in self.target_dir.glob(f'**/*{ext}'):
                # Skip temporary Word files (starting with ~$)
                if not file.name.startswith('~$'):
                    word_files.append(file)
        
        return sorted(word_files)
    
    def convert_single_file(self, word_file: Path) -> bool:
        """Chuyển đổi một file Word thành PDF"""
        try:
            output_file = word_file.with_suffix('.pdf')
            
            # Nếu PDF đã tồn tại, bỏ qua
            if output_file.exists():
                logger.info(f"⏭️ PDF already exists, skipping: {output_file.name}")
                return True
            
            logger.info(f"🔄 Converting: {word_file.name}")
            
            # Add small delay to avoid LibreOffice race conditions
            time.sleep(0.5)
            
            # Method 1: Try docx2pdf (best for Windows)
            try:
                from docx2pdf import convert
                convert(str(word_file), str(output_file))
                
                if output_file.exists():
                    logger.info(f"✅ Success with docx2pdf: {output_file.name}")
                    self.success_count += 1
                    return True
                    
            except ImportError:
                logger.warning("docx2pdf not available, trying win32com...")
            except Exception as e:
                logger.warning(f"docx2pdf failed for {word_file.name}: {e}")
            
            # Method 2: Try win32com (Windows Word automation)
            try:
                import win32com.client
                
                # Start Word application
                word_app = win32com.client.Dispatch("Word.Application")
                word_app.Visible = False
                word_app.DisplayAlerts = False
                
                # Open document
                doc = word_app.Documents.Open(str(word_file.absolute()))
                
                # Export to PDF
                doc.ExportAsFixedFormat(
                    OutputFileName=str(output_file.absolute()),
                    ExportFormat=17,  # PDF format
                    OpenAfterExport=False,
                    OptimizeFor=0,
                    BitmapMissingFonts=True,
                    DocStructureTags=True,
                    CreateBookmarks=0,
                    IncludeDocProps=True,
                    KeepIRM=True,
                    CreateWordBookmarks=0,
                    UseDocumentProfile=False
                )
                
                # Close document and Word
                doc.Close()
                word_app.Quit()
                
                if output_file.exists():
                    logger.info(f"✅ Success with Word automation: {output_file.name}")
                    self.success_count += 1
                    return True
                    
            except ImportError:
                logger.warning("win32com not available, trying LibreOffice...")
            except Exception as e:
                logger.warning(f"Word automation failed for {word_file.name}: {e}")
            
            # Method 1: Try LibreOffice (if available)
            try:
                import subprocess
                
                # Try to find LibreOffice executable
                soffice_paths = [
                    "soffice",  # If in PATH
                    r"C:\Program Files\LibreOffice\program\soffice.exe",
                    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
                ]
                
                soffice_cmd = None
                for path in soffice_paths:
                    try:
                        if path == "soffice":
                            # Try running from PATH
                            result = subprocess.run([path, "--version"], capture_output=True, timeout=5)
                            if result.returncode == 0:
                                soffice_cmd = path
                                break
                        else:
                            # Check if file exists
                            if Path(path).exists():
                                soffice_cmd = path
                                break
                    except:
                        continue
                
                if soffice_cmd:
                    cmd = [
                        soffice_cmd,
                        "--headless",
                        "--convert-to", "pdf",
                        "--outdir", str(word_file.parent),
                        str(word_file)
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                    
                    if result.returncode == 0 and output_file.exists():
                        logger.info(f"✅ Success with LibreOffice: {output_file.name}")
                        self.success_count += 1
                        return True
                    else:
                        logger.warning(f"LibreOffice failed for {word_file.name}: {result.stderr}")
                else:
                    logger.warning("LibreOffice executable not found")
                    
            except FileNotFoundError:
                logger.warning("LibreOffice not found")
            except Exception as e:
                logger.warning(f"LibreOffice failed for {word_file.name}: {e}")
            
            # All methods failed
            error_msg = f"All conversion methods failed for: {word_file.name}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            self.error_count += 1
            return False
            
        except Exception as e:
            error_msg = f"Unexpected error converting {word_file.name}: {str(e)}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            self.error_count += 1
            return False
    
    def convert_all(self, max_workers: int = 1):
        """Chuyển đổi tất cả file Word thành PDF"""
        word_files = self.find_word_files()
        
        if not word_files:
            logger.info("❌ No Word files found in directory!")
            return
        
        logger.info(f"📁 Found {len(word_files)} Word files in: {self.target_dir}")
        logger.info(f"🚀 Starting conversion with {max_workers} parallel workers...")
        
        # Convert files sequentially to avoid LibreOffice race conditions
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.convert_single_file, word_file) for word_file in word_files]
            
            for future in futures:
                future.result()  # Wait for completion
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """In tóm tắt kết quả"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 CONVERSION SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"✅ Successful conversions: {self.success_count}")
        logger.info(f"❌ Failed conversions: {self.error_count}")
        logger.info(f"📊 Total files processed: {self.success_count + self.error_count}")
        
        if self.errors:
            logger.info(f"\n❌ ERRORS:")
            for error in self.errors:
                logger.info(f"   - {error}")
        
        if self.success_count > 0:
            logger.info(f"\n🎉 {self.success_count} PDF files created successfully!")
        
        logger.info(f"📁 Output location: {self.target_dir}")

def main():
    """Main function"""
    # Thư mục cần xử lý
    target_directory = r"D:\Thang\hoi-nong-dan-gia-kiem\public\cong-an-daklak\van-kien-in-an-chinh-thuc"
    
    try:
        logger.info(f"🔧 Initializing Batch Word to PDF Converter...")
        logger.info(f"📁 Target directory: {target_directory}")
        
        converter = BatchWordToPDFConverter(target_directory)
        converter.convert_all(max_workers=2)  # Giảm workers để tránh quá tải
        
    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("❌ Conversion cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()