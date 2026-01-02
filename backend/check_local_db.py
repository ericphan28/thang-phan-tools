import sqlite3
import os

db_path = "utility.db"

if os.path.exists(db_path):
    print(f"✅ Found database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\n📊 Tables ({len(tables)}):")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Count users
    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"\n👥 Users: {user_count}")
        
        # Get user list
        cursor.execute("SELECT id, username, email, is_active FROM users LIMIT 5")
        users = cursor.fetchall()
        print("\n👤 First 5 users:")
        for user in users:
            print(f"  - ID:{user[0]}, Username:{user[1]}, Email:{user[2]}, Active:{user[3]}")
    except sqlite3.OperationalError as e:
        print(f"\n❌ Error reading users: {e}")
    
    # Count AI keys
    try:
        cursor.execute("SELECT COUNT(*) FROM ai_provider_keys")
        key_count = cursor.fetchone()[0]
        print(f"\n🔑 AI Provider Keys: {key_count}")
        
        cursor.execute("SELECT provider, key_name, is_active FROM ai_provider_keys")
        keys = cursor.fetchall()
        for key in keys:
            print(f"  - {key[0]}: {key[1]} (Active: {key[2]})")
    except sqlite3.OperationalError:
        print("\n⚠️ No AI provider keys table")
    
    conn.close()
else:
    print(f"❌ Database not found: {db_path}")
    print(f"   Current directory: {os.getcwd()}")
    print(f"   Files in directory:")
    for f in os.listdir('.'):
        if f.endswith('.db'):
            print(f"     - {f}")
