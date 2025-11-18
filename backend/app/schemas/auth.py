"""
Authentication and Authorization Schemas
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


# ===== USER SCHEMAS =====

class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 characters)")
    email: EmailStr = Field(..., description="Valid email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, max_length=100, description="Password (minimum 8 characters)")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v


# Note: UserUpdate moved to user.py to avoid duplication
# Import from user.py if needed: from app.schemas.user import UserUpdate


class UserInDB(UserBase):
    """User schema with database fields"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    roles: List[str] = []  # List of role names
    
    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    """User response schema (public, no sensitive data)"""
    pass


# ===== AUTHENTICATION SCHEMAS =====

class Token(BaseModel):
    """JWT token response"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenData(BaseModel):
    """Data stored inside JWT token"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []


class LoginRequest(BaseModel):
    """Login request schema"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class LoginResponse(BaseModel):
    """Login response schema"""
    success: bool = True
    message: str = "Login successful"
    user: UserResponse
    token: Token


class RegisterRequest(UserCreate):
    """Register request schema (alias for UserCreate)"""
    pass


class RegisterResponse(BaseModel):
    """Register response schema"""
    success: bool = True
    message: str = "User registered successfully"
    user: UserResponse


# ===== ROLE SCHEMAS =====

class RoleBase(BaseModel):
    """Base role schema"""
    name: str = Field(..., min_length=2, max_length=50, description="Role name")
    description: Optional[str] = Field(None, max_length=200, description="Role description")


class RoleCreate(RoleBase):
    """Schema for creating a new role"""
    permissions: List['PermissionCreate'] = []


class RoleUpdate(BaseModel):
    """Schema for updating role"""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class RoleResponse(RoleBase):
    """Role response schema"""
    id: int
    created_at: datetime
    permissions: List['PermissionResponse'] = []
    
    class Config:
        from_attributes = True


# ===== PERMISSION SCHEMAS =====

class PermissionBase(BaseModel):
    """Base permission schema"""
    resource: str = Field(..., description="Resource name (e.g., 'image', 'document')")
    action: str = Field(..., description="Action name (e.g., 'read', 'write', 'delete')")


class PermissionCreate(PermissionBase):
    """Schema for creating a new permission"""
    pass


class PermissionResponse(PermissionBase):
    """Permission response schema"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== USER ROLE ASSIGNMENT =====

class UserRoleAssignment(BaseModel):
    """Schema for assigning roles to user"""
    user_id: int = Field(..., description="User ID")
    role_names: List[str] = Field(..., description="List of role names to assign")


class UserRoleResponse(BaseModel):
    """Response after role assignment"""
    success: bool = True
    message: str = "Roles assigned successfully"
    user_id: int
    roles: List[str]


# ===== PASSWORD CHANGE =====

class PasswordChange(BaseModel):
    """Schema for changing password"""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v


class PasswordChangeResponse(BaseModel):
    """Response after password change"""
    success: bool = True
    message: str = "Password changed successfully"


# Forward references
RoleCreate.model_rebuild()
RoleResponse.model_rebuild()
