"""
Test PDF to Word batch conversion via API
"""
import requests
import os
from pathlib import Path

# Test với 1 file PDF đơn giản
API_URL = "http://localhost:8000/api/v1/documents/batch/pdf-to-word"

# Tạo test PDF đơn giản
test_pdf = Path("test_input.pdf")
if not test_pdf.exists():
    # Tạo PDF test bằng reportlab
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(str(test_pdf), pagesize=letter)
        c.drawString(100, 750, "Test PDF Document")
        c.drawString(100, 730, "This is a simple test for batch PDF to Word conversion.")
        c.save()
        print(f"✅ Created test PDF: {test_pdf}")
    except ImportError:
        print("❌ reportlab not installed. Creating empty PDF...")
        test_pdf.write_bytes(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n210\n%%EOF")
        print(f"✅ Created minimal test PDF: {test_pdf}")

# Test API
print(f"\n📡 Testing batch PDF to Word conversion...")
print(f"API: {API_URL}")

try:
    with open(test_pdf, 'rb') as f:
        files = [('files', (test_pdf.name, f, 'application/pdf'))]
        
        print(f"📤 Uploading {test_pdf.name}...")
        response = requests.post(API_URL, files=files, timeout=60)
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            output_file = Path("test_batch_output.zip")
            output_file.write_bytes(response.content)
            print(f"✅ ZIP created successfully: {output_file} ({len(response.content)} bytes)")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()

# Cleanup
if test_pdf.exists():
    test_pdf.unlink()
    print(f"🧹 Cleaned up: {test_pdf}")
