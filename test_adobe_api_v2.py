"""
Adobe PDF Services API - Demo Script (Official SDK)
Demo chuyển PDF sang Word bằng Adobe PDF Services Python SDK

Yêu cầu:
1. pip install pdfservices-sdk python-dotenv
2. Tạo file .env với:
   PDF_SERVICES_CLIENT_ID=your_client_id
   PDF_SERVICES_CLIENT_SECRET=your_client_secret

Lấy credentials tại: https://acrobatservices.adobe.com/dc-integration-creation-app-cdn/main.html?api=pdf-services-api
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Adobe PDF Services SDK
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

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Giảm noise từ SDK


class AdobePDFService:
    """Adobe PDF Services API Client"""
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        """
        Initialize Adobe PDF Service
        
        Args:
            client_id: Adobe Client ID (or set PDF_SERVICES_CLIENT_ID env var)
            client_secret: Adobe Client Secret (or set PDF_SERVICES_CLIENT_SECRET env var)
        """
        self.client_id = client_id or os.getenv('PDF_SERVICES_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('PDF_SERVICES_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Missing credentials. Set PDF_SERVICES_CLIENT_ID and PDF_SERVICES_CLIENT_SECRET "
                "environment variables or pass them to constructor."
            )
        
        # Create credentials
        self.credentials = ServicePrincipalCredentials(
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
    def pdf_to_word(self, input_pdf: Path, output_docx: Path) -> bool:
        """
        Convert PDF to Word (DOCX) using Adobe PDF Services
        
        Args:
            input_pdf: Path to input PDF file
            output_docx: Path to output DOCX file
            
        Returns:
            True if successful, False otherwise
        """
        print("=" * 60)
        print("🚀 ADOBE PDF TO WORD CONVERSION")
        print("=" * 60)
        print(f"Input:  {input_pdf}")
        print(f"Output: {output_docx}")
        print()
        
        try:
            # Step 1: Read input file
            print("📄 Step 1: Đọc file PDF...")
            with open(input_pdf, 'rb') as file:
                input_stream = file.read()
            print(f"✅ Đã đọc {len(input_stream):,} bytes")
            print()
            
            # Step 2: Create PDF Services instance
            print("🔐 Step 2: Khởi tạo Adobe PDF Services...")
            pdf_services = PDFServices(credentials=self.credentials)
            print("✅ Đã kết nối với Adobe API")
            print()
            
            # Step 3: Upload file to Adobe cloud
            print("📤 Step 3: Upload PDF lên Adobe Cloud...")
            input_asset = pdf_services.upload(
                input_stream=input_stream,
                mime_type=PDFServicesMediaType.PDF
            )
            print("✅ Upload thành công!")
            print()
            
            # Step 4: Create export parameters
            print("⚙️  Step 4: Cấu hình conversion...")
            export_pdf_params = ExportPDFParams(
                target_format=ExportPDFTargetFormat.DOCX
            )
            print("✅ Target format: DOCX")
            print()
            
            # Step 5: Create and submit job
            print("🔄 Step 5: Tạo và submit conversion job...")
            export_pdf_job = ExportPDFJob(
                input_asset=input_asset,
                export_pdf_params=export_pdf_params
            )
            
            location = pdf_services.submit(export_pdf_job)
            print("✅ Job đã được submit!")
            print()
            
            # Step 6: Get job result (polling automatically handled by SDK)
            print("⏳ Step 6: Đợi conversion hoàn thành...")
            pdf_services_response = pdf_services.get_job_result(location, ExportPDFResult)
            print("✅ Conversion hoàn thành!")
            print()
            
            # Step 7: Download result
            print("⬇️  Step 7: Download file Word...")
            result_asset: CloudAsset = pdf_services_response.get_result().get_asset()
            stream_asset: StreamAsset = pdf_services.get_content(result_asset)
            
            # Step 8: Save to file
            print("💾 Step 8: Lưu file...")
            with open(output_docx, "wb") as file:
                file.write(stream_asset.get_input_stream())
            
            print(f"✅ Đã lưu: {output_docx}")
            print()
            
            # Success summary
            print("=" * 60)
            print("🎉 HOÀN THÀNH!")
            print("=" * 60)
            print(f"✅ File Word đã được tạo: {output_docx}")
            print(f"📊 Kích thước: {output_docx.stat().st_size:,} bytes")
            print()
            
            return True
            
        except ServiceApiException as e:
            print()
            print("=" * 60)
            print("❌ LỖI API!")
            print("=" * 60)
            print(f"Error: {e}")
            print()
            print("💡 Gợi ý:")
            print("   - Kiểm tra credentials trong file .env")
            print("   - Đảm bảo bạn chưa vượt quá 500 transactions/tháng (Free Tier)")
            print("   - Kiểm tra kết nối internet")
            print()
            return False
            
        except ServiceUsageException as e:
            print()
            print("=" * 60)
            print("❌ LỖI USAGE!")
            print("=" * 60)
            print(f"Error: {e}")
            print()
            print("💡 Gợi ý:")
            print("   - Bạn có thể đã hết quota (500 transactions/tháng)")
            print("   - Check usage tại: https://developer.adobe.com/console")
            print()
            return False
            
        except SdkException as e:
            print()
            print("=" * 60)
            print("❌ LỖI SDK!")
            print("=" * 60)
            print(f"Error: {e}")
            print()
            return False
            
        except Exception as e:
            print()
            print("=" * 60)
            print("❌ LỖI KHÔNG MONG ĐỢI!")
            print("=" * 60)
            print(f"Error: {e}")
            print()
            return False


def main():
    """Main demo function"""
    
    print("=" * 60)
    print("📄 ADOBE PDF SERVICES API - PYTHON SDK DEMO")
    print("=" * 60)
    print()
    
    # Check credentials
    client_id = os.getenv("PDF_SERVICES_CLIENT_ID")
    client_secret = os.getenv("PDF_SERVICES_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ THIẾU CREDENTIALS!")
        print()
        print("Bạn cần tạo file .env với nội dung:")
        print()
        print("PDF_SERVICES_CLIENT_ID=your_client_id_here")
        print("PDF_SERVICES_CLIENT_SECRET=your_client_secret_here")
        print()
        print("📖 Lấy credentials tại:")
        print("   https://acrobatservices.adobe.com/dc-integration-creation-app-cdn/main.html?api=pdf-services-api")
        print()
        print("📚 Hoặc xem hướng dẫn chi tiết trong:")
        print("   - ADOBE_API_GUIDE.md")
        print("   - QUICKSTART_ADOBE.md")
        print()
        return
    
    print(f"✅ Client ID: {client_id[:30]}...")
    print(f"✅ Client Secret: {'*' * 30}...")
    print()
    
    # Tạo service client
    try:
        service = AdobePDFService(client_id, client_secret)
    except ValueError as e:
        print(f"❌ {e}")
        return
    
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
    success = service.pdf_to_word(test_pdf, output_docx)
    
    if success:
        print("🎯 So sánh kết quả:")
        print(f"   1. File gốc:    test_complex_word.docx")
        print(f"   2. PDF:         test_complex_word.pdf")
        print(f"   3. Adobe out:   test_adobe_output.docx")
        print()
        print("   Mở 3 files để so sánh chất lượng!")
        print()
        print("✨ Adobe PDF Services Features:")
        print("   ✅ AI-powered conversion (Adobe Sensei)")
        print("   ✅ Giữ nguyên định dạng cực tốt")
        print("   ✅ Hỗ trợ fonts, colors, tables, images")
        print("   ✅ Free Tier: 500 conversions/tháng")
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
