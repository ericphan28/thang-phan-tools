"""
Script test template docxtpl với dữ liệu thực

✅ SỬ DỤNG DOCXTPL (python-docx-template)
✅ GIỮ NGUYÊN 100% ĐỊNH DẠNG
✅ TỰ ĐỘNG 100%
"""

from docxtpl import DocxTemplate
import json
from pathlib import Path
from datetime import datetime

def test_docxtpl_template():
    """
    Test template docxtpl với JSON data
    """
    
    print("🚀 TEST TEMPLATE DOCXTPL")
    print("="*60)
    
    # Check if template exists - UPDATED to use FINAL V4
    template_path = Path("mau_2c_template_FINAL_V4.docx")
    if not template_path.exists():
        print(f"❌ ERROR: Template chưa tạo!")
        print(f"   Vui lòng chạy: python improve_table_newlines.py")
        return False
    
    # Check if JSON data exists - UPDATED to use COMPLETE V3
    json_path = Path("mau_2c_DATA_COMPLETE_V3.json")
    if not json_path.exists():
        print(f"❌ ERROR: Không tìm thấy {json_path}")
        return False
    
    print(f"📖 Load template: {template_path}")
    doc = DocxTemplate(template_path)
    
    print(f"📖 Load JSON data: {json_path}")
    with open(json_path, encoding='utf-8') as f:
        context = json.load(f)
    
    print(f"✅ Loaded {len(context)} fields")
    print(f"   - Simple fields: {sum(1 for v in context.values() if not isinstance(v, list))}")
    print(f"   - Array fields: {sum(1 for v in context.values() if isinstance(v, list))}")
    
    # Add signature date if not present
    if 'ngay_ky' not in context:
        today = datetime.now()
        context['ngay_ky'] = str(today.day)
        context['thang_ky'] = str(today.month)
        context['nam_ky'] = str(today.year)
    
    print("\n🔧 Render template with data...")
    try:
        doc.render(context)
        print("   ✅ Render thành công!")
    except Exception as e:
        print(f"   ❌ Lỗi khi render: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Save output
    output_path = Path("OUTPUT_MAU_2C_DOCXTPL.docx")
    print(f"\n💾 Lưu file: {output_path}")
    doc.save(str(output_path))
    
    file_size = output_path.stat().st_size
    print("\n" + "="*60)
    print("✅ THÀNH CÔNG!")
    print(f"📄 Output: {output_path}")
    print(f"📊 Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    
    print("\n💡 KIỂM TRA:")
    print(f"   1. Mở file: {output_path}")
    print(f"   2. Xem định dạng có giống gốc không")
    print(f"   3. Xem dữ liệu có đúng không")
    print(f"   4. Xem bảng có data không")
    
    return True

if __name__ == "__main__":
    try:
        success = test_docxtpl_template()
        if not success:
            print("\n❌ Test thất bại!")
            exit(1)
        else:
            print("\n🎉 TEST HOÀN TẤT!")
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
