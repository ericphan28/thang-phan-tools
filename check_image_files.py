"""
HƯỚNG DẪN: Tạo PDF với ảnh bìa

⚠️ VẤN ĐỀ:
Files TIFF hiện tại KHÔNG THỂ đọc được bằng Python PIL.
Lỗi: "cannot identify image file"

🔍 NGUYÊN NHÂN CÓ THỂ:
1. File TIFF bị corrupt
2. Format TIFF đặc biệt (multi-layer, compressed với codec không hỗ trợ)
3. File extension .tif nhưng không phải TIFF thực sự

✅ GIẢI PHÁP:

Option 1: Convert TIFF → PNG/JPG bằng tool khác
----------------------------------------------
1. Mở files trong Photoshop/GIMP/Paint.NET
2. Export as PNG hoặc JPG
3. Lưu với tên:
   - "van kien 1.png" (bia cuối)
   - "van kien 2.png" (bia đầu)
4. Chạy lại script với files PNG

Option 2: Sử dụng Online Converter
----------------------------------------------
1. Upload files lên: https://convertio.co/tif-png/
2. Download files PNG
3. Chạy lại script

Option 3: Kiểm tra files có đúng format không
----------------------------------------------
Files có thể KHÔNG PHẢI TIFF thực sự.
Thử mở bằng:
- Windows Photo Viewer
- IrfanView
- XnView
- Adobe Photoshop

Nếu không mở được → files bị lỗi

📝 SAU KHI CÓ FILES PNG/JPG:

Chạy script sau (đã tạo sẵn):

    python create_pdf_with_covers_png.py

Script sẽ:
1. Convert DOCX → PDF (nội dung chính)
2. Tối ưu ảnh PNG bìa (resize, compress)
3. Tạo PDF với 3 phần:
   - Bia đầu (full page, no margins)
   - Nội dung DOCX
   - Bia cuối (full page, no margins)
4. Lưu tại: VAN_KIEN_HOAN_CHINH_FULL.pdf

🎯 HOẶC:

Nếu bạn đã có files PNG/JPG sẵn, update paths trong script này:

"""

from pathlib import Path

BASE_DIR = Path(r"D:\Thang\hoi-nong-dan-gia-kiem\public\cong-an-daklak\van-kien-hoan-chinh-full")

print("="*70)
print("📋 KIỂM TRA FILES")
print("="*70)

# Check what image files exist
image_extensions = ['.png', '.jpg', '.jpeg', '.tif', '.tiff']
image_files = []

for ext in image_extensions:
    files = list(BASE_DIR.glob(f"*{ext}"))
    image_files.extend(files)

if image_files:
    print(f"\n✅ Tìm thấy {len(image_files)} files ảnh:")
    for f in sorted(image_files):
        size_mb = f.stat().st_size / (1024*1024)
        print(f"   • {f.name} ({size_mb:.2f} MB)")
        
        # Try to identify which can be opened
        try:
            from PIL import Image
            with Image.open(f) as img:
                print(f"     ✅ CÓ THỂ đọc được: {img.size[0]}x{img.size[1]}, {img.mode}")
        except Exception as e:
            print(f"     ❌ KHÔNG ĐỌC ĐƯỢC: {str(e)[:50]}")
else:
    print("\n❌ Không tìm thấy files ảnh nào")

print("\n" + "="*70)
print("📝 HÀNH ĐỘNG TIẾP THEO:")
print("="*70)

print("""
1. Convert files TIFF sang PNG/JPG bằng Photoshop hoặc online tool
2. Lưu files PNG với tên:
   - van kien 1.png (bia cuối)
   - van kien 2.png (bia đầu)
3. Chạy lại script với files PNG

HOẶC:

Nếu đã có files PNG, update script với đúng tên files.
""")
