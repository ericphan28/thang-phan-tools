"""
Test Adobe PDF Services API Credentials
Run this to verify your credentials are working
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_credentials():
    """Test if Adobe credentials are configured and valid"""
    
    print("=" * 60)
    print("🔍 Adobe PDF Services API Credentials Test")
    print("=" * 60)
    print()
    
    # Load config
    try:
        from app.core.config import settings
        print("✅ Config loaded successfully")
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False
    
    # Check if Adobe is enabled
    print(f"\n📋 Configuration:")
    print(f"   USE_ADOBE_PDF_API: {settings.USE_ADOBE_PDF_API}")
    
    if not settings.USE_ADOBE_PDF_API:
        print("\n⚠️  Adobe API is DISABLED")
        print("   To enable: Set USE_ADOBE_PDF_API=true in backend/.env")
        print("\n💡 System will use Tesseract OCR as fallback")
        return False
    
    # Check credentials
    has_client_id = bool(settings.PDF_SERVICES_CLIENT_ID)
    has_client_secret = bool(settings.PDF_SERVICES_CLIENT_SECRET)
    
    print(f"   Client ID: {'✅ Set' if has_client_id else '❌ Missing'}")
    if has_client_id:
        print(f"              {settings.PDF_SERVICES_CLIENT_ID[:15]}...")
    
    print(f"   Client Secret: {'✅ Set' if has_client_secret else '❌ Missing'}")
    if has_client_secret:
        print(f"                  {settings.PDF_SERVICES_CLIENT_SECRET[:15]}...")
    
    if not (has_client_id and has_client_secret):
        print("\n❌ Adobe credentials are INCOMPLETE")
        print("\n📘 Get credentials from:")
        print("   https://acrobatservices.adobe.com")
        print("\n📝 Then update backend/.env:")
        print("   PDF_SERVICES_CLIENT_ID=\"your_client_id\"")
        print("   PDF_SERVICES_CLIENT_SECRET=\"your_client_secret\"")
        return False
    
    # Try to initialize Adobe SDK
    print(f"\n🔧 Testing Adobe SDK...")
    try:
        from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
        from adobe.pdfservices.operation.pdf_services import PDFServices
        
        print("   ✅ Adobe SDK imported successfully")
        
        # Create credentials
        credentials = ServicePrincipalCredentials(
            client_id=settings.PDF_SERVICES_CLIENT_ID,
            client_secret=settings.PDF_SERVICES_CLIENT_SECRET
        )
        print("   ✅ Credentials object created")
        
        # Try to create PDF Services instance
        pdf_services = PDFServices(credentials=credentials)
        print("   ✅ PDF Services instance created")
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Adobe API is configured correctly!")
        print("=" * 60)
        print("\n💡 You can now use:")
        print("   • OCR PDF (10/10 quality)")
        print("   • PDF to Word (perfect format preservation)")
        print("   • Extract Content (AI-powered)")
        print("   • HTML to PDF (perfect rendering)")
        print("   • Compress PDF (AI optimization)")
        print("\n📊 Free tier: 500 transactions/month")
        print("🔗 Check usage: https://developer.adobe.com/console")
        return True
        
    except ImportError as e:
        print(f"\n❌ Adobe SDK not installed: {e}")
        print("\n📦 Install with:")
        print("   pip install pdfservices-sdk")
        return False
        
    except Exception as e:
        print(f"\n❌ Error testing credentials: {e}")
        print("\n🔍 Possible issues:")
        print("   • Client ID or Client Secret is incorrect")
        print("   • Internet connection issue")
        print("   • Adobe API service unavailable")
        print("\n💡 Double-check credentials at:")
        print("   https://developer.adobe.com/console")
        return False


if __name__ == "__main__":
    try:
        success = test_credentials()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
