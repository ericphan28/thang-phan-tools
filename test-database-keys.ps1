# Test Database Keys Only (No .env fallback)

Write-Host "🧪 Testing database-only keys..." -ForegroundColor Cyan

# Test 1: Check keys in database
Write-Host "`n1️⃣ Checking keys in database..." -ForegroundColor Yellow
cd backend
python scripts/check_keys.py

# Test 2: Try to initialize GeminiService
Write-Host "`n2️⃣ Testing GeminiService initialization..." -ForegroundColor Yellow
python -c @"
from app.core.database import get_db
from app.services.gemini_service import GeminiService

db = next(get_db())
try:
    service = GeminiService(db, user_id=1)
    print('✅ GeminiService initialized successfully')
    print(f'   Using key ID: {service.current_key_id}')
except ValueError as e:
    print(f'❌ Error: {e}')
"@

Write-Host "`n✅ Test complete!" -ForegroundColor Green
Write-Host "`n📋 Expectations:" -ForegroundColor Cyan
Write-Host "  - If keys exist in DB: ✅ Should initialize successfully" -ForegroundColor White
Write-Host "  - If no keys in DB: ❌ Should raise ValueError (no fallback to .env)" -ForegroundColor White
