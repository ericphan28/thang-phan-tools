"""
Database Migration Script - Add Quota System Columns
Adds subscription_tier, ai_quota_monthly, ai_usage_this_month, quota_reset_date to users table
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import SessionLocal, engine
from sqlalchemy import text

def migrate_add_quota_columns():
    """Add quota columns to users table"""
    db = SessionLocal()
    
    print("=" * 80)
    print("📦 DATABASE MIGRATION: Add Quota System Columns")
    print("=" * 80)
    
    try:
        # Check if columns already exist
        print("\n🔍 Checking existing columns...")
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('subscription_tier', 'ai_quota_monthly', 'ai_usage_this_month', 'quota_reset_date')
        """))
        existing_columns = [row[0] for row in result]
        
        if existing_columns:
            print(f"   ℹ️  Found existing columns: {existing_columns}")
        
        # Add columns if not exist
        migrations = [
            ("subscription_tier", "VARCHAR(20) DEFAULT 'FREE' NOT NULL"),
            ("ai_quota_monthly", "INTEGER DEFAULT 3 NOT NULL"),
            ("ai_usage_this_month", "INTEGER DEFAULT 0 NOT NULL"),
            ("quota_reset_date", "TIMESTAMP")
        ]
        
        for col_name, col_def in migrations:
            if col_name not in existing_columns:
                print(f"\n✅ Adding column: {col_name}")
                db.execute(text(f"""
                    ALTER TABLE users 
                    ADD COLUMN {col_name} {col_def}
                """))
                db.commit()
                print(f"   ✅ Added: {col_name}")
            else:
                print(f"\n⏭️  Skipping {col_name} (already exists)")
        
        # Update existing users to have quota_reset_date
        print("\n🔄 Updating existing users...")
        db.execute(text("""
            UPDATE users 
            SET quota_reset_date = NOW() + INTERVAL '30 days'
            WHERE quota_reset_date IS NULL
        """))
        db.commit()
        print("   ✅ Set quota_reset_date for existing users")
        
        # Verify
        print("\n✅ Verifying migration...")
        result = db.execute(text("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('subscription_tier', 'ai_quota_monthly', 'ai_usage_this_month', 'quota_reset_date')
            ORDER BY column_name
        """))
        
        print("\n📊 New columns in users table:")
        for row in result:
            print(f"   - {row[0]:25} {row[1]:20} default={row[2]}")
        
        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    migrate_add_quota_columns()
