"""
Migration script: Add Gemini API Keys Management tables
Run: python scripts/add_gemini_keys_tables.py
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from app.core.config import settings
from app.core.database import Base

# Import models để register vào Base.metadata
from app.models.gemini_keys import (
    GeminiAPIKey,
    GeminiKeyQuota,
    GeminiKeyUsageLog,
    GeminiKeyRotationLog
)

def main():
    print("🔧 Creating Gemini API Keys Management tables...")
    
    # Create engine
    engine = create_engine(
        settings.DATABASE_URL,
        echo=True  # Show SQL statements
    )
    
    # Create tables (checkfirst=True không tạo lại nếu đã tồn tại)
    Base.metadata.create_all(bind=engine, checkfirst=True)
    
    print("✅ Tables created successfully!")
    print("\nCreated tables:")
    print("  - gemini_api_keys")
    print("  - gemini_key_quotas")
    print("  - gemini_key_usage_log")
    print("  - gemini_key_rotation_log")
    
    print("\n📝 Next steps:")
    print("  1. Add .env variable: GEMINI_ENCRYPTION_KEY (generate: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')")
    print("  2. Add your first key: POST /api/v1/admin/gemini-keys/keys")
    print("  3. View dashboard: GET /api/v1/admin/gemini-keys/dashboard")

if __name__ == "__main__":
    main()
