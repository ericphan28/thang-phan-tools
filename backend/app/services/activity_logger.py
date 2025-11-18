"""
Activity Logger Service
Helper functions to log user activities
"""
from sqlalchemy.orm import Session
from fastapi import Request
import json
from typing import Optional, Any

from app.models.auth_models import ActivityLog


def log_activity(
    db: Session,
    user_id: Optional[int],
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    details: Optional[dict] = None,
    request: Optional[Request] = None
) -> ActivityLog:
    """
    Log an activity to the database
    
    Args:
        db: Database session
        user_id: ID of the user performing the action
        action: Action type (create, update, delete, login, logout)
        resource_type: Type of resource (user, role, permission)
        resource_id: ID of the affected resource
        details: Additional details as dictionary
        request: FastAPI request object (for IP and user agent)
    
    Returns:
        ActivityLog: Created activity log entry
    """
    # Get IP address and user agent from request
    ip_address = None
    user_agent = None
    
    if request:
        # Get real IP (handle proxies)
        ip_address = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not ip_address:
            ip_address = request.headers.get("X-Real-IP", "")
        if not ip_address:
            ip_address = request.client.host if request.client else None
        
        user_agent = request.headers.get("User-Agent", "")[:255]  # Limit length
    
    # Convert details to JSON string
    details_str = None
    if details:
        try:
            details_str = json.dumps(details, ensure_ascii=False)
        except (TypeError, ValueError):
            details_str = str(details)
    
    # Create log entry
    log = ActivityLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details_str,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(log)
    db.commit()
    db.refresh(log)
    
    return log


def log_user_action(
    db: Session,
    user_id: int,
    action: str,
    target_user_id: int,
    details: Optional[dict] = None,
    request: Optional[Request] = None
):
    """Log a user-related action"""
    return log_activity(
        db=db,
        user_id=user_id,
        action=action,
        resource_type="user",
        resource_id=target_user_id,
        details=details,
        request=request
    )


def log_role_action(
    db: Session,
    user_id: int,
    action: str,
    role_id: int,
    details: Optional[dict] = None,
    request: Optional[Request] = None
):
    """Log a role-related action"""
    return log_activity(
        db=db,
        user_id=user_id,
        action=action,
        resource_type="role",
        resource_id=role_id,
        details=details,
        request=request
    )


def log_auth_action(
    db: Session,
    user_id: Optional[int],
    action: str,
    details: Optional[dict] = None,
    request: Optional[Request] = None
):
    """Log an authentication action (login, logout)"""
    return log_activity(
        db=db,
        user_id=user_id,
        action=action,
        resource_type="auth",
        resource_id=user_id,
        details=details,
        request=request
    )
