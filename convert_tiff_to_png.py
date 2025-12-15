"""
Convert TIFF files to PNG using PIL with fallback methods
"""

from PIL import Image
from pathlib import Path
import sys

def convert_tiff_to_png(tiff_path):
    """Convert TIFF to PNG"""
    tiff_file = Path(tiff_path)
    
    if not tiff_file.exists():
        print(f"❌ File không tồn tại: {tiff_file}")
        return None
    
    print(f"📸 Đang convert: {tiff_file.name}")
    print(f"   Size: {tiff_file.stat().st_size / (1024*1024):.2f} MB")
    
    try:
        # Method 1: Direct PIL open
        print("   🔄 Method 1: PIL direct open...")
        Image.MAX_IMAGE_PIXELS = None
        img = Image.open(tiff_file)
        
        # Handle multi-page TIFF
        if hasattr(img, 'n_frames'):
            print(f"   • Multi-page TIFF: {img.n_frames} frames")
            img.seek(0)  # First page
        
        img.load()
        print(f"   ✅ Loaded: {img.size[0]}x{img.size[1]}, mode={img.mode}")
        
    except Exception as e:
        print(f"   ❌ Method 1 failed: {e}")
        
        # Method 2: Try with different TIFF plugin settings
        try:
            print("   🔄 Method 2: TIFF plugin with settings...")
            from PIL import TiffImagePlugin
            
            # Disable strict checks
            TiffImagePlugin.PREFIXES.append(b'II')
            TiffImagePlugin.PREFIXES.append(b'MM')
            
            img = Image.open(tiff_file)
            img.load()
            print(f"   ✅ Loaded: {img.size[0]}x{img.size[1]}, mode={img.mode}")
            
        except Exception as e2:
            print(f"   ❌ Method 2 failed: {e2}")
            print(f"\n💡 Suggestion: Use online converter or Photoshop to convert TIFF → PNG")
            return None
    
    # Convert to RGB if needed
    if img.mode in ('RGBA', 'LA', 'P', 'CMYK'):
        print(f"   🔄 Converting {img.mode} → RGB")
        img = img.convert('RGB')
    
    # Save as PNG
    png_path = tiff_file.parent / f"{tiff_file.stem}.png"
    print(f"   💾 Saving to: {png_path.name}")
    
    img.save(png_path, 'PNG', optimize=True)
    
    png_size = png_path.stat().st_size / (1024*1024)
    print(f"   ✅ Saved: {png_size:.2f} MB")
    print(f"   📊 Size change: {tiff_file.stat().st_size / (1024*1024):.2f} MB → {png_size:.2f} MB")
    
    return png_path

# Convert the two cover images
BASE_DIR = Path(r"D:\Thang\hoi-nong-dan-gia-kiem\public\cong-an-daklak\van-kien-hoan-chinh-full")

print("="*70)
print("🔄 CONVERT TIFF → PNG")
print("="*70)

files_to_convert = [
    BASE_DIR / "van kien 1.tif",  # Back cover
    BASE_DIR / "van kien 2.tif",  # Front cover
]

results = []
for tiff_file in files_to_convert:
    print()
    result = convert_tiff_to_png(tiff_file)
    results.append((tiff_file, result))
    print()

print("="*70)
print("📊 SUMMARY")
print("="*70)

for original, converted in results:
    if converted:
        print(f"✅ {original.name} → {converted.name}")
    else:
        print(f"❌ {original.name} → FAILED")

if all(r[1] for r in results):
    print("\n🎉 All files converted successfully!")
    print("\n💡 Now you can run create_pdf_with_covers.py")
    print("   But change .tif to .png in the file paths")
else:
    print("\n⚠️ Some files failed to convert")
    print("💡 Try using online converter or Photoshop")
