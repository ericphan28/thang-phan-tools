#!/usr/bin/env python3
"""
Test Adobe PDF Services API endpoints - Direct API Testing
No browser needed - Test trực tiếp qua API
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

def login():
    """Login and get access token"""
    print("🔐 Đăng nhập...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data['token']['access_token']
        print(f"✅ Đăng nhập thành công! Token: {token[:50]}...")
        return token
    else:
        print(f"❌ Đăng nhập thất bại: {response.status_code}")
        print(response.text)
        return None

def test_split_pdf(token, pdf_path, page_ranges):
    """Test Split PDF API"""
    print(f"\n📄 Test Split PDF: {pdf_path}")
    print(f"   Page ranges: {page_ranges}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
        data = {
            'page_ranges': page_ranges,
            'output_prefix': 'split'
        }
        
        response = requests.post(
            f"{BASE_URL}/documents/pdf/split",
            headers=headers,
            files=files,
            data=data
        )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Split PDF THÀNH CÔNG!")
        try:
            result = response.json()
            print(f"   Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        except:
            print(f"   Response length: {len(response.content)} bytes")
            # Save to file
            output_path = "test_split_output.pdf"
            with open(output_path, 'wb') as out:
                out.write(response.content)
            print(f"   Đã lưu: {output_path}")
    else:
        print(f"   ❌ Split PDF THẤT BẠI!")
        print(f"   Error: {response.text}")
    
    return response.status_code == 200

def test_combine_pdf(token, pdf_paths, page_ranges=None):
    """Test Combine PDF API"""
    print(f"\n📑 Test Combine PDF: {len(pdf_paths)} files")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    files = []
    for idx, pdf_path in enumerate(pdf_paths):
        with open(pdf_path, 'rb') as f:
            files.append(('files', (Path(pdf_path).name, f.read(), 'application/pdf')))
    
    data = {}
    if page_ranges:
        data['page_ranges'] = json.dumps(page_ranges)
    
    response = requests.post(
        f"{BASE_URL}/documents/pdf/combine",
        headers=headers,
        files=files,
        data=data
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Combine PDF THÀNH CÔNG!")
        output_path = "test_combine_output.pdf"
        with open(output_path, 'wb') as out:
            out.write(response.content)
        print(f"   Đã lưu: {output_path}")
    else:
        print(f"   ❌ Combine PDF THẤT BẠI!")
        print(f"   Error: {response.text}")
    
    return response.status_code == 200

def test_pdf_to_word(token, pdf_path):
    """Test PDF to Word conversion"""
    print(f"\n📝 Test PDF to Word: {pdf_path}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
        
        response = requests.post(
            f"{BASE_URL}/documents/pdf-to-word",
            headers=headers,
            files=files
        )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ PDF to Word THÀNH CÔNG!")
        output_path = "test_output.docx"
        with open(output_path, 'wb') as out:
            out.write(response.content)
        print(f"   Đã lưu: {output_path}")
    else:
        print(f"   ❌ PDF to Word THẤT BẠI!")
        print(f"   Error: {response.text}")
    
    return response.status_code == 200

def test_protect_pdf(token, pdf_path, password):
    """Test Protect PDF API"""
    print(f"\n🔒 Test Protect PDF: {pdf_path}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
        data = {
            'user_password': password,
            'permissions': json.dumps(['print', 'copy'])
        }
        
        response = requests.post(
            f"{BASE_URL}/documents/pdf/protect",
            headers=headers,
            files=files,
            data=data
        )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Protect PDF THÀNH CÔNG!")
        output_path = "test_protected.pdf"
        with open(output_path, 'wb') as out:
            out.write(response.content)
        print(f"   Đã lưu: {output_path}")
    else:
        print(f"   ❌ Protect PDF THẤT BẠI!")
        print(f"   Error: {response.text}")
    
    return response.status_code == 200

def test_watermark_pdf(token, pdf_path, watermark_text):
    """Test Watermark PDF API"""
    print(f"\n💧 Test Watermark PDF: {pdf_path}")
    print(f"   Watermark text: {watermark_text}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
        data = {
            'text': watermark_text,
            'opacity': '0.3',
            'rotation': '45'
        }
        
        response = requests.post(
            f"{BASE_URL}/documents/pdf/watermark",
            headers=headers,
            files=files,
            data=data
        )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Watermark PDF THÀNH CÔNG!")
        output_path = "test_watermarked.pdf"
        with open(output_path, 'wb') as out:
            out.write(response.content)
        print(f"   Đã lưu: {output_path}")
    else:
        print(f"   ❌ Watermark PDF THẤT BẠI!")
        print(f"   Error: {response.text}")
    
    return response.status_code == 200

def test_linearize_pdf(token, pdf_path):
    """Test Linearize PDF API"""
    print(f"\n⚡ Test Linearize PDF: {pdf_path}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
        
        response = requests.post(
            f"{BASE_URL}/documents/pdf/linearize",
            headers=headers,
            files=files
        )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Linearize PDF THÀNH CÔNG!")
        output_path = "test_linearized.pdf"
        with open(output_path, 'wb') as out:
            out.write(response.content)
        print(f"   Đã lưu: {output_path}")
    else:
        print(f"   ❌ Linearize PDF THẤT BẠI!")
        print(f"   Error: {response.text}")
    
    return response.status_code == 200

def test_autotag_pdf(token, pdf_path):
    """Test Auto-Tag PDF API"""
    print(f"\n🏷️  Test Auto-Tag PDF: {pdf_path}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
        
        response = requests.post(
            f"{BASE_URL}/documents/pdf/autotag",
            headers=headers,
            files=files
        )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Auto-Tag PDF THÀNH CÔNG!")
        output_path = "test_tagged.pdf"
        with open(output_path, 'wb') as out:
            out.write(response.content)
        print(f"   Đã lưu: {output_path}")
    else:
        print(f"   ❌ Auto-Tag PDF THẤT BẠI!")
        print(f"   Error: {response.text}")
    
    return response.status_code == 200

def main():
    """Run all tests"""
    print("="*70)
    print("🧪 ADOBE PDF SERVICES API - DIRECT TESTING")
    print("="*70)
    
    # Login
    token = login()
    if not token:
        print("\n❌ Không thể tiếp tục без token")
        return
    
    # Find test PDF - Try outputs folder first (avoid signed PDFs)
    test_pdf = Path("backend/uploads/outputs/1.3. Nội quy, quy chế Đại hội.pdf")
    if not test_pdf.exists():
        print(f"\n⚠️  Test PDF không tồn tại: {test_pdf}")
        # Try to find any PDF
        pdf_files = list(Path("backend/uploads/outputs").glob("*.pdf"))
        if not pdf_files:
            pdf_files = list(Path("backend/uploads").glob("**/*.pdf"))
        if pdf_files:
            test_pdf = pdf_files[0]
            print(f"✅ Dùng file: {test_pdf}")
        else:
            print("❌ Không tìm thấy file PDF nào!")
            return
    
    print(f"\n📁 Test PDF: {test_pdf}")
    print(f"   Size: {test_pdf.stat().st_size / 1024:.2f} KB")
    
    results = {}
    
    # Test 1: Split PDF (Critical - đã fix)
    results['Split PDF'] = test_split_pdf(token, str(test_pdf), "1-2")
    
    # Test 2: PDF to Word
    results['PDF to Word'] = test_pdf_to_word(token, str(test_pdf))
    
    # Test 3: Protect PDF
    results['Protect PDF'] = test_protect_pdf(token, str(test_pdf), "test123")
    
    # Test 4: Watermark PDF
    results['Watermark PDF'] = test_watermark_pdf(token, str(test_pdf), "CONFIDENTIAL")
    
    # Test 5: Linearize PDF
    results['Linearize PDF'] = test_linearize_pdf(token, str(test_pdf))
    
    # Test 6: Auto-Tag PDF
    results['Auto-Tag PDF'] = test_autotag_pdf(token, str(test_pdf))
    
    # Test 7: Combine PDF (if we have multiple PDFs)
    pdf_files = list(Path("backend/uploads").glob("**/*.pdf"))[:2]
    if len(pdf_files) >= 2:
        results['Combine PDF'] = test_combine_pdf(token, [str(p) for p in pdf_files], ["1-2", "all"])
    else:
        print(f"\n⚠️  Cần ít nhất 2 PDF files để test Combine (chỉ có {len(pdf_files)})")
        results['Combine PDF'] = None
    
    # Summary
    print("\n" + "="*70)
    print("📊 KẾT QUẢ TEST")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    for feature, status in results.items():
        if status is True:
            print(f"✅ {feature}")
        elif status is False:
            print(f"❌ {feature}")
        else:
            print(f"⏭️  {feature} (bỏ qua)")
    
    print(f"\n📈 Tổng kết: {passed} passed, {failed} failed, {skipped} skipped")
    print("="*70)

if __name__ == "__main__":
    main()
