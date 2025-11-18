"""
User Management API Endpoints
Only accessible by superusers/admins
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
import math

from app.core.database import get_db
from app.api.dependencies import get_current_superuser
from app.models.auth_models import User
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserDetailResponse,
    UserListResponse, UserRoleAssignment, RoleInfo
)
from app.services.activity_logger import log_user_action
from app.services.user_service import UserService


router = APIRouter()


@router.get("/stats", response_model=dict)
def get_user_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Get user statistics (admin only)"""
    return UserService.get_user_stats(db)


@router.get("/", response_model=UserListResponse)
def list_users(
    search: Optional[str] = Query(None, description="Search in username, email, full_name"),
    role: Optional[str] = Query(None, description="Filter by role name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_superuser: Optional[bool] = Query(None, description="Filter by superuser status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Get paginated list of users with filters (admin only)"""
    users, total = UserService.get_users(
        db=db,
        search=search,
        role=role,
        is_active=is_active,
        is_superuser=is_superuser,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    total_pages = math.ceil(total / page_size)
    
    user_responses = []
    for user in users:
        user_responses.append(UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=[role.name for role in user.roles]
        ))
    
    return UserListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        users=user_responses
    )


@router.get("/{user_id}", response_model=UserDetailResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Get user by ID with detailed information (admin only)"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserDetailResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=[role.name for role in user.roles],
        role_details=[
            RoleInfo(id=role.id, name=role.name, description=role.description)
            for role in user.roles
        ]
    )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Create a new user (admin only)"""
    user = UserService.create_user(db, user_data)
    
    # Log activity
    log_user_action(
        db=db,
        user_id=current_user.id,
        action="create",
        target_user_id=user.id,
        details={"username": user.username, "email": user.email},
        request=request
    )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=[role.name for role in user.roles]
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Update user information (admin only)"""
    user = UserService.update_user(db, user_id, user_data)
    
    # Log activity
    log_user_action(
        db=db,
        user_id=current_user.id,
        action="update",
        target_user_id=user.id,
        details={"username": user.username, "changes": user_data.model_dump(exclude_unset=True)},
        request=request
    )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=[role.name for role in user.roles]
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Delete a user (admin only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    # Get user info before deletion
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        username = user.username
        # Log activity
        log_user_action(
            db=db,
            user_id=current_user.id,
            action="delete",
            target_user_id=user_id,
            details={"username": username},
            request=request
        )
    
    UserService.delete_user(db, user_id)
    return None


@router.post("/{user_id}/roles", response_model=UserResponse)
def assign_roles_to_user(
    user_id: int,
    role_assignment: UserRoleAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Assign roles to user (replaces existing roles) (admin only)"""
    user = UserService.assign_roles(db, user_id, role_assignment.role_ids)
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=[role.name for role in user.roles]
    )


@router.post("/{user_id}/roles/add", response_model=UserResponse)
def add_roles_to_user(
    user_id: int,
    role_assignment: UserRoleAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Add roles to user (keeps existing roles) (admin only)"""
    user = UserService.add_roles(db, user_id, role_assignment.role_ids)
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=[role.name for role in user.roles]
    )


@router.post("/{user_id}/roles/remove", response_model=UserResponse)
def remove_roles_from_user(
    user_id: int,
    role_assignment: UserRoleAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Remove roles from user (admin only)"""
    user = UserService.remove_roles(db, user_id, role_assignment.role_ids)
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=[role.name for role in user.roles]
    )


@router.post("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Activate a user (admin only)"""
    user = UserService.update_user(db, user_id, UserUpdate(is_active=True))
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=[role.name for role in user.roles]
    )


@router.post("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Deactivate a user (admin only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself"
        )
    
    user = UserService.update_user(db, user_id, UserUpdate(is_active=False))
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=[role.name for role in user.roles]
    )
