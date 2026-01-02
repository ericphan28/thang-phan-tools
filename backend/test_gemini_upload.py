"""Test Gemini PDF upload functionality"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.ai_usage_service import get_api_key
import google.generativeai as genai

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Get API key
api_key = get_api_key('gemini', db)
print(f"✅ Gemini API key exists: {bool(api_key)}")
if api_key:
    print(f"✅ Key prefix: {api_key[:20]}...")
    
    # Configure genai
    genai.configure(api_key=api_key)
    print("✅ Genai configured")
    
    # Try to upload a test PDF (use any existing PDF)
    test_pdf = Path(__file__).parent.parent / "test_pdf_with_text.pdf"
    
    if test_pdf.exists():
        print(f"📄 Test PDF: {test_pdf}")
        try:
            print("📤 Uploading PDF to Gemini...")
            uploaded_file = genai.upload_file(str(test_pdf), mime_type="application/pdf")
            print(f"✅ Upload successful! File: {uploaded_file.name}")
            print(f"📊 State: {uploaded_file.state.name}")
            
            # Wait for processing
            import time
            while uploaded_file.state.name == "PROCESSING":
                print("⏳ Processing...")
                time.sleep(1)
                uploaded_file = genai.get_file(uploaded_file.name)
            
            print(f"✅ Final state: {uploaded_file.state.name}")
            
            # Test generation
            if uploaded_file.state.name == "ACTIVE":
                print("💬 Testing content generation...")
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content([
                    "Extract all text from this PDF",
                    uploaded_file
                ])
                print(f"✅ Response received! Length: {len(response.text)}")
                print(f"📝 First 200 chars: {response.text[:200]}")
                
                # Cleanup
                genai.delete_file(uploaded_file.name)
                print("✅ File deleted")
            else:
                print(f"❌ Upload failed: {uploaded_file.state.name}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ No test PDF found at {test_pdf}")
else:
    print("❌ No Gemini API key found in database!")

db.close()
