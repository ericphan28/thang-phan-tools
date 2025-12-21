#!/usr/bin/env python3
"""
Test Smart PDF OCR Feature
Tests the new smart PDF OCR endpoint that uses Gemini/Claude only for scanned PDFs
"""

import requests
import json
from pathlib import Path
import time

BASE_URL = "http://localhost:8000/api/v1/documents"

def create_test_pdf_with_text():
    """Create a test PDF with text (not scanned)"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    pdf_path = Path("test_text_based.pdf")
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.drawString(100, 750, "This is a text-based PDF with searchable text.")
    c.drawString(100, 730, "It contains regular text that can be extracted directly.")
    c.drawString(100, 710, "Tiếng Việt: Xin chào, đây là văn bản có thể tìm kiếm được.")
    c.save()
    
    return pdf_path

def test_smart_pdf_ocr():
    """Test smart PDF OCR feature"""
    print("🧪 Testing Smart PDF OCR Feature")
    print("=" * 50)
    
    # Test 1: Text-based PDF (should use direct extraction)
    print("\n📝 Test 1: Text-based PDF")
    text_pdf = create_test_pdf_with_text()
    
    try:
        url = f"{BASE_URL}/pdf/ocr-smart"
        print(f"   🔗 Calling: {url}")
        with open(text_pdf, 'rb') as f:
            response = requests.post(
                url,
                files={"file": ("test.pdf", f, "application/pdf")},
                data={
                    "ai_engine": "gemini",
                    "language": "vi"
                }
            )
        
        if response.status_code == 200:
            result = response.json()
            processing = result.get("processing", {})
            
            print(f"✅ Success!")
            print(f"   📄 PDF Type: {processing.get('pdf_type')}")
            print(f"   ⚙️ Method: {processing.get('method')}")
            print(f"   🚀 Engine: {processing.get('engine')}")
            print(f"   ⏱️ Time: {processing.get('time_seconds')}s")
            print(f"   📊 Text Length: {result.get('char_count')} chars")
            
            if 'ai_usage' in result:
                ai_usage = result['ai_usage']
                print(f"   💰 AI Cost: ${ai_usage.get('total_cost_usd', 0)}")
            else:
                print(f"   💰 AI Cost: $0.00 (direct extraction)")
                
            print(f"   📝 Sample Text: {result.get('text', '')[:100]}...")
            
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        if text_pdf.exists():
            text_pdf.unlink()
    
    # Test 2: Test with different AI engines
    print("\n🤖 Test 2: AI Engine Comparison")
    
    # Create a simple image-like PDF using an image
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create test image
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw Vietnamese text
        text = "Xin chào, đây là văn bản tiếng Việt\\nĐây là tài liệu được scan từ hình ảnh"
        draw.text((20, 50), text, fill='black')
        
        # Save as PDF using reportlab
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.utils import ImageReader
        import io
        
        # Convert PIL to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_reader = ImageReader(img_buffer)
        
        # Create PDF with image
        scanned_pdf = Path("test_scanned.pdf")
        c = canvas.Canvas(str(scanned_pdf), pagesize=letter)
        c.drawImage(img_reader, 100, 500, width=400, height=200)
        c.save()
        
        # Test with Gemini
        print("\\n📊 Testing with Gemini:")
        with open(scanned_pdf, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/pdf/ocr-smart",
                files={"file": ("scanned.pdf", f, "application/pdf")},
                data={
                    "ai_engine": "gemini",
                    "language": "vi"
                }
            )
        
        if response.status_code == 200:
            result = response.json()
            processing = result.get("processing", {})
            
            print(f"   ✅ Gemini OCR Success!")
            print(f"   📄 PDF Type: {processing.get('pdf_type')}")
            print(f"   ⚙️ Method: {processing.get('method')}")
            print(f"   ⏱️ Time: {processing.get('time_seconds')}s")
            
            if 'ai_usage' in result:
                ai_usage = result['ai_usage']
                print(f"   💰 Cost: ${ai_usage.get('total_cost_usd', 0)}")
                print(f"   🎯 Tokens: {ai_usage.get('total_tokens', 0)}")
                print(f"   💸 Cost/page: ${ai_usage.get('cost_per_page', 0)}")
            
            print(f"   📝 Extracted: {result.get('text', '')[:100]}...")
        else:
            error_detail = response.json().get('detail', 'Unknown error') if response.headers.get('content-type') == 'application/json' else response.text
            print(f"   ❌ Gemini failed: {response.status_code}")
            print(f"   ℹ️ Error: {error_detail}")
        
        # Test with Claude
        print("\\n🧠 Testing with Claude:")
        with open(scanned_pdf, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/pdf/ocr-smart",
                files={"file": ("scanned.pdf", f, "application/pdf")},
                data={
                    "ai_engine": "claude",
                    "language": "vi"
                }
            )
        
        if response.status_code == 200:
            result = response.json()
            processing = result.get("processing", {})
            
            print(f"   ✅ Claude OCR Success!")
            print(f"   📄 PDF Type: {processing.get('pdf_type')}")
            print(f"   ⚙️ Method: {processing.get('method')}")
            print(f"   ⏱️ Time: {processing.get('time_seconds')}s")
            
            if 'ai_usage' in result:
                ai_usage = result['ai_usage']
                print(f"   💰 Cost: ${ai_usage.get('total_cost_usd', 0)}")
                print(f"   🎯 Tokens: {ai_usage.get('total_tokens', 0)}")
                print(f"   💸 Cost/page: ${ai_usage.get('cost_per_page', 0)}")
            
            print(f"   📝 Extracted: {result.get('text', '')[:100]}...")
        else:
            error_detail = response.json().get('detail', 'Unknown error') if response.headers.get('content-type') == 'application/json' else response.text
            print(f"   ❌ Claude failed: {response.status_code}")
            print(f"   ℹ️ Error: {error_detail}")
            
        # Cleanup
        if scanned_pdf.exists():
            scanned_pdf.unlink()
            
    except Exception as e:
        print(f"❌ Scanned PDF test failed: {e}")
    
    print("\\n🎉 Smart PDF OCR test completed!")

if __name__ == "__main__":
    test_smart_pdf_ocr()