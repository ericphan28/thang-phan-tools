# 🔐 QUICKSTART - Authentication System

## 🚀 1. Initialize Database (5 minutes)

```powershell
cd D:\thang\utility-server\backend
python -m app.scripts.init_auth
```

**What it creates:**
- ✅ Tables: users, roles, permissions
- ✅ Roles: viewer, editor, admin  
- ✅ Admin user: `admin` / `admin123` ⚠️
- ✅ Demo users: `john_viewer`, `jane_editor` (password: `password123`)

---

## 🏃 2. Start Server (1 minute)

```powershell
cd D:\thang\utility-server\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open: **http://localhost:8000/docs**

---

## 🧪 3. Test APIs (3 minutes)

### A. Login (Get Token)

**Request:**
```http
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**PowerShell:**
```powershell
$body = @{username="admin"; password="admin123"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $body -ContentType "application/json"
$token = $response.token.access_token
Write-Host "Token: $token"
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "roles": ["admin"]
  },
  "token": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```

### B. Get Current User Info

**Request:**
```http
GET http://localhost:8000/api/v1/auth/me
Authorization: Bearer {your_token}
```

**PowerShell:**
```powershell
$headers = @{Authorization = "Bearer $token"}
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" -Method GET -Headers $headers
```

### C. List All Users (Admin Only)

**Request:**
```http
GET http://localhost:8000/api/v1/users
Authorization: Bearer {admin_token}
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/users" -Method GET -Headers $headers
```

---

## 🛡️ 4. Protect Your API Endpoints

### Simple Auth (Just Login Required)

```python
from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user
from app.models.models import User

router = APIRouter()

@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return {"username": user.username}
```

### Role-Based Auth

```python
from app.api.dependencies import require_roles

@router.delete("/data/{id}")
async def delete_data(
    id: int,
    user: User = Depends(require_roles(["admin", "editor"]))
):
    return {"message": f"Deleted by {user.username}"}
```

### Permission-Based Auth

```python
from app.api.dependencies import require_permission

@router.post("/upload")
async def upload_image(
    file: UploadFile,
    user: User = Depends(require_permission("image", "write"))
):
    return {"message": "Image uploaded"}
```

### Superuser Only

```python
from app.api.dependencies import get_current_superuser

@router.post("/system/reset")
async def reset_system(user: User = Depends(get_current_superuser)):
    return {"message": "System reset"}
```

---

## 📚 5. Complete Documentation

- **English Guide:** `AUTHENTICATION_SETUP.md`
- **Hướng dẫn Tiếng Việt:** `VIETNAMESE_AUTH_GUIDE.md`
- **Original Auth Architecture:** `AUTH_GUIDE.md`

---

## 🔒 6. Security Checklist

⚠️ **IMPORTANT - Do these IMMEDIATELY:**

```powershell
# 1. Change admin password
$changePass = @{
    old_password = "admin123"
    new_password = "YourStrongPassword123!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/change-password" `
    -Method POST -Headers $headers -Body $changePass -ContentType "application/json"
```

```env
# 2. Update JWT_SECRET_KEY in backend/.env
JWT_SECRET_KEY=your-very-long-random-secret-key-at-least-32-characters
```

```python
# 3. Generate secure key
import secrets
print(secrets.token_urlsafe(32))
```

---

## 📋 7. API Endpoints Summary

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login (get token)
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/change-password` - Change password
- `POST /api/v1/auth/logout` - Logout

### User Management (Admin only)
- `GET /api/v1/users` - List all users
- `GET /api/v1/users/{id}` - Get user by ID
- `POST /api/v1/users` - Create user
- `PATCH /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user
- `POST /api/v1/users/{id}/roles` - Assign roles
- `DELETE /api/v1/users/{id}/roles/{role}` - Remove role

---

## 🎭 8. Default Roles & Permissions

| Role | Permissions |
|------|-------------|
| **viewer** | image:read, document:read, face:read |
| **editor** | viewer permissions + image:write, document:write, face:write |
| **admin** | editor permissions + all:delete, user:* |
| **superuser** | Bypass all checks, full access |

---

## 🐛 9. Common Errors

| Error | Solution |
|-------|----------|
| "User not found" | Run init script again |
| "Token has expired" | Login again or refresh token |
| "Access denied" | User needs correct role/permission |
| "Database connection failed" | Check PostgreSQL running |

---

## ✅ 10. Files Created

```
✅ backend/app/models/models.py          - Updated with Role, Permission
✅ backend/app/schemas/auth.py           - All auth schemas
✅ backend/app/core/security.py          - JWT & password utilities
✅ backend/app/api/dependencies.py       - Auth dependencies
✅ backend/app/api/v1/endpoints/auth.py  - Auth endpoints
✅ backend/app/api/v1/endpoints/users.py - User management
✅ backend/app/scripts/init_auth.py      - Database init
✅ backend/app/main.py                   - Updated with routers
✅ AUTHENTICATION_SETUP.md               - Complete English guide
✅ VIETNAMESE_AUTH_GUIDE.md              - Hướng dẫn Tiếng Việt
✅ QUICKSTART_AUTH.md                    - This file
```

---

## 🎉 Done!

Your authentication system is **READY**! 🚀

**Next Steps:**
1. Run init script
2. Start server
3. Test login at http://localhost:8000/docs
4. Change admin password
5. Start building your protected APIs!

**Need Help?**
- Read: `AUTHENTICATION_SETUP.md` (detailed guide)
- Read: `VIETNAMESE_AUTH_GUIDE.md` (hướng dẫn chi tiết)
- Check: http://localhost:8000/docs (interactive API docs)
