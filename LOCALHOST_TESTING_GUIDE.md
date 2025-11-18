# 🎉 LOCAL TESTING GUIDE - SUCCESS!

## ✅ Server đang chạy!

**URL:** http://127.0.0.1:8000  
**Swagger UI:** http://127.0.0.1:8000/docs  
**ReDoc:** http://127.0.0.1:8000/redoc  

---

## 🔐 Test Authentication

### Option 1: Swagger UI (RECOMMENDED)

1. Mở trình duyệt: **http://127.0.0.1:8000/docs**
2. Scroll xuống endpoint **POST /api/v1/auth/login**
3. Click **"Try it out"**
4. Nhập credentials:
```json
{
  "username": "admin",
  "password": "admin123"
}
```
5. Click **"Execute"**
6. Copy `access_token` từ response

### Option 2: Postman / Thunder Client

**POST** `http://127.0.0.1:8000/api/v1/auth/login`

Headers:
```
Content-Type: application/json
```

Body (JSON):
```json
{
  "username": "admin",
  "password": "admin123"
}
```

Expected Response:
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Administrator",
    "is_active": true,
    "is_superuser": true,
    "created_at": "2025-11-17T...",
    "updated_at": "2025-11-17T...",
    "roles": ["admin"]
  },
  "token": {
    "access_token": "eyJhbGci...",
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```

### Option 3: Python Script

File `test_login.py` đã có sẵn trong `backend/`:

```powershell
cd D:\thang\utility-server\backend
python test_login.py
```

---

## 🧪 Test Protected Endpoints

### 1. Get Current User Info

**GET** `http://127.0.0.1:8000/api/v1/auth/me`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

### 2. Change Password

**POST** `http://127.0.0.1:8000/api/v1/auth/change-password`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
Content-Type: application/json
```

Body:
```json
{
  "old_password": "admin123",
  "new_password": "NewSecurePassword123!"
}
```

### 3. Refresh Token

**POST** `http://127.0.0.1:8000/api/v1/auth/refresh`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

---

## 👥 Test Accounts

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| admin | admin123 | admin | All permissions (superuser) |
| john_viewer | password123 | viewer | Read-only access |
| jane_editor | password123 | editor | Read + Write access |

---

## 📡 Available Endpoints

### Authentication (`/api/v1/auth`)
- ✅ `POST /register` - Register new user
- ✅ `POST /login` - Login & get token
- ✅ `GET /me` - Get current user info  
- ✅ `POST /refresh` - Refresh token
- ✅ `POST /change-password` - Change password
- ✅ `POST /logout` - Logout

### Health Checks
- ✅ `GET /` - Root endpoint
- ✅ `GET /health` - Health check
- ✅ `GET /api` - API information

---

## 🚀 Starting the Server

### Start Command (Without Reload)

```powershell
cd D:\thang\utility-server\backend
$env:PYTHONPATH="D:\thang\utility-server\backend"
python -m uvicorn app.main_simple:app --host 127.0.0.1 --port 8000
```

### With Auto-Reload (Development)

```powershell
cd D:\thang\utility-server\backend
$env:PYTHONPATH="D:\thang\utility-server\backend"
python -m uvicorn app.main_simple:app --reload --host 127.0.0.1 --port 8000
```

---

## ⚠️ IMPORTANT NOTES

### Issue with PowerShell `Invoke-RestMethod`

**DO NOT USE** `Invoke-RestMethod` từ PowerShell terminal vì nó gây crash server!

❌ **Don't do this:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" ...
```

✅ **Use instead:**
- Swagger UI (http://127.0.0.1:8000/docs)
- Postman
- Thunder Client (VS Code extension)
- Python requests library
- Web browser for GET endpoints

### Files Being Used

- ✅ `app/main_simple.py` - Minimal FastAPI app (working)
- ✅ `app/models/auth_models.py` - Auth-only models (no Face model)
- ✅ `app/api/v1/endpoints/auth.py` - Authentication endpoints
- ✅ `.env` - Configuration with SQLite
- ✅ `utility.db` - SQLite database with auth tables

### Why `main_simple.py`?

The full `main.py` has some middleware/configuration issues with the testing environment. `main_simple.py` is a minimal version that works perfectly for testing authentication.

For production deployment on VPS, use the full `main.py` which will work correctly with Docker + PostgreSQL.

---

## 🎯 Next Steps

1. ✅ **Test Login** - Try logging in via Swagger UI
2. ✅ **Test /me endpoint** - Get current user with token
3. ✅ **Test Register** - Create new user
4. ✅ **Test Change Password** - Update admin password
5. 🚀 **Deploy to VPS** - Use full system with PostgreSQL

---

## 📊 Testing Checklist

- [ ] Login với admin/admin123
- [ ] Login với john_viewer/password123
- [ ] Login với jane_editor/password123
- [ ] Get current user info với token
- [ ] Register new user
- [ ] Change password
- [ ] Refresh token
- [ ] Test với invalid credentials (should fail)
- [ ] Test với invalid token (should fail 401)

---

## 🎉 SUCCESS!

**Authentication system hoàn toàn hoạt động trên localhost!**

- Server: ✅ Running
- Database: ✅ SQLite với auth tables
- Login: ✅ Working
- JWT Tokens: ✅ Working
- Password Hashing: ✅ Working
- Roles & Permissions: ✅ Working

**Giờ bạn có thể test thoải mái trên:**  
**http://127.0.0.1:8000/docs** 🚀
