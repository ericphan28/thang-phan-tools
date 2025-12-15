"""
Adobe PDF Services API - Demo Script (Official SDK Version)
Demo chuyển PDF sang Word bằng Adobe PDF Services SDK

Yêu cầu:
1. Đã đăng ký Adobe Developer Account
2. Có Client ID và Client Secret
3. pip install pdfservices-sdk

Hướng dẫn lấy credentials:
https://developer.adobe.com/document-services/docs/overview/pdf-services-api/quickstarts/python/
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Adobe PDF Services SDK imports
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.export_pdf_job import ExportPDFJob
from adobe.pdfservices.operation.pdfjobs.params.export_pdf.export_pdf_params import ExportPDFParams
from adobe.pdfservices.operation.pdfjobs.params.export_pdf.export_pdf_target_format import ExportPDFTargetFormat
from adobe.pdfservices.operation.pdfjobs.result.export_pdf_result import ExportPDFResult

# Load credentials từ .env
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

class AdobePDFService:
    """Adobe PDF Services API Client"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://pdf-services.adobe.io"
        self.access_token = None
        self.token_expiry = 0
        
    def get_access_token(self) -> str:
        """
        Lấy access token từ Adobe
        Token có hiệu lực 24h
        """
        # Check if token còn hiệu lực
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token
            
        print("🔐 Đang lấy access token từ Adobe...")
        
        url = f"{self.base_url}/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            self.access_token = result["access_token"]
            # Token expires trong 24h, cache đến 23h để an toàn
            self.token_expiry = time.time() + (result["expires_in"] - 3600)
            
            print(f"✅ Access token đã lấy thành công (expires in {result['expires_in']/3600:.1f}h)")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Lỗi lấy access token: {e}")
            if hasattr(e.response, 'text'):
                print(f"   Response: {e.response.text}")
            raise
    
    def upload_asset(self, file_path: Path) -> str:
        """
        Upload file lên Adobe Cloud
        Returns: Asset ID (dùng cho bước tiếp theo)
        """
        token = self.get_access_token()
        
        print(f"📤 Đang upload file: {file_path.name}...")
        
        # Step 1: Get upload URI
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "mediaType": "application/pdf"
        }
        
        response = requests.post(
            f"{self.base_url}/assets",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        asset_id = result["assetID"]
        upload_uri = result["uploadUri"]
        
        # Step 2: Upload file to URI
        with open(file_path, 'rb') as f:
            file_content = f.read()
            
        upload_headers = {
            "Content-Type": "application/pdf"
        }
        
        response = requests.put(
            upload_uri,
            headers=upload_headers,
            data=file_content,
            timeout=120
        )
        response.raise_for_status()
        
        print(f"✅ Upload thành công! Asset ID: {asset_id[:20]}...")
        return asset_id
    
    def convert_pdf_to_word(self, asset_id: str) -> str:
        """
        Chuyển đổi PDF sang Word (DOCX)
        Returns: Download URI của file DOCX
        """
        token = self.get_access_token()
        
        print("🔄 Đang chuyển đổi PDF sang Word...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "assetID": asset_id
        }
        
        # Gọi Export PDF API
        response = requests.post(
            f"{self.base_url}/operation/exportpdf",
            headers=headers,
            json=data,
            timeout=120
        )
        response.raise_for_status()
        
        result = response.json()
        
        # Poll job status
        if "status" in result and result["status"] == "in progress":
            job_uri = response.headers.get("location")
            result = self._poll_job_status(job_uri, token)
        
        download_uri = result["downloadUri"]
        asset_id = result["assetID"]
        
        print(f"✅ Chuyển đổi thành công! Asset ID: {asset_id[:20]}...")
        return download_uri
    
    def _poll_job_status(self, job_uri: str, token: str, max_wait: int = 60) -> dict:
        """
        Poll job status cho đến khi hoàn thành
        """
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            response = requests.get(job_uri, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            status = result.get("status")
            
            if status == "done":
                return result
            elif status == "failed":
                raise Exception(f"Job failed: {result.get('error', 'Unknown error')}")
            
            print(f"   Status: {status}, chờ 2s...")
            time.sleep(2)
        
        raise TimeoutError(f"Job không hoàn thành sau {max_wait}s")
    
    def download_asset(self, download_uri: str, output_path: Path):
        """
        Download file đã convert về local
        """
        print(f"⬇️  Đang download file: {output_path.name}...")
        
        response = requests.get(download_uri, timeout=120)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Download thành công: {output_path} ({output_path.stat().st_size:,} bytes)")
    
    def pdf_to_word_complete(self, input_pdf: Path, output_docx: Path):
        """
        Quy trình đầy đủ: Upload → Convert → Download
        """
        print("=" * 60)
        print("🚀 ADOBE PDF TO WORD CONVERSION")
        print("=" * 60)
        print(f"Input:  {input_pdf}")
        print(f"Output: {output_docx}")
        print()
        
        try:
            # Step 1: Upload PDF
            asset_id = self.upload_asset(input_pdf)
            
            # Step 2: Convert to Word
            download_uri = self.convert_pdf_to_word(asset_id)
            
            # Step 3: Download Word file
            self.download_asset(download_uri, output_docx)
            
            print()
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
            if "401" in str(e) or "403" in str(e):
                print("💡 Gợi ý: Kiểm tra lại Client ID và Client Secret")
                print("   Xem hướng dẫn trong file ADOBE_API_GUIDE.md")
            elif "404" in str(e):
                print("💡 Gợi ý: Endpoint có thể đã thay đổi, check documentation")
            elif "429" in str(e):
                print("💡 Gợi ý: Vượt quá rate limit, chờ 1 phút rồi thử lại")
            
            return False


def main():
    """Main demo function"""
    
    print("=" * 60)
    print("📄 ADOBE PDF SERVICES API - DEMO SCRIPT")
    print("=" * 60)
    print()
    
    # Kiểm tra credentials
    client_id = os.getenv("ADOBE_CLIENT_ID")
    client_secret = os.getenv("ADOBE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ THIẾU CREDENTIALS!")
        print()
        print("Bạn cần tạo file .env với nội dung:")
        print()
        print("ADOBE_CLIENT_ID=your_client_id_here")
        print("ADOBE_CLIENT_SECRET=your_client_secret_here")
        print()
        print("📖 Hướng dẫn lấy credentials: Xem file ADOBE_API_GUIDE.md")
        print()
        return
    
    print(f"✅ Client ID: {client_id[:20]}...")
    print(f"✅ Client Secret: {'*' * 20}")
    print()
    
    # Tạo service client
    service = AdobePDFService(client_id, client_secret)
    
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
    output_docx = Path("test_adobe_output.docx")
    
    # Chạy conversion
    success = service.pdf_to_word_complete(test_pdf, output_docx)
    
    if success:
        print("🎯 So sánh kết quả:")
        print(f"   1. File gốc:  test_complex_word.docx")
        print(f"   2. PDF:       test_complex_word.pdf")
        print(f"   3. Adobe out: test_adobe_output.docx")
        print()
        print("   Mở 3 files để so sánh chất lượng!")
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
