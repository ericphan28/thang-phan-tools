import requests
import json

def create_claude_usage_manually():
    """Manually log Claude usage via AI admin test endpoint"""
    url = "http://localhost:8000/api/v1/ai-admin/keys"
    
    try:
        # Get Claude API key ID
        response = requests.get(url)
        if response.status_code == 200:
            keys = response.json()
            claude_key = None
            for key in keys:
                if key.get('provider') == 'claude':
                    claude_key = key
                    break
            
            if claude_key:
                print(f"Found Claude key: {claude_key['key_name']}")
                
                # Test the Claude key to generate usage
                test_url = f"http://localhost:8000/api/v1/ai-admin/keys/{claude_key['id']}/test"
                test_response = requests.post(test_url)
                
                if test_response.status_code == 200:
                    result = test_response.json()
                    print(f"✅ Claude test result: {result}")
                    
                    # Run multiple tests to generate more usage
                    for i in range(5):
                        test_response = requests.post(test_url)
                        if test_response.status_code == 200:
                            print(f"✅ Claude test {i+2} completed")
                        else:
                            print(f"❌ Claude test {i+2} failed")
                    
                    return True
                else:
                    print(f"❌ Claude test failed: {test_response.text}")
                    return False
            else:
                print("❌ Claude key not found")
                return False
        else:
            print(f"❌ Failed to get keys: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Manually creating Claude usage data...")
    create_claude_usage_manually()