"""
ComPDF API - Demo Script (REST API Version)
Test PDF to Word conversion với ComPDF API

Credentials của bạn:
- Public Key: public_key_1fb69e380c8b8452c86bcf3cbe947e2e
- Secret Key: secret_key_12ef29c45538a1de93e565f22ab63dd3

Yêu cầu:
pip install requests

Documentation: https://api.compdf.com/api-libraries/overview
API Reference: https://api.compdf.com/api-reference/overview
"""

import os
import time
import requests
from pathlib import Path

class ComPDFService:
    """ComPDF API Client - REST API wrapper"""
    
    BASE_URL = "https://api.compdf.com/v1"
    
    def __init__(self, public_key: str, secret_key: str):
        self.public_key = public_key
        self.secret_key = secret_key
        
    def _get_headers(self) -> dict:
        """Get request headers with authentication"""
        return {
            "x-api-key": self.public_key,
            "Content-Type": "application/json"
        }
    
    def create_task(self, task_type: str = "pdf-to-word") -> str:
        """Create conversion task"""
        url = f"{self.BASE_URL}/task/{task_type}"
        headers = self._get_headers()
        
        response = requests.post(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if result.get("code") != "200":
            raise Exception(f"Failed to create task: {result.get('msg')}")
        
        return result["data"]["taskId"]
    
    def upload_file(self, task_id: str, file_path: Path, parameters: dict) -> str:
        """Upload file to task"""
        url = f"{self.BASE_URL}/file/upload"
        headers = {
            "x-api-key": self.public_key
        }
        
        # Prepare multipart data
        with open(file_path, 'rb') as f:
            files = {
                'file': (file_path.name, f, 'application/pdf')
            }
            data = {
                'taskId': task_id,
                'parameter': str(parameters)  # JSON string
            }
            
            response = requests.post(url, headers=headers, files=files, data=data, timeout=120)
        
        response.raise_for_status()
        
        result = response.json()
        if result.get("code") != "200":
            raise Exception(f"Failed to upload file: {result.get('msg')}")
        
        return result["data"]["fileKey"]
    
    def execute_task(self, task_id: str):
        """Execute task"""
        url = f"{self.BASE_URL}/execute/start"
        headers = self._get_headers()
        data = {
            "taskId": task_id
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if result.get("code") != "200":
            raise Exception(f"Failed to execute task: {result.get('msg')}")
    
    def get_task_info(self, task_id: str) -> dict:
        """Get task status and info"""
        url = f"{self.BASE_URL}/task/list"
        headers = self._get_headers()
        data = {
            "taskId": task_id
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if result.get("code") != "200":
            raise Exception(f"Failed to get task info: {result.get('msg')}")
        
        return result["data"]["list"][0] if result["data"]["list"] else None
        
    def pdf_to_word(
        self,
        input_pdf: Path,
        output_docx: Path,
        is_flow_layout: bool = True,
        is_contain_img: bool = True,
        is_contain_annot: bool = True
    ) -> bool:
        """
        Chuyển đổi PDF sang Word (DOCX)
        
        Parameters:
        - input_pdf: Path to PDF file
        - output_docx: Path to output DOCX file
        - is_flow_layout: True = flow layout (giữ format), False = box layout
        - is_contain_img: Include images in output
        - is_contain_annot: Include annotations/comments
        
        Returns:
        - True if successful, False otherwise
        """
        print("=" * 60)
        print("🚀 COMPDF PDF TO WORD CONVERSION")
        print("=" * 60)
        print(f"Input:  {input_pdf}")
        print(f"Output: {output_docx}")
        print()
        
        try:
            # Step 1: Create task
            print("📋 Step 1: Tạo task conversion...")
            task_id = self.create_task("pdf-to-word")
            print(f"✅ Task ID: {task_id}")
            print()
            
            # Step 2: Configure parameters
            print("⚙️  Step 2: Cấu hình parameters...")
            
            import json
            parameters = json.dumps({
                "isFlowLayout": "1" if is_flow_layout else "0",
                "isContainImg": "1" if is_contain_img else "0",
                "isContainAnnot": "1" if is_contain_annot else "0"
            })
            
            print(f"   - Flow Layout: {'Yes' if is_flow_layout else 'No'} (giữ format)")
            print(f"   - Include Images: {'Yes' if is_contain_img else 'No'}")
            print(f"   - Include Annotations: {'Yes' if is_contain_annot else 'No'}")
            print()
            
            # Step 3: Upload file
            print(f"📤 Step 3: Upload file ({input_pdf.stat().st_size:,} bytes)...")
            file_key = self.upload_file(task_id, input_pdf, parameters)
            print(f"✅ Upload thành công! File key: {file_key[:20] if len(file_key) > 20 else file_key}...")
            print()
            
            # Step 4: Execute task
            print("🔄 Step 4: Bắt đầu conversion...")
            self.execute_task(task_id)
            print("✅ Task đã được submit!")
            print()
            
            # Step 5: Poll status
            print("⏳ Step 5: Đợi conversion hoàn thành...")
            max_wait = 60  # 60 seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                task_info = self.get_task_info(task_id)
                status = task_info.get("status")
                
                print(f"   Status: {status}", end="")
                
                if status == "TaskFinish":
                    print(" ✅")
                    break
                elif status == "TaskFailed":
                    print(" ❌")
                    error_msg = task_info.get("errorMsg", "Unknown error")
                    raise Exception(f"Task failed: {error_msg}")
                else:
                    print(f" (waiting...)")
                    time.sleep(3)
            else:
                raise TimeoutError(f"Task không hoàn thành sau {max_wait}s")
            
            print()
            
            # Step 6: Download result
            print("⬇️  Step 6: Download file Word...")
            task_info = self.get_task_info(task_id)
            file_list = task_info.get("fileList", [])
            
            if not file_list:
                raise Exception("Không có file output")
            
            # Download first file (usually only one)
            download_url = file_list[0].get("fileUrl")
            
            response = requests.get(download_url, timeout=120)
            response.raise_for_status()
            
            with open(output_docx, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Download thành công!")
            print()
            
            # Summary
            print("=" * 60)
            print("🎉 HOÀN THÀNH!")
            print("=" * 60)
            print(f"✅ File Word đã được tạo: {output_docx}")
            print(f"📊 Kích thước: {output_docx.stat().st_size:,} bytes")
            print()
            
            return True
            
        except Exception as e:
            print()
            print("=" * 60)
            print("❌ LỖI!")
            print("=" * 60)
            print(f"Error: {str(e)}")
            print()
            
            # Troubleshooting hints
            if "authentication" in str(e).lower() or "401" in str(e):
                print("💡 Gợi ý: Kiểm tra lại Public Key và Secret Key")
            elif "404" in str(e):
                print("💡 Gợi ý: File không tìm thấy hoặc task ID không hợp lệ")
            elif "timeout" in str(e).lower():
                print("💡 Gợi ý: File quá lớn, thử lại hoặc tăng timeout")
            
            return False


def main():
    """Main demo function"""
    
    print("=" * 60)
    print("📄 COMPDF API - DEMO SCRIPT")
    print("=" * 60)
    print()
    
    # Credentials của bạn (từ screenshot)
    public_key = "public_key_1fb69e380c8b8452c86bcf3cbe947e2e"
    secret_key = "secret_key_12ef29c45538a1de93e565f22ab63dd3"
    
    print(f"✅ Public Key: {public_key[:30]}...")
    print(f"✅ Secret Key: {secret_key[:30]}...")
    print()
    
    # Tạo service client
    service = ComPDFService(public_key, secret_key)
    
    # Tìm file PDF test
    test_pdf = Path("test_complex_word.pdf")
    
    if not test_pdf.exists():
        print(f"❌ Không tìm thấy file test: {test_pdf}")
        print()
        print("💡 Tạo file test bằng lệnh:")
        print("   python test_word_formatting.py")
        print()
        return
    
    # Output file
    output_docx = Path("test_compdf_output.docx")
    
    # Chạy conversion với các tùy chọn
    print("🎯 Conversion Options:")
    print("   - Flow Layout: Giữ nguyên format (recommended)")
    print("   - Include Images: Yes")
    print("   - Include Annotations: Yes")
    print()
    
    success = service.pdf_to_word(
        input_pdf=test_pdf,
        output_docx=output_docx,
        is_flow_layout=True,      # Giữ format như Word gốc
        is_contain_img=True,       # Bao gồm hình ảnh
        is_contain_annot=True      # Bao gồm comments
    )
    
    if success:
        print("🎯 So sánh kết quả:")
        print(f"   1. File gốc:    test_complex_word.docx")
        print(f"   2. PDF:         test_complex_word.pdf")
        print(f"   3. ComPDF out:  test_compdf_output.docx")
        print()
        print("   Mở 3 files để so sánh chất lượng!")
        print()
        print("📊 ComPDF API Features:")
        print("   ✅ Giữ nguyên định dạng (flow layout)")
        print("   ✅ Bảo toàn hình ảnh và tables")
        print("   ✅ Hỗ trợ tiếng Việt tốt")
        print("   ✅ Giá rẻ hơn Adobe (~$50/month cho 1000 files)")
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Đã hủy bởi người dùng")
    except Exception as e:
        print(f"\n\n❌ Lỗi không mong đợi: {e}")
        import traceback
        traceback.print_exc()
