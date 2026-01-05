# ✅ Migration: Chuyển sang Database Keys Management

**Ngày:** 5/1/2026  
**Mục đích:** Xóa GEMINI_API_KEY khỏi .env, chuyển sang quản lý qua Admin > AI Keys

---

## 📋 Tổng Quan

**Trước đây:**
- Gemini API key hardcoded trong `.env` → `GEMINI_API_KEY=AIza...`
- Không rotation, không encryption, không tracking usage per key

**Bây giờ:**
- Keys lưu trong database table `gemini_api_keys`
- Encrypted với `GEMINI_ENCRYPTION_KEY` (AES-256 Fernet)
- Auto-rotation khi quota gần hết hoặc lỗi
- Track usage per key, per model
- Quản lý qua UI: **Admin > AI Keys**

---

## ✅ Localhost - DONE

**File:** `backend/.env`

```diff
# Google Gemini AI
USE_GEMINI_API=true
- GEMINI_API_KEY=AIzaSyAesIpOllwdwj6PbHMcE3gi2TA6wWXWO6I
+ # GEMINI_API_KEY - DEPRECATED: Chuyển sang quản lý qua Admin > AI Keys (database)
+ # Old backup: AIzaSyAesIpOllwdwj6PbHMcE3gi2TA6wWXWO6I
GEMINI_MODEL=gemini-2.5-flash
```

**Backend restarted:** ✅ Đang chạy, lấy keys từ database

---

## ⚠️ VPS - TODO

### Bước 1: Update .env trên VPS

**Option A - Tự động (PowerShell):**
```powershell
.\update-vps-env.ps1
```

**Option B - Manual (SSH):**
```bash
ssh root@165.99.59.47

cd /root/thang-phan-tools/backend

# Backup .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Comment GEMINI_API_KEY
nano .env
# Thay dòng: GEMINI_API_KEY=AIza...
# Thành:    # GEMINI_API_KEY - DEPRECATED (use Admin > AI Keys)
#           # Old: AIza...

# Save: Ctrl+O, Enter, Ctrl+X
```

### Bước 2: Thêm Keys vào Database trên VPS

**SSH vào VPS:**
```bash
ssh root@165.99.59.47
cd /root/thang-phan-tools
```

**Option A - Qua UI (Recommended):**
1. Mở browser: `http://165.99.59.47/admin/gemini-keys`
2. Login admin account
3. Click "+ Add Key"
4. Điền form:
   - Key Name: `orc-xa-gia-kiem-02`
   - Account Email: `ericphan28@gmail.com`
   - API Key: `AIza...` (lấy từ .env.backup)
   - Priority: `10`
   - Monthly Quota: `1500000`
5. Click "Create Key"
6. Lặp lại cho các keys còn lại

**Option B - Script (faster):**
```bash
cd backend
python << 'EOF'
from app.core.database import get_db
from app.services.gemini_key_service import GeminiKeyService

db = next(get_db())
service = GeminiKeyService(db)

keys = [
    {"name": "orc-xa-gia-kiem-02", "email": "ericphan28@gmail.com", "key": "AIza...", "priority": 10, "quota": 1500000},
    {"name": "orc-xa-gia-kiem-03", "email": "ericphan28@gmail.com", "key": "AIza...", "priority": 10, "quota": 1500000},
    {"name": "orc-xa-gia-kiem-04", "email": "ericphan28@gmail.com", "key": "AIza...", "priority": 10, "quota": 1500000},
]

for k in keys:
    service.create_key(
        key_name=k["name"],
        account_email=k["email"],
        api_key=k["key"],
        priority=k["priority"],
        monthly_quota_limit=k["quota"]
    )
    print(f"✅ Added key: {k['name']}")

db.commit()
EOF
```

### Bước 3: Restart Backend trên VPS

```bash
cd /root/thang-phan-tools
docker-compose -f docker-compose.prod.yml restart backend
docker-compose -f docker-compose.prod.yml logs -f backend
# Ctrl+C để thoát logs
```

**Kiểm tra:**
```bash
# Xem backend logs
docker-compose -f docker-compose.prod.yml logs backend | tail -20

# Should see:
# ✅ Loaded .env from /app/.env
# ✅ Connected to database
# INFO: Application startup complete
```

---

## 🧪 Testing

**Test 1 - API lấy keys từ database:**
```bash
curl http://localhost:8000/api/v1/admin/gemini-keys/keys \
  -H "Authorization: Bearer YOUR_TOKEN"
  
# Expected: JSON array with encrypted keys
```

**Test 2 - Generate content (should auto-select best key):**
```bash
curl http://localhost:8000/api/v1/documents/ocr \
  -F "file=@test.pdf" \
  -H "Authorization: Bearer YOUR_TOKEN"
  
# Should work WITHOUT needing GEMINI_API_KEY in .env
```

**Test 3 - Check key usage logs:**
```bash
# Open browser: http://localhost:5173/admin/gemini-keys
# Click "Dashboard" tab
# Should see usage statistics per key
```

---

## 🔄 Rollback (If Needed)

**Nếu có lỗi, restore .env cũ:**

**Localhost:**
```powershell
# Uncomment GEMINI_API_KEY in backend/.env
# Restart backend
```

**VPS:**
```bash
ssh root@165.99.59.47
cd /root/thang-phan-tools/backend
cp .env.backup.YYYYMMDD_HHMMSS .env
cd ..
docker-compose -f docker-compose.prod.yml restart backend
```

---

## 📊 System Behavior

**GeminiService Logic (app/services/gemini_service.py):**

1. **Try database keys first:**
   ```python
   selected_key = self.key_service.select_best_key()
   # Priority: status=ACTIVE, highest quota remaining, lowest priority number
   ```

2. **Fallback to .env if no DB keys:**
   ```python
   if not selected_key:
       api_key = get_api_key("gemini", db)  # Gets from GEMINI_API_KEY in .env
   ```

3. **Auto-rotation on errors:**
   - 429 (quota exceeded) → Rotate to next key
   - 403 (invalid key) → Mark FAILED, rotate
   - Success → Update usage counter

**DocumentService (app/services/document_service.py):**
- Still reads `GEMINI_API_KEY` from .env for backward compatibility
- But all AI operations go through `GeminiService` wrapper → Uses DB keys

---

## 🎯 Benefits

✅ **Security:** Keys encrypted in database, not plain text in .env  
✅ **Scalability:** Add multiple keys, auto-balance load  
✅ **Reliability:** Auto-rotation on quota/errors  
✅ **Tracking:** Per-key usage logs, cost analytics  
✅ **Management:** UI to CRUD keys without editing .env  

---

## 📝 Notes

- `GEMINI_ENCRYPTION_KEY` **PHẢI GIỮ NGUYÊN** trong .env (cả localhost và VPS)
- Nếu đổi `GEMINI_ENCRYPTION_KEY`, tất cả keys trong DB sẽ không decrypt được
- Old backup key trong comment chỉ để reference, không được sử dụng
- Frontend Edit Dialog đã fix (duplicate closing tags removed)

---

**Status:** Localhost ✅ | VPS ⚠️ (chờ update)
