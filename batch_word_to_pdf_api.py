"""
Batch Word to PDF Converter using API
Sử dụng backend API để convert files Word thành PDF
"""

import os
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
import logging
from typing import List
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIWordToPDFConverter:
    def __init__(self, target_directory: str, api_base: str = "http://localhost:8000"):
        self.target_dir = Path(target_directory)
        self.api_base = api_base
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
    
    async def convert_single_file(self, session: aiohttp.ClientSession, word_file: Path) -> bool:
        """Chuyển đổi một file Word thành PDF qua API"""
        try:
            output_file = word_file.with_suffix('.pdf')
            
            # Nếu PDF đã tồn tại, bỏ qua
            if output_file.exists():
                logger.info(f"⏭️ PDF already exists, skipping: {output_file.name}")
                return True
            
            logger.info(f"🔄 Converting: {word_file.name}")
            
            # Đọc file Word
            async with aiofiles.open(word_file, 'rb') as f:
                file_content = await f.read()
            
            # Tạo form data
            data = aiohttp.FormData()
            data.add_field('file', 
                          file_content, 
                          filename=word_file.name,
                          content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            
            # Gửi request đến API
            async with session.post(
                f"{self.api_base}/api/v1/documents/convert/word-to-pdf",
                data=data,
                timeout=aiohttp.ClientTimeout(total=120)  # 2 phút timeout
            ) as response:
                
                if response.status == 200:
                    # Lưu file PDF
                    pdf_content = await response.read()
                    async with aiofiles.open(output_file, 'wb') as f:
                        await f.write(pdf_content)
                    
                    logger.info(f"✅ Successfully converted: {output_file.name}")
                    self.success_count += 1
                    return True
                else:
                    error_text = await response.text()
                    error_msg = f"API error for {word_file.name}: {response.status} - {error_text}"
                    logger.error(error_msg)
                    self.errors.append(error_msg)
                    self.error_count += 1
                    return False
                    
        except asyncio.TimeoutError:
            error_msg = f"Timeout converting {word_file.name}"
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
    
    async def convert_all(self, max_concurrent: int = 2):
        """Chuyển đổi tất cả file Word thành PDF qua API"""
        word_files = self.find_word_files()
        
        if not word_files:
            logger.info("❌ No Word files found in directory!")
            return
        
        # Lọc bỏ file temp
        valid_files = [f for f in word_files if not f.name.startswith('~$')]
        
        logger.info(f"📁 Found {len(valid_files)} valid Word files in: {self.target_dir}")
        logger.info(f"🚀 Starting API conversion with {max_concurrent} concurrent requests...")
        
        # Tạo session HTTP
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=300)  # 5 phút timeout tổng
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Chuyển đổi với concurrency control
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def convert_with_semaphore(file_path):
                async with semaphore:
                    return await self.convert_single_file(session, file_path)
            
            # Thực hiện conversion
            tasks = [convert_with_semaphore(word_file) for word_file in valid_files]
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """In tóm tắt kết quả"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 API CONVERSION SUMMARY")
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

async def main():
    """Main async function"""
    # Thư mục cần xử lý
    target_directory = r"D:\Thang\hoi-nong-dan-gia-kiem\public\cong-an-daklak\van-kien-in-an-chinh-thuc"
    api_base = "http://localhost:8000"
    
    try:
        logger.info(f"🔧 Initializing API Batch Word to PDF Converter...")
        logger.info(f"📁 Target directory: {target_directory}")
        logger.info(f"🌐 API endpoint: {api_base}")
        
        converter = APIWordToPDFConverter(target_directory, api_base)
        await converter.convert_all(max_concurrent=2)  # 2 files cùng lúc
        
    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
    except KeyboardInterrupt:
        logger.info("❌ Conversion cancelled by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())