"""
Direct test of PDF to Word without API
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from pathlib import Path
from app.services.document_service import DocumentService

async def test():
    # Create service
    service = DocumentService()
    
    # Test file
    test_pdf = Path("test_pdf_with_text.pdf")
    if not test_pdf.exists():
        print("Test PDF not found")
        return
    
    print("Testing PDF to Word Smart...")
    
    try:
        # Call method directly with Path
        result = await service.pdf_to_word_smart(
            input_file=test_pdf,
            language="vi"
        )
        
        print(f"SUCCESS! Output: {result}")
        
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
