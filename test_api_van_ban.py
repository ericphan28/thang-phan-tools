"""
Script test API kiểm tra thể thức
"""
import requests
import sys

# Test 1: Health check
print("=" * 50)
print("TEST 1: Health Check")
print("=" * 50)
try:
    response = requests.get("http://localhost:8000/api/v1/vb-hanh-chinh/health")
    print(f"✅ Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("TEST 2: Check API với file văn bản mẫu")
print("=" * 50)

# Đọc access token từ localStorage (cần login trước)
print("\n⚠️ Cần login để lấy access_token!")
print("Vào http://localhost:5173/login, login xong mở Console và chạy:")
print("console.log(localStorage.getItem('access_token'))")
print("\nSau đó paste token vào đây:")

token = input("\nPaste access_token: ").strip()

if not token:
    print("❌ Không có token! Hãy login trước.")
    sys.exit(1)

# Test upload file
import os
test_file = "test_documents/1_VAN_BAN_CHUAN.txt"

if not os.path.exists(test_file):
    print(f"❌ File {test_file} không tồn tại!")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {token}"
}

files = {
    "file": open(test_file, "rb")
}

data = {
    "chi_tiet_cao": "false",
    "luu_database": "true"
}

print(f"\n📤 Uploading {test_file}...")
print("⏳ Đang xử lý (có thể mất 10-20 giây)...\n")

try:
    response = requests.post(
        "http://localhost:8000/api/v1/vb-hanh-chinh/check-the-thuc",
        headers=headers,
        files=files,
        data=data,
        timeout=60
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ THÀNH CÔNG!")
        print(f"Điểm: {result['tong_diem']}/100")
        print(f"Loại văn bản: {result['loai_van_ban']}")
        print(f"Số vi phạm: {len(result['vi_pham'])}")
        print(f"Số thành phần đạt: {len(result['dat_yeu_cau'])}")
    else:
        print(f"\n❌ LỖI: {response.status_code}")
        print(f"Chi tiết: {response.text}")
        
except requests.exceptions.Timeout:
    print("\n❌ TIMEOUT! API mất quá 60 giây.")
    print("Có thể do:")
    print("- Gemini API chậm")
    print("- File quá lớn")
    print("- Backend bị treo")
    
except Exception as e:
    print(f"\n❌ LỖI: {e}")

finally:
    files["file"].close()
