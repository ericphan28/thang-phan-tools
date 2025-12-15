import os
import uuid
import base64
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from fastapi import HTTPException
import google.generativeai as genai
from python_docx import Document
from python_docx.shared import Inches
from python_docx.enum.text import WD_ALIGN_PARAGRAPH
import fitz  # PyMuPDF

# Setup logging
logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, output_dir: Path, adobe_credentials: Dict[str, Any] = None):
        self.output_dir = output_dir
        self.adobe_credentials = adobe_credentials
        self.output_dir.mkdir(exist_ok=True)
        
        # Configure Gemini API
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        logger.info(f"DocumentService initialized with output directory: {output_dir}")

    async def pdf_to_word_with_gemini(self, input_file: Path, output_filename: Optional[str] = None) -> Path:
        """
        Convert PDF to Word using Gemini API - Simple approach
        """
        if input_file.suffix.lower() != '.pdf':
            raise HTTPException(400, "File must be .pdf")
        
        output_filename = output_filename or input_file.stem + ".docx"
        output_path = self.output_dir / output_filename
        
        try:
            logger.info(f"Converting PDF to Word with Gemini: {input_file}")
            
            # Read and upload PDF to Gemini
            with open(input_file, 'rb') as f:
                pdf_data = f.read()
            
            # Upload to Gemini
            pdf_file = genai.upload_file(input_file, mime_type="application/pdf")
            logger.info(f"Uploaded PDF to Gemini successfully")
            
            # Simple, natural prompt
            prompt = """
Hãy trích xuất toàn bộ nội dung văn bản từ PDF này. 
Giữ nguyên định dạng và cấu trúc của tài liệu.
Trả về JSON với format:
{
  "content": [
    {
      "type": "paragraph",
      "text": "nội dung đoạn văn"
    }
  ]
}
"""
            
            # Send to Gemini
            response = self.gemini_model.generate_content([pdf_file, prompt])
            logger.info("Received response from Gemini")
            
            if not response or not response.text:
                raise HTTPException(500, "Gemini API returned empty response")
            
            # Parse response
            import json
            try:
                # Clean the response text
                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                
                response_data = json.loads(response_text)
                logger.info(f"Successfully parsed Gemini response: {len(response_data.get('content', []))} items")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                logger.error(f"Response text: {response_text[:500]}")
                raise HTTPException(500, "Invalid JSON response from Gemini")
            
            # Create Word document
            await self._create_word_from_json(response_data, output_path)
            
            logger.info(f"Successfully created Word document: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error in PDF to Word conversion: {str(e)}")
            logger.exception("Full error details:")
            raise HTTPException(500, f"PDF to Word conversion failed: {str(e)}")
    
    async def _create_word_from_json(self, data: Dict[str, Any], output_path: Path):
        """Create Word document from JSON data"""
        try:
            doc = Document()
            
            content_items = data.get('content', [])
            if not content_items:
                logger.warning("No content items found in response")
                # Add a placeholder paragraph
                doc.add_paragraph("Không thể trích xuất nội dung từ PDF.")
                doc.save(str(output_path))
                return
            
            for item in content_items:
                if isinstance(item, dict):
                    text = item.get('text', '').strip()
                    item_type = item.get('type', 'paragraph')
                    
                    if text:
                        if item_type in ['header', 'heading']:
                            doc.add_heading(text, level=1)
                        else:
                            doc.add_paragraph(text)
                elif isinstance(item, str):
                    # Handle direct string content
                    doc.add_paragraph(item.strip())
            
            doc.save(str(output_path))
            logger.info(f"Word document saved successfully: {output_path}")
            
        except Exception as e:
            logger.error(f"Error creating Word document: {str(e)}")
            logger.exception("Full error details:")
            raise