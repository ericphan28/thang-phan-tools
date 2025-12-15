"""
Test OCR Features
Kiểm tra tính năng OCR (Optical Character Recognition)
"""

import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_URL = "http://localhost:8000/api/v1"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_test(name, status, message=""):
    """Print test result with colors"""
    color = GREEN if status == "✅" else RED if status == "❌" else YELLOW
    print(f"{color}{status} {name}{RESET} {message}")

def create_test_image_with_text(filename="test_ocr.png", text="Test OCR\nHello World\n2025"):
    """Tạo ảnh có text để test OCR"""
    img_path = Path("uploads") / filename
    img_path.parent.mkdir(exist_ok=True)
    
    # Create white image
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Draw text
    draw.text((50, 50), text, fill='black', font=font)
    
    # Save
    img.save(img_path)
    return img_path

def create_vietnamese_test_image(filename="test_vietnamese.png"):
    """Tạo ảnh có text tiếng Việt"""
    img_path = Path("uploads") / filename
    img_path.parent.mkdir(exist_ok=True)
    
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    text = "Tiếng Việt\nĐây là văn bản\nCông Cụ Xử Lý File"
    draw.text((50, 50), text, fill='black', font=font)
    
    img.save(img_path)
    return img_path

def test_ocr_extract_text():
    """Test OCR extract text từ ảnh"""
    try:
        img_path = create_test_image_with_text("ocr_test.png")
        
        with open(img_path, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/ocr/extract",
                files={"file": ("test.png", f, "image/png")}
            )
        
        if response.status_code == 200:
            data = response.json()
            text = data.get('text', '')
            confidence = data.get('confidence', 0)
            print_test("OCR Extract Text", "✅", f"({len(text)} chars, confidence: {confidence:.1f}%)")
            if text:
                print(f"   📝 Extracted: {text[:100]}")
            return True
        else:
            print_test("OCR Extract Text", "❌", f"Status {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print_test("OCR Extract Text", "❌", str(e))
        return False

def test_ocr_vietnamese():
    """Test OCR với tiếng Việt"""
    try:
        img_path = create_vietnamese_test_image("vietnamese_test.png")
        
        with open(img_path, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/ocr/vietnamese",
                files={"file": ("test.png", f, "image/png")},
                data={"include_english": "true", "gpu": "false"}
            )
        
        if response.status_code == 200:
            data = response.json()
            text = data.get('text', '')
            print_test("OCR Vietnamese", "✅", f"({len(text)} chars)")
            if text:
                print(f"   📝 Extracted: {text[:100]}")
            return True
        else:
            print_test("OCR Vietnamese", "❌", f"Status {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print_test("OCR Vietnamese", "❌", str(e))
        return False

def test_pdf_ocr():
    """Test OCR trên PDF (nếu có)"""
    try:
        # Create a simple PDF with reportlab
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from io import BytesIO
        
        pdf_path = Path("uploads") / "test_ocr.pdf"
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.drawString(100, 750, "Test OCR on PDF")
        c.drawString(100, 730, "This is a test document")
        c.drawString(100, 710, "Tiếng Việt: Công Cụ Xử Lý File")
        c.save()
        
        with open(pdf_path, 'wb') as f:
            f.write(buffer.getvalue())
        
        with open(pdf_path, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/documents/pdf/ocr",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        if response.status_code == 200:
            print_test("PDF OCR", "✅", f"({len(response.content)} bytes)")
            return True
        else:
            print_test("PDF OCR", "❌", f"Status {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print_test("PDF OCR", "❌", str(e))
        return False

def test_image_to_searchable_pdf():
    """Test chuyển ảnh thành PDF có thể search được (OCR)"""
    try:
        img_path = create_test_image_with_text("searchable_test.png")
        
        with open(img_path, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/ocr/image-to-searchable-pdf",
                files={"file": ("test.png", f, "image/png")}
            )
        
        if response.status_code == 200:
            print_test("Image → Searchable PDF", "✅", f"({len(response.content)} bytes)")
            return True
        else:
            print_test("Image → Searchable PDF", "❌", f"Status {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print_test("Image → Searchable PDF", "❌", str(e))
        return False

def test_batch_ocr():
    """Test batch OCR nhiều ảnh"""
    try:
        img1 = create_test_image_with_text("batch_ocr_1.png", "Document 1\nPage One")
        img2 = create_test_image_with_text("batch_ocr_2.png", "Document 2\nPage Two")
        
        with open(img1, 'rb') as f1, open(img2, 'rb') as f2:
            response = requests.post(
                f"{BASE_URL}/ocr/batch-extract",
                files=[
                    ("files", ("img1.png", f1, "image/png")),
                    ("files", ("img2.png", f2, "image/png"))
                ]
            )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print_test("Batch OCR", "✅", f"({len(results)} images processed)")
            return True
        else:
            print_test("Batch OCR", "❌", f"Status {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print_test("Batch OCR", "❌", str(e))
        return False

def main():
    """Chạy tất cả OCR tests"""
    print("\n" + "="*60)
    print("🔍 TESTING OCR FEATURES")
    print("="*60 + "\n")
    
    tests = [
        ("OCR Extract Text", test_ocr_extract_text),
        ("OCR Vietnamese", test_ocr_vietnamese),
        ("PDF OCR", test_pdf_ocr),
        ("Image → Searchable PDF", test_image_to_searchable_pdf),
        ("Batch OCR", test_batch_ocr),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_test(name, "❌", f"Exception: {e}")
            results.append((name, False))
        print()  # Empty line between tests
    
    # Summary
    print("="*60)
    print("📊 OCR TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    print(f"\n{GREEN}✅ Passed: {passed}{RESET}")
    print(f"{RED}❌ Failed: {failed}{RESET}")
    print(f"Total: {len(results)}")
    print(f"Success Rate: {passed/len(results)*100:.1f}%")
    
    if failed > 0:
        print(f"\n{RED}Failed tests:{RESET}")
        for name, result in results:
            if not result:
                print(f"  - {name}")
    
    print("\n" + "="*60 + "\n")
    
    return passed, failed

if __name__ == "__main__":
    passed, failed = main()
    exit(0 if failed == 0 else 1)
