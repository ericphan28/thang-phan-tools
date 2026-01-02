"""
Script to create van_ban_hanh_chinh table
Run: python scripts/create_van_ban_table.py
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import Base, engine
from app.models.van_ban_models import VanBanHanhChinh, MucDoKhan, TrangThaiVanBan

def create_tables():
    """Create all tables defined in models"""
    print("🔨 Creating database tables...")
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Table 'van_ban_hanh_chinh' created successfully!")
        
        # Verify table exists
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'van_ban_hanh_chinh' in tables:
            print("✅ Verified: Table exists in database")
            
            # Show columns
            columns = inspector.get_columns('van_ban_hanh_chinh')
            print(f"\n📋 Table has {len(columns)} columns:")
            for col in columns[:5]:  # Show first 5
                print(f"   - {col['name']} ({col['type']})")
            print(f"   ... and {len(columns) - 5} more columns")
        else:
            print("❌ Error: Table not found after creation")
            
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_tables()
