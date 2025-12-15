#!/usr/bin/env python3
"""
Demo friendly error messages for Adobe PDF APIs
"""
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

print("="*70)
print("🧪 DEMO: FRIENDLY ERROR MESSAGES")
print("="*70)

# Login
print("\n🔐 Đăng nhập...")
response = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
token = response.json()['token']['access_token']
print("✅ Đã đăng nhập!\n")

headers = {"Authorization": f"Bearer {token}"}

# Test 1: Protected PDF
print("="*70)
print("TEST 1: Protected PDF (File bị bảo vệ bằng mật khẩu)")
print("="*70)

protected_pdf = Path("backend/uploads/outputs/báo giá cá  03   151125_protected.pdf")
if protected_pdf.exists():
    with open(protected_pdf, 'rb') as f:
        files = {'file': (protected_pdf.name, f, 'application/pdf')}
        data = {'page_ranges': '1-2', 'output_prefix': 'test'}
        
        response = requests.post(
            f"{BASE_URL}/documents/pdf/split",
            headers=headers,
            files=files,
            data=data
        )
    
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"\n📝 Message hiển thị cho user:\n")
        print(response.json()['detail'])
else:
    print("⚠️  File not found")

# Test 2: Signed PDF
print("\n" + "="*70)
print("TEST 2: Signed PDF (File có chữ ký điện tử)")
print("="*70)

signed_pdf = Path("backend/uploads/documents/25-bnn-kem1.pdf")
if signed_pdf.exists():
    with open(signed_pdf, 'rb') as f:
        files = {'file': (signed_pdf.name, f, 'application/pdf')}
        
        response = requests.post(
            f"{BASE_URL}/documents/pdf/linearize",
            headers=headers,
            files=files
        )
    
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"\n📝 Message hiển thị cho user:\n")
        print(response.json()['detail'])
else:
    print("⚠️  File not found")

# Test 3: Normal PDF (Success case)
print("\n" + "="*70)
print("TEST 3: Normal PDF (File bình thường - should succeed)")
print("="*70)

normal_pdf = Path("backend/uploads/outputs/1.3. Nội quy, quy chế Đại hội.pdf")
if normal_pdf.exists():
    with open(normal_pdf, 'rb') as f:
        files = {'file': (normal_pdf.name, f, 'application/pdf')}
        data = {'page_ranges': '1-2', 'output_prefix': 'test'}
        
        response = requests.post(
            f"{BASE_URL}/documents/pdf/split",
            headers=headers,
            files=files,
            data=data
        )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("\n✅ SUCCESS! File xử lý thành công")
        print(f"Output size: {len(response.content)} bytes")
    else:
        print(f"\n❌ Unexpected error:\n{response.json()['detail']}")
else:
    print("⚠️  File not found")

# Test 4: Invalid page ranges
print("\n" + "="*70)
print("TEST 4: Invalid Page Ranges")
print("="*70)

if normal_pdf.exists():
    with open(normal_pdf, 'rb') as f:
        files = {'file': (normal_pdf.name, f, 'application/pdf')}
        data = {'page_ranges': '1-999', 'output_prefix': 'test'}  # Invalid range
        
        response = requests.post(
            f"{BASE_URL}/documents/pdf/split",
            headers=headers,
            files=files,
            data=data
        )
    
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"\n📝 Message hiển thị cho user:\n")
        print(response.json()['detail'])

print("\n" + "="*70)
print("✅ DEMO HOÀN TẤT")
print("="*70)
print("\n💡 Tất cả error messages đều:")
print("   • Dùng emoji dễ thương 😔")
print("   • Giải thích rõ ràng bằng tiếng Việt")
print("   • Đưa ra giải pháp cụ thể 💡")
print("   • Thân thiện với người dùng")
