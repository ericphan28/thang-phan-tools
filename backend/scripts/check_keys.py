"""
Check keys in database
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.core.database import engine

with engine.connect() as conn:
    result = conn.execute(text('SELECT id, key_name, account_email, status FROM gemini_api_keys ORDER BY id'))
    rows = result.fetchall()
    
    print(f"\n📊 Found {len(rows)} keys in database:\n")
    
    if len(rows) == 0:
        print("❌ Không có keys nào trong database!")
        print("\nKiểm tra:")
        print("1. Bạn đã chạy migration chưa? python scripts/add_gemini_keys_tables.py")
        print("2. Bạn đã thêm keys qua UI chưa?")
    else:
        for row in rows:
            print(f"  ID: {row[0]:2d} | Name: {row[1]:30s} | Email: {row[2] or 'N/A':30s} | Status: {row[3]}")
