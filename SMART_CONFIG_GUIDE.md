# 🧠 SMART CONFIG - Auto Environment Detection

## 🎯 Ý Tưởng
Code **tự động phát hiện môi trường** và chọn database host phù hợp:

```
┌─────────────────────────────────────────────────────────────┐
│  LOCALHOST (Development)                                    │
│  ✅ No /.dockerenv file                                     │
│  → Use VPS public IP: 165.99.59.47:5432                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  VPS DOCKER (Production)                                    │
│  ✅ File /.dockerenv exists                                 │
│  → Use Docker internal: postgres:5432                       │
└─────────────────────────────────────────────────────────────┘
```

**Kết quả:** Push code lên GitHub → Deploy → **KHÔNG cần sửa config!** 🎉

---

## 🚀 SETUP (1 lệnh)

```powershell
.\setup-smart-config.ps1
```

Script sẽ:
1. ✅ Expose PostgreSQL trên VPS (nếu chưa)
2. ✅ Setup firewall (chỉ cho IP của bạn)
3. ✅ Lấy credentials từ VPS
4. ✅ Update local `.env`
5. ✅ Test connection

**Thời gian:** ~2 phút

---

## 📋 Cách Hoạt Động

### File: `backend/app/core/config.py`

```python
@property
def DATABASE_URL(self) -> str:
    # Check if running inside Docker
    is_docker = os.path.exists('/.dockerenv')
    
    if is_docker:
        # Production - internal network
        db_host = "postgres"
    else:
        # Development - VPS public IP
        db_host = "165.99.59.47"
    
    return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{db_host}:5432/{self.DB_NAME}"
```

### File: `backend/.env`

```dotenv
# Same config for both localhost and production!
DB_USER=utility_user
DB_PASSWORD=your_secure_password
DB_NAME=utility_db
DB_PORT=5432
```

---

## 🔄 Workflow

### Development (Localhost)
```
1. Code trong backend/
2. python -m uvicorn app.main_simple:app --reload
3. Backend tự động detect: "Not in Docker"
4. Connect to: 165.99.59.47:5432 ✅
```

### Production (VPS)
```
1. git push
2. GitHub Actions build & deploy
3. Backend runs in Docker container
4. Backend tự động detect: "In Docker"
5. Connect to: postgres:5432 (internal) ✅
```

**ZERO config change!** 🎉

---

## ✅ Ưu Điểm

| Feature | Status |
|---------|--------|
| Zero config deploy | ✅ |
| Tự động phát hiện môi trường | ✅ |
| Bảo mật (Docker internal) | ✅ |
| Dễ debug (VPS direct) | ✅ |
| Team collaboration | ✅ |
| No third-party dependency | ✅ |

---

## 🧪 Testing

```powershell
# Test detection logic
python test-smart-config.py
```

Output:
```
✅ Localhost: Using 165.99.59.47:5432
✅ Docker: Will use postgres:5432
✅ Connection: Test passed
```

---

## 🔒 Bảo Mật

### Localhost → VPS
- Kết nối qua internet
- Firewall restrict to your IP only
- Strong password required

### Docker → PostgreSQL
- Internal network only
- Port 5432 NOT exposed to internet
- No external access

**Best of both worlds!** 🎯

---

## 📊 So Sánh Với Phương Án Khác

| Phương án | Config Deploy | Bảo mật | Phụ thuộc |
|-----------|---------------|---------|-----------|
| **Smart Config** | ✅ Zero | ⭐⭐⭐ Cao | Không |
| Supabase | ✅ Zero | ⭐⭐⭐ Cao | Third-party |
| Expose VPS | ✅ Zero | ⭐⭐ TB | Không |
| SSH Tunnel | ❌ Cần tunnel | ⭐⭐⭐ Cao | SSH |

---

## 🎯 Khi Nào Dùng?

### ✅ Phù hợp:
- Solo developer hoặc small team
- Tự host, không phụ thuộc third-party
- Cần bảo mật cao (Docker internal)
- Muốn zero config deploy

### ⚠️ Không phù hợp:
- Offline development
- Need localhost DB (không muốn phụ thuộc VPS)
- Very large team (nhiều người conflict)

---

## 📝 File Structure

```
backend/
├── app/
│   └── core/
│       └── config.py          # Smart detection logic ✨
├── .env                       # DB credentials (same for all)
└── .env.example               # Template

setup-smart-config.ps1         # Auto setup script
test-smart-config.py           # Test detection
```

---

## 🚨 Troubleshooting

### ❌ Connection refused
```bash
# Check VPS PostgreSQL running
ssh root@165.99.59.47
docker ps | grep postgres

# Check port exposed
docker-compose -f /opt/utility-server/docker-compose.prod.yml ps
```

### ❌ Wrong detection
```bash
# Manual override
export DB_HOST="your_custom_host"
```

### ❌ Password error
```bash
# Get correct password from VPS
ssh root@165.99.59.47
cat /opt/utility-server/.env | grep DB_PASSWORD
```

---

## 🎉 Kết Quả

**Trước:**
```
Localhost:  DATABASE_URL=sqlite://...
Production: DATABASE_URL=postgresql://...@postgres:5432/...
→ Phải sửa khi deploy ❌
```

**Sau (Smart Config):**
```dotenv
# Same for both!
DB_USER=utility_user
DB_PASSWORD=secure_pass
DB_NAME=utility_db

# Auto-detect:
Localhost  → postgresql://...@165.99.59.47:5432/... (detected)
Production → postgresql://...@postgres:5432/...      (detected)
→ KHÔNG cần sửa gì! ✅
```

---

## 📖 Next Steps

1. **Setup:** Run `.\setup-smart-config.ps1`
2. **Test:** Run `python test-smart-config.py`
3. **Develop:** Start backend normally
4. **Deploy:** `git push` - no config change needed!

---

## 💡 Pro Tips

### Override cho testing:
```bash
# Tạm thời dùng host khác
export DB_HOST="localhost"
python -m uvicorn app.main_simple:app --reload
```

### Multiple VPS:
```bash
# Dev VPS
export DB_HOST="dev.vps.com"

# Staging VPS
export DB_HOST="staging.vps.com"
```

### Check hiện tại đang dùng host nào:
```python
from app.core.config import settings
print(settings.DATABASE_URL)
```

---

## 🎯 TÓM TẮT

**Smart Config = Tự động + Zero Config + Bảo mật**

✅ Localhost auto dùng VPS IP
✅ Docker auto dùng internal host
✅ Deploy không cần sửa gì
✅ Team dùng chung config
✅ Production internal network (secure)

**Perfect cho self-hosted solution!** 🚀
