"""
Create PDF with Cover Pages
- Front cover: van kien 2.tif (full page, no margins)
- Main content: FILE TỔNG VĂN KIỆN BẢN WEB.docx
- Back cover: van kien 1.tif (full page, no margins)

Requirements:
- Optimize image size before adding
- Cover images fill entire page (no white space)
- Save to root folder
"""

import os
from pathlib import Path
from PIL import Image
from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import subprocess
import io

# Paths
BASE_DIR = Path(r"D:\Thang\hoi-nong-dan-gia-kiem\public\cong-an-daklak\van-kien-hoan-chinh-full")
MAIN_DOCX = BASE_DIR / "FILE TỔNG VĂN KIỆN BẢN WEB.docx"
BACK_COVER = BASE_DIR / "van kien 1.tif"  # Bia cuối
FRONT_COVER = BASE_DIR / "van kien 2.tif"  # Bia đầu
OUTPUT_PDF = BASE_DIR / "VAN_KIEN_HOAN_CHINH_FULL.pdf"

print("="*70)
print("📄 TẠO FILE PDF HOÀN CHỈNH")
print("="*70)
print(f"\n📁 Thư mục làm việc: {BASE_DIR}")
print(f"📄 Nội dung chính: {MAIN_DOCX.name}")
print(f"🖼️ Bia đầu: {FRONT_COVER.name}")
print(f"🖼️ Bia cuối: {BACK_COVER.name}")
print(f"💾 Output: {OUTPUT_PDF.name}\n")

# Check files exist
print("🔍 Kiểm tra files...")
for file_path, name in [(MAIN_DOCX, "Nội dung chính"), 
                         (FRONT_COVER, "Bia đầu"), 
                         (BACK_COVER, "Bia cuối")]:
    if file_path.exists():
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"  ✅ {name}: {size_mb:.2f} MB")
    else:
        print(f"  ❌ {name}: KHÔNG TÌM THẤY!")
        exit(1)

print("\n" + "="*70)

# Step 1: Convert DOCX to PDF
print("\n📝 BƯỚC 1: Chuyển DOCX → PDF")
print("-"*70)

main_content_pdf = BASE_DIR / "temp_main_content.pdf"

# Clean up old temp files first
for temp_file in [main_content_pdf, BASE_DIR / "FILE TỔNG VĂN KIỆN BẢN WEB.pdf"]:
    if temp_file.exists():
        print(f"🧹 Xóa file cũ: {temp_file.name}")
        temp_file.unlink()

try:
    # Use LibreOffice for conversion (if available)
    print("🔄 Sử dụng LibreOffice để convert...")
    
    # Try common LibreOffice paths
    libreoffice_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        r"C:\Program Files\LibreOffice 7\program\soffice.exe",
    ]
    
    libreoffice_exe = None
    for path in libreoffice_paths:
        if os.path.exists(path):
            libreoffice_exe = path
            break
    
    if libreoffice_exe:
        print(f"  ✅ Tìm thấy LibreOffice: {libreoffice_exe}")
        
        # Convert using LibreOffice
        cmd = [
            libreoffice_exe,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(BASE_DIR),
            str(MAIN_DOCX)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # LibreOffice saves as "FILE TỔNG VĂN KIỆN BẢN WEB.pdf"
        expected_output = BASE_DIR / "FILE TỔNG VĂN KIỆN BẢN WEB.pdf"
        
        if expected_output.exists():
            # Rename to temp file
            expected_output.rename(main_content_pdf)
            print(f"  ✅ Convert thành công: {main_content_pdf.stat().st_size / (1024*1024):.2f} MB")
        else:
            raise Exception("LibreOffice không tạo được file PDF")
    else:
        print("  ⚠️ Không tìm thấy LibreOffice!")
        print("  💡 Hãy cài LibreOffice để convert DOCX → PDF")
        print("  📥 Download: https://www.libreoffice.org/download/")
        exit(1)
        
except Exception as e:
    print(f"  ❌ Lỗi convert: {e}")
    exit(1)

# Step 2: Optimize and create cover PDFs
print("\n🖼️ BƯỚC 2: Tối ưu và tạo PDF cho ảnh bìa")
print("-"*70)

def optimize_image(image_path, max_size_mb=5):
    """Optimize image size while maintaining quality"""
    print(f"\n  📸 Xử lý: {image_path.name}")
    
    # Open image with error handling
    try:
        # Enable all TIFF plugins
        from PIL import TiffImagePlugin
        Image.MAX_IMAGE_PIXELS = None  # Remove limit
        
        # Try to open
        img = Image.open(image_path)
        
        # For multi-page TIFF, get first page
        if hasattr(img, 'n_frames') and img.n_frames > 1:
            print(f"    • Multi-page TIFF detected: {img.n_frames} pages")
            print(f"    • Sử dụng trang đầu tiên")
            img.seek(0)
        
        # Load the image data
        img.load()
        
    except Exception as e:
        print(f"    ❌ Lỗi đọc file: {e}")
        print(f"    🔄 Thử phương pháp thay thế...")
        
        # Alternative: Try to convert first with imagemagick if available
        try:
            import subprocess
            temp_png = image_path.parent / f"temp_{image_path.stem}.png"
            
            # Try using ImageMagick convert command
            result = subprocess.run(
                ['magick', 'convert', str(image_path) + '[0]', str(temp_png)],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0 and temp_png.exists():
                print(f"    ✅ Đã convert sang PNG tạm")
                img = Image.open(temp_png)
                temp_png.unlink()  # Clean up
            else:
                raise Exception("ImageMagick conversion failed")
        except Exception as e2:
            print(f"    ❌ Không thể xử lý file: {e2}")
            print(f"    💡 Hãy convert file TIFF sang PNG/JPG trước rồi thử lại")
            raise
    
    original_size = image_path.stat().st_size / (1024 * 1024)
    print(f"    • Kích thước gốc: {original_size:.2f} MB")
    print(f"    • Dimensions: {img.size[0]} x {img.size[1]} pixels")
    print(f"    • Mode: {img.mode}")
    
    # Convert TIFF to RGB if needed
    if img.mode in ('RGBA', 'LA', 'P'):
        print(f"    • Chuyển {img.mode} → RGB")
        img = img.convert('RGB')
    
    # If image is too large, resize proportionally
    max_dimension = 3000  # pixels
    if max(img.size) > max_dimension:
        ratio = max_dimension / max(img.size)
        new_size = tuple(int(dim * ratio) for dim in img.size)
        print(f"    • Resize: {img.size} → {new_size}")
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # Save optimized to temporary file
    temp_path = image_path.parent / f"temp_{image_path.stem}.jpg"
    
    # Try different quality levels
    for quality in [95, 90, 85, 80]:
        img.save(temp_path, 'JPEG', quality=quality, optimize=True)
        new_size = temp_path.stat().st_size / (1024 * 1024)
        
        if new_size <= max_size_mb or quality == 80:
            print(f"    • Tối ưu: {original_size:.2f} MB → {new_size:.2f} MB (quality={quality})")
            print(f"    • Giảm: {((original_size - new_size) / original_size * 100):.1f}%")
            break
    
    return temp_path, img.size

def create_cover_pdf(image_path, output_path):
    """Create PDF with image filling entire page (no margins)"""
    
    # Optimize image first
    optimized_image, img_size = optimize_image(image_path)
    
    print(f"\n  📄 Tạo PDF: {output_path.name}")
    
    # Create PDF with image dimensions as page size (no white space)
    img_width, img_height = img_size
    
    # Use A4 size for standard documents
    page_width, page_height = A4
    
    # Create PDF
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
    
    # Draw image to fill entire page (stretch if needed)
    c.drawImage(
        str(optimized_image),
        0, 0,  # x, y position (bottom-left corner)
        width=page_width,
        height=page_height,
        preserveAspectRatio=False  # Fill entire page
    )
    
    c.save()
    
    # Write to file
    packet.seek(0)
    with open(output_path, 'wb') as f:
        f.write(packet.read())
    
    # Clean up temp file
    optimized_image.unlink()
    
    print(f"    ✅ Đã tạo: {output_path.stat().st_size / 1024:.2f} KB")

# Create cover PDFs
front_cover_pdf = BASE_DIR / "temp_front_cover.pdf"
back_cover_pdf = BASE_DIR / "temp_back_cover.pdf"

create_cover_pdf(FRONT_COVER, front_cover_pdf)
create_cover_pdf(BACK_COVER, back_cover_pdf)

# Step 3: Merge PDFs
print("\n🔗 BƯỚC 3: Ghép các PDF lại")
print("-"*70)

merger = PdfWriter()

# Add front cover
print("  1️⃣ Thêm bia đầu...")
with open(front_cover_pdf, 'rb') as f:
    merger.append(f)
print(f"    ✅ Đã thêm bia đầu")

# Add main content
print("  2️⃣ Thêm nội dung chính...")
with open(main_content_pdf, 'rb') as f:
    reader = PdfReader(f)
    num_pages = len(reader.pages)
    merger.append(f)
print(f"    ✅ Đã thêm {num_pages} trang nội dung")

# Add back cover
print("  3️⃣ Thêm bia cuối...")
with open(back_cover_pdf, 'rb') as f:
    merger.append(f)
print(f"    ✅ Đã thêm bia cuối")

# Write final PDF
print("\n💾 Lưu file PDF...")
with open(OUTPUT_PDF, 'wb') as f:
    merger.write(f)
merger.close()

output_size = OUTPUT_PDF.stat().st_size / (1024 * 1024)
print(f"  ✅ Đã lưu: {OUTPUT_PDF}")
print(f"  📊 Kích thước: {output_size:.2f} MB")
print(f"  📄 Tổng số trang: {num_pages + 2} (bia đầu + {num_pages} nội dung + bia cuối)")

# Cleanup temp files
print("\n🧹 Dọn dẹp files tạm...")
for temp_file in [main_content_pdf, front_cover_pdf, back_cover_pdf]:
    if temp_file.exists():
        temp_file.unlink()
        print(f"  🗑️ Đã xóa: {temp_file.name}")

print("\n" + "="*70)
print("✅ HOÀN THÀNH!")
print("="*70)
print(f"\n📂 File PDF đã được tạo tại:")
print(f"   {OUTPUT_PDF}")
print(f"\n💡 Cấu trúc PDF:")
print(f"   • Trang 1: Bia đầu (van kien 2.tif) - Full page, no margins")
print(f"   • Trang 2-{num_pages+1}: Nội dung chính (DOCX)")
print(f"   • Trang {num_pages+2}: Bia cuối (van kien 1.tif) - Full page, no margins")
print("\n🎉 Success!\n")
