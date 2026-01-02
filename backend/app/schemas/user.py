"""
User Management Schemas
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscore and dash')
        return v


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, max_length=100)
    is_active: bool = True
    is_superuser: bool = False
    role_ids: Optional[List[int]] = Field(default=None, description="List of role IDs to assign")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    role_ids: Optional[List[int]] = Field(None, description="List of role IDs to assign")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters')
            if not re.search(r'[A-Za-z]', v):
                raise ValueError('Password must contain at least one letter')
            if not re.search(r'[0-9]', v):
                raise ValueError('Password must contain at least one number')
        return v


class ProfileUpdate(BaseModel):
    """Schema for user updating their own profile"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)


class UserRoleAssignment(BaseModel):
    """Schema for assigning roles to user"""
    role_ids: List[int] = Field(..., description="List of role IDs to assign")


class RoleInfo(BaseModel):
    """Role information in user response"""
    id: int
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    roles: List[str]  # List of role names
    
    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """Detailed user response with full role info"""
    role_details: List[RoleInfo]
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Response for list users with pagination"""
    total: int
    page: int
    page_size: int
    total_pages: int
    users: List[UserResponse]


class UserSearchParams(BaseModel):
    """Search parameters for users"""
    search: Optional[str] = Field(None, description="Search in username, email, full_name")
    role: Optional[str] = Field(None, description="Filter by role name")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_superuser: Optional[bool] = Field(None, description="Filter by superuser status")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: str = Field("created_at", description="Sort field: username, email, created_at")
    sort_order: str = Field("desc", description="Sort order: asc or desc")
    
    @field_validator('sort_order')
    @classmethod
    def validate_sort_order(cls, v):
        if v.lower() not in ['asc', 'desc']:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v.lower()
    
    @field_validator('sort_by')
    @classmethod
    def validate_sort_by(cls, v):
        allowed_fields = ['username', 'email', 'created_at', 'updated_at', 'full_name']
        if v not in allowed_fields:
            raise ValueError(f'Sort by must be one of: {", ".join(allowed_fields)}')
        return v
