"""
Modern OCR Service (2025)
Uses Tesseract OCR - Fast and reliable OCR supporting Vietnamese and multiple languages
EasyOCR disabled to avoid PyTorch (900MB) dependency
"""

from pathlib import Path
from typing import List, Optional, Tuple
# import easyocr  # DISABLED: Requires PyTorch (900MB)
import pytesseract
from PIL import Image
from fastapi import UploadFile, HTTPException
import aiofiles


class OCRService:
    """
    Modern OCR service using Tesseract
    
    Supports:
    - Vietnamese (vie)
    - English (eng)
    - Multiple other languages via Tesseract
    
    Note: EasyOCR disabled to avoid PyTorch (900MB) dependency
    """
    
    def __init__(self, upload_dir: str = "uploads/ocr"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_tesseract_config(self, languages: List[str]) -> str:
        """Convert language codes to Tesseract format"""
        # Map common codes to Tesseract codes
        lang_map = {
            'vi': 'vie',
            'en': 'eng',
            'zh': 'chi_sim',
            'ja': 'jpn',
            'ko': 'kor'
        }
        
        tesseract_langs = [lang_map.get(lang, lang) for lang in languages]
        return '+'.join(tesseract_langs)
    
    async def save_upload_file(self, upload_file: UploadFile) -> Path:
        """Save uploaded image"""
        file_path = self.upload_dir / upload_file.filename
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await upload_file.read()
            await out_file.write(content)
            
        return file_path
    
    # ==================== OCR Detection ====================
    
    async def extract_text(
        self,
        input_path: Path,
        languages: List[str] = ['vi', 'en'],
        detail: int = 1,  # 0=simple text, 1=bounding box + confidence
        paragraph: bool = False,
        gpu: bool = False  # Ignored for Tesseract compatibility
    ) -> dict:
        """
        Extract text from image using Tesseract OCR
        
        Args:
            input_path: Image file path
            languages: List of language codes (e.g., ['vi', 'en'])
            detail: 0=text only, 1=bounding box + confidence
            paragraph: Group text into paragraphs (not used)
            gpu: Ignored (kept for API compatibility)
        
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Open image
            image = Image.open(input_path)
            
            # Get Tesseract language config
            lang_config = self._get_tesseract_config(languages)
            
            if detail == 0:
                # Simple text extraction
                text = pytesseract.image_to_string(image, lang=lang_config)
                
                return {
                    "text": text.strip(),
                    "languages": languages,
                    "num_detections": len([line for line in text.split('\n') if line.strip()])
                }
            else:
                # Detailed with bounding boxes and confidence
                data = pytesseract.image_to_data(image, lang=lang_config, output_type=pytesseract.Output.DICT)
                
                formatted_results = []
                full_text = []
                
                n_boxes = len(data['text'])
                for i in range(n_boxes):
                    text = data['text'][i].strip()
                    if text:  # Skip empty detections
                        conf = float(data['conf'][i]) / 100.0  # Convert to 0-1 scale
                        
                        # Get bounding box
                        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                        
                        formatted_results.append({
                            "text": text,
                            "confidence": conf if conf >= 0 else 0.0,
                            "bbox": {
                                "top_left": [x, y],
                                "top_right": [x + w, y],
                                "bottom_right": [x + w, y + h],
                                "bottom_left": [x, y + h]
                            }
                        })
                        full_text.append(text)
                
                return {
                    "text": " ".join(full_text),
                    "languages": languages,
                    "num_detections": len(formatted_results),
                    "detections": formatted_results,
                    "avg_confidence": sum(d["confidence"] for d in formatted_results) / len(formatted_results) if formatted_results else 0
                }
                
        except Exception as e:
            raise HTTPException(500, f"OCR failed: {str(e)}")
    
    # ==================== Vietnamese Specific ====================
    
    async def extract_vietnamese_text(
        self,
        input_path: Path,
        include_english: bool = True,
        gpu: bool = False
    ) -> dict:
        """
        Extract Vietnamese text (optimized for Vietnamese)
        
        Args:
            input_path: Image file path
            include_english: Also detect English text
            gpu: Use GPU acceleration
        
        Returns:
            Dictionary with Vietnamese text and metadata
        """
        languages = ['vi']
        if include_english:
            languages.append('en')
        
        return await self.extract_text(
            input_path,
            languages=languages,
            detail=1,
            gpu=gpu
        )
    
    # ==================== Multi-language ====================
    
    async def detect_language_and_extract(
        self,
        input_path: Path,
        gpu: bool = False
    ) -> dict:
        """
        Auto-detect language and extract text
        
        Tries common language combinations:
        1. Vietnamese + English
        2. English only
        3. Chinese + English
        """
        # Try Vietnamese first (most common in Vietnam)
        try:
            result = await self.extract_text(
                input_path,
                languages=['vi', 'en'],
                detail=1,
                gpu=gpu
            )
            
            if result['avg_confidence'] > 0.5:
                result['detected_languages'] = ['vi', 'en']
                return result
        except:
            pass
        
        # Try English only
        try:
            result = await self.extract_text(
                input_path,
                languages=['en'],
                detail=1,
                gpu=gpu
            )
            
            if result['avg_confidence'] > 0.5:
                result['detected_languages'] = ['en']
                return result
        except:
            pass
        
        # Fallback: Vietnamese + English (best effort)
        result = await self.extract_text(
            input_path,
            languages=['vi', 'en'],
            detail=1,
            gpu=gpu
        )
        result['detected_languages'] = ['vi', 'en']
        return result
    
    # ==================== Cleanup ====================
    
    async def cleanup_file(self, file_path: Path) -> None:
        """Delete a file"""
        if file_path.exists():
            file_path.unlink()
