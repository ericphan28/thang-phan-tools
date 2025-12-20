"""Recreate database with all tables"""
import os
import sys

# Remove old database
db_path = "utility.db"
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✅ Deleted old database: {db_path}")

# Now import and initialize
from app.core.database import init_db, engine
from sqlalchemy import inspect

print("🔨 Creating all tables...")
init_db()

# Verify tables were created
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"\n✅ Database created with {len(tables)} tables:")
for table in sorted(tables):
    print(f"   - {table}")

print("\n🎉 Database initialization complete!")
