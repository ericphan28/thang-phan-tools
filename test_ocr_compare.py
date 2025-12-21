#!/usr/bin/env python
"""Test OCR comparison API endpoints."""

import requests
import sys
from pathlib import Path

# API endpoint
BASE_URL = "http://localhost:8000/api/v1/ocr-compare"

def test_compare_engines():
    """Test compare-engines endpoint with sample image."""
    # Find a test image
    test_images = [
        "d:/Thang/thang-phan-tools/test_files/ocr_vietnamese.png",
        "d:/Thang/thang-phan-tools/test_files/ocr_extract.png",
        "d:/Thang/thang-phan-tools/test_files/ocr_auto.png",
    ]
    
    test_image = None
    for img_path in test_images:
        if Path(img_path).exists():
            test_image = img_path
            break
    
    if not test_image:
        print("❌ No test image found. Please provide a test image.")
        print("Looking for images in:")
        for img_path in test_images:
            print(f"  - {img_path}")
        return False
    
    print(f"✅ Using test image: {test_image}")
    
    # Prepare request
    url = f"{BASE_URL}/compare-engines"
    
    with open(test_image, "rb") as f:
        files = {"file": (Path(test_image).name, f, "image/png")}
        data = {
            "engines": "adobe,tesseract,gemini",
            "language": "vie"
        }
        
        print(f"\n📤 Sending request to {url}")
        print(f"   Engines: {data['engines']}")
        print(f"   Language: {data['language']}")
        
        try:
            response = requests.post(url, files=files, data=data, timeout=60)
            
            print(f"\n📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ SUCCESS! API Response:")
                print(f"   File: {result.get('file')}")
                print(f"   Image size: {result.get('image_size')}")
                print(f"   Language: {result.get('language')}")
                print(f"\n   Results:")
                
                for engine, data in result.get('results', {}).items():
                    print(f"\n   🔍 {engine.upper()}:")
                    print(f"      Status: {data.get('status')}")
                    if data.get('status') == 'success':
                        print(f"      Text length: {len(data.get('text', ''))}")
                        print(f"      Processing time: {data.get('processing_time_ms')}ms")
                        print(f"      Text preview: {data.get('text', '')[:100]}...")
                    else:
                        print(f"      Error: {data.get('error')}")
                
                return True
            else:
                print(f"\n❌ ERROR {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"\n❌ Request failed: {str(e)}")
            return False

def test_smart_ocr():
    """Test smart-ocr endpoint (placeholder)."""
    url = f"{BASE_URL}/smart-ocr"
    print(f"\n📤 Testing {url}")
    
    try:
        response = requests.post(url, files={"file": ("test.png", b"fake", "image/png")}, timeout=10)
        print(f"📥 Response: {response.status_code} - {response.text[:200]}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("="*70)
    print("🧪 OCR Comparison API Test Suite")
    print("="*70)
    
    tests = [
        ("Compare Engines", test_compare_engines),
        ("Smart OCR", test_smart_ocr),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"Testing: {test_name}")
        print(f"{'='*70}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 Test Summary")
    print(f"{'='*70}")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nTotal: {passed}/{total} passed")
    
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
