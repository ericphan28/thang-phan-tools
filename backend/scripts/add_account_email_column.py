"""
Migration: Add account_email column to gemini_api_keys table
Thêm column lưu email tài khoản Google tạo API key
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.core.database import engine

def migrate():
    """Add account_email column"""
    print("🔧 Adding account_email column to gemini_api_keys...")
    
    migration_sql = """
    -- Add account_email column if not exists
    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name = 'gemini_api_keys' 
            AND column_name = 'account_email'
        ) THEN
            ALTER TABLE gemini_api_keys 
            ADD COLUMN account_email VARCHAR(255) NULL;
            
            CREATE INDEX IF NOT EXISTS idx_gemini_keys_account_email 
            ON gemini_api_keys(account_email);
            
            RAISE NOTICE 'Added account_email column';
        ELSE
            RAISE NOTICE 'account_email column already exists';
        END IF;
    END $$;
    """
    
    with engine.connect() as conn:
        conn.execute(text(migration_sql))
        conn.commit()
    
    print("✅ Migration completed successfully!")
    print("📧 Column account_email added to gemini_api_keys")
    print("\nUsage:")
    print("  - Lưu email tài khoản Google tạo API key")
    print("  - VD: ericphan28@gmail.com")
    print("  - Giúp track keys từ cùng 1 account")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
