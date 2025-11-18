"""
Add activity_logs table to the database
Run this script to create the activity_logs table
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.database import engine, Base
from app.models.auth_models import ActivityLog


def create_activity_logs_table():
    """Create activity_logs table"""
    print("Creating activity_logs table...")
    
    # Create only the ActivityLog table
    ActivityLog.__table__.create(bind=engine, checkfirst=True)
    
    print("✅ Activity logs table created successfully!")


if __name__ == "__main__":
    create_activity_logs_table()
