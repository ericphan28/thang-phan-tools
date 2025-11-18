"""
Authentication endpoints
"""
from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token
)
from app.core.config import settings
# Use auth_models for SQLite compatibility (no Face model with ARRAY type)
from app.models.auth_models import User, Role
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    Token,
    UserResponse,
    PasswordChange,
    PasswordChangeResponse
)
from app.api.dependencies import (
    get_current_user,
    get_current_active_user
)
from app.services.activity_logger import log_auth_action

router = APIRouter()


# Simple test endpoint
@router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"success": True, "message": "Auth endpoint is working!"}


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    - **username**: Unique username (3-50 characters)
    - **email**: Valid email address
    - **password**: Strong password (min 8 characters, must contain letters and digits)
    - **full_name**: Optional full name
    
    Returns user information and success message (no token, must login separately)
    """
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        if existing_user.username == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=False
    )
    
    # Assign default "viewer" role if it exists
    default_role = db.query(Role).filter(Role.name == "viewer").first()
    if default_role:
        new_user.roles.append(default_role)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Prepare response
    user_response = UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        is_active=new_user.is_active,
        is_superuser=new_user.is_superuser,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        roles=[role.name for role in new_user.roles]
    )
    
    return RegisterResponse(
        success=True,
        message="User registered successfully. Please login.",
        user=user_response
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login with username/email and password
    
    - **username**: Username or email address
    - **password**: User password
    
    Returns JWT access token and user information
    """
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == credentials.username) | (User.email == credentials.username)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Get user roles and permissions
    roles = [role.name for role in user.roles]
    permissions = []
    for role in user.roles:
        for perm in role.permissions:
            perm_str = f"{perm.resource}:{perm.action}"
            if perm_str not in permissions:
                permissions.append(perm_str)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": roles,
            "permissions": permissions,
            "is_superuser": user.is_superuser
        },
        expires_delta=access_token_expires
    )
    
    # Prepare response
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=roles
    )
    
    token = Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    )
    
    # Log successful login
    log_auth_action(
        db=db,
        user_id=user.id,
        action="login",
        details={"username": user.username},
        request=request
    )
    
    return LoginResponse(
        success=True,
        message="Login successful",
        user=user_response,
        token=token
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information
    
    Requires: Valid JWT token in Authorization header
    
    Returns current user profile
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        roles=[role.name for role in current_user.roles]
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Refresh access token
    
    Requires: Valid JWT token in Authorization header
    
    Returns new access token
    """
    # Get user roles and permissions
    roles = [role.name for role in current_user.roles]
    permissions = []
    for role in current_user.roles:
        for perm in role.permissions:
            perm_str = f"{perm.resource}:{perm.action}"
            if perm_str not in permissions:
                permissions.append(perm_str)
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "roles": roles,
            "permissions": permissions,
            "is_superuser": current_user.is_superuser
        },
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/change-password", response_model=PasswordChangeResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password
    
    Requires: Valid JWT token in Authorization header
    
    - **old_password**: Current password
    - **new_password**: New password (min 8 characters, must contain letters and digits)
    
    Returns success message
    """
    # Verify old password
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Check new password is different
    if password_data.old_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return PasswordChangeResponse(
        success=True,
        message="Password changed successfully"
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user
    
    Note: Since we're using JWT tokens (stateless), logout is handled client-side
    by deleting the token. This endpoint is provided for consistency and can be
    extended with token blacklisting if needed.
    
    Returns success message
    """
    return {
        "success": True,
        "message": "Logged out successfully. Please delete your access token."
    }
