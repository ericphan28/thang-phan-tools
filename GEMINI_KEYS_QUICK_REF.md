# 🚀 Gemini Keys - Quick Reference

## URLs
- **Admin Dashboard**: http://localhost:5173/admin/gemini-keys
- **API Docs**: http://localhost:8000/docs#/Gemini%20Keys

## Setup (One-time)

```bash
# 1. Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 2. Add to backend/.env
GEMINI_ENCRYPTION_KEY=<generated-key>

# 3. Run migration
cd backend
python scripts/add_gemini_keys_tables.py

# 4. Restart backend
Ctrl+Shift+P → Run Task → Backend Server
```

## Common Tasks

### Add New Key (UI)
1. Go to http://localhost:5173/admin/gemini-keys
2. Tab "Quản lý Keys" → "+ Thêm Key"
3. Fill: Name, API Key, Priority, Quotas
4. Click "Tạo Key"

### Add New Key (API)
```bash
curl -X POST http://localhost:8000/admin/gemini-keys/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Key",
    "api_key": "AIza...",
    "priority": 5,
    "is_default": false,
    "quotas": [
      {"quota_type": "MONTHLY", "limit_value": 1000000},
      {"quota_type": "DAILY", "limit_value": 50000}
    ]
  }'
```

### Check Current Usage
```bash
# Dashboard metrics
curl http://localhost:8000/admin/gemini-keys/dashboard \
  -H "Authorization: Bearer <token>"

# Usage logs (last 100)
curl "http://localhost:8000/admin/gemini-keys/usage-logs?limit=100" \
  -H "Authorization: Bearer <token>"
```

### Manual Rotation
```bash
curl -X POST http://localhost:8000/admin/gemini-keys/{key_id}/rotate \
  -H "Authorization: Bearer <token>"
```

### Reset Quotas (Monthly)
```bash
curl -X POST http://localhost:8000/admin/gemini-keys/quotas/reset \
  -H "Authorization: Bearer <token>"
```

## Auto-Rotation Triggers

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Low quota | <5% remaining | Switch to next key |
| Rate limit | HTTP 429 | Immediate switch |
| Invalid key | API error | Mark revoked, switch |

## Key Selection Priority

1. **Status**: Active only (không lấy Inactive/Revoked)
2. **Default**: Ưu tiên key có `is_default=true`
3. **Priority**: Số cao hơn = dùng trước (1-10)
4. **Quota**: Còn nhiều quota hơn
5. **Last used**: Ít dùng gần đây hơn

## Database Tables

```
gemini_api_keys         → Keys + encryption
gemini_key_quotas       → Limits + usage
gemini_key_usage_log    → Mỗi lần gọi AI
gemini_key_rotation_log → Mỗi lần switch key
```

## Key Status Flow

```
ACTIVE → QUOTA_EXCEEDED → (reset quota) → ACTIVE
  ↓
INACTIVE (manual disable)
  ↓
REVOKED (key error, cannot re-enable)
```

## Troubleshooting

| Error | Fix |
|-------|-----|
| "No active keys" | Add key hoặc check status |
| "Encryption key not configured" | Add `GEMINI_ENCRYPTION_KEY` to .env |
| "Invalid token" | Encryption key changed, re-add keys |
| Auto-rotation not working | Check `track_usage()` được gọi |

## File Locations

**Backend**:
- Models: `app/models/gemini_keys.py`
- Service: `app/services/gemini_key_service.py`
- API: `app/api/v1/endpoints/gemini_keys.py`
- Migration: `scripts/add_gemini_keys_tables.py`

**Frontend**:
- Page: `pages/GeminiKeysManagementPage.tsx`
- Components: `components/gemini-keys/`
- Service: `services/geminiKeysService.ts`

## Environment Variables

```bash
# Required
GEMINI_ENCRYPTION_KEY=m0Qx1ZN...  # For encrypting keys

# Optional (backward compatibility)
GEMINI_API_KEY=AIza...            # Fallback if no keys in DB
GEMINI_MODEL=gemini-2.5-flash     # Default model
```

---

**Need help?** Check [GEMINI_KEYS_MANAGEMENT.md](GEMINI_KEYS_MANAGEMENT.md) for full docs.
