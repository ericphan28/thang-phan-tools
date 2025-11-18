"""
Pydantic schemas package
"""
from app.schemas.auth import (
    # User schemas
    UserBase,
    UserCreate,
    UserInDB,
    UserResponse,
    
    # Authentication schemas
    Token,
    TokenData,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    
    # Role schemas
    RoleBase,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    
    # Permission schemas
    PermissionBase,
    PermissionCreate,
    PermissionResponse,
    
    # User role assignment
    UserRoleAssignment,
    UserRoleResponse,
    
    # Password change
    PasswordChange,
    PasswordChangeResponse,
)

# Import UserUpdate from user.py instead
from app.schemas.user import UserUpdate

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    
    # Auth
    "Token",
    "TokenData",
    "LoginRequest",
    "LoginResponse",
    "RegisterRequest",
    "RegisterResponse",
    
    # Role
    "RoleBase",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    
    # Permission
    "PermissionBase",
    "PermissionCreate",
    "PermissionResponse",
    
    # User Role
    "UserRoleAssignment",
    "UserRoleResponse",
    
    # Password
    "PasswordChange",
    "PasswordChangeResponse",
]
