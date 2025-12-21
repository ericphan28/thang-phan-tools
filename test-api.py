import requests
import json

print("\n=== TESTING BACKEND API ===\n")

# Test 1: Health Check
print("1. Testing Health Check...")
try:
    response = requests.get("http://localhost:8000/health")
    print(f"✓ OK - Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
except Exception as e:
    print(f"✗ FAILED: {e}\n")
    exit(1)

# Test 2: Login with admin
print("2. Testing Login with admin/admin123...")
try:
    data = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post("http://localhost:8000/api/auth/login", json=data)
    print(f"✓ OK - Status: {response.status_code}")
    result = response.json()
    print(f"   User: {result['user']['username']}")
    print(f"   Token: {result['access_token'][:50]}...\n")
except Exception as e:
    print(f"✗ FAILED: {e}")
    print(f"   Response: {response.text}\n")

# Test 3: Login with custom user
print("3. Testing Login with cym_sunset@yahoo.com...")
try:
    data = {
        "username": "cym_sunset@yahoo.com",
        "password": "Tnt@9961266"
    }
    response = requests.post("http://localhost:8000/api/auth/login", json=data)
    print(f"✓ OK - Status: {response.status_code}")
    result = response.json()
    print(f"   User: {result['user']['email']}")
    print(f"   Token: {result['access_token'][:50]}...\n")
except Exception as e:
    print(f"✗ FAILED: {e}")
    print(f"   Response: {response.text}\n")

print("=== TEST COMPLETE ===")
print("\nFrontend: http://localhost:5173")
print("Backend:  http://localhost:8000/docs")
