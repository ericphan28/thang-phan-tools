"""
Test OCR Features - Simple Version
Only tests 3 actual endpoints: /extract, /vietnamese, /auto-detect
"""

import requests
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

BASE_URL = "http://localhost:8000/api/v1"

def print_test(name, status, detail=""):
    """Print formatted test result"""
    status_icon = "✅" if status == "✅" else "❌"
    print(f"{status_icon} {name}: {detail}")

def create_test_image(filename, text="Hello World\nTest OCR\n2025"):
    """Tạo ảnh test có text"""
    os.makedirs("test_files", exist_ok=True)
    img_path = os.path.join("test_files", filename)
    
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 50), text, fill='black', font=font)
    img.save(img_path)
    return img_path

def create_vietnamese_image(filename):
    """Tạo ảnh có text tiếng Việt"""
    text = "Tiếng Việt\nCông Cụ Xử Lý File\nĐây là văn bản test"
    return create_test_image(filename, text)

def test_ocr_extract():
    """Test /ocr/extract - Extract text from image"""
    print("\n" + "="*60)
    print("TEST 1: OCR Extract Text (English + Vietnamese)")
    print("="*60)
    
    try:
        img_path = create_test_image("ocr_extract.png", "Hello World\nTest OCR 2025\nTiếng Việt")
        
        with open(img_path, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/ocr/extract",
                files={"file": ("test.png", f, "image/png")},
                data={
                    "languages": "vi,en",
                    "detail": "1",
                    "paragraph": "false",
                    "gpu": "false"
                }
            )
        
        if response.status_code == 200:
            data = response.json()
            text = data.get('text', '')
            confidence = data.get('confidence', 0)
            print_test("OCR Extract", "✅", f"Extracted {len(text)} chars, confidence: {confidence:.1f}%")
            if text:
                print(f"   📝 Text: {text[:200]}")
            return True
        else:
            print_test("OCR Extract", "❌", f"Status {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_test("OCR Extract", "❌", str(e))
        return False

def test_ocr_vietnamese():
    """Test /ocr/vietnamese - Vietnamese optimized OCR"""
    print("\n" + "="*60)
    print("TEST 2: OCR Vietnamese (Optimized)")
    print("="*60)
    
    try:
        img_path = create_vietnamese_image("ocr_vietnamese.png")
        
        with open(img_path, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/ocr/vietnamese",
                files={"file": ("test.png", f, "image/png")},
                data={
                    "include_english": "true",
                    "gpu": "false"
                }
            )
        
        if response.status_code == 200:
            data = response.json()
            text = data.get('text', '')
            confidence = data.get('confidence', 0)
            print_test("OCR Vietnamese", "✅", f"Extracted {len(text)} chars, confidence: {confidence:.1f}%")
            if text:
                print(f"   📝 Text: {text[:200]}")
            return True
        else:
            print_test("OCR Vietnamese", "❌", f"Status {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_test("OCR Vietnamese", "❌", str(e))
        return False

def test_ocr_auto_detect():
    """Test /ocr/auto-detect - Auto detect language"""
    print("\n" + "="*60)
    print("TEST 3: OCR Auto-Detect Language")
    print("="*60)
    
    try:
        img_path = create_test_image("ocr_auto.png", "Mixed Text\nEnglish and Vietnamese\nTiếng Việt")
        
        with open(img_path, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/ocr/auto-detect",
                files={"file": ("test.png", f, "image/png")},
                data={"gpu": "false"}
            )
        
        if response.status_code == 200:
            data = response.json()
            text = data.get('text', '')
            detected_lang = data.get('detected_language', 'unknown')
            confidence = data.get('confidence', 0)
            print_test("OCR Auto-Detect", "✅", f"Language: {detected_lang}, {len(text)} chars, confidence: {confidence:.1f}%")
            if text:
                print(f"   📝 Text: {text[:200]}")
            return True
        else:
            print_test("OCR Auto-Detect", "❌", f"Status {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_test("OCR Auto-Detect", "❌", str(e))
        return False

def main():
    """Run all OCR tests"""
    print("\n" + "="*70)
    print("🔍 OCR FEATURES TEST - 3 Endpoints")
    print("="*70)
    print(f"Backend: {BASE_URL}")
    print("="*70)
    
    tests = [
        ("OCR Extract (vi,en)", test_ocr_extract),
        ("OCR Vietnamese", test_ocr_vietnamese),
        ("OCR Auto-Detect", test_ocr_auto_detect),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for name, result in results:
        status = f"{GREEN}✅ PASS{RESET}" if result else f"{RED}❌ FAIL{RESET}"
        print(f"{status} - {name}")
    
    print("\n" + "-"*70)
    print(f"{GREEN}Passed: {passed}/{len(results)}{RESET}")
    print(f"{RED}Failed: {failed}/{len(results)}{RESET}")
    print(f"Success Rate: {passed/len(results)*100:.1f}%")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
