"""
Add phone and address columns to users table
Run: python scripts/add_user_contact_fields.py
"""
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import text
from app.core.database import SessionLocal

def add_contact_fields():
    """Add phone and address columns to users table"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("ADDING CONTACT FIELDS TO USERS TABLE")
        print("="*70 + "\n")
        
        # Check if columns already exist
        check_phone = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='phone'
        """)
        
        check_address = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='address'
        """)
        
        phone_exists = db.execute(check_phone).fetchone()
        address_exists = db.execute(check_address).fetchone()
        
        # Add phone column if not exists
        if not phone_exists:
            print("📱 Adding 'phone' column...")
            db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN phone VARCHAR(20)
            """))
            print("✅ Phone column added successfully")
        else:
            print("⚠️  Phone column already exists, skipping")
        
        # Add address column if not exists
        if not address_exists:
            print("📍 Adding 'address' column...")
            db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN address VARCHAR(255)
            """))
            print("✅ Address column added successfully")
        else:
            print("⚠️  Address column already exists, skipping")
        
        db.commit()
        
        print("\n" + "="*70)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_contact_fields()
