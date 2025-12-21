"""
Test Smart PDF to Word Conversion
"""
import requests
from pathlib import Path

API_BASE = "http://localhost:8000/api/v1"

def test_pdf_to_word_smart():
    # Use the test PDF we created earlier
    test_pdf = Path("test_pdf_with_text.pdf")
    
    if not test_pdf.exists():
        print("❌ Test PDF not found. Creating one...")
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(str(test_pdf), pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "TEST DOCUMENT - HỢP ĐỒNG MUA BÁN")
        c.setFont("Helvetica", 12)
        c.drawString(100, 720, "Số: 123/2024")
        c.drawString(100, 700, "Ngày: 20/12/2025")
        c.drawString(100, 670, "")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 640, "BÊN A: Công ty ABC")
        c.setFont("Helvetica", 12)
        c.drawString(100, 620, "Địa chỉ: 123 Đường XYZ, Hà Nội")
        c.drawString(100, 600, "Điện thoại: 0123456789")
        c.save()
        print("Created test_pdf_with_text.pdf")
    
    print("\nTesting Smart PDF to Word Conversion")
    print("=" * 60)
    
    with open(test_pdf, 'rb') as f:
        files = {"file": (test_pdf.name, f, "application/pdf")}
        data = {"language": "vi"}
        
        print(f"\nUploading: {test_pdf.name}")
        print(f"Endpoint: {API_BASE}/documents/pdf/to-word-smart")
        
        response = requests.post(
            f"{API_BASE}/documents/pdf/to-word-smart",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        output_file = Path("output_converted.docx")
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        print(f"\nSUCCESS!")
        print(f"Output: {output_file} ({len(response.content)} bytes)")
        print(f"Technology: {response.headers.get('X-Technology-Model')}")
        print(f"Feature: {response.headers.get('X-Technology-Feature')}")
        print(f"\nOpen the file to check formatting!")
        
    else:
        print(f"\nFAILED: {response.status_code}")
        try:
            print(f"Error: {response.json().get('detail', response.text)}")
        except:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    test_pdf_to_word_smart()
