"""Test Mau 2C with Python requests"""
import requests
import json
from pathlib import Path

# Files
template = r"d:\thang\utility-server\templates\so_yeu_ly_lich_2c_template.docx"
json_file = r"d:\thang\utility-server\templates\mau_2c_sample_1_can_bo_tre.json"
output = r"d:\thang\utility-server\templates\test_2c_result.pdf"
url = "http://localhost:8000/api/v1/documents/pdf/generate"

print("=" * 80)
print("TEST MAU 2C-TCTW-98")
print("=" * 80)

# Read JSON
with open(json_file, 'r', encoding='utf-8') as f:
    json_data = f.read()

print(f"\n✓ Read JSON file: {len(json_data)} characters")
print(f"✓ Template: {Path(template).name}")

# Prepare multipart form data
files = {
    'template_file': ('template.docx', open(template, 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
}

data = {
    'json_data': json_data,  # Send as string in form data
    'output_format': 'pdf'
}

print(f"\n→ Sending request to {url}...")

try:
    response = requests.post(url, files=files, data=data, timeout=30)
    
    if response.status_code == 200:
        # Save PDF
        with open(output, 'wb') as f:
            f.write(response.content)
        
        size_kb = len(response.content) / 1024
        print(f"\n✅ SUCCESS! Generated PDF: {size_kb:.2f} KB")
        print(f"📄 File saved: {output}")
        
    else:
        print(f"\n❌ ERROR {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")
finally:
    files['template_file'][1].close()
