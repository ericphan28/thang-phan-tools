# Fix Gotenberg - Word/Excel to PDF Issue

**Date:** 2025-11-21  
**Issue:** Word to PDF và Excel to PDF trả về lỗi 500  
**Root Cause:** Gotenberg container chưa được start  
**Status:** ✅ **FIXED**

---

## 🐛 Vấn Đề

Khi test trên frontend `http://165.99.59.47/tools`, các chức năng convert:
- ❌ Word to PDF → Error 500
- ❌ Excel to PDF → Error 500
- ✅ PDF to Word → Hoạt động bình thường

**Error logs:**
```
INFO: 172.18.0.5:49860 - "POST /api/documents/convert/excel-to-pdf HTTP/1.0" 500 Internal Server Error
INFO: 172.18.0.5:49864 - "POST /api/documents/convert/word-to-pdf HTTP/1.0" 500 Internal Server Error
```

---

## 🔍 Nguyên Nhân

### Phân Tích:
1. Backend code sử dụng **Gotenberg** service để convert Office files (Word/Excel) sang PDF
2. Gotenberg là Docker microservice chạy LibreOffice headless
3. Khi check containers: `docker ps | grep gotenberg` → **Không có kết quả**
4. **Kết luận:** Gotenberg container chưa được start

### Tại Sao Gotenberg Không Chạy:
- Container có trong `docker-compose.yml`
- Nhưng chưa được start cùng các services khác
- Có thể do deploy ban đầu chỉ start backend/frontend/db/redis
- Hoặc container bị stop/crashed trước đó

---

## ✅ Giải Pháp

### Bước 1: Start Gotenberg Container
```bash
ssh root@165.99.59.47
cd /opt/utility-server
docker-compose up -d gotenberg
```

**Kết quả:**
```
gotenberg Pulled
Container utility_gotenberg Creating
Container utility_gotenberg Started
```

### Bước 2: Verify Gotenberg Health
```bash
docker ps | grep gotenberg
curl http://localhost:3000/health
```

**Output:**
```
866324140b95   gotenberg/gotenberg:8   Up 2 minutes (healthy)   0.0.0.0:3000->3000/tcp

{"status":"up","details":{
  "chromium":{"status":"up"},
  "libreoffice":{"status":"up"}
}}
```

✅ Gotenberg đã healthy với LibreOffice và Chromium ready!

---

## 🧪 Test Kết Quả

### Automated Test Script
Tạo script Python `test_auto_convert.py` để test tự động:

```bash
cd D:\thang\utility-server
python test_auto_convert.py
```

### Test Results:
```
🚀 STARTING AUTO TEST - WORD/EXCEL TO PDF
Server: http://165.99.59.47

✅ Health Check: PASS
✅ Login (admin): PASS  
✅ Gotenberg Service: PASS
✅ Word → PDF: PASS (36KB → 31KB PDF)
✅ Excel → PDF: PASS (5KB → 16KB PDF)

Total: 4/4 tests passed (100%)
🎉 ALL TESTS PASSED!
```

### Manual Test (Frontend):
1. Vào `http://165.99.59.47/tools`
2. Login với `admin/admin123`
3. Test upload Word file → Convert to PDF → ✅ **SUCCESS**
4. Test upload Excel file → Convert to PDF → ✅ **SUCCESS**

---

## 📋 Chi Tiết Kỹ Thuật

### Gotenberg Service
- **Image:** gotenberg/gotenberg:8
- **Port:** 3000
- **Functions:**
  - LibreOffice conversion (Word, Excel, PowerPoint → PDF)
  - Chromium PDF rendering (HTML → PDF)
- **Memory:** Limit 1GB, Reserved 512MB

### Backend Integration
File: `backend/app/services/document_service.py`

```python
async def word_to_pdf(self, input_file: Path) -> Path:
    """Convert Word to PDF using Gotenberg API"""
    
    # Call Gotenberg LibreOffice endpoint
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{self.gotenberg_url}/forms/libreoffice/convert",
            files=files
        )
    
    # Fallback to local LibreOffice if Gotenberg unavailable
    except httpx.ConnectError:
        return await self._word_to_pdf_libreoffice_fallback(input_file)
```

**Gotenberg URL:** `http://gotenberg:3000` (internal Docker network)

### API Endpoints
- `POST /api/documents/convert/word-to-pdf` - Convert Word → PDF
- `POST /api/documents/convert/excel-to-pdf` - Convert Excel → PDF
- `POST /api/documents/convert/ppt-to-pdf` - Convert PowerPoint → PDF

---

## 🚀 Deployment Checklist

Để tránh vấn đề này trong tương lai:

### 1. Start All Services
```bash
cd /opt/utility-server
docker-compose up -d
```

Ensure ALL services start:
- ✅ postgres
- ✅ redis
- ✅ **gotenberg** ← Quan trọng!
- ✅ backend
- ✅ nginx

### 2. Verify All Containers Running
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Expected output:
```
NAMES                STATUS              PORTS
utility_postgres     Up (healthy)        0.0.0.0:5432->5432/tcp
utility_redis        Up (healthy)        0.0.0.0:6379->6379/tcp
utility_gotenberg    Up (healthy)        0.0.0.0:3000->3000/tcp
utility_backend      Up (healthy)        0.0.0.0:8000->8000/tcp
utility_nginx        Up                  0.0.0.0:80->80/tcp
```

### 3. Health Check Script
```bash
# Quick health check
curl http://localhost/health                # Backend
curl http://localhost:3000/health           # Gotenberg
docker ps | grep -E 'postgres|redis|gotenberg|backend|nginx'
```

### 4. Auto-Start on Reboot
Ensure `restart: unless-stopped` in docker-compose.yml:

```yaml
gotenberg:
  image: gotenberg/gotenberg:8
  container_name: utility_gotenberg
  restart: unless-stopped  # ← Important!
  networks:
    - utility_network
```

---

## 📝 Lessons Learned

### 1. Service Dependencies
- Backend phụ thuộc vào Gotenberg cho Office conversion
- Nếu Gotenberg không chạy → lỗi 500 (không phải lỗi code)
- Cần verify TẤT CẢ services khi deploy

### 2. Error Handling
- Backend có fallback to local LibreOffice
- Nhưng trong container không có LibreOffice cài sẵn
- Nên phải đảm bảo Gotenberg luôn chạy

### 3. Testing Strategy
- Test manual không đủ - cần automated tests
- Script `test_auto_convert.py` giúp phát hiện vấn đề nhanh
- Nên chạy test script sau mỗi deploy

### 4. Monitoring
- Cần monitor health của ALL services, không chỉ backend
- Gotenberg health endpoint: `/health`
- Return JSON với status của LibreOffice và Chromium

---

## 🔧 Troubleshooting Guide

### Issue: Gotenberg not starting

**Check logs:**
```bash
docker logs utility_gotenberg --tail=100
```

**Common causes:**
- Out of memory (needs 512MB minimum)
- Port 3000 already in use
- Docker image pull failed

**Solutions:**
```bash
# Restart Gotenberg
docker-compose restart gotenberg

# Rebuild if needed
docker-compose build gotenberg --no-cache
docker-compose up -d gotenberg

# Check resource usage
docker stats utility_gotenberg --no-stream
```

### Issue: Conversion still fails

**Check Gotenberg connectivity from backend:**
```bash
# From backend container
docker exec utility_backend curl http://gotenberg:3000/health

# Expected: {"status":"up",...}
```

**Check network:**
```bash
docker network inspect utility-server_utility_network | grep -A 5 gotenberg
```

### Issue: Slow conversion

**Optimize Gotenberg:**
- Increase memory limit in docker-compose.yml
- Add more environment variables for tuning:

```yaml
gotenberg:
  environment:
    - CHROMIUM_DISABLE_WEB_SECURITY=true
    - CHROMIUM_IGNORE_CERTIFICATE_ERRORS=true
    - LOG_LEVEL=info  # or debug
```

---

## ✨ Summary

| Item | Before | After |
|------|--------|-------|
| **Gotenberg Status** | ❌ Not running | ✅ Running (healthy) |
| **Word → PDF** | ❌ Error 500 | ✅ Success |
| **Excel → PDF** | ❌ Error 500 | ✅ Success |
| **Test Results** | N/A | ✅ 4/4 (100%) |

**Time to Fix:** ~5 minutes  
**Downtime:** None (other services still working)  
**Impact:** High (major feature not working)  
**Solution Complexity:** Low (just start container)

---

**Fixed by:** GitHub Copilot  
**Date:** 2025-11-21 23:50:00 +07:00  
**Test Script:** `test_auto_convert.py`
