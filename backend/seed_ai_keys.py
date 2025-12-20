"""
Seed AI Provider Keys from .env to database
"""
import os
from dotenv import load_dotenv
from app.core.database import SessionLocal
from app.models.models import AIProviderKey
from datetime import datetime

load_dotenv()

def seed_api_keys():
    db = SessionLocal()
    
    try:
        # Check if keys already exist
        existing_count = db.query(AIProviderKey).count()
        if existing_count > 0:
            print(f"⚠️  Database already has {existing_count} API keys. Skipping seed.")
            return
        
        keys_to_add = []
        
        # Gemini API Key
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            keys_to_add.append(AIProviderKey(
                provider="gemini",
                key_name="Production Gemini Key (from .env)",
                api_key=gemini_key,
                is_active=True,
                is_primary=True,
                monthly_limit=100.0,  # $100/month limit
                rate_limit_rpm=60,
                created_at=datetime.utcnow()
            ))
            print("✅ Added Gemini API key")
        
        # Claude API Key
        claude_key = os.getenv("ANTHROPIC_API_KEY")
        if claude_key:
            keys_to_add.append(AIProviderKey(
                provider="claude",
                key_name="Production Claude Key (from .env)",
                api_key=claude_key,
                is_active=True,
                is_primary=True,
                monthly_limit=200.0,  # $200/month limit
                rate_limit_rpm=50,
                created_at=datetime.utcnow()
            ))
            print("✅ Added Claude API key")
        
        # Adobe API Keys
        adobe_client_id = os.getenv("ADOBE_CLIENT_ID")
        adobe_client_secret = os.getenv("ADOBE_CLIENT_SECRET")
        if adobe_client_id and adobe_client_secret:
            keys_to_add.append(AIProviderKey(
                provider="adobe",
                key_name="Production Adobe PDF Services (from .env)",
                api_key="",  # Adobe uses client_id/secret instead
                client_id=adobe_client_id,
                client_secret=adobe_client_secret,
                is_active=True,
                is_primary=True,
                monthly_limit=50.0,  # $50/month limit
                rate_limit_rpm=30,
                created_at=datetime.utcnow()
            ))
            print("✅ Added Adobe PDF Services credentials")
        
        if keys_to_add:
            db.add_all(keys_to_add)
            db.commit()
            print(f"\n🎉 Successfully seeded {len(keys_to_add)} API keys to database!")
        else:
            print("❌ No API keys found in .env file")
    
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding keys: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Seeding AI Provider API Keys...\n")
    seed_api_keys()
