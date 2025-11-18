# 🔐 API AUTHENTICATION & AUTHORIZATION GUIDE

**Date:** 17/11/2025  
**Project:** Utility Server API  
**Topic:** JWT Authentication + Role-Based Access Control (RBAC)

---

## 🎯 TỔNG QUAN

Bạn muốn:
1. ✅ **Authentication** - Xác thực user (đăng nhập)
2. ✅ **Authorization** - Phân quyền (permission)
3. ✅ API chỉ cho phép user đã login
4. ✅ Các endpoint khác nhau có permission khác nhau

---

## 🏗️ KIẾN TRÚC HỆ THỐNG AUTH

```
┌─────────────────────────────────────────────────────────┐
│  CLIENT (Browser/Mobile App)                             │
└─────────────────────────────────────────────────────────┘
                    │
                    │ 1. POST /auth/login
                    │    {username, password}
                    ▼
┌─────────────────────────────────────────────────────────┐
│  API SERVER (FastAPI)                                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Auth Endpoint                                    │   │
│  │ - Verify credentials                            │   │
│  │ - Generate JWT token                            │   │
│  │ - Return token                                  │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                    │
                    │ 2. Return JWT token
                    │    {access_token: "eyJ..."}
                    ▼
┌─────────────────────────────────────────────────────────┐
│  CLIENT                                                  │
│  - Save token (localStorage/cookie)                      │
└─────────────────────────────────────────────────────────┘
                    │
                    │ 3. Call protected API
                    │    Header: Authorization: Bearer eyJ...
                    ▼
┌─────────────────────────────────────────────────────────┐
│  API SERVER                                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Middleware                                       │   │
│  │ - Extract token                                 │   │
│  │ - Verify token signature                        │   │
│  │ - Check expiration                              │   │
│  │ - Get user info from token                      │   │
│  │ - Check permissions                             │   │
│  └─────────────────────────────────────────────────┘   │
│                    │                                     │
│                    │ ✅ Valid? → Process request         │
│                    │ ❌ Invalid? → Return 401            │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 COMPONENTS CẦN THIẾT

### 1️⃣ Database Models

```python
# models/models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

# Many-to-Many relationship table
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey('roles.id'))
    resource = Column(String, nullable=False)  # e.g., "image", "document", "user"
    action = Column(String, nullable=False)    # e.g., "read", "write", "delete"
    
    # Relationships
    role = relationship("Role", back_populates="permissions")
```

**Giải thích:**
- `User`: User account
- `Role`: Vai trò (admin, editor, viewer...)
- `Permission`: Quyền cụ thể (đọc ảnh, xóa file...)
- `user_roles`: Many-to-many (1 user có nhiều roles, 1 role có nhiều users)

---

### 2️⃣ Pydantic Schemas

```python
# schemas/auth.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# ===== USER SCHEMAS =====

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    roles: List[str] = []  # List of role names
    
    class Config:
        from_attributes = True

class User(UserInDB):
    """User response (không trả password)"""
    pass


# ===== AUTH SCHEMAS =====

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds

class TokenData(BaseModel):
    """Data inside JWT token"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    user: User
    token: Token


# ===== ROLE & PERMISSION SCHEMAS =====

class PermissionBase(BaseModel):
    resource: str  # "image", "document", "user"
    action: str    # "read", "write", "delete"

class Permission(PermissionBase):
    id: int
    
    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    permissions: List[PermissionBase] = []

class Role(RoleBase):
    id: int
    permissions: List[Permission] = []
    
    class Config:
        from_attributes = True
```

---

### 3️⃣ Security Utilities

```python
# core/security.py

from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Settings
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token
    
    Args:
        data: Dictionary to encode in token (user_id, username, roles, etc.)
        expires_delta: Token expiration time
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),  # issued at
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token data
    
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

---

### 4️⃣ Dependencies (Authentication)

```python
# api/dependencies.py

from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.models import User, Role, Permission

# HTTP Bearer token extractor
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Usage:
        @router.get("/me")
        def get_me(user: User = Depends(get_current_user)):
            return user
    """
    token = credentials.credentials
    
    # Decode token
    payload = decode_access_token(token)
    user_id: int = payload.get("user_id")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (shorthand)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """Only allow superusers"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def require_roles(allowed_roles: List[str]):
    """
    Dependency factory for role-based access control
    
    Usage:
        @router.get("/admin-only")
        def admin_only(user: User = Depends(require_roles(["admin"]))):
            return {"message": "You are admin!"}
    """
    async def check_roles(current_user: User = Depends(get_current_user)) -> User:
        user_roles = [role.name for role in current_user.roles]
        
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(allowed_roles)}"
            )
        
        return current_user
    
    return check_roles


def require_permission(resource: str, action: str):
    """
    Dependency factory for permission-based access control
    
    Usage:
        @router.delete("/images/{id}")
        def delete_image(
            id: int,
            user: User = Depends(require_permission("image", "delete"))
        ):
            # Delete image
            pass
    """
    async def check_permission(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Superuser has all permissions
        if current_user.is_superuser:
            return current_user
        
        # Check permissions through roles
        for role in current_user.roles:
            permissions = db.query(Permission).filter(
                Permission.role_id == role.id,
                Permission.resource == resource,
                Permission.action == action
            ).first()
            
            if permissions:
                return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requires permission: {action} on {resource}"
        )
    
    return check_permission
```

---

### 5️⃣ Auth Endpoints

```python
# api/v1/endpoints/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models.models import User, Role
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    UserCreate,
    User as UserSchema,
    Token
)
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register new user
    
    - **username**: unique username (3-50 chars)
    - **email**: unique email
    - **password**: password (min 8 chars)
    - **full_name**: optional full name
    """
    # Check if username exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=False
    )
    
    # Assign default role (viewer)
    default_role = db.query(Role).filter(Role.name == "viewer").first()
    if default_role:
        new_user.roles.append(default_role)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=LoginResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login to get JWT access token
    
    - **username**: your username
    - **password**: your password
    
    Returns:
        - **user**: user information
        - **token**: JWT access token (use in Authorization header)
    """
    # Find user
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Get user roles
    user_roles = [role.name for role in user.roles]
    
    # Get user permissions
    permissions = []
    for role in user.roles:
        for perm in role.permissions:
            perm_str = f"{perm.resource}:{perm.action}"
            if perm_str not in permissions:
                permissions.append(perm_str)
    
    # Token payload
    token_data = {
        "user_id": user.id,
        "username": user.username,
        "roles": user_roles,
        "permissions": permissions
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )
    
    return {
        "user": user,
        "token": {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds
        }
    }


@router.get("/me", response_model=UserSchema)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    
    Requires: Authentication (Bearer token)
    """
    return current_user


@router.post("/refresh", response_model=Token)
def refresh_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Refresh access token
    
    Requires: Valid access token
    Returns: New access token
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Get user roles and permissions
    user_roles = [role.name for role in current_user.roles]
    
    permissions = []
    for role in current_user.roles:
        for perm in role.permissions:
            perm_str = f"{perm.resource}:{perm.action}"
            if perm_str not in permissions:
                permissions.append(perm_str)
    
    token_data = {
        "user_id": current_user.id,
        "username": current_user.username,
        "roles": user_roles,
        "permissions": permissions
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
```

---

### 6️⃣ Protected Endpoints Example

```python
# api/v1/endpoints/images.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User
from app.api.dependencies import (
    get_current_user,
    require_permission,
    require_roles
)

router = APIRouter(prefix="/images", tags=["Images"])


@router.post("/upload")
def upload_image(
    file: UploadFile = File(...),
    user: User = Depends(require_permission("image", "write")),
    db: Session = Depends(get_db)
):
    """
    Upload image
    
    Requires: 
        - Authentication
        - Permission: write on image
    """
    # Process upload
    return {
        "message": "Image uploaded successfully",
        "filename": file.filename,
        "uploaded_by": user.username
    }


@router.get("/")
def list_images(
    user: User = Depends(require_permission("image", "read")),
    db: Session = Depends(get_db)
):
    """
    List all images
    
    Requires:
        - Authentication
        - Permission: read on image
    """
    return {
        "message": "List of images",
        "user": user.username
    }


@router.delete("/{image_id}")
def delete_image(
    image_id: int,
    user: User = Depends(require_permission("image", "delete")),
    db: Session = Depends(get_db)
):
    """
    Delete image
    
    Requires:
        - Authentication
        - Permission: delete on image
    """
    return {
        "message": f"Image {image_id} deleted",
        "deleted_by": user.username
    }


@router.get("/admin-only")
def admin_only_endpoint(
    user: User = Depends(require_roles(["admin"]))
):
    """
    Admin only endpoint
    
    Requires:
        - Authentication
        - Role: admin
    """
    return {
        "message": "You are admin!",
        "user": user.username
    }
```

---

## 🎓 CÁC LOẠI AUTHENTICATION

### 1️⃣ Public Endpoints (Không cần auth)

```python
@router.get("/health")
def health_check():
    """Anyone can access"""
    return {"status": "healthy"}
```

### 2️⃣ Protected Endpoints (Cần auth)

```python
@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    """Must be logged in"""
    return user
```

### 3️⃣ Role-Based Access

```python
@router.get("/admin")
def admin_only(user: User = Depends(require_roles(["admin"]))):
    """Must have 'admin' role"""
    return {"message": "Admin area"}
```

### 4️⃣ Permission-Based Access

```python
@router.delete("/images/{id}")
def delete_image(
    id: int,
    user: User = Depends(require_permission("image", "delete"))
):
    """Must have 'delete' permission on 'image' resource"""
    # Delete logic
    pass
```

---

## 📊 ROLE & PERMISSION MATRIX

### Recommended Roles:

| Role | Description | Permissions |
|------|-------------|-------------|
| **viewer** | Chỉ xem | read: image, document, text |
| **editor** | Xem + chỉnh sửa | read, write: image, document, text |
| **admin** | Full access | read, write, delete: all |
| **superuser** | System admin | ALL permissions |

### Permission Format:

```
resource:action

Examples:
- image:read       → Đọc ảnh
- image:write      → Upload/edit ảnh
- image:delete     → Xóa ảnh
- document:read    → Đọc document
- document:write   → Upload document
- user:read        → Xem user list
- user:write       → Tạo/edit user
- user:delete      → Xóa user
```

---

## 🔧 SETUP DATABASE

```python
# scripts/init_auth.py

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.models import User, Role, Permission
from app.core.security import get_password_hash

def init_db():
    """Initialize database with default roles and admin user"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create roles
        roles_data = [
            {
                "name": "viewer",
                "description": "Can only view content",
                "permissions": [
                    {"resource": "image", "action": "read"},
                    {"resource": "document", "action": "read"},
                    {"resource": "text", "action": "read"},
                ]
            },
            {
                "name": "editor",
                "description": "Can view and edit content",
                "permissions": [
                    {"resource": "image", "action": "read"},
                    {"resource": "image", "action": "write"},
                    {"resource": "document", "action": "read"},
                    {"resource": "document", "action": "write"},
                    {"resource": "text", "action": "read"},
                    {"resource": "text", "action": "write"},
                ]
            },
            {
                "name": "admin",
                "description": "Full access to content",
                "permissions": [
                    {"resource": "image", "action": "read"},
                    {"resource": "image", "action": "write"},
                    {"resource": "image", "action": "delete"},
                    {"resource": "document", "action": "read"},
                    {"resource": "document", "action": "write"},
                    {"resource": "document", "action": "delete"},
                    {"resource": "text", "action": "read"},
                    {"resource": "text", "action": "write"},
                    {"resource": "text", "action": "delete"},
                    {"resource": "user", "action": "read"},
                    {"resource": "user", "action": "write"},
                ]
            }
        ]
        
        for role_data in roles_data:
            # Check if role exists
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if existing_role:
                print(f"Role '{role_data['name']}' already exists, skipping...")
                continue
            
            # Create role
            role = Role(
                name=role_data["name"],
                description=role_data["description"]
            )
            db.add(role)
            db.flush()
            
            # Create permissions
            for perm_data in role_data["permissions"]:
                permission = Permission(
                    role_id=role.id,
                    resource=perm_data["resource"],
                    action=perm_data["action"]
                )
                db.add(permission)
            
            print(f"Created role: {role_data['name']}")
        
        db.commit()
        
        # Create superuser
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if not existing_admin:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                is_active=True,
                is_superuser=True
            )
            
            # Assign admin role
            admin_role = db.query(Role).filter(Role.name == "admin").first()
            if admin_role:
                admin_user.roles.append(admin_role)
            
            db.add(admin_user)
            db.commit()
            
            print("Created superuser: admin / admin123")
        else:
            print("Superuser 'admin' already exists, skipping...")
        
        print("\n✅ Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
```

---

## 🚀 CÁCH SỬ DỤNG

### 1️⃣ Initialize Database

```bash
# SSH vào VPS
ssh root@YOUR_VPS_IP

# Vào container backend
docker exec -it utility_backend bash

# Run init script
python scripts/init_auth.py

# Exit container
exit
```

### 2️⃣ Test với curl/Postman

#### A. Register new user

```bash
curl -X POST "http://YOUR_VPS_IP/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "john12345",
    "full_name": "John Doe"
  }'

# Response:
{
  "id": 2,
  "username": "john",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-11-17T10:30:00Z",
  "roles": ["viewer"]
}
```

#### B. Login

```bash
curl -X POST "http://YOUR_VPS_IP/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "john12345"
  }'

# Response:
{
  "user": {
    "id": 2,
    "username": "john",
    "email": "john@example.com",
    ...
  },
  "token": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 604800
  }
}
```

#### C. Call protected API

```bash
# Save token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Call protected endpoint
curl -X GET "http://YOUR_VPS_IP/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"

# Response: Your user info
```

#### D. Upload image (requires permission)

```bash
curl -X POST "http://YOUR_VPS_IP/api/v1/images/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@image.jpg"

# If user has "image:write" permission: Success
# If not: 403 Forbidden
```

---

### 3️⃣ Test qua Swagger UI

```
1. Mở: http://YOUR_VPS_IP/docs

2. Login để lấy token:
   - Expand "POST /api/v1/auth/login"
   - Click "Try it out"
   - Nhập username và password
   - Click "Execute"
   - Copy "access_token" từ response

3. Authorize Swagger:
   - Click nút "Authorize" (🔒 icon) ở trên cùng
   - Nhập: Bearer YOUR_TOKEN
   - Click "Authorize"
   - Click "Close"

4. Bây giờ có thể test protected endpoints:
   - GET /api/v1/auth/me
   - POST /api/v1/images/upload
   - etc.
```

---

## 📝 BEST PRACTICES

### 1️⃣ Security

```python
# ✅ DO:
- Dùng HTTPS trong production
- Set strong JWT_SECRET_KEY (random 64+ chars)
- Hash passwords với bcrypt
- Set reasonable token expiration (7 days max)
- Validate input (Pydantic)
- Rate limiting cho login endpoint

# ❌ DON'T:
- Không lưu password plain text
- Không commit JWT_SECRET_KEY vào git
- Không dùng HTTP trong production
- Không set token expiration quá dài
```

### 2️⃣ Token Management

```python
# Client side (JavaScript):
// Save token
localStorage.setItem('access_token', response.token.access_token);

// Add to all requests
const token = localStorage.getItem('access_token');
fetch('/api/v1/images/upload', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// Logout
localStorage.removeItem('access_token');
```

### 3️⃣ Error Handling

```python
# Handle auth errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code == 401:
        return JSONResponse(
            status_code=401,
            content={
                "detail": exc.detail,
                "code": "UNAUTHORIZED"
            }
        )
    # ... other error codes
```

---

## 🎯 TÓM TẮT

Để implement authentication + authorization:

**1. Database Models** ✅
   - User, Role, Permission tables

**2. Security Utilities** ✅
   - Password hashing
   - JWT token generation/verification

**3. Dependencies** ✅
   - get_current_user
   - require_roles
   - require_permission

**4. Auth Endpoints** ✅
   - POST /auth/register
   - POST /auth/login
   - GET /auth/me

**5. Protected Endpoints** ✅
   - Add `Depends(get_current_user)`
   - Or `Depends(require_permission(...))`

**6. Initialize DB** ✅
   - Create default roles
   - Create admin user

---

**Bạn muốn tôi:**
1. ✅ **Tạo file code đầy đủ** (models, endpoints, dependencies)?
2. 🔧 **Hướng dẫn integrate** vào project hiện tại?
3. 🧪 **Tạo test script** để test auth?

Chọn đi! 😊
