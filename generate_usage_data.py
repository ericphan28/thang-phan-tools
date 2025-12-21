import requests
import json

# Test OCR with Gemini to generate usage data
def test_ocr():
    url = "http://localhost:8000/api/v1/ocr-compare/compare-engines"
    
    # Test with existing image
    try:
        with open("test_files/ocr_vietnamese.png", "rb") as f:
            files = {"file": ("test.png", f, "image/png")}
            data = {"language": "vi"}
            
            response = requests.post(url, files=files, data=data)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("OCR Success!")
                gemini_result = result.get('gemini', {})
                if gemini_result:
                    text_length = len(gemini_result.get('text', ''))
                    print(f"Gemini found: {text_length} characters")
                    print(f"Processing time: {gemini_result.get('processing_time_seconds', 0):.2f}s")
                return True
            else:
                print(f"Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    # Run multiple tests to generate usage data
    print("🧪 Generating usage data...")
    
    for i in range(3):
        print(f"\nTest {i+1}/3:")
        success = test_ocr()
        if success:
            print("✅ Generated usage data")
        else:
            print("❌ Failed to generate data")