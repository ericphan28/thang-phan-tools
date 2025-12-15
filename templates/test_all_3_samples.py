"""Test all 3 samples of Mau 2C"""
import requests
import json
from pathlib import Path

template = r"d:\thang\utility-server\templates\so_yeu_ly_lich_2c_template.docx"
url = "http://localhost:8000/api/v1/documents/pdf/generate"

samples = [
    {
        "name": "Mau 1: Can bo tre - Chuyen vien",
        "json": r"d:\thang\utility-server\templates\mau_2c_sample_1_can_bo_tre.json",
        "output": r"d:\thang\utility-server\templates\output_2c_can_bo_tre.pdf"
    },
    {
        "name": "Mau 2: Can bo trung nien - Pho Truong phong",
        "json": r"d:\thang\utility-server\templates\mau_2c_sample_2_trung_nien.json",
        "output": r"d:\thang\utility-server\templates\output_2c_trung_nien.pdf"
    },
    {
        "name": "Mau 3: Can bo cao cap - Giam doc So",
        "json": r"d:\thang\utility-server\templates\mau_2c_sample_3_giam_doc_so.json",
        "output": r"d:\thang\utility-server\templates\output_2c_giam_doc_so.pdf"
    }
]

print("=" * 80)
print("TEST TAT CA 3 MAU DU LIEU - MAU 2C-TCTW-98")
print("=" * 80)

results = []

for idx, sample in enumerate(samples, 1):
    print(f"\n{'='*80}")
    print(f"Test {idx}/3: {sample['name']}")
    print(f"{'='*80}")
    
    # Read JSON
    with open(sample['json'], 'r', encoding='utf-8') as f:
        json_data = f.read()
    
    print(f"  JSON size: {len(json_data)} characters")
    
    # Prepare request
    files = {
        'template_file': ('template.docx', open(template, 'rb'), 
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
    }
    
    data = {
        'json_data': json_data,
        'output_format': 'pdf'
    }
    
    try:
        response = requests.post(url, files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            # Save PDF
            with open(sample['output'], 'wb') as f:
                f.write(response.content)
            
            size_kb = len(response.content) / 1024
            print(f"  ✅ SUCCESS! {size_kb:.2f} KB")
            results.append(("✅", sample['name'], f"{size_kb:.2f} KB"))
        else:
            print(f"  ❌ ERROR {response.status_code}: {response.text[:200]}")
            results.append(("❌", sample['name'], f"Error {response.status_code}"))
            
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        results.append(("❌", sample['name'], str(e)))
    finally:
        files['template_file'][1].close()

# Summary
print(f"\n{'='*80}")
print("TONG KET")
print(f"{'='*80}")
for status, name, size in results:
    print(f"{status} {name}: {size}")

print(f"\n{'='*80}")
print("File outputs:")
for sample in samples:
    if Path(sample['output']).exists():
        size = Path(sample['output']).stat().st_size / 1024
        print(f"  • {Path(sample['output']).name}: {size:.2f} KB")
