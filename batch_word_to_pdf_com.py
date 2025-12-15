"""
Giải pháp thay thế: Sử dụng Microsoft Word COM để convert
Nếu máy có Microsoft Word thì có thể dùng trực tiếp
"""

import os
import sys
from pathlib import Path
import logging
from typing import List

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WordCOMConverter:
    def __init__(self, target_directory: str):
        self.target_dir = Path(target_directory)
        self.success_count = 0
        self.error_count = 0
        self.errors = []
        
        if not self.target_dir.exists():
            raise FileNotFoundError(f"Directory not found: {target_directory}")
    
    def find_word_files(self) -> List[Path]:
        """Tìm tất cả file Word trong thư mục (bỏ qua temp files)"""
        word_extensions = ['.docx', '.doc']
        word_files = []
        
        for ext in word_extensions:
            files = self.target_dir.glob(f'**/*{ext}')
            # Lọc bỏ file tạm (bắt đầu với ~$)
            valid_files = [f for f in files if not f.name.startswith('~$')]
            word_files.extend(valid_files)
        
        return sorted(word_files)
    
    def convert_single_file(self, word_file: Path) -> bool:
        """Chuyển đổi một file Word thành PDF bằng COM"""
        try:
            output_file = word_file.with_suffix('.pdf')
            
            # Nếu PDF đã tồn tại, bỏ qua
            if output_file.exists():
                logger.info(f"⏭️ PDF already exists, skipping: {output_file.name}")
                return True
            
            logger.info(f"🔄 Converting: {word_file.name}")
            
            # Import win32com
            import win32com.client
            
            # Start Word application
            word_app = None
            try:
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
                
                # Close document
                doc.Close()
                
                if output_file.exists():
                    logger.info(f"✅ Successfully converted: {output_file.name}")
                    self.success_count += 1
                    return True
                else:
                    logger.error(f"❌ PDF not created: {word_file.name}")
                    self.error_count += 1
                    return False
                    
            finally:
                # Always close Word application
                if word_app:
                    try:
                        word_app.Quit()
                    except:
                        pass
                        
        except ImportError:
            error_msg = "win32com not available. Please install: pip install pywin32"
            logger.error(error_msg)
            self.errors.append(error_msg)
            self.error_count += 1
            return False
        except Exception as e:
            error_msg = f"Error converting {word_file.name}: {str(e)}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            self.error_count += 1
            return False
    
    def convert_all(self):
        """Chuyển đổi tất cả file Word thành PDF"""
        word_files = self.find_word_files()
        
        if not word_files:
            logger.info("❌ No Word files found in directory!")
            return
        
        logger.info(f"📁 Found {len(word_files)} Word files in: {self.target_dir}")
        logger.info(f"🚀 Starting Word COM conversion...")
        
        # Convert files one by one (COM doesn't handle concurrency well)
        for word_file in word_files:
            self.convert_single_file(word_file)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """In tóm tắt kết quả"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 WORD COM CONVERSION SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"✅ Successful conversions: {self.success_count}")
        logger.info(f"❌ Failed conversions: {self.error_count}")
        logger.info(f"📊 Total files processed: {self.success_count + self.error_count}")
        
        if self.errors:
            logger.info(f"\n❌ ERRORS:")
            for error in self.errors[:5]:  # Show first 5 errors
                logger.info(f"   - {error}")
            if len(self.errors) > 5:
                logger.info(f"   ... and {len(self.errors) - 5} more errors")
        
        if self.success_count > 0:
            logger.info(f"\n🎉 {self.success_count} PDF files created successfully!")
        
        logger.info(f"📁 Output location: {self.target_dir}")

def main():
    """Main function"""
    # Thư mục cần xử lý
    target_directory = r"D:\Thang\hoi-nong-dan-gia-kiem\public\cong-an-daklak\van-kien-in-an-chinh-thuc"
    
    try:
        logger.info(f"🔧 Initializing Word COM Converter...")
        logger.info(f"📁 Target directory: {target_directory}")
        
        converter = WordCOMConverter(target_directory)
        converter.convert_all()
        
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