"""
Migration script: Add Document AI tables
Run: python backend/scripts/add_document_ai_tables.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, inspect
from app.core.config import settings
from app.core.database import Base
from app.models.auth_models import User
from app.models.document_ai_models import (
    Project, Document, AITask, ReportSection, StatisticalData, ReportTemplate
)

def run_migration():
    """Create all Document AI tables"""
    print("🔧 Starting Document AI tables migration...")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # Tables to create
    new_tables = [
        'projects', 'documents', 'ai_tasks', 
        'report_sections', 'statistical_data', 'report_templates'
    ]
    
    print(f"\n📊 Existing tables: {len(existing_tables)}")
    for table in existing_tables:
        print(f"   ✓ {table}")
    
    print(f"\n🆕 Creating Document AI tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Check what was created
    inspector = inspect(engine)
    current_tables = inspector.get_table_names()
    
    created_count = 0
    for table in new_tables:
        if table in current_tables:
            if table not in existing_tables:
                print(f"   ✅ Created: {table}")
                created_count += 1
            else:
                print(f"   ℹ️  Already exists: {table}")
        else:
            print(f"   ❌ Failed to create: {table}")
    
    print(f"\n🎉 Migration completed!")
    print(f"   Created {created_count} new table(s)")
    print(f"   Total tables: {len(current_tables)}")
    
    # Show columns for new tables
    print(f"\n📋 Table structures:")
    for table in new_tables:
        if table in current_tables:
            columns = inspector.get_columns(table)
            print(f"\n   {table}:")
            for col in columns:
                print(f"      - {col['name']}: {col['type']}")

if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
