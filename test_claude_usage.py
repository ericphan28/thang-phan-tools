import requests
import json

def test_claude_ocr():
    """Test OCR with Claude to generate usage data"""
    url = "http://localhost:8000/api/v1/ocr-compare/compare-engines"
    
    try:
        # Test with existing image and request Claude
        with open("test_files/ocr_vietnamese.png", "rb") as f:
            files = {"file": ("test-claude.png", f, "image/png")}
            # Request both Gemini and Claude
            data = {"language": "vi"}
            
            response = requests.post(url, files=files, data=data)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("OCR Compare Success!")
                
                # Check engines section
                if "engines" in result:
                    engines = result["engines"]
                    print(f"Available engines: {list(engines.keys())}")
                    
                    # Check Claude result specifically
                    if "claude" in engines:
                        claude_result = engines["claude"]
                        if "error" in claude_result:
                            print(f"❌ Claude Error: {claude_result['error']}")
                            print(f"   Reason: {claude_result.get('reason', 'Unknown')}")
                            print(f"   Available: {claude_result.get('available', False)}")
                        else:
                            text_length = len(claude_result.get('text', ''))
                            print(f"✅ Claude found: {text_length} characters")
                            print(f"   Processing time: {claude_result.get('processing_time_seconds', 0):.2f}s")
                    else:
                        print("❌ Claude not in engines")
                else:
                    print("❌ No engines section in response")
                    print(f"Response keys: {list(result.keys())}")
                
                return True
            else:
                print(f"Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Claude OCR to generate usage data...")
    
    for i in range(3):
        print(f"\nTest {i+1}/3:")
        test_claude_ocr()