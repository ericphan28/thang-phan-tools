"""
Modern Image Processing API Endpoints (2025)
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import Optional

from app.services.image_service import ImageService

router = APIRouter(tags=["Image Processing"])

# Initialize service
img_service = ImageService()


@router.post("/resize")
async def resize_image(
    file: UploadFile = File(..., description="Image file"),
    width: Optional[int] = Form(None, description="Target width (pixels)"),
    height: Optional[int] = Form(None, description="Target height (pixels)"),
    keep_aspect_ratio: bool = Form(True, description="Keep aspect ratio"),
    output_format: str = Form("png", description="Output format (png, jpg, webp)"),
):
    """
    Resize image
    
    **Examples:**
    - `width=800` only → Scale proportionally to 800px width
    - `height=600` only → Scale proportionally to 600px height
    - `width=800, height=600, keep_aspect_ratio=True` → Fit within 800x600
    - `width=800, height=600, keep_aspect_ratio=False` → Exact 800x600 (may stretch)
    """
    input_path = await img_service.save_upload_file(file)
    
    try:
        output_path = await img_service.resize_image(
            input_path, width, height, keep_aspect_ratio, output_format
        )
        
        return FileResponse(
            path=output_path,
            media_type=f"image/{output_format}",
            filename=output_path.name
        )
    finally:
        await img_service.cleanup_file(input_path)


@router.post("/crop")
async def crop_image(
    file: UploadFile = File(..., description="Image file"),
    left: int = Form(..., description="Left coordinate"),
    top: int = Form(..., description="Top coordinate"),
    right: int = Form(..., description="Right coordinate"),
    bottom: int = Form(..., description="Bottom coordinate"),
    output_format: str = Form("png", description="Output format"),
):
    """
    Crop image to rectangle
    
    **Coordinates:**
    - (0, 0) = top-left corner
    - Crop box: (left, top) to (right, bottom)
    """
    input_path = await img_service.save_upload_file(file)
    
    try:
        output_path = await img_service.crop_image(
            input_path, left, top, right, bottom, output_format
        )
        
        return FileResponse(
            path=output_path,
            media_type=f"image/{output_format}",
            filename=output_path.name
        )
    finally:
        await img_service.cleanup_file(input_path)


@router.post("/rotate")
async def rotate_image(
    file: UploadFile = File(..., description="Image file"),
    angle: int = Form(90, description="Rotation angle (degrees, counter-clockwise)"),
    expand: bool = Form(True, description="Expand canvas to fit rotated image"),
    output_format: str = Form("png", description="Output format"),
):
    """
    Rotate image
    
    **Common angles:**
    - 90 = rotate 90° counter-clockwise
    - 180 = rotate 180°
    - 270 = rotate 90° clockwise
    - -90 = rotate 90° clockwise
    """
    input_path = await img_service.save_upload_file(file)
    
    try:
        output_path = await img_service.rotate_image(
            input_path, angle, expand, output_format
        )
        
        return FileResponse(
            path=output_path,
            media_type=f"image/{output_format}",
            filename=output_path.name
        )
    finally:
        await img_service.cleanup_file(input_path)


@router.post("/convert")
async def convert_format(
    file: UploadFile = File(..., description="Image file"),
    output_format: str = Form(..., description="Target format (png, jpg, webp, bmp, gif)"),
    quality: int = Form(95, ge=1, le=100, description="JPEG quality (1-100)"),
):
    """
    Convert image format
    
    **Supported formats:**
    - PNG: Lossless, supports transparency
    - JPG/JPEG: Lossy compression, smaller files
    - WebP: Modern format, best compression
    - BMP: Uncompressed bitmap
    - GIF: Animated images
    - HEIC/HEIF: iPhone photos (input only)
    """
    input_path = await img_service.save_upload_file(file)
    
    try:
        output_path = await img_service.convert_format(
            input_path, output_format, quality
        )
        
        return FileResponse(
            path=output_path,
            media_type=f"image/{output_format}",
            filename=output_path.name
        )
    finally:
        await img_service.cleanup_file(input_path)


@router.post("/remove-background")
async def remove_background(
    file: UploadFile = File(..., description="Image file"),
    output_format: str = Form("png", description="Output format (png recommended for transparency)"),
):
    """
    Remove background using AI
    
    - Uses **U2-Net** deep learning model (SOTA)
    - Automatically detects and removes background
    - Returns transparent PNG
    - Works best with clear subjects (people, objects, products)
    
    **Use cases:**
    - Product photos for e-commerce
    - Profile pictures
    - Photo editing
    """
    input_path = await img_service.save_upload_file(file)
    
    try:
        output_path = await img_service.remove_background(
            input_path, output_format
        )
        
        return FileResponse(
            path=output_path,
            media_type=f"image/{output_format}",
            filename=output_path.name
        )
    finally:
        await img_service.cleanup_file(input_path)


@router.post("/enhance")
async def enhance_image(
    file: UploadFile = File(..., description="Image file"),
    brightness: float = Form(1.0, ge=0.0, le=2.0, description="Brightness (0.0-2.0, 1.0=original)"),
    contrast: float = Form(1.0, ge=0.0, le=2.0, description="Contrast (0.0-2.0, 1.0=original)"),
    saturation: float = Form(1.0, ge=0.0, le=2.0, description="Color saturation (0.0-2.0, 1.0=original)"),
    sharpness: float = Form(1.0, ge=0.0, le=2.0, description="Sharpness (0.0-2.0, 1.0=original)"),
    output_format: str = Form("png", description="Output format"),
):
    """
    Enhance image quality
    
    **Parameters:**
    - `brightness`: 0.0 = black, 1.0 = original, 2.0 = very bright
    - `contrast`: 0.0 = gray, 1.0 = original, 2.0 = high contrast
    - `saturation`: 0.0 = grayscale, 1.0 = original, 2.0 = vivid colors
    - `sharpness`: 0.0 = blurred, 1.0 = original, 2.0 = sharp
    
    **Example:** Brighten dark photo:
    ```
    brightness=1.3, contrast=1.2, saturation=1.1, sharpness=1.1
    ```
    """
    input_path = await img_service.save_upload_file(file)
    
    try:
        output_path = await img_service.enhance_image(
            input_path, brightness, contrast, saturation, sharpness, output_format
        )
        
        return FileResponse(
            path=output_path,
            media_type=f"image/{output_format}",
            filename=output_path.name
        )
    finally:
        await img_service.cleanup_file(input_path)


@router.post("/compress")
async def compress_image(
    file: UploadFile = File(..., description="Image file"),
    quality: int = Form(85, ge=1, le=100, description="Compression quality (1-100)"),
    max_width: Optional[int] = Form(None, description="Max width (optional resize)"),
    max_height: Optional[int] = Form(None, description="Max height (optional resize)"),
    output_format: str = Form("jpg", description="Output format (jpg or webp recommended)"),
):
    """
    Compress image for web
    
    - Reduces file size while maintaining visual quality
    - Optional resizing for further compression
    - Best with JPG or WebP format
    
    **Example:** Compress for web upload:
    ```
    quality=85, max_width=1920, output_format=webp
    ```
    
    **Typical quality values:**
    - 95-100: Maximum quality (large files)
    - 85-94: High quality (recommended for web)
    - 70-84: Medium quality (smaller files)
    - <70: Low quality (very small files, visible artifacts)
    """
    input_path = await img_service.save_upload_file(file)
    
    try:
        output_path = await img_service.compress_image(
            input_path, quality, max_width, max_height, output_format
        )
        
        return FileResponse(
            path=output_path,
            media_type=f"image/{output_format}",
            filename=output_path.name
        )
    finally:
        await img_service.cleanup_file(input_path)


@router.post("/filter")
async def apply_filter(
    file: UploadFile = File(..., description="Image file"),
    filter_name: str = Form(..., description="Filter name"),
    output_format: str = Form("png", description="Output format"),
):
    """
    Apply image filter
    
    **Available filters:**
    - `blur`: Gaussian blur effect
    - `sharpen`: Make image sharper
    - `edge_enhance`: Enhance edges
    - `smooth`: Smooth filter
    - `grayscale`: Convert to black & white
    
    **Example:**
    ```
    filter_name=grayscale
    ```
    """
    input_path = await img_service.save_upload_file(file)
    
    try:
        output_path = await img_service.apply_filter(
            input_path, filter_name, output_format
        )
        
        return FileResponse(
            path=output_path,
            media_type=f"image/{output_format}",
            filename=output_path.name
        )
    finally:
        await img_service.cleanup_file(input_path)


@router.post("/info")
async def get_image_info(
    file: UploadFile = File(..., description="Image file"),
):
    """
    Get image information
    
    Returns:
    - Format (PNG, JPEG, etc.)
    - Color mode (RGB, RGBA, etc.)
    - Dimensions (width x height)
    - File size
    - Has transparency
    """
    input_path = await img_service.save_upload_file(file)
    
    try:
        info = await img_service.get_image_info(input_path)
        return {"filename": file.filename, **info}
    finally:
        await img_service.cleanup_file(input_path)
