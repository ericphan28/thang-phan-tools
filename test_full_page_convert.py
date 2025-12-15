"""
Tạo PDF FULL PAGE từ TIF bằng LibreOffice + crop margins
"""
from pathlib import Path
import subprocess
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from PIL import Image
import io

def tif_to_full_page_pdf(tif_path: Path, pdf_path: Path):
    """Convert TIF to FULL PAGE PDF (no margins)"""
    try:
        print(f"📄 Converting {tif_path.name} to FULL PAGE PDF...")
        
        # Step 1: Convert TIF to PDF using LibreOffice
        print(f"   Step 1: Converting TIF to PDF with LibreOffice...")
        soffice_cmd = r"C:\Program Files\LibreOffice\program\soffice.exe"
        
        temp_pdf = tif_path.parent / (tif_path.stem + "_temp_libreoffice.pdf")
        
        cmd = [
            soffice_cmd,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(tif_path.parent),
            str(tif_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # LibreOffice creates PDF with .pdf extension
        lo_output = tif_path.parent / (tif_path.stem + ".pdf")
        
        if lo_output.exists():
            if lo_output != temp_pdf:
                lo_output.rename(temp_pdf)
            print(f"   ✅ Converted to PDF: {temp_pdf.name}")
        else:
            raise Exception("LibreOffice conversion failed")
        
        # Step 2: Extract image from PDF and create FULL PAGE version
        print(f"   Step 2: Creating FULL PAGE version (removing margins)...")
        
        reader = PdfReader(temp_pdf)
        first_page = reader.pages[0]
        
        # Extract images from the PDF page
        if '/XObject' in first_page['/Resources']:
            xObject = first_page['/Resources']['/XObject'].get_object()
            
            for obj_name in xObject:
                obj = xObject[obj_name]
                
                if obj['/Subtype'] == '/Image':
                    # Extract image data
                    size = (obj['/Width'], obj['/Height'])
                    data = obj.get_data()
                    
                    # Determine color space
                    if obj['/ColorSpace'] == '/DeviceRGB':
                        mode = "RGB"
                    elif obj['/ColorSpace'] == '/DeviceGray':
                        mode = "L"
                    else:
                        mode = "RGB"
                    
                    # Create image
                    img = Image.frombytes(mode, size, data)
                    
                    # Create FULL PAGE PDF with this image
                    c = canvas.Canvas(str(pdf_path), pagesize=A4)
                    a4_width, a4_height = A4
                    
                    # Draw image to fill entire page
                    c.drawImage(ImageReader(img),
                               0, 0,
                               width=a4_width,
                               height=a4_height,
                               preserveAspectRatio=False,
                               mask='auto')
                    
                    c.save()
                    
                    print(f"   ✅ Created FULL PAGE PDF: {pdf_path.name}")
                    
                    # Cleanup temp file
                    temp_pdf.unlink()
                    
                    file_size = pdf_path.stat().st_size / 1024
                    print(f"   📊 File size: {file_size:.1f} KB")
                    
                    return True
        
        # Fallback: if can't extract image, just use the converted PDF
        print(f"   ⚠️  Could not extract image, using converted PDF as-is")
        temp_pdf.rename(pdf_path)
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# Test
if __name__ == "__main__":
    base_dir = Path(r"D:\Thang\hoi-nong-dan-gia-kiem\public\cong-an-daklak\van-kien-in-an-chinh-thuc")
    
    tif_file = base_dir / "van kien 2.tif"
    pdf_file = base_dir / "test-full-page.pdf"
    
    print("="*60)
    print("Testing FULL PAGE PDF creation")
    print("="*60)
    
    if tif_to_full_page_pdf(tif_file, pdf_file):
        print(f"\n✅ SUCCESS! Check: {pdf_file}")
    else:
        print(f"\n❌ FAILED!")
