"""
Gemini Service - Auto-logging wrapper for all Gemini API calls

Usage:
    from app.services.gemini_service import GeminiService
    
    gemini = GeminiService(db)
    response = gemini.generate_content(prompt, model="gemini-2.5-flash")
    # ✅ Auto-logged to database!
"""
import google.generativeai as genai
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
import time
from datetime import datetime
from pathlib import Path

from app.core.config import settings
from app.services.ai_usage_service import log_usage, get_api_key
from app.services.gemini_key_service import GeminiKeyService
from app.schemas.gemini_keys import UsageLogCreate, UsageStatusEnum


class GeminiService:
    """
    Wrapper for Gemini API with automatic usage logging
    
    Features:
    - Auto-logs every API call to database
    - Tracks tokens, cost, processing time
    - Handles errors and logs them
    - Zero-config - just use it like normal Gemini SDK
    - NEW: Auto key selection & rotation from database
    """
    
    def __init__(self, db: Session, user_id: Optional[int] = None):
        """
        Initialize Gemini service with auto-logging
        
        Args:
            db: SQLAlchemy database session
            user_id: Optional user ID for tracking
        """
        self.db = db
        self.user_id = user_id
        self.key_service = GeminiKeyService(db)
        
        # Get API key from database ONLY (no fallback to .env)
        selected_key = self.key_service.select_best_key()
        if not selected_key:
            raise ValueError(
                "Không tìm thấy Gemini API key nào khả dụng. "
                "Vui lòng thêm key tại Admin > AI Keys."
            )
        
        api_key = selected_key.api_key_decrypted
        self.current_key_id = selected_key.id
        
        # Configure Gemini
        genai.configure(api_key=api_key)
    
    def generate_content(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash",
        operation: str = "generate",
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """
        Generate content with Gemini - AUTO-LOGGED
        
        Args:
            prompt: The prompt to send
            model: Model name (gemini-2.5-flash, gemini-2.5-pro, etc.)
            operation: Operation name for logging (e.g., "text-to-word", "ocr", etc.)
            metadata: Additional metadata to log
            **kwargs: Additional arguments for generate_content
        
        Returns:
            GenerateContentResponse object
        
        Raises:
            Exception: If API call fails
        """
        start_time = time.time()
        error_message = None
        response = None
        
        try:
            # Create model
            model_obj = genai.GenerativeModel(model)
            
            # Generate content
            response = model_obj.generate_content(prompt, **kwargs)
            
            # Extract token usage
            input_tokens = response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0
            output_tokens = response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Log success
            log_usage(
                db=self.db,
                provider="gemini",
                model=model,
                endpoint=operation,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                processing_time=processing_time,
                status="success",
                user_id=self.user_id,
                request_metadata=metadata
            )
            
            return response
            
        except Exception as e:
            error_message = str(e)
            processing_time = time.time() - start_time
            
            # Log error
            log_usage(
                db=self.db,
                provider="gemini",
                model=model,
                endpoint=operation,
                input_tokens=0,
                output_tokens=0,
                processing_time=processing_time,
                status="error",
                error_message=error_message,
                user_id=self.user_id,
                request_metadata=metadata
            )
            
            # Re-raise exception
            raise
    
    def generate_content_stream(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash",
        operation: str = "generate-stream",
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Generate content with streaming - AUTO-LOGGED
        
        Note: Token counting for streaming is done at the end
        
        Args:
            prompt: The prompt to send
            model: Model name
            operation: Operation name for logging
            metadata: Additional metadata
            **kwargs: Additional arguments
        
        Yields:
            Content chunks
        """
        start_time = time.time()
        error_message = None
        total_input_tokens = 0
        total_output_tokens = 0
        
        try:
            # Create model
            model_obj = genai.GenerativeModel(model)
            
            # Generate content with streaming
            response_stream = model_obj.generate_content(prompt, stream=True, **kwargs)
            
            # Yield chunks and collect token counts
            for chunk in response_stream:
                if hasattr(chunk, 'usage_metadata'):
                    total_input_tokens = chunk.usage_metadata.prompt_token_count
                    total_output_tokens = chunk.usage_metadata.candidates_token_count
                yield chunk
            
            # Log after stream completes
            processing_time = time.time() - start_time
            log_usage(
                db=self.db,
                provider="gemini",
                model=model,
                endpoint=operation,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
                processing_time=processing_time,
                status="success",
                user_id=self.user_id,
                request_metadata=metadata
            )
            
        except Exception as e:
            error_message = str(e)
            processing_time = time.time() - start_time
            
            # Log error
            log_usage(
                db=self.db,
                provider="gemini",
                model=model,
                endpoint=operation,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
                processing_time=processing_time,
                status="error",
                error_message=error_message,
                user_id=self.user_id,
                request_metadata=metadata
            )
            
            raise
    
    def count_tokens(self, text: str, model: str = "gemini-2.5-flash") -> int:
        """
        Count tokens in text - NOT LOGGED (free operation)
        
        Args:
            text: Text to count
            model: Model name
        
        Returns:
            Token count
        """
        model_obj = genai.GenerativeModel(model)
        return model_obj.count_tokens(text).total_tokens
    
    def list_models(self) -> List[str]:
        """
        List available Gemini models - NOT LOGGED (free operation)
        
        Returns:
            List of model names
        """
        models = genai.list_models()
        return [m.name for m in models if 'generateContent' in m.supported_generation_methods]
    
    def generate_content_with_pdf(
        self,
        prompt: str,
        pdf_path: str,
        model: str = "gemini-2.5-flash",
        operation: str = "pdf_extraction",
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """
        Generate content with PDF upload - AUTO-LOGGED
        
        Gemini 2.5 supports direct PDF upload without image conversion!
        Much faster and more efficient than page-by-page image OCR.
        
        Args:
            prompt: Text prompt for extraction
            pdf_path: Path to PDF file
            model: Model name (gemini-2.5-flash recommended)
            operation: Operation name for logging
            metadata: Additional metadata
            **kwargs: Additional arguments
        
        Returns:
            GenerateContentResponse
        """
        start_time = time.time()
        error_message = None
        response = None
        uploaded_file = None
        
        try:
            # Upload PDF to Gemini (with fallback for older library versions)
            print(f"\n{'='*80}", flush=True)
            print(f"🚀 GEMINI PDF UPLOAD - START", flush=True)
            print(f"📄 File: {Path(pdf_path).name}", flush=True)
            print(f"{'='*80}\n", flush=True)
            
            # Check if upload_file is available (newer versions)
            if hasattr(genai, 'upload_file'):
                print("📤 Using genai.upload_file() method (recommended)", flush=True)
                uploaded_file = genai.upload_file(pdf_path, mime_type="application/pdf")
                print(f"✅ File uploaded to Gemini: {uploaded_file.name}", flush=True)
                
                # Wait for processing
                import time as time_module
                while uploaded_file.state.name == "PROCESSING":
                    print("⏳ Waiting for Gemini to process PDF...", flush=True)
                    time_module.sleep(1)
                    uploaded_file = genai.get_file(uploaded_file.name)
                
                if uploaded_file.state.name == "FAILED":
                    raise ValueError(f"PDF upload failed: {uploaded_file.state}")
                
                # Create model
                model_obj = genai.GenerativeModel(model)
                print(f"🤖 Model created: {model}", flush=True)
                
                # Generate content with PDF
                print(f"💬 Sending prompt + PDF to Gemini...", flush=True)
                response = model_obj.generate_content([prompt, uploaded_file], **kwargs)
                
            else:
                # Fallback for older versions: use base64 encoding
                print("📤 Using base64 fallback method (older library version)", flush=True)
                import base64
                
                # Read PDF and encode to base64
                with open(pdf_path, 'rb') as f:
                    pdf_bytes = f.read()
                    pdf_base64 = base64.b64encode(pdf_bytes).decode()
                
                print(f"📄 PDF encoded: {len(pdf_base64)} characters", flush=True)
                
                # Create content with inline data
                model_obj = genai.GenerativeModel(model)
                print(f"🤖 Model created: {model}", flush=True)
                
                print(f"💬 Sending prompt + PDF (base64) to Gemini...", flush=True)
                response = model_obj.generate_content([
                    prompt,
                    {
                        "mime_type": "application/pdf",
                        "data": pdf_base64
                    }
                ], **kwargs)
            
            print(f"✅ Gemini response received!", flush=True)
            
            # DEBUG: Log response text to check [VSPAN=N] markers
            response_text = response.text
            print(f"\n{'='*80}", flush=True)
            print(f"📄 GEMINI RESPONSE TEXT (FULL - searching for TABLE blocks):", flush=True)
            print(f"{'='*80}", flush=True)
            
            # Find all [TABLE]...[/TABLE] blocks
            import re
            table_blocks = re.findall(r'\[TABLE\](.*?)\[/TABLE\]', response_text, re.DOTALL)
            if table_blocks:
                print(f"🔍 Found {len(table_blocks)} TABLE blocks", flush=True)
                for i, table in enumerate(table_blocks, 1):
                    print(f"\n{'='*80}", flush=True)
                    print(f"📊 TABLE {i} (first 5000 chars):", flush=True)
                    print(f"{'='*80}", flush=True)
                    print(table[:5000], flush=True)
                    
                    # Count [VSPAN=] markers in this table
                    vspan_markers = re.findall(r'\[VSPAN=(\d+)\]', table)
                    if vspan_markers:
                        print(f"\n🔍 VSPAN markers in TABLE {i}: {vspan_markers}", flush=True)
                        print(f"   Max VSPAN: {max(int(x) for x in vspan_markers)}", flush=True)
                    print(f"{'='*80}", flush=True)
            else:
                print(f"⚠️ NO [TABLE] blocks found!", flush=True)
                print(f"Response length: {len(response_text)} chars", flush=True)
                print(f"First 5000 chars:\n{response_text[:5000]}", flush=True)
            print(f"\n{'='*80}\n", flush=True)
            
            # Extract token usage
            input_tokens = response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0
            output_tokens = response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            print(f"✅ SUCCESS - PDF processed in {processing_time:.2f}s", flush=True)
            print(f"📊 Tokens: {input_tokens} in / {output_tokens} out", flush=True)
            print(f"💰 Cost: ~${(input_tokens * 0.00000125 + output_tokens * 0.00000500):.4f}", flush=True)
            print(f"{'='*80}\n", flush=True)
            
            # Log success
            log_usage(
                db=self.db,
                provider="gemini",
                model=model,
                endpoint=operation,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                processing_time=processing_time,
                status="success",
                user_id=self.user_id,
                request_metadata=metadata
            )
            
            return response
            
        except Exception as e:
            error_message = str(e)
            processing_time = time.time() - start_time
            
            # Log error
            log_usage(
                db=self.db,
                provider="gemini",
                model=model,
                endpoint=operation,
                input_tokens=0,
                output_tokens=0,
                processing_time=processing_time,
                status="error",
                error_message=error_message,
                user_id=self.user_id,
                request_metadata=metadata
            )
            
            raise
        finally:
            # Cleanup uploaded file (only if using upload_file method)
            if uploaded_file and hasattr(genai, 'delete_file'):
                try:
                    genai.delete_file(uploaded_file.name)
                    print(f"🗑️ Cleaned up uploaded file: {uploaded_file.name}", flush=True)
                except Exception as cleanup_error:
                    print(f"⚠️ Cleanup warning: {cleanup_error}", flush=True)
                    pass  # Ignore cleanup errors
    
    def generate_content_with_image(
        self,
        prompt: str,
        image_base64: str,
        model: str = "gemini-2.5-flash",
        operation: str = "vision",
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """
        Generate content with image (Gemini Vision) - AUTO-LOGGED
        
        Args:
            prompt: Text prompt
            image_base64: Base64 encoded image (PNG/JPEG)
            model: Model name (must support vision, e.g., gemini-2.5-flash)
            operation: Operation name for logging
            metadata: Additional metadata
            **kwargs: Additional arguments
        
        Returns:
            GenerateContentResponse
        """
        import google.generativeai as genai
        from PIL import Image
        import io
        import base64
        
        start_time = time.time()
        error_message = None
        response = None
        
        try:
            # Decode base64 image
            img_bytes = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(img_bytes))
            
            # Create model (must support vision)
            model_obj = genai.GenerativeModel(model)
            
            # Generate content with image
            response = model_obj.generate_content([prompt, image], **kwargs)
            
            # Extract token usage
            input_tokens = response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0
            output_tokens = response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Log success
            log_usage(
                db=self.db,
                provider="gemini",
                model=model,
                endpoint=operation,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                processing_time=processing_time,
                status="success",
                user_id=self.user_id,
                request_metadata=metadata
            )
            
            return response
            
        except Exception as e:
            error_message = str(e)
            processing_time = time.time() - start_time
            
            # Log error
            log_usage(
                db=self.db,
                provider="gemini",
                model=model,
                endpoint=operation,
                input_tokens=0,
                output_tokens=0,
                processing_time=processing_time,
                status="error",
                error_message=error_message,
                user_id=self.user_id,
                request_metadata=metadata
            )
            
            # Re-raise exception
            raise
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Tính cost dựa trên pricing của Gemini models
        Pricing (Jan 2026): https://ai.google.dev/pricing
        """
        # Pricing per 1M tokens (USD)
        PRICING = {
            "gemini-2.5-flash": {"input": 0.30, "output": 2.50},
            "gemini-2.5-flash-lite": {"input": 0.10, "output": 0.40},
            "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
            "gemini-2.0-flash-vision": {"input": 0.30, "output": 2.50},
            "gemini-2.0-flash": {"input": 0.30, "output": 2.50},
        }
        
        # Default pricing if model not found
        default_pricing = {"input": 0.30, "output": 2.50}
        pricing = PRICING.get(model, default_pricing)
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return round(input_cost + output_cost, 6)


# Convenience function for quick usage
def get_gemini_service(db: Session, user_id: Optional[int] = None) -> GeminiService:
    """
    Get Gemini service with auto-logging
    
    Example:
        gemini = get_gemini_service(db, user_id=1)
        response = gemini.generate_content("Hello")
    """
    return GeminiService(db, user_id)
