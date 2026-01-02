"""
FastAPI dependencies for authentication and authorization
"""
from typing import List, Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
# Use auth_models for SQLite compatibility (no Face model with ARRAY type)
from app.models.auth_models import User, Role, Permission

# HTTP Bearer security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token (REQUIRED)
    
    Usage:
        @router.get("/me")
        def get_me(user: User = Depends(get_current_user)):
            return user
    
    Args:
        credentials: HTTP Authorization credentials (Bearer token)
        db: Database session
    
    Returns:
        User object
    
    Raises:
        HTTPException: 401 if token invalid, user not found, or user inactive
    """
    token = credentials.credentials
    
    # Decode and verify token
    payload = decode_access_token(token)
    user_id: Optional[int] = payload.get("user_id")
    
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


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current authenticated user from JWT token (OPTIONAL - for demo/public routes)
    
    Returns None if no token provided or token invalid (doesn't raise error)
    
    Usage:
        @router.post("/ocr-demo")
        async def ocr_demo(user: Optional[User] = Depends(get_current_user_optional)):
            if user:
                # Authenticated user - track quota
                pass
            else:
                # Demo user - no tracking
                pass
    
    Args:
        authorization: Authorization header (Bearer token) - OPTIONAL
        db: Database session
    
    Returns:
        User object if authenticated, None if not
    """
    if not authorization:
        return None
    
    try:
        # Extract token from "Bearer <token>"
        if not authorization.startswith("Bearer "):
            return None
            
        token = authorization.replace("Bearer ", "")
        
        # Decode and verify token
        payload = decode_access_token(token)
        user_id: Optional[int] = payload.get("user_id")
        
        if user_id is None:
            return None
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        
        if user is None or not user.is_active:
            return None
        
        return user
    
    except Exception:
        # Any error → return None (demo mode)
        return None


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (convenience dependency)
    
    Usage:
        @router.get("/profile")
        def get_profile(user: User = Depends(get_current_active_user)):
            return user
    
    Returns:
        Active user object
    
    Raises:
        HTTPException: 403 if user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require current user to be a superuser
    
    Usage:
        @router.delete("/users/{user_id}")
        def delete_user(user_id: int, admin: User = Depends(get_current_superuser)):
            # Only superusers can access
            pass
    
    Returns:
        Superuser object
    
    Raises:
        HTTPException: 403 if user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Superuser access required."
        )
    return current_user


def require_roles(allowed_roles: List[str]):
    """
    Dependency factory for role-based access control
    
    Usage:
        @router.get("/admin-dashboard")
        def admin_dashboard(user: User = Depends(require_roles(["admin", "moderator"]))):
            return {"message": "Welcome to admin dashboard"}
    
    Args:
        allowed_roles: List of role names that are allowed
    
    Returns:
        Dependency function that checks user roles
    
    Example:
        # Only users with 'admin' or 'moderator' role can access
        @router.get("/admin")
        def admin_only(user: User = Depends(require_roles(["admin"]))):
            return {"message": "Admin area"}
    """
    async def check_roles(
        current_user: User = Depends(get_current_user)
    ) -> User:
        # Superuser has access to everything
        if current_user.is_superuser:
            return current_user
        
        # Get user's role names
        user_roles = [role.name for role in current_user.roles]
        
        # Check if user has any of the allowed roles
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {', '.join(allowed_roles)}"
            )
        
        return current_user
    
    return check_roles


def require_permission(resource: str, action: str):
    """
    Dependency factory for permission-based access control
    
    Usage:
        @router.delete("/images/{image_id}")
        def delete_image(
            image_id: int,
            user: User = Depends(require_permission("image", "delete"))
        ):
            # Only users with 'delete' permission on 'image' resource can access
            pass
    
    Args:
        resource: Resource name (e.g., "image", "document", "user")
        action: Action name (e.g., "read", "write", "delete")
    
    Returns:
        Dependency function that checks user permissions
    
    Example:
        # Only users with write permission on image resource
        @router.post("/images/upload")
        def upload_image(
            file: UploadFile,
            user: User = Depends(require_permission("image", "write"))
        ):
            # Upload logic
            pass
    """
    async def check_permission(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Superuser has all permissions
        if current_user.is_superuser:
            return current_user
        
        # Check if user has required permission through any of their roles
        has_permission = False
        
        for role in current_user.roles:
            permission = db.query(Permission).filter(
                Permission.role_id == role.id,
                Permission.resource == resource,
                Permission.action == action
            ).first()
            
            if permission:
                has_permission = True
                break
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires permission: {action} on {resource}"
            )
        
        return current_user
    
    return check_permission


def require_any_permission(permissions: List[tuple]):
    """
    Dependency factory for checking if user has ANY of the specified permissions
    
    Usage:
        @router.get("/content")
        def view_content(
            user: User = Depends(require_any_permission([
                ("image", "read"),
                ("document", "read")
            ]))
        ):
            # User needs either image:read OR document:read
            pass
    
    Args:
        permissions: List of (resource, action) tuples
    
    Returns:
        Dependency function that checks if user has any of the permissions
    """
    async def check_any_permission(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Superuser has all permissions
        if current_user.is_superuser:
            return current_user
        
        # Check if user has any of the required permissions
        for resource, action in permissions:
            for role in current_user.roles:
                permission = db.query(Permission).filter(
                    Permission.role_id == role.id,
                    Permission.resource == resource,
                    Permission.action == action
                ).first()
                
                if permission:
                    return current_user
        
        # No permission found
        perm_strings = [f"{res}:{act}" for res, act in permissions]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Requires any of: {', '.join(perm_strings)}"
        )
    
    return check_any_permission


# Optional: Extract token without raising exception (for optional auth)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None
    Useful for endpoints that have optional authentication
    
    Usage:
        @router.get("/public-or-private")
        def mixed_endpoint(user: Optional[User] = Depends(get_current_user_optional)):
            if user:
                return {"message": f"Hello {user.username}"}
            else:
                return {"message": "Hello guest"}
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
