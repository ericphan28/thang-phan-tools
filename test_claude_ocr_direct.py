import requests
import json
import os

# Test Claude OCR directly
ocr_endpoint = "http://localhost:8000/api/v1/ocr-compare/compare-engines"

# Use a sample image file - create a simple one
sample_image_path = "test_image.png"

# Create a simple test image if it doesn't exist
if not os.path.exists(sample_image_path):
    from PIL import Image, ImageDraw, ImageFont
    import io
    
    # Create a simple test image with text
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw some Vietnamese text
    text = "Xin chào, đây là văn bản tiếng Việt\nVới dấu thanh và ký tự đặc biệt"
    draw.text((10, 50), text, fill='black')
    
    img.save(sample_image_path, 'PNG')
    print(f"✅ Created test image: {sample_image_path}")

# Test OCR compare with engines including Claude
with open(sample_image_path, 'rb') as f:
    files = {'file': f}
    data = {
        'engines': 'claude,gemini',
        'language': 'vi'
    }
    
    print("🚀 Calling OCR compare with Claude and Gemini...")
    response = requests.post(ocr_endpoint, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ OCR Response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Check Claude specifically
        if 'claude' in result.get('engines', {}):
            claude_result = result['engines']['claude']
            if claude_result.get('available'):
                print(f"\n✅ Claude OCR Success!")
                print(f"   Text: {claude_result.get('text', '')[:100]}...")
                print(f"   Usage: {claude_result.get('usage', {})}")
            else:
                print(f"\n❌ Claude OCR Failed:")
                print(f"   Error: {claude_result.get('error', 'Unknown error')}")
    else:
        print(f"❌ OCR Request failed: {response.status_code}")
        print(f"Response: {response.text}")

# Cleanup
if os.path.exists(sample_image_path):
    os.remove(sample_image_path)