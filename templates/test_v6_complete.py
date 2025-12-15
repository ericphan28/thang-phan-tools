#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST TEMPLATE V6 COMPLETE
=========================
Render và check xem còn dấu chấm không
"""

from docxtpl import DocxTemplate
import json
from docx import Document

def flatten_dict(d, parent_key='', sep='_'):
    """Flatten nested dict"""
    items = []
    for k, v in d.items():
        if k.startswith('_'):
            continue
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def main():
    TEMPLATE = "mau_2c_V6_COMPLETE_TEMPLATE.docx"
    OUTPUT = "OUTPUT_V6_COMPLETE.docx"
    JSON_FILE = "mau_2c_DATA_RESTRUCTURED.json"
    
    print(f"📖 Loading template: {TEMPLATE}")
    doc = DocxTemplate(TEMPLATE)
    
    print(f"📊 Loading data: {JSON_FILE}")
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Flatten nested structure
    flat_data = flatten_dict(data)
    
    # Also keep original nested structure for arrays
    render_data = {**flat_data}
    
    # Keep arrays as-is for loops
    if 'hoc_tap' in data:
        render_data['hoc_tap'] = data['hoc_tap']
    if 'cong_tac' in data:
        render_data['cong_tac'] = data['cong_tac']
    if 'gia_dinh' in data:
        render_data['gia_dinh'] = data['gia_dinh']
    
    print(f"✅ Loaded {len(render_data)} fields")
    
    print(f"🎨 Rendering...")
    doc.render(render_data)
    
    print(f"💾 Saving: {OUTPUT}")
    doc.save(OUTPUT)
    
    # Check for dots
    print(f"\n🔍 Checking for remaining dots...")
    output_doc = Document(OUTPUT)
    dot_count = 0
    
    for i, para in enumerate(output_doc.paragraphs):
        text = para.text
        # Count sequences of 3+ dots
        if '...' in text or '…..' in text:
            dot_count += 1
            if dot_count <= 10:  # Show first 10
                print(f"⚠️ P{i}: {text[:100]}")
    
    print(f"\n{'='*60}")
    print(f"📊 Paragraphs with dots: {dot_count}")
    print(f"📄 Output: {OUTPUT}")
    
    if dot_count == 0:
        print(f"🎉 PERFECT! Không còn dấu chấm!")
    elif dot_count < 10:
        print(f"✅ RẤT TỐT! Chỉ còn {dot_count} chỗ (có thể là format cố định)")
    elif dot_count < 30:
        print(f"⚠️ KHÁ TỐT! Còn {dot_count} chỗ cần improve")
    else:
        print(f"❌ CẦN CẢI THIỆN! Còn {dot_count} chỗ thiếu")
    
    print(f"\n✅ HOÀN THÀNH! Kiểm tra file: {OUTPUT}")

if __name__ == "__main__":
    main()
