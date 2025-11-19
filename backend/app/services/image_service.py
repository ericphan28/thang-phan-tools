"""
Modern Image Processing Service (2025)
Features: Resize, crop, rotate, format conversion, AI background removal
"""

import io
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageEnhance, ImageFilter
import pillow_heif
from rembg import remove
from fastapi import UploadFile, HTTPException
import aiofiles


# Register HEIF opener (for iPhone photos)
pillow_heif.register_heif_opener()


class ImageService:
    """Modern image processing service with AI features"""
    
    def __init__(self, upload_dir: str = "uploads/images"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        self.output_dir = Path("uploads/outputs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported formats
        self.supported_formats = {
            'jpg', 'jpeg', 'png', 'webp', 'bmp', 'gif', 'tiff', 'heic', 'heif'
        }
    
    async def save_upload_file(self, upload_file: UploadFile) -> Path:
        """Save uploaded image file"""
        file_path = self.upload_dir / upload_file.filename
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await upload_file.read()
            await out_file.write(content)
            
        return file_path
    
    def _load_image(self, input_path: Path) -> Image.Image:
        """Load image with format auto-detection"""
        try:
            img = Image.open(input_path)
            # Convert to RGB if necessary (for PNG with transparency, etc.)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            return img
        except Exception as e:
            raise HTTPException(400, f"Cannot load image: {str(e)}")
    
    # ==================== Resize ====================
    
    async def resize_image(
        self,
        input_path: Path,
        width: Optional[int] = None,
        height: Optional[int] = None,
        keep_aspect_ratio: bool = True,
        output_format: str = 'png'
    ) -> Path:
        """
        Resize image
        
        - If only width: scale proportionally
        - If only height: scale proportionally  
        - If both: resize to exact dimensions or keep aspect ratio
        """
        img = self._load_image(input_path)
        original_width, original_height = img.size
        
        # Calculate new dimensions
        if width and height and keep_aspect_ratio:
            # Fit within bounds
            ratio = min(width / original_width, height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
        elif width and not height:
            ratio = width / original_width
            new_width = width
            new_height = int(original_height * ratio)
        elif height and not width:
            ratio = height / original_height
            new_width = int(original_width * ratio)
            new_height = height
        elif width and height:
            new_width = width
            new_height = height
        else:
            raise HTTPException(400, "Must specify at least width or height")
        
        # Resize with high quality
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save
        output_path = self.output_dir / f"{input_path.stem}_resized.{output_format}"
        img_resized.save(output_path, quality=95)
        
        return output_path
    
    # ==================== Crop ====================
    
    async def crop_image(
        self,
        input_path: Path,
        left: int,
        top: int,
        right: int,
        bottom: int,
        output_format: str = 'png'
    ) -> Path:
        """Crop image to specified rectangle"""
        img = self._load_image(input_path)
        
        # Validate crop box
        if left < 0 or top < 0 or right > img.width or bottom > img.height:
            raise HTTPException(400, f"Invalid crop box. Image size: {img.width}x{img.height}")
        
        if left >= right or top >= bottom:
            raise HTTPException(400, "Invalid crop box dimensions")
        
        # Crop
        img_cropped = img.crop((left, top, right, bottom))
        
        # Save
        output_path = self.output_dir / f"{input_path.stem}_cropped.{output_format}"
        img_cropped.save(output_path, quality=95)
        
        return output_path
    
    # ==================== Rotate ====================
    
    async def rotate_image(
        self,
        input_path: Path,
        angle: int,
        expand: bool = True,
        output_format: str = 'png'
    ) -> Path:
        """
        Rotate image by angle (degrees)
        
        - angle: rotation angle (positive = counter-clockwise)
        - expand: if True, expand image to fit rotated content
        """
        img = self._load_image(input_path)
        
        # Rotate
        img_rotated = img.rotate(angle, expand=expand, fillcolor=(255, 255, 255))
        
        # Save
        output_path = self.output_dir / f"{input_path.stem}_rotated.{output_format}"
        img_rotated.save(output_path, quality=95)
        
        return output_path
    
    # ==================== Format Conversion ====================
    
    async def convert_format(
        self,
        input_path: Path,
        output_format: str,
        quality: int = 95
    ) -> Path:
        """Convert image format (PNG, JPG, WebP, etc.)"""
        if output_format.lower() not in self.supported_formats:
            raise HTTPException(400, f"Unsupported format. Supported: {self.supported_formats}")
        
        img = self._load_image(input_path)
        
        # Handle WebP
        if output_format.lower() == 'webp':
            output_path = self.output_dir / f"{input_path.stem}.webp"
            img.save(output_path, 'WebP', quality=quality)
        else:
            output_path = self.output_dir / f"{input_path.stem}.{output_format}"
            img.save(output_path, quality=quality if output_format.lower() in ['jpg', 'jpeg'] else None)
        
        return output_path
    
    # ==================== AI Background Removal ====================
    
    async def remove_background(
        self,
        input_path: Path,
        output_format: str = 'png'
    ) -> Path:
        """
        Remove background using AI (rembg with U2-Net model)
        
        - Uses SOTA deep learning model
        - Preserves transparency (PNG)
        - Fast inference
        """
        # Read image
        with open(input_path, 'rb') as f:
            input_data = f.read()
        
        # Remove background (AI inference)
        output_data = remove(input_data)
        
        # Save
        output_path = self.output_dir / f"{input_path.stem}_no_bg.{output_format}"
        
        with open(output_path, 'wb') as f:
            f.write(output_data)
        
        return output_path
    
    # ==================== Image Enhancement ====================
    
    async def enhance_image(
        self,
        input_path: Path,
        brightness: float = 1.0,  # 1.0 = no change
        contrast: float = 1.0,
        saturation: float = 1.0,
        sharpness: float = 1.0,
        output_format: str = 'png'
    ) -> Path:
        """
        Enhance image quality
        
        - brightness: 0.0 to 2.0 (1.0 = original)
        - contrast: 0.0 to 2.0 (1.0 = original)
        - saturation: 0.0 to 2.0 (1.0 = original)
        - sharpness: 0.0 to 2.0 (1.0 = original)
        """
        img = self._load_image(input_path)
        
        # Apply enhancements
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness)
        
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)
        
        if saturation != 1.0:
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(saturation)
        
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(sharpness)
        
        # Save
        output_path = self.output_dir / f"{input_path.stem}_enhanced.{output_format}"
        img.save(output_path, quality=95)
        
        return output_path
    
    # ==================== Compression ====================
    
    async def compress_image(
        self,
        input_path: Path,
        quality: int = 85,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        output_format: str = 'jpg'
    ) -> Path:
        """
        Compress image for web
        
        - Reduces file size while maintaining quality
        - Optional resizing
        - Best for JPG/WebP
        """
        img = self._load_image(input_path)
        
        # Resize if needed
        if max_width or max_height:
            original_width, original_height = img.size
            
            if max_width and max_height:
                ratio = min(max_width / original_width, max_height / original_height)
            elif max_width:
                ratio = max_width / original_width
            else:
                ratio = max_height / original_height
            
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save with compression
        output_path = self.output_dir / f"{input_path.stem}_compressed.{output_format}"
        
        if output_format.lower() == 'webp':
            img.save(output_path, 'WebP', quality=quality, method=6)  # method=6 = best compression
        else:
            img.save(output_path, quality=quality, optimize=True)
        
        return output_path
    
    # ==================== Filters ====================
    
    async def apply_filter(
        self,
        input_path: Path,
        filter_name: str,
        output_format: str = 'png'
    ) -> Path:
        """
        Apply image filter
        
        Supported filters:
        - blur: Gaussian blur
        - sharpen: Sharpen filter
        - edge_enhance: Edge enhancement
        - smooth: Smooth filter
        - grayscale: Convert to grayscale
        """
        img = self._load_image(input_path)
        
        # Apply filter
        if filter_name == 'blur':
            img = img.filter(ImageFilter.GaussianBlur(radius=5))
        elif filter_name == 'sharpen':
            img = img.filter(ImageFilter.SHARPEN)
        elif filter_name == 'edge_enhance':
            img = img.filter(ImageFilter.EDGE_ENHANCE)
        elif filter_name == 'smooth':
            img = img.filter(ImageFilter.SMOOTH)
        elif filter_name == 'grayscale':
            img = img.convert('L').convert('RGB')
        else:
            raise HTTPException(400, f"Unknown filter: {filter_name}")
        
        # Save
        output_path = self.output_dir / f"{input_path.stem}_{filter_name}.{output_format}"
        img.save(output_path, quality=95)
        
        return output_path
    
    # ==================== Info ====================
    
    async def get_image_info(self, input_path: Path) -> dict:
        """Get image information"""
        img = Image.open(input_path)
        
        return {
            "format": img.format,
            "mode": img.mode,
            "width": img.width,
            "height": img.height,
            "file_size_bytes": input_path.stat().st_size,
            "has_transparency": img.mode in ('RGBA', 'LA', 'P'),
        }
    
    # ==================== Cleanup ====================
    
    async def cleanup_file(self, file_path: Path) -> None:
        """Delete a file"""
        if file_path.exists():
            file_path.unlink()
