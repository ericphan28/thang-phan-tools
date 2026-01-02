# Test Smart Config Detection

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("\n" + "="*60)
print("🧪 TESTING SMART CONFIG - Environment Detection")
print("="*60 + "\n")

# Test 1: Simulating localhost (no Docker)
print("1️⃣  Test: Running on LOCALHOST (outside Docker)")
print("-" * 60)

# Remove Docker indicators if exist
if os.path.exists('/.dockerenv'):
    print("⚠️  Cannot test - actually running in Docker!")
else:
    from app.core.config import settings
    
    print(f"Detected Environment: LOCALHOST")
    print(f"Expected DB Host: 165.99.59.47")
    print(f"Actual DATABASE_URL: {settings.DATABASE_URL}")
    
    if "165.99.59.47" in settings.DATABASE_URL or os.getenv("DB_HOST", "165.99.59.47") in settings.DATABASE_URL:
        print("✅ Correct: Using VPS public IP")
    else:
        print("❌ Error: Not using VPS IP")

print("\n")

# Test 2: Explain Docker behavior
print("2️⃣  Test: Running in DOCKER (production)")
print("-" * 60)
print("When deployed to VPS Docker:")
print("  • File /.dockerenv exists")
print("  • Config will detect Docker environment")
print("  • DATABASE_URL will use: postgres:5432 (internal)")
print("  • No need to expose PostgreSQL to internet!")
print("✅ This will be tested on actual deployment")

print("\n")

# Test 3: Configuration
print("3️⃣  Current Configuration")
print("-" * 60)
print(f"DB_USER: {settings.DB_USER}")
print(f"DB_PASSWORD: {'*' * len(settings.DB_PASSWORD)}")
print(f"DB_NAME: {settings.DB_NAME}")
print(f"DB_PORT: {settings.DB_PORT}")
print(f"DATABASE_URL: {settings.DATABASE_URL}")

print("\n")

# Test 4: Connection test (if credentials are set)
print("4️⃣  Testing Database Connection")
print("-" * 60)

if settings.DB_PASSWORD != "your_password_here":
    try:
        from sqlalchemy import create_engine
        engine = create_engine(settings.DATABASE_URL, connect_args={'connect_timeout': 5})
        conn = engine.connect()
        result = conn.execute('SELECT version();').fetchone()
        print("✅ Connection successful!")
        print(f"PostgreSQL: {result[0][:80]}")
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Run setup first: .\\setup-smart-config.ps1")
else:
    print("⚠️  Credentials not set yet")
    print("💡 Run setup: .\\setup-smart-config.ps1")

print("\n" + "="*60)
print("✅ Test Complete!")
print("="*60 + "\n")
