"""
Tạo PDF hoàn chỉnh với bìa trước và bìa sau
Create complete PDF book with front and back covers
"""
import os
from pathlib import Path
from PIL import Image
from pypdf import PdfWriter, PdfReader
import sys

def tif_to_pdf(tif_path: Path, pdf_path: Path):
    """Convert TIF image to PDF with FULL PAGE A4 (no margins)"""
    try:
        print(f"📄 Converting {tif_path.name} to PDF (FULL PAGE)...")
        
        # Don't use LibreOffice - it adds margins
        # Use PIL/Pillow for full control
        
        # Don't use LibreOffice - it adds margins
        # Use PIL/Pillow for full control
        
        # Method: Use imageio + ReportLab for FULL PAGE rendering
        try:
            import imageio.v3 as iio
            import numpy as np
            from PIL import Image
            from reportlab.pdfgen import canvas as pdf_canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.utils import ImageReader
            
            print(f"   Loading TIF with imageio...")
            
            # Load TIF file with imageio (handles complex TIFF formats)
            img_array = iio.imread(tif_path)
            
            print(f"   Original shape: {img_array.shape}")
            
            # Convert to PIL Image - handle CMYK properly
            if len(img_array.shape) == 3:
                channels = img_array.shape[2]
                
                if channels == 5:  # CMYK + Alpha
                    print(f"   Converting from CMYK+Alpha to RGB (preserving colors)...")
                    # Extract CMYK channels (first 4)
                    cmyk = img_array[:, :, :4]
                    
                    # Convert CMYK to RGB using proper formula
                    # CMYK values are typically 0-255
                    C = cmyk[:, :, 0].astype(float) / 255.0
                    M = cmyk[:, :, 1].astype(float) / 255.0
                    Y = cmyk[:, :, 2].astype(float) / 255.0
                    K = cmyk[:, :, 3].astype(float) / 255.0
                    
                    # CMYK to RGB conversion formula
                    R = 255 * (1 - C) * (1 - K)
                    G = 255 * (1 - M) * (1 - K)
                    B = 255 * (1 - Y) * (1 - K)
                    
                    # Stack RGB channels
                    rgb_array = np.stack([R, G, B], axis=2).astype('uint8')
                    img = Image.fromarray(rgb_array)
                    
                elif channels == 4:  # Could be CMYK or RGBA
                    print(f"   Converting 4-channel image to RGB...")
                    # Try as CMYK first
                    try:
                        C = img_array[:, :, 0].astype(float) / 255.0
                        M = img_array[:, :, 1].astype(float) / 255.0
                        Y = img_array[:, :, 2].astype(float) / 255.0
                        K = img_array[:, :, 3].astype(float) / 255.0
                        
                        R = 255 * (1 - C) * (1 - K)
                        G = 255 * (1 - M) * (1 - K)
                        B = 255 * (1 - Y) * (1 - K)
                        
                        rgb_array = np.stack([R, G, B], axis=2).astype('uint8')
                        img = Image.fromarray(rgb_array)
                    except:
                        # Fallback: treat as RGBA and drop alpha
                        img = Image.fromarray(img_array[:, :, :3].astype('uint8'))
                        
                elif channels == 3:  # RGB
                    img = Image.fromarray(img_array.astype('uint8'))
                else:
                    # Unknown format, take first 3 channels
                    img = Image.fromarray(img_array[:, :, :3].astype('uint8'))
            else:
                # Grayscale
                img = Image.fromarray(img_array.astype('uint8'))
            
            if img.mode != 'RGB':
                print(f"   Converting from {img.mode} to RGB...")
                img = img.convert('RGB')
            
            # Resize image to EXACT A4 size at high DPI for quality
            # A4 = 210mm x 297mm at 300 DPI = 2480 x 3508 pixels
            a4_width_px = 2480
            a4_height_px = 3508
            
            print(f"   Resizing to EXACT A4 size: {a4_width_px}x{a4_height_px} pixels (300 DPI)...")
            
            # Resize image to exact A4 dimensions (will stretch/distort if needed)
            img_resized = img.resize((a4_width_px, a4_height_px), Image.Resampling.LANCZOS)
            
            # Save directly as PDF with PIL (no margins)
            print(f"   Saving as PDF with PIL (zero margins)...")
            img_resized.save(
                pdf_path, 
                "PDF",
                resolution=300.0,  # High DPI for quality
                quality=95,  # High quality
                optimize=True
            )
            
            file_size = pdf_path.stat().st_size / 1024  # KB
            print(f"✅ Created FULL PAGE PDF: {pdf_path.name} ({file_size:.1f} KB)")
            return True
            
        except ImportError as e:
            print(f"   ❌ Missing library: {e}")
            print(f"   Please install: pip install imageio")
            return False
            
        except Exception as e:
            print(f"   ❌ Conversion failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ Error converting {tif_path.name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def optimize_pdf_to_a4(pdf_path: Path) -> bool:
    """Optimize existing PDF to A4 size"""
    try:
        # This would need additional PDF manipulation
        # For now, just return True if file exists
        return pdf_path.exists()
    except:
        return False

def merge_pdfs_with_covers(front_cover: Path, content: Path, back_cover: Path, output: Path):
    """Merge front cover + content + back cover into one PDF"""
    try:
        from pypdf import PdfWriter as PdfMerger, PdfReader
        
        print(f"\n📚 Creating complete book with covers...")
        
        # Convert TIF covers to PDF
        front_pdf = front_cover.parent / (front_cover.stem + "_temp.pdf")
        back_pdf = back_cover.parent / (back_cover.stem + "_temp.pdf")
        
        print(f"\n1️⃣ Converting front cover: {front_cover.name}")
        if not tif_to_pdf(front_cover, front_pdf):
            return False
        
        print(f"\n2️⃣ Converting back cover: {back_cover.name}")
        if not tif_to_pdf(back_cover, back_pdf):
            return False
        
        # Merge PDFs
        print(f"\n3️⃣ Merging PDFs...")
        merger = PdfMerger()
        
        # Add front cover
        print(f"   📄 Adding front cover: {front_pdf.name}")
        with open(front_pdf, 'rb') as f:
            front_reader = PdfReader(f)
            for page in front_reader.pages:
                merger.add_page(page)
        
        # Add content
        print(f"   📄 Adding content: {content.name} ({get_pdf_page_count(content)} pages)")
        with open(content, 'rb') as f:
            content_reader = PdfReader(f)
            for page in content_reader.pages:
                merger.add_page(page)
        
        # Add back cover
        print(f"   📄 Adding back cover: {back_pdf.name}")
        with open(back_pdf, 'rb') as f:
            back_reader = PdfReader(f)
            for page in back_reader.pages:
                merger.add_page(page)
        
        # Write output
        print(f"\n4️⃣ Writing final PDF: {output.name}")
        with open(output, 'wb') as f:
            merger.write(f)
        merger.close()
        
        # Get final stats
        total_pages = get_pdf_page_count(output)
        file_size = output.stat().st_size / (1024 * 1024)  # MB
        
        print(f"\n5️⃣ Optimizing PDF size...")
        try:
            # Try to compress/optimize the PDF
            reader = PdfReader(output)
            writer = PdfMerger()
            
            for page in reader.pages:
                writer.add_page(page)
            
            # Compress
            for page in writer.pages:
                page.compress_content_streams()
            
            # Write back
            temp_output = output.parent / (output.stem + "_temp.pdf")
            with open(temp_output, 'wb') as f:
                writer.write(f)
            
            # Replace original with compressed version
            temp_output.replace(output)
            
            optimized_size = output.stat().st_size / (1024 * 1024)
            saved = ((file_size - optimized_size) / file_size) * 100
            print(f"   ✅ Optimized: {file_size:.2f} MB → {optimized_size:.2f} MB (saved {saved:.1f}%)")
            file_size = optimized_size
            
        except Exception as e:
            print(f"   ⚠️  Optimization skipped: {e}")
        
        # Cleanup temp files
        print(f"\n6️⃣ Cleaning up temporary files...")
        front_pdf.unlink()
        back_pdf.unlink()
        print(f"   🧹 Deleted: {front_pdf.name}")
        print(f"   🧹 Deleted: {back_pdf.name}")
        
        print(f"\n" + "="*60)
        print(f"✅ SUCCESS! Complete book created:")
        print(f"   📖 File: {output.name}")
        print(f"   📄 Total pages: {total_pages}")
        print(f"   💾 File size: {file_size:.2f} MB")
        print(f"   📂 Location: {output.parent}")
        print(f"="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error merging PDFs: {e}")
        import traceback
        traceback.print_exc()
        
        # Cleanup temp files on error
        try:
            if front_pdf.exists():
                front_pdf.unlink()
            if back_pdf.exists():
                back_pdf.unlink()
        except:
            pass
        
        return False

def get_pdf_page_count(pdf_path: Path) -> int:
    """Get number of pages in PDF"""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            return len(reader.pages)
    except:
        return 0

def main():
    print("="*60)
    print("📚 TẠO PDF HOÀN CHỈNH VỚI BÌA TRƯỚC VÀ SAU")
    print("   Create Complete PDF Book with Covers")
    print("="*60)
    
    # Define paths
    base_dir = Path(r"D:\Thang\hoi-nong-dan-gia-kiem\public\cong-an-daklak\van-kien-in-an-chinh-thuc")
    
    front_cover = base_dir / "van kien 2.tif"  # Bìa trước
    back_cover = base_dir / "van kien 1.tif"   # Bìa sau
    content_pdf = base_dir / "van-kien-tong-hop.pdf"  # Nội dung
    output_pdf = base_dir / "van-kien-FINAL.pdf"  # Output - FINAL VERSION (NO MARGINS)
    
    print(f"\n📋 Configuration:")
    print(f"   🎨 Front Cover: {front_cover.name}")
    print(f"   📄 Content: {content_pdf.name}")
    print(f"   🎨 Back Cover: {back_cover.name}")
    print(f"   📖 Output: {output_pdf.name}")
    
    # Check if files exist
    print(f"\n🔍 Checking files...")
    missing_files = []
    
    if not front_cover.exists():
        missing_files.append(f"Front cover: {front_cover.name}")
    else:
        print(f"   ✅ Front cover found: {front_cover.name}")
    
    if not content_pdf.exists():
        missing_files.append(f"Content PDF: {content_pdf.name}")
    else:
        pages = get_pdf_page_count(content_pdf)
        print(f"   ✅ Content PDF found: {content_pdf.name} ({pages} pages)")
    
    if not back_cover.exists():
        missing_files.append(f"Back cover: {back_cover.name}")
    else:
        print(f"   ✅ Back cover found: {back_cover.name}")
    
    if missing_files:
        print(f"\n❌ ERROR: Missing files:")
        for f in missing_files:
            print(f"   - {f}")
        return False
    
    # Check if output already exists
    if output_pdf.exists():
        print(f"\n⚠️  Warning: Output file already exists: {output_pdf.name}")
        response = input("   Do you want to overwrite it? (y/n): ").strip().lower()
        if response != 'y':
            print("   ❌ Cancelled by user")
            return False
        print("   🔄 Will overwrite existing file...")
    
    # Create the book
    print(f"\n" + "="*60)
    success = merge_pdfs_with_covers(front_cover, content_pdf, back_cover, output_pdf)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
