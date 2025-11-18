# 🔐 Authentication System - Complete Setup Guide

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Quick Start](#quick-start)
3. [Database Setup](#database-setup)
4. [API Endpoints](#api-endpoints)
5. [Usage Examples](#usage-examples)
6. [Security Best Practices](#security-best-practices)

---

## 🎯 System Overview

Authentication system with:
- ✅ JWT token-based authentication
- ✅ Role-Based Access Control (RBAC): viewer, editor, admin
- ✅ Permission-Based Access Control: resource:action format
- ✅ Password hashing with bcrypt
- ✅ User management endpoints

### Built Files:
```
backend/app/
├── models/models.py           # ✅ Updated (User, Role, Permission)
├── schemas/auth.py            # ✅ Created (All auth schemas)
├── core/security.py           # ✅ Updated (JWT, password hashing)
├── api/
│   ├── dependencies.py        # ✅ Created (Auth dependencies)
│   └── v1/endpoints/
│       ├── auth.py            # ✅ Created (Login, register, me)
│       └── users.py           # ✅ Created (User management)
├── scripts/
│   └── init_auth.py           # ✅ Created (DB initialization)
└── main.py                    # ✅ Updated (Routers included)
```

---

## 🚀 Quick Start

### Step 1: Initialize Database

```bash
cd D:\thang\utility-server\backend

# Run initialization script
python -m app.scripts.init_auth
```

**What it creates:**
- ✅ Database tables (users, roles, permissions)
- ✅ Default roles: viewer, editor, admin
- ✅ Superuser: `admin` / `admin123`
- ✅ Demo users: `john_viewer` / `password123`, `jane_editor` / `password123`

### Step 2: Start Server

```bash
# Make sure you're in backend directory
cd D:\thang\utility-server\backend

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Test API

Open browser: http://localhost:8000/docs

You'll see:
- 🔐 Authentication endpoints
- 👥 User Management endpoints
- 📝 Interactive API documentation

---

## 🗄️ Database Setup

### Method 1: Using Init Script (Recommended)

```bash
python -m app.scripts.init_auth
```

### Method 2: Manual Setup

```python
# Python shell
from app.core.database import SessionLocal, Base, engine
from app.models.models import User, Role, Permission
from app.core.security import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

# Create role
db = SessionLocal()
admin_role = Role(name="admin", description="Administrator")
db.add(admin_role)
db.commit()

# Create user
admin = User(
    username="admin",
    email="admin@example.com",
    hashed_password=get_password_hash("admin123"),
    is_active=True,
    is_superuser=True
)
admin.roles.append(admin_role)
db.add(admin)
db.commit()
```

---

## 🔌 API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication Endpoints

#### 1. Register New User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "Password123",
  "full_name": "New User"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully. Please login.",
  "user": {
    "id": 4,
    "username": "newuser",
    "email": "user@example.com",
    "full_name": "New User",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "roles": ["viewer"]
  }
}
```

#### 2. Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "System Administrator",
    "is_active": true,
    "is_superuser": true,
    "created_at": "2024-01-15T08:00:00",
    "updated_at": "2024-01-15T08:00:00",
    "roles": ["admin"]
  },
  "token": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```

#### 3. Get Current User Info
```http
GET /auth/me
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "System Administrator",
  "is_active": true,
  "is_superuser": true,
  "created_at": "2024-01-15T08:00:00",
  "updated_at": "2024-01-15T08:00:00",
  "roles": ["admin"]
}
```

#### 4. Refresh Token
```http
POST /auth/refresh
Authorization: Bearer {old_token}
```

#### 5. Change Password
```http
POST /auth/change-password
Authorization: Bearer {token}
Content-Type: application/json

{
  "old_password": "admin123",
  "new_password": "NewSecurePass123"
}
```

#### 6. Logout
```http
POST /auth/logout
Authorization: Bearer {token}
```

### User Management Endpoints (Admin Only)

#### 1. List All Users
```http
GET /users?skip=0&limit=100
Authorization: Bearer {admin_token}
```

#### 2. Get User by ID
```http
GET /users/{user_id}
Authorization: Bearer {admin_token}
```

#### 3. Create User
```http
POST /users
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "username": "employee1",
  "email": "employee1@example.com",
  "password": "Password123",
  "full_name": "Employee One"
}
```

#### 4. Update User
```http
PATCH /users/{user_id}
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "email": "newemail@example.com",
  "full_name": "Updated Name",
  "is_active": true
}
```

#### 5. Delete User
```http
DELETE /users/{user_id}
Authorization: Bearer {admin_token}
```

#### 6. Assign Roles to User
```http
POST /users/{user_id}/roles
Authorization: Bearer {admin_token}
Content-Type: application/json

["admin", "editor"]
```

#### 7. Remove Role from User
```http
DELETE /users/{user_id}/roles/{role_name}
Authorization: Bearer {admin_token}
```

---

## 💡 Usage Examples

### Example 1: Full Authentication Flow (PowerShell)

```powershell
# 1. Register new user
$registerBody = @{
    username = "testuser"
    email = "test@example.com"
    password = "Test123456"
    full_name = "Test User"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" `
    -Method POST `
    -Body $registerBody `
    -ContentType "application/json"

# 2. Login
$loginBody = @{
    username = "testuser"
    password = "Test123456"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -Body $loginBody `
    -ContentType "application/json"

$token = $response.token.access_token

# 3. Get current user info
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" `
    -Method GET `
    -Headers $headers
```

### Example 2: Protected Endpoint with Permissions

```python
from fastapi import APIRouter, Depends
from app.api.dependencies import require_permission, require_roles
from app.models.models import User

router = APIRouter()

# Only users with 'write' permission on 'image' resource
@router.post("/upload")
async def upload_image(
    file: UploadFile,
    user: User = Depends(require_permission("image", "write"))
):
    # Only users with image:write permission can access
    return {"message": f"Image uploaded by {user.username}"}

# Only admin and editor roles
@router.delete("/images/{image_id}")
async def delete_image(
    image_id: int,
    user: User = Depends(require_roles(["admin", "editor"]))
):
    # Only admin or editor can delete
    return {"message": f"Image {image_id} deleted by {user.username}"}

# Only superuser
@router.post("/admin/action")
async def admin_action(
    user: User = Depends(get_current_superuser)
):
    # Only superuser can access
    return {"message": "Admin action executed"}
```

### Example 3: Python Client

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login
login_data = {
    "username": "admin",
    "password": "admin123"
}
response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
token = response.json()["token"]["access_token"]

# Use token for authenticated requests
headers = {
    "Authorization": f"Bearer {token}"
}

# Get current user
user_info = requests.get(f"{BASE_URL}/auth/me", headers=headers)
print(user_info.json())

# List all users (admin only)
users = requests.get(f"{BASE_URL}/users", headers=headers)
print(users.json())
```

### Example 4: JavaScript/Fetch

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';

// Login
async function login() {
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: 'admin',
      password: 'admin123'
    })
  });
  
  const data = await response.json();
  const token = data.token.access_token;
  
  // Store token
  localStorage.setItem('token', token);
  return token;
}

// Get current user
async function getCurrentUser() {
  const token = localStorage.getItem('token');
  
  const response = await fetch(`${BASE_URL}/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
}

// Upload image with authentication
async function uploadImage(file) {
  const token = localStorage.getItem('token');
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${BASE_URL}/image/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  return await response.json();
}
```

---

## 🔒 Security Best Practices

### 1. Change Default Passwords
```bash
# After initialization, immediately change admin password
curl -X POST "http://localhost:8000/api/v1/auth/change-password" \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "admin123",
    "new_password": "YourStrongPassword123!"
  }'
```

### 2. Update JWT Secret Key

Edit `backend/.env`:
```env
JWT_SECRET_KEY=your-very-long-random-secret-key-here-min-32-chars
```

Generate secure key:
```python
import secrets
print(secrets.token_urlsafe(32))
# Output: "kR9jP2mN5qT8wX4bY7zC1aD6eF3gH0iJ"
```

### 3. Remove Demo Users in Production

```python
# In production, delete demo users
from app.core.database import SessionLocal
from app.models.models import User

db = SessionLocal()
db.query(User).filter(User.username.in_(["john_viewer", "jane_editor"])).delete()
db.commit()
```

### 4. Token Security

- ✅ Store tokens securely (httpOnly cookies or secure storage)
- ✅ Don't expose tokens in URLs
- ✅ Use HTTPS in production
- ✅ Set appropriate token expiration time

### 5. Password Policy

Implemented in `schemas/auth.py`:
- ✅ Minimum 8 characters
- ✅ Must contain letters and digits
- ✅ Hashed with bcrypt (cost factor 12)

---

## 🎭 Default Roles & Permissions

### Viewer Role
- `image:read` - View images
- `document:read` - View documents
- `face:read` - View face recognition results

### Editor Role
- All viewer permissions +
- `image:write` - Upload/edit images
- `document:write` - Upload/edit documents
- `face:write` - Add face data

### Admin Role
- All editor permissions +
- `image:delete` - Delete images
- `document:delete` - Delete documents
- `face:delete` - Delete face data
- `user:read` - View users
- `user:write` - Create/edit users
- `user:delete` - Delete users

### Superuser
- ✅ Bypass all permission checks
- ✅ Full access to everything
- ✅ Cannot be limited by roles

---

## 🧪 Testing

### Test with cURL

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Get current user (replace {token} with actual token)
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer {token}"

# List users
curl -X GET "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer {token}"
```

### Test with Swagger UI

1. Open: http://localhost:8000/docs
2. Click "Authorize" button (🔓 icon)
3. Login to get token
4. Enter token: `Bearer {your_token}`
5. Click "Authorize"
6. Now you can test all protected endpoints

---

## 🐛 Troubleshooting

### Error: "User not found"
- Check username spelling
- Verify user exists in database
- Run init script if database is empty

### Error: "Token has expired"
- Token expires after 24 hours (default)
- Login again to get new token
- Or use refresh token endpoint

### Error: "Access denied. Requires permission"
- User doesn't have required role/permission
- Admin needs to assign correct role
- Check roles: `GET /auth/me`

### Error: "Database connection failed"
- Verify PostgreSQL is running
- Check DATABASE_URL in `.env`
- Test connection: `psql -U utility_user -d utility_db`

---

## 📚 Additional Resources

- FastAPI Auth Tutorial: https://fastapi.tiangolo.com/tutorial/security/
- JWT Documentation: https://jwt.io/
- OAuth2 Scopes: https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/

---

## ✅ Checklist

Before deploying to production:

- [ ] Change admin password
- [ ] Update JWT_SECRET_KEY
- [ ] Remove demo users
- [ ] Enable HTTPS
- [ ] Set up token blacklist (optional)
- [ ] Configure CORS properly
- [ ] Set up monitoring/logging
- [ ] Test all endpoints
- [ ] Document custom permissions
- [ ] Set up backup strategy

---

## 🎉 Success!

Your authentication system is ready! Test it:

```bash
# Quick test
curl http://localhost:8000/api/v1/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Happy coding! 🚀
