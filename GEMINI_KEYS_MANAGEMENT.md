# 🔑 Gemini API Keys Management System

## 📚 Tổng quan

Hệ thống quản lý nhiều Gemini API keys với tính năng:
- **Multi-key management**: Lưu trữ & quản lý nhiều API keys
- **Auto-rotation**: Tự động chuyển key khi hết quota
- **Quota tracking**: Theo dõi usage cho từng key
- **Encryption**: Mã hóa AES-256 khi lưu database
- **Admin Dashboard**: UI quản lý với charts & metrics

---

## 🏗️ Kiến trúc

### Database Schema (4 tables)

```sql
-- Table 1: Lưu trữ API keys (encrypted)
gemini_api_keys (
  id, name, api_key_encrypted, status, priority, is_default,
  created_at, updated_at, last_used_at, last_rotation_at
)

-- Table 2: Quota limits cho mỗi key
gemini_key_quotas (
  id, key_id, quota_type (MONTHLY/DAILY/PER_MINUTE),
  limit_value, used_value, reset_at
)

-- Table 3: Logs mỗi lần sử dụng key
gemini_key_usage_log (
  id, key_id, model, tokens_used, cost_usd, status, 
  error_message, user_id, created_at
)

-- Table 4: Logs mỗi lần rotation
gemini_key_rotation_log (
  id, from_key_id, to_key_id, reason, triggered_by, created_at
)
```

### Backend Services

**GeminiKeyService** (`app/services/gemini_key_service.py`):
- `encrypt_api_key()`: Mã hóa key trước khi lưu DB
- `decrypt_api_key()`: Giải mã khi cần dùng
- `select_best_key()`: Chọn key tốt nhất (ưu tiên priority, còn quota)
- `rotate_key()`: Tự động chuyển sang key khác
- `track_usage()`: Log usage + check auto-rotation
- `reset_monthly_quotas()`: Reset monthly quota (cronjob)

**API Endpoints** (`/admin/gemini-keys/*`):
```
POST   /admin/gemini-keys/                Create key
GET    /admin/gemini-keys/                List keys
GET    /admin/gemini-keys/{id}            Get key detail
PUT    /admin/gemini-keys/{id}            Update key
DELETE /admin/gemini-keys/{id}            Delete key
GET    /admin/gemini-keys/dashboard       Get metrics
GET    /admin/gemini-keys/usage-logs      Get usage history
GET    /admin/gemini-keys/rotation-logs   Get rotation history
POST   /admin/gemini-keys/{id}/rotate     Manual rotate
POST   /admin/gemini-keys/quotas/reset    Reset all quotas
```

### Frontend Components

**Route**: `http://localhost:5173/admin/gemini-keys`

**Pages**:
- `GeminiKeysManagementPage.tsx`: Main page với 4 tabs

**Components** (`components/gemini-keys/`):
1. **DashboardTab.tsx**: 
   - 4 Overview cards (total keys, usage 7 days, success rate, total cost)
   - LineChart: Usage trends + success rate
   - BarChart: Top models sử dụng
   - Tables: Top users, recent rotations

2. **KeysManagementTab.tsx**:
   - Table danh sách keys (name, status, priority, quota)
   - Add Key dialog với form validation
   - Edit/Delete/Rotate actions
   - Status badges (Active, Quota Exceeded, Inactive)

3. **UsageLogsTab.tsx**:
   - Filterable logs table (by key, limit)
   - Summary stats (total requests, success/failed, cost)

4. **RotationLogsTab.tsx**:
   - Rotation history table
   - Statistics (total rotations, manual/auto)

---

## 🚀 Setup & Deployment

### 1. Backend Setup

**Generate encryption key**:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Add to `.env`**:
```bash
GEMINI_ENCRYPTION_KEY=<your-generated-key>
```

**Run migration**:
```bash
cd backend
python scripts/add_gemini_keys_tables.py
```

Expected output:
```
✅ Created table: gemini_api_keys
✅ Created table: gemini_key_quotas
✅ Created table: gemini_key_usage_log
✅ Created table: gemini_key_rotation_log
```

**Restart backend**:
```bash
# Use VS Code task
Ctrl+Shift+P → Run Task → Backend Server
```

### 2. Frontend Setup

**Install dependencies** (already done):
```bash
cd frontend
npm install @radix-ui/react-dropdown-menu recharts @radix-ui/react-dialog @radix-ui/react-tabs
```

**Start frontend**:
```bash
Ctrl+Shift+P → Run Task → Frontend Server
```

---

## 📖 Usage Guide

### Thêm API Key mới

1. Truy cập: `http://localhost:5173/admin/gemini-keys`
2. Tab "Quản lý Keys" → Click **"+ Thêm Key"**
3. Nhập thông tin:
   - **Tên key**: VD: "Personal Key - Thang"
   - **API Key**: Paste key từ Google AI Studio
   - **Priority**: 1-10 (số cao = ưu tiên dùng trước)
   - **Monthly Quota**: VD: 1000000 tokens/month
   - **Daily Quota**: VD: 50000 tokens/day
   - **Per-minute Quota**: VD: 1000 tokens/minute
   - **Set as default**: Check nếu muốn làm key mặc định
4. Click **"Tạo Key"**

### Xem Usage Metrics

**Dashboard Tab**:
- Overview cards: Total keys, usage 7 ngày, success rate, total cost
- LineChart: Xem trend usage theo ngày
- BarChart: Top models được dùng nhiều nhất
- Tables: Top users, recent rotations

**Usage Logs Tab**:
- Filter by key_id
- Set limit (10, 50, 100, 500)
- Xem chi tiết: model, tokens, cost, status, timestamp

### Manual Rotation

Khi cần force switch sang key khác:
1. Tab "Quản lý Keys" → Click **"⋮"** (menu) bên cạnh key
2. Chọn **"Rotate"**
3. Confirm dialog → Rotation sẽ được log

### Auto-Rotation Logic

System tự động rotate khi:
1. **Quota < 5%**: Key còn dưới 5% quota → Auto switch
2. **Rate limit**: Key bị rate limited → Switch ngay
3. **Key error**: Key invalid hoặc revoked → Switch

**Priority selection**:
- Chọn key có `priority` cao nhất
- Trong cùng priority → Chọn key còn nhiều quota nhất
- Nếu có `is_default=true` → Ưu tiên key đó

---

## 🔒 Security

### Encryption at Rest
- API keys được mã hóa AES-256 (Fernet) trước khi lưu DB
- Chỉ decrypt khi cần sử dụng
- Encryption key lưu trong `.env` (không commit to Git)

### Access Control
- **Admin only**: Tất cả endpoints yêu cầu `superuser` role
- JWT authentication với token expiry
- API keys không bao giờ expose trong response (masked)

### Best Practices
1. Rotate encryption key định kỳ (6 tháng/lần)
2. Enable audit logs cho mọi thao tác
3. Set alerts khi quota gần hết (<10%)
4. Xóa keys cũ không dùng

---

## 🤖 Auto-Reset Quotas (Cronjob)

### Setup APScheduler (Recommended)

**Add to `main_simple.py`**:
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.gemini_key_service import GeminiKeyService
from app.core.database import get_db

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', day=1, hour=0, minute=0)  # 00:00 ngày 1 hàng tháng
async def reset_monthly():
    db = next(get_db())
    try:
        GeminiKeyService.reset_monthly_quotas(db)
    finally:
        db.close()

@scheduler.scheduled_job('cron', hour=0, minute=0)  # 00:00 mỗi ngày
async def reset_daily():
    db = next(get_db())
    try:
        GeminiKeyService.reset_daily_quotas(db)
    finally:
        db.close()

@app.on_event("startup")
async def startup():
    scheduler.start()
```

**Install APScheduler**:
```bash
pip install apscheduler
```

### Manual Reset (API)

```bash
curl -X POST http://localhost:8000/admin/gemini-keys/quotas/reset \
  -H "Authorization: Bearer <admin-token>"
```

---

## 📊 Monitoring & Alerts

### Key Metrics to Track

1. **Quota Usage**:
   - Current usage %
   - Trend (increasing/stable)
   - Time to depletion (predict)

2. **Success Rate**:
   - Target: >95%
   - Alert if <90% in 1 hour

3. **Cost Tracking**:
   - Daily/monthly spend
   - Budget alerts

4. **Rotation Frequency**:
   - Auto vs manual rotations
   - Spike detection (too frequent = issue)

### Dashboard Widgets

**Overview Cards** (real-time):
- Total Keys: Active/Inactive count
- 7-day Usage: Total requests
- Success Rate: % successful requests
- Total Cost: Sum cost_usd 7 days

**Charts**:
- Usage Trends: LineChart (daily requests + success rate)
- Top Models: BarChart (model usage distribution)

**Tables**:
- Top Users: Ai dùng nhiều nhất (by request count)
- Recent Rotations: 10 rotations gần nhất

---

## 🐛 Troubleshooting

### Error: "No active keys available"

**Nguyên nhân**:
- Tất cả keys đều hết quota hoặc inactive
- Không có keys nào trong DB

**Fix**:
1. Check dashboard → "Tổng số Keys" = 0?
2. Add key mới hoặc reset quotas
3. Check status của keys (phải ACTIVE)

### Error: "Encryption key not configured"

**Nguyên nhân**:
- `.env` thiếu `GEMINI_ENCRYPTION_KEY`

**Fix**:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy output vào .env
GEMINI_ENCRYPTION_KEY=<output>
```

### Error: "Invalid token" khi decrypt

**Nguyên nhân**:
- Encryption key đã thay đổi sau khi encrypt
- Data bị corrupt

**Fix**:
1. Backup DB
2. Delete keys cũ
3. Re-add keys với encryption key mới

### Auto-rotation không hoạt động

**Check**:
1. Cronjob có chạy không? (logs)
2. `track_usage()` có được gọi sau mỗi AI request không?
3. Threshold settings (default: <5% quota)

**Debug**:
```python
# In GeminiService.generate_content(), add:
print(f"[DEBUG] Tracked usage, quota now: {quota.used_value}/{quota.limit_value}")
```

---

## 🎯 Roadmap

### Phase 1: Core Features ✅
- [x] Database schema + migration
- [x] Encryption service
- [x] Key selection logic
- [x] Auto-rotation
- [x] Usage tracking
- [x] Admin API endpoints
- [x] Frontend dashboard

### Phase 2: Enhancements 🚧
- [ ] APScheduler cronjobs
- [ ] Email alerts (quota <10%)
- [ ] Export usage reports (CSV/Excel)
- [ ] Key performance comparison
- [ ] Budget limits per key

### Phase 3: Advanced 📋
- [ ] Multi-tenant support (keys per organization)
- [ ] API key rotation via Google API (auto-renew)
- [ ] Predictive quota alerts (ML-based)
- [ ] Integration with other AI providers (OpenAI, Claude)

---

## 📝 Notes

**Tại sao cần multi-key management?**
1. **Quota limits**: 1 key có giới hạn monthly/daily/per-minute
2. **Redundancy**: 1 key lỗi → Tự động switch sang key khác
3. **Cost distribution**: Spread cost across multiple billing accounts
4. **Performance**: Tránh rate limiting bằng cách rotate keys

**Khi nào auto-rotate?**
- Quota < 5% (configurable)
- Rate limit error (429)
- Key invalid/revoked
- Manual trigger via UI

**Cost calculation**:
- Based on `tokens_used` × model pricing
- Logged in `gemini_key_usage_log.cost_usd`
- Dashboard shows total 7-day cost

---

**Last Updated**: Dec 30, 2025  
**Version**: 1.0.0  
**Author**: Thang Phan  
**License**: Internal Use Only
