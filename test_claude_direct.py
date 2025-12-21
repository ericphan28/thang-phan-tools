import anthropic
import os
import base64

# Test direct Claude API call
def test_claude_direct():
    """Test Claude API directly without OCR pipeline"""
    try:
        # Get API key from environment
        claude_key = os.getenv("CLAUDE_API_KEY")
        if not claude_key:
            return "No CLAUDE_API_KEY found in environment"
        
        print(f"✅ Found Claude API key: {claude_key[:20]}...")
        
        # Initialize Claude client
        client = anthropic.Anthropic(api_key=claude_key)
        print("✅ Claude client initialized")
        
        # Create a simple text request
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[
                {
                    "role": "user", 
                    "content": "Say 'Hello from Claude OCR test!' in Vietnamese"
                }
            ]
        )
        
        print("✅ Claude API call successful!")
        print(f"Response: {message.content[0].text}")
        print(f"Usage: {message.usage}")
        
        return {
            "success": True,
            "response": message.content[0].text,
            "usage": {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens
            }
        }
        
    except Exception as e:
        print(f"❌ Claude API error: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("🧪 Testing Claude API directly...")
    result = test_claude_direct()
    print(f"Final result: {result}")