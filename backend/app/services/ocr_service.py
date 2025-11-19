"""
Modern OCR Service (2025)
Uses EasyOCR - Deep Learning OCR supporting 80+ languages including Vietnamese
"""

from pathlib import Path
from typing import List, Optional, Tuple
import easyocr
from fastapi import UploadFile, HTTPException
import aiofiles


class OCRService:
    """
    Modern OCR service with deep learning
    
    Supports:
    - Vietnamese (vi)
    - English (en)
    - Chinese (ch_sim, ch_tra)
    - Japanese (ja)
    - Korean (ko)
    - And 75+ more languages!
    """
    
    def __init__(self, upload_dir: str = "uploads/ocr"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize readers (lazy loading)
        self._readers = {}
    
    def _get_reader(self, languages: List[str], gpu: bool = False) -> easyocr.Reader:
        """Get or create EasyOCR reader for specific languages"""
        lang_key = tuple(sorted(languages))
        
        if lang_key not in self._readers:
            # Create new reader
            self._readers[lang_key] = easyocr.Reader(
                lang_list=languages,
                gpu=gpu,  # Set to True if CUDA available
                model_storage_directory='models/easyocr',
                download_enabled=True
            )
            
        return self._readers[lang_key]
    
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
        gpu: bool = False
    ) -> dict:
        """
        Extract text from image using deep learning OCR
        
        Args:
            input_path: Image file path
            languages: List of language codes (e.g., ['vi', 'en'])
            detail: 0=text only, 1=bounding box + confidence, 2=detailed
            paragraph: Group text into paragraphs
            gpu: Use GPU acceleration (requires CUDA)
        
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            reader = self._get_reader(languages, gpu)
            
            # Perform OCR
            results = reader.readtext(
                str(input_path),
                detail=detail,
                paragraph=paragraph
            )
            
            # Format results
            if detail == 0:
                # Simple text list
                return {
                    "text": "\n".join(results),
                    "languages": languages,
                    "num_detections": len(results)
                }
            else:
                # Detailed with bounding boxes
                formatted_results = []
                full_text = []
                
                for detection in results:
                    bbox, text, confidence = detection
                    
                    formatted_results.append({
                        "text": text,
                        "confidence": float(confidence),
                        "bbox": {
                            "top_left": bbox[0],
                            "top_right": bbox[1],
                            "bottom_right": bbox[2],
                            "bottom_left": bbox[3]
                        }
                    })
                    full_text.append(text)
                
                return {
                    "text": "\n".join(full_text),
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
