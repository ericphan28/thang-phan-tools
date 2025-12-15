"""Test template moi - giu nguyen cau truc"""
import requests
from pathlib import Path

template = r"d:\thang\utility-server\templates\mau_2c_template_correct.docx"
json_file = r"d:\thang\utility-server\templates\mau_2c_simple.json"
output = r"d:\thang\utility-server\templates\test_2c_correct.pdf"
url = "http://localhost:8000/api/v1/documents/pdf/generate"

print("="*80)
print("TEST TEMPLATE MOI - GIU NGUYEN CAU TRUC")
print("="*80)

# Read JSON
with open(json_file, 'r', encoding='utf-8') as f:
    json_data = f.read()

print(f"\nJSON size: {len(json_data)} characters")

# Send request
files = {
    'template_file': ('template.docx', open(template, 'rb'), 
                     'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
}

data = {
    'json_data': json_data,
    'output_format': 'pdf'
}

print(f"Sending request...")

try:
    response = requests.post(url, files=files, data=data, timeout=30)
    
    if response.status_code == 200:
        with open(output, 'wb') as f:
            f.write(response.content)
        
        size_kb = len(response.content) / 1024
        print(f"\nSUCCESS! File size: {size_kb:.2f} KB")
        print(f"File: {output}")
    else:
        print(f"\nERROR {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"\nException: {e}")
finally:
    files['template_file'][1].close()
