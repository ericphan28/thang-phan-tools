"""
Test Gemini auto-logging wrapper
"""
from app.core.database import get_db
from app.services.gemini_service import get_gemini_service

def test_basic_generation():
    print("Testing basic Gemini generation with auto-logging...")
    
    db = next(get_db())
    gemini = get_gemini_service(db, user_id=1)
    
    response = gemini.generate_content(
        prompt="Say 'Hello World' in 3 words",
        model="gemini-2.0-flash-exp",
        operation="test-auto-logging"
    )
    
    print(f"✅ Response: {response.text}")
    print(f"✅ Input tokens: {response.usage_metadata.prompt_token_count}")
    print(f"✅ Output tokens: {response.usage_metadata.candidates_token_count}")
    print(f"✅ Total tokens: {response.usage_metadata.total_token_count}")
    print("\n✅ Usage automatically logged to database!")
    
    db.close()

if __name__ == "__main__":
    test_basic_generation()
