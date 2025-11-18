"""
Role Management API Endpoints
Only accessible by superusers/admins
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.dependencies import get_current_superuser
from app.models.auth_models import User, Role, Permission
from app.services.activity_logger import log_role_action


router = APIRouter()


# Role Schemas (inline for simplicity)
from pydantic import BaseModel, Field, computed_field
from typing import Optional

from pydantic import BaseModel, Field, computed_field
from typing import Optional

class PermissionInfo(BaseModel):
    id: int
    role_id: int
    resource: str
    action: str
    
    @computed_field
    @property
    def name(self) -> str:
        """Generate display name from resource and action"""
        return f"{self.resource}.{self.action}"
    
    @computed_field
    @property
    def description(self) -> str:
        """Generate description from resource and action"""
        action_map = {
            'create': 'Tạo',
            'read': 'Xem',
            'update': 'Cập nhật',
            'delete': 'Xóa',
        }
        resource_map = {
            'user': 'người dùng',
            'role': 'vai trò',
            'permission': 'quyền hạn',
            'face': 'nhận diện khuôn mặt',
            'document': 'tài liệu',
            'image': 'hình ảnh',
        }
        action_text = action_map.get(self.action.lower(), self.action)
        resource_text = resource_map.get(self.resource.lower(), self.resource)
        return f"{action_text} {resource_text}"
    
    class Config:
        from_attributes = True


class RoleInfo(BaseModel):
    id: int
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


class RoleDetailInfo(RoleInfo):
    permissions: List[PermissionInfo]
    
    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    permission_specs: Optional[List[dict]] = Field(None, description="List of {resource, action} dicts")


class RoleUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=200)
    permission_specs: Optional[List[dict]] = Field(None, description="List of {resource, action} dicts")


@router.get("/", response_model=List[RoleInfo])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get all roles (admin only)
    """
    roles = db.query(Role).all()
    return roles


@router.get("/{role_id}", response_model=RoleDetailInfo)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get role by ID with permissions (admin only)
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    return role


@router.post("/", response_model=RoleDetailInfo, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: RoleCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Create a new role (admin only)
    """
    # Check if role name exists
    existing_role = db.query(Role).filter(Role.name == role_data.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name already exists"
        )
    
    # Create role
    role = Role(
        name=role_data.name,
        description=role_data.description
    )
    db.add(role)
    db.flush()  # Get role.id without committing
    
    # Create permissions if provided
    if role_data.permission_specs:
        for spec in role_data.permission_specs:
            permission = Permission(
                role_id=role.id,
                resource=spec.get('resource', ''),
                action=spec.get('action', '')
            )
            db.add(permission)
    
    db.commit()
    db.refresh(role)
    
    # Log activity
    log_role_action(
        db=db,
        user_id=current_user.id,
        action="create",
        role_id=role.id,
        details={"role_name": role.name, "permissions_count": len(role_data.permission_specs or [])},
        request=request
    )
    
    return role


@router.put("/{role_id}", response_model=RoleDetailInfo)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Update role (admin only)
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Update description
    if role_data.description is not None:
        role.description = role_data.description
    
    # Update permissions - delete old and create new
    if role_data.permission_specs is not None:
        # Delete existing permissions
        db.query(Permission).filter(Permission.role_id == role_id).delete()
        
        # Create new permissions
        for spec in role_data.permission_specs:
            # spec is a dict with 'resource' and 'action' keys
            resource = spec.get('resource', '') if isinstance(spec, dict) else ''
            action = spec.get('action', '') if isinstance(spec, dict) else ''
            
            permission = Permission(
                role_id=role.id,
                resource=resource,
                action=action
            )
            db.add(permission)
    
    db.commit()
    db.refresh(role)
    
    # Log activity
    log_role_action(
        db=db,
        user_id=current_user.id,
        action="update",
        role_id=role.id,
        details={"role_name": role.name, "permissions_count": len(role.permissions)},
        request=request
    )
    
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Delete a role (admin only)
    
    ⚠️ This will remove the role from all users!
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Prevent deleting default roles
    if role.name in ["admin", "viewer", "editor"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete default system roles"
        )
    
    role_name = role.name
    
    # Log activity before deletion
    log_role_action(
        db=db,
        user_id=current_user.id,
        action="delete",
        role_id=role_id,
        details={"role_name": role_name},
        request=request
    )
    
    db.delete(role)
    db.commit()
    
    return None


@router.get("/{role_id}/users", response_model=List[dict])
def get_role_users(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get all users with this role (admin only)
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    users = db.query(User).join(User.roles).filter(Role.id == role_id).all()
    
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active
        }
        for user in users
    ]


# Permission endpoints
@router.get("/permissions/all", response_model=List[PermissionInfo])
def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get all available permissions (admin only)
    """
    permissions = db.query(Permission).all()
    return permissions


@router.get("/permissions/{permission_id}", response_model=PermissionInfo)
def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get permission by ID (admin only)
    """
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    return permission
