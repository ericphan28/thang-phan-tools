"""Test Gemini Vision API with image"""
import google.generativeai as genai
from pathlib import Path
import os
from PIL import Image

# Configure Gemini - use a test key for now (user needs to add their own)
# For testing, you can get a free API key from: https://makersuite.google.com/app/apikey
api_key = input("Enter your Gemini API key (or press Enter to skip): ").strip()
if not api_key:
    print("No API key provided. Please get one from https://makersuite.google.com/app/apikey")
    exit(1)
    
genai.configure(api_key=api_key)
print(f"Configured Gemini API")

# Open image with PIL (no need to upload)
# Open image with PIL (no need to upload)
image_path = Path("D:/Thang/thang-phan-tools/test_files/ocr_vietnamese.png")
print(f"Loading image: {image_path}")

image = Image.open(image_path)
print(f"Image loaded: {image.size}")

# Use Gemini 2.5 Flash for OCR
model = genai.GenerativeModel("gemini-2.5-flash")

prompt = """Trích xuất TOÀN BỘ văn bản trong ảnh này.

YÊU CẦU:
- Giữ chính xác 100% ký tự Tiếng Việt (ă, â, ê, ô, ơ, ư, đ, dấu thanh)
- Giữ nguyên cấu trúc, xuống dòng, thụt lề
- Chỉ trả về văn bản, KHÔNG thêm giải thích

Trả về văn bản:"""

response = model.generate_content([prompt, image])
print(f"\n✅ Gemini OCR Result:\n{response.text}")
print(f"\nChar count: {len(response.text)}")
print(f"Word count: {len(response.text.split())}")
