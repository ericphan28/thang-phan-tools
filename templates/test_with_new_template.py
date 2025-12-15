"""Test template sau khi edit xong"""
import requests
from pathlib import Path
import sys

# Bạn sẽ đổi tên file sau khi edit xong
template = r"d:\thang\utility-server\templates\mau_2c_template_final.docx"
json_file = r"d:\thang\utility-server\templates\mau_2c_DATA_FULL.json"
output = r"d:\thang\utility-server\templates\OUTPUT_MAU_2C_FINAL.pdf"
url = "http://localhost:8000/api/v1/documents/pdf/generate"

# Check file tồn tại
if not Path(template).exists():
    print("❌ ERROR: Template chưa tạo xong!")
    print(f"   Bạn cần:")
    print(f"   1. Edit file: mau_2c_TEMPLATE_DE_EDIT.docx")
    print(f"   2. Lưu thành: mau_2c_template_final.docx")
    print(f"   3. Chạy lại script này")
    sys.exit(1)

print("="*80)
print("TEST TEMPLATE FINAL - SAU KHI EDIT TAY")
print("="*80)

# Read JSON
with open(json_file, 'r', encoding='utf-8') as f:
    json_data = f.read()

print(f"\n✓ Template: {Path(template).name}")
print(f"✓ JSON: {Path(json_file).name} ({len(json_data)} characters)")

# Send request
files = {
    'template_file': ('template.docx', open(template, 'rb'), 
                     'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
}

data = {
    'json_data': json_data,
    'output_format': 'pdf'
}

print(f"\n→ Generating PDF...")

try:
    response = requests.post(url, files=files, data=data, timeout=30)
    
    if response.status_code == 200:
        with open(output, 'wb') as f:
            f.write(response.content)
        
        size_kb = len(response.content) / 1024
        print(f"\n✅ THÀNH CÔNG!")
        print(f"   File size: {size_kb:.2f} KB")
        print(f"   Output: {output}")
        print(f"\n📄 Mở file để kiểm tra:")
        print(f"   start {output}")
    else:
        print(f"\n❌ ERROR {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")
finally:
    files['template_file'][1].close()
