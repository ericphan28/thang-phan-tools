# 🔐 Hướng Dẫn Sử Dụng Xác Thực API

## 🎯 Tổng Quan

Hệ thống xác thực đã được tạo hoàn chỉnh với:
- ✅ **JWT Token** - Xác thực bằng token
- ✅ **RBAC** - Phân quyền theo vai trò (viewer, editor, admin)
- ✅ **Permission** - Kiểm soát chi tiết (image:write, document:delete, etc.)
- ✅ **Password Hash** - Mã hóa mật khẩu với bcrypt

---

## 🚀 Bắt Đầu Nhanh

### Bước 1: Khởi Tạo Database

```powershell
cd D:\thang\utility-server\backend

# Chạy script khởi tạo
python -m app.scripts.init_auth
```

**Kết quả:**
- ✅ Tạo bảng: users, roles, permissions
- ✅ Tạo 3 roles: viewer, editor, admin
- ✅ Tạo admin: `admin` / `admin123` ⚠️ **ĐỔI NGAY**
- ✅ Tạo user demo: `john_viewer`, `jane_editor` (password: `password123`)

### Bước 2: Chạy Server

```powershell
cd D:\thang\utility-server\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Bước 3: Kiểm Tra

Mở trình duyệt: **http://localhost:8000/docs**

---

## 🔌 Các API Endpoint

### Base URL
```
http://localhost:8000/api/v1
```

### 1️⃣ Đăng Ký (Register)

```http
POST /auth/register
Content-Type: application/json

{
  "username": "nguoidung1",
  "email": "user@example.com",
  "password": "MatKhau123",
  "full_name": "Nguyễn Văn A"
}
```

### 2️⃣ Đăng Nhập (Login)

```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Trả về:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "roles": ["admin"]
  },
  "token": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```

**Lưu token này để dùng cho các request sau!**

### 3️⃣ Lấy Thông Tin User Hiện Tại

```http
GET /auth/me
Authorization: Bearer {token}
```

### 4️⃣ Đổi Mật Khẩu

```http
POST /auth/change-password
Authorization: Bearer {token}
Content-Type: application/json

{
  "old_password": "admin123",
  "new_password": "MatKhauMoi123"
}
```

### 5️⃣ Refresh Token

```http
POST /auth/refresh
Authorization: Bearer {token_cũ}
```

---

## 👥 Quản Lý Users (Chỉ Admin)

### Xem Tất Cả Users
```http
GET /users
Authorization: Bearer {admin_token}
```

### Xem User Theo ID
```http
GET /users/{user_id}
Authorization: Bearer {admin_token}
```

### Tạo User Mới
```http
POST /users
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "username": "nhanvien1",
  "email": "nhanvien1@example.com",
  "password": "Password123",
  "full_name": "Nhân Viên 1"
}
```

### Gán Roles Cho User
```http
POST /users/{user_id}/roles
Authorization: Bearer {admin_token}
Content-Type: application/json

["editor", "viewer"]
```

### Xóa User
```http
DELETE /users/{user_id}
Authorization: Bearer {admin_token}
```

---

## 💻 Ví Dụ Sử Dụng

### Ví Dụ 1: PowerShell - Đăng Nhập & Gọi API

```powershell
# 1. Đăng nhập
$loginData = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -Body $loginData `
    -ContentType "application/json"

# 2. Lấy token
$token = $response.token.access_token
Write-Host "Token: $token"

# 3. Gọi API cần xác thực
$headers = @{
    Authorization = "Bearer $token"
}

$userInfo = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" `
    -Method GET `
    -Headers $headers

Write-Host "User: $($userInfo.username)"
Write-Host "Roles: $($userInfo.roles -join ', ')"
```

### Ví Dụ 2: Python - Client Script

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Đăng nhập
def login(username, password):
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    data = response.json()
    return data["token"]["access_token"]

# Lấy thông tin user
def get_user_info(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    return response.json()

# Sử dụng
token = login("admin", "admin123")
print(f"Token: {token}")

user = get_user_info(token)
print(f"User: {user['username']}")
print(f"Roles: {', '.join(user['roles'])}")
```

### Ví Dụ 3: JavaScript/Fetch

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';

// Đăng nhập
async function login(username, password) {
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  const data = await response.json();
  const token = data.token.access_token;
  
  // Lưu token
  localStorage.setItem('token', token);
  return token;
}

// Gọi API với token
async function callProtectedAPI() {
  const token = localStorage.getItem('token');
  
  const response = await fetch(`${BASE_URL}/auth/me`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  return await response.json();
}

// Sử dụng
await login('admin', 'admin123');
const user = await callProtectedAPI();
console.log('User:', user.username);
```

---

## 🛡️ Bảo Vệ API Endpoints

### Cách 1: Chỉ Cần Đăng Nhập

```python
from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user
from app.models.models import User

router = APIRouter()

@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    # Chỉ user đã login mới vào được
    return {"username": user.username, "email": user.email}
```

### Cách 2: Yêu Cầu Role Cụ Thể

```python
from app.api.dependencies import require_roles

# Chỉ admin và editor
@router.delete("/data/{id}")
async def delete_data(
    id: int,
    user: User = Depends(require_roles(["admin", "editor"]))
):
    return {"message": f"Deleted by {user.username}"}

# Chỉ admin
@router.post("/admin/action")
async def admin_action(
    user: User = Depends(require_roles(["admin"]))
):
    return {"message": "Admin action"}
```

### Cách 3: Yêu Cầu Permission Cụ Thể

```python
from app.api.dependencies import require_permission

# Cần quyền "write" trên resource "image"
@router.post("/upload")
async def upload_image(
    file: UploadFile,
    user: User = Depends(require_permission("image", "write"))
):
    # Chỉ user có permission image:write
    return {"message": f"Uploaded by {user.username}"}

# Cần quyền "delete" trên resource "document"
@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    user: User = Depends(require_permission("document", "delete"))
):
    return {"message": "Document deleted"}
```

### Cách 4: Chỉ Superuser

```python
from app.api.dependencies import get_current_superuser

@router.post("/system/reset")
async def reset_system(
    user: User = Depends(get_current_superuser)
):
    # Chỉ superuser (is_superuser=True)
    return {"message": "System reset"}
```

---

## 🎭 Roles & Permissions

### Viewer (Người Xem)
- ✅ `image:read` - Xem hình ảnh
- ✅ `document:read` - Xem tài liệu
- ✅ `face:read` - Xem kết quả nhận diện

### Editor (Người Chỉnh Sửa)
- ✅ Tất cả quyền của Viewer
- ✅ `image:write` - Upload/sửa hình
- ✅ `document:write` - Upload/sửa tài liệu
- ✅ `face:write` - Thêm dữ liệu khuôn mặt

### Admin (Quản Trị Viên)
- ✅ Tất cả quyền của Editor
- ✅ `image:delete` - Xóa hình ảnh
- ✅ `document:delete` - Xóa tài liệu
- ✅ `face:delete` - Xóa dữ liệu khuôn mặt
- ✅ `user:read` - Xem users
- ✅ `user:write` - Tạo/sửa users
- ✅ `user:delete` - Xóa users

### Superuser
- ✅ Bypass tất cả permission checks
- ✅ Toàn quyền truy cập
- ✅ Không bị giới hạn bởi roles

---

## 🔒 Bảo Mật

### 1. Đổi Mật Khẩu Admin Ngay Lập Tức

```powershell
$changePassword = @{
    old_password = "admin123"
    new_password = "MatKhauManh123!"
} | ConvertTo-Json

$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/change-password" `
    -Method POST `
    -Headers $headers `
    -Body $changePassword `
    -ContentType "application/json"
```

### 2. Đổi JWT Secret Key

Sửa file `backend/.env`:
```env
JWT_SECRET_KEY=key-bao-mat-cua-ban-toi-thieu-32-ky-tu-ngau-nhien
```

Tạo key ngẫu nhiên:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 3. Xóa Demo Users (Production)

```python
from app.core.database import SessionLocal
from app.models.models import User

db = SessionLocal()
db.query(User).filter(
    User.username.in_(["john_viewer", "jane_editor"])
).delete()
db.commit()
```

---

## 🐛 Xử Lý Lỗi Thường Gặp

### Lỗi: "User not found"
- ✅ Kiểm tra username đúng chưa
- ✅ Chạy lại init script: `python -m app.scripts.init_auth`

### Lỗi: "Token has expired"
- ✅ Token hết hạn sau 24h
- ✅ Đăng nhập lại để lấy token mới
- ✅ Hoặc dùng refresh token: `POST /auth/refresh`

### Lỗi: "Access denied. Requires permission"
- ✅ User không có quyền cần thiết
- ✅ Admin cần gán role phù hợp
- ✅ Kiểm tra roles: `GET /auth/me`

### Lỗi: "Database connection failed"
- ✅ Kiểm tra PostgreSQL đang chạy
- ✅ Kiểm tra DATABASE_URL trong `.env`

---

## 📝 Các Files Đã Tạo

```
backend/app/
├── models/models.py              # ✅ Models (User, Role, Permission)
├── schemas/auth.py               # ✅ Schemas (Login, Token, etc.)
├── core/security.py              # ✅ JWT & Password utilities
├── api/
│   ├── dependencies.py           # ✅ Auth dependencies
│   └── v1/endpoints/
│       ├── auth.py               # ✅ Login, register, me
│       └── users.py              # ✅ User management
├── scripts/
│   └── init_auth.py              # ✅ Database init script
└── main.py                       # ✅ Updated with routers
```

---

## ✅ Checklist Trước Khi Deploy

- [ ] Đổi mật khẩu admin
- [ ] Đổi JWT_SECRET_KEY
- [ ] Xóa demo users
- [ ] Bật HTTPS
- [ ] Cấu hình CORS đúng
- [ ] Test tất cả endpoints
- [ ] Backup database

---

## 🎉 Hoàn Thành!

Test nhanh:
```powershell
# PowerShell
$loginData = @{username="admin"; password="admin123"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST -Body $loginData -ContentType "application/json"
```

Chúc bạn thành công! 🚀
