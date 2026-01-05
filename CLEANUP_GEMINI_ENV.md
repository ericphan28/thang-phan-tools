# ✅ DONE: Xóa Hoàn Toàn GEMINI_API_KEY

**Ngày:** 6/1/2026  
**Status:** Localhost ✅ DONE | VPS ⚠️ Pending

---

## 🎯 Thay Đổi

### 1. Code Changes

**GeminiService (app/services/gemini_service.py):**
```diff
- # Fallback to old method (get from .env via ai_usage_service)
- api_key = get_api_key("gemini", db)
- if not api_key:
-     raise ValueError("No Gemini API key available...")
- self.current_key_id = None

+ # Get API key from database ONLY (no fallback to .env)
+ selected_key = self.key_service.select_best_key()
+ if not selected_key:
+     raise ValueError(
+         "Không tìm thấy Gemini API key nào khả dụng. "
+         "Vui lòng thêm key tại Admin > AI Keys."
+     )
```

**DocumentService (app/services/document_service.py):**
```diff
- self.gemini_api_key = os.getenv("GEMINI_API_KEY")
- if self.gemini_api_key and GEMINI_AVAILABLE:
-     genai.configure(api_key=self.gemini_api_key)
-     self.use_gemini = True

+ # Google Gemini API - Uses database keys via GeminiService
+ self.use_gemini = GEMINI_AVAILABLE
+ logger.info("✅ Keys managed via database (Admin > AI Keys)")
```

Error messages:
```diff
- raise ValueError("Gemini API not configured. Set GEMINI_API_KEY in .env")
+ raise ValueError("Gemini API không khả dụng. Vui lòng thêm API keys tại Admin > AI Keys")
```

### 2. .env Changes

**Localhost (backend/.env):**
```diff
# Google Gemini AI
- GEMINI_API_KEY=AIzaSyAesIpOllwdwj6PbHMcE3gi2TA6wWXWO6I
+ # Keys managed in database (Admin > AI Keys)

- GEMINI_ENCRYPTION_KEY=...  # (for database storage)
+ GEMINI_ENCRYPTION_KEY=...  # DO NOT CHANGE!
```

**VPS - Script:** `update-vps-env.ps1`
- Xóa hoàn toàn dòng `GEMINI_API_KEY=...`
- Không giữ backup trong comment

---

## ✅ Localhost Status

**Database Keys:**
```
📊 Found 3 keys in database:
  ID: 4 | orc-xa-gia-kiem-02 | ericphan28@gmail.com | ACTIVE
  ID: 5 | orc-xa-gia-kiem-03 | ericphan28@gmail.com | ACTIVE
  ID: 6 | orc-xa-gia-kiem-04 | ericphan28@gmail.com | ACTIVE
```

**Backend:** ✅ Running, no GEMINI_API_KEY in .env  
**Frontend:** ✅ Running on port 5173  
**Test:** ✅ Can access http://localhost:5173/admin/gemini-keys

---

## ⚠️ VPS - Pending Actions

### Bước 1: Xóa GEMINI_API_KEY khỏi .env

```powershell
.\update-vps-env.ps1
```

Hoặc manual:
```bash
ssh root@165.99.59.47
cd /root/thang-phan-tools/backend
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
nano .env
# XÓA dòng: GEMINI_API_KEY=...
# Save & exit
```

### Bước 2: Thêm Keys vào Database

**UI (Recommended):**
1. Mở: http://165.99.59.47/admin/gemini-keys
2. Login admin
3. Click "+ Add Key" 3 lần với:
   - orc-xa-gia-kiem-02 | ericphan28@gmail.com | AIza... | Priority 10
   - orc-xa-gia-kiem-03 | ericphan28@gmail.com | AIza... | Priority 10
   - orc-xa-gia-kiem-04 | ericphan28@gmail.com | AIza... | Priority 10

### Bước 3: Restart Backend

```bash
ssh root@165.99.59.47
cd /root/thang-phan-tools
docker-compose -f docker-compose.prod.yml restart backend
docker-compose logs -f backend  # Check logs
```

---

## 🧪 Validation

**Test 1 - No keys in DB:**
```python
from app.services.gemini_service import GeminiService
service = GeminiService(db, user_id=1)
# Should raise: ValueError("Không tìm thấy Gemini API key...")
```

**Test 2 - Keys exist in DB:**
```python
service = GeminiService(db, user_id=1)
# Should work: service.current_key_id = 4 (or 5, 6)
```

**Test 3 - API Call:**
```bash
curl http://localhost:8000/api/v1/documents/ocr \
  -F "file=@test.pdf" \
  -H "Authorization: Bearer TOKEN"
# Should work with database keys ONLY
```

---

## 🔒 Security Notes

**CRITICAL - Keep in .env:**
```bash
GEMINI_ENCRYPTION_KEY=m0Qx1ZN0moTTrS3YsSS2Ovi3qtw-VTiR91sldZCZn6A=
```

**⚠️ WARNING:**
- Nếu mất `GEMINI_ENCRYPTION_KEY`, tất cả keys trong DB sẽ không decrypt được
- Không commit key này vào git (đã có trong .gitignore)
- Backup .env.backup files có chứa GEMINI_ENCRYPTION_KEY

---

## 📊 Behavior

| Scenario | Old Behavior | New Behavior |
|----------|--------------|--------------|
| No .env key | Error | Error (same) |
| .env key only | Use .env | **Error** (no fallback) |
| DB keys only | Use DB | Use DB (expected) |
| Both .env & DB | Use DB (fallback to .env) | Use DB (no .env read) |
| No keys anywhere | Error | Error (clear message) |

---

## 🎯 Benefits

✅ **Single source of truth:** Database ONLY  
✅ **No confusion:** .env không còn GEMINI_API_KEY  
✅ **Clear errors:** "Vui lòng thêm key tại Admin > AI Keys"  
✅ **Forced migration:** Developers phải dùng UI để add keys  

---

**Next:** Run `.\update-vps-env.ps1` để update VPS! 🚀
