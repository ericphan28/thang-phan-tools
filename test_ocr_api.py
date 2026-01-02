#!/usr/bin/env python3
"""Test OCR API endpoint directly"""

import requests

# Test endpoint
url = "http://localhost:8000/api/v1/documents/ocr-to-word"
pdf_file = "test_pdf_with_text.pdf"

print(f"🧪 Testing OCR API: {url}")
print(f"📄 Using file: {pdf_file}")
print("-" * 50)

try:
    with open(pdf_file, 'rb') as f:
        files = {'file': (pdf_file, f, 'application/pdf')}
        
        print("📤 Sending request (no auth - demo mode)...")
        response = requests.post(url, files=files, timeout=30)
        
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"\n✅ SUCCESS! Word file received ({len(response.content)} bytes)")
            # Save output
            with open("test_ocr_output.docx", 'wb') as out:
                out.write(response.content)
            print("💾 Saved to: test_ocr_output.docx")
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(f"📄 Response Body:\n{response.text}")
            
except FileNotFoundError:
    print(f"❌ File not found: {pdf_file}")
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to backend. Is it running?")
except Exception as e:
    print(f"❌ Error: {e}")
