import sqlite3
import os

def check_database(db_path, label):
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n✅ {label}:")
        print(f"   Path: {db_path}")
        print(f"   Tables: {[t[0] for t in tables]}")
        conn.close()
    else:
        print(f"\n❌ {label}: NOT FOUND")
        print(f"   Path: {db_path}")

# Check both locations
check_database("D:/thang/utility-server/backend/utility.db", "Backend DB")
check_database("D:/thang/utility-server/utility.db", "Parent DB")
