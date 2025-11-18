"""
Activity Log API Endpoints
For viewing audit trail of system activities
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.dependencies import get_current_superuser
from app.models.auth_models import User, ActivityLog

router = APIRouter()


# Schemas
from pydantic import BaseModel, Field

class ActivityLogInfo(BaseModel):
    id: int
    user_id: Optional[int]
    username: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[int]
    details: Optional[str]
    ip_address: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class ActivityLogListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    logs: List[ActivityLogInfo]


@router.get("/", response_model=ActivityLogListResponse)
def list_activity_logs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action (create/update/delete)"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type (user/role/permission)"),
    date_from: Optional[str] = Query(None, description="Filter from date (ISO format)"),
    date_to: Optional[str] = Query(None, description="Filter to date (ISO format)"),
    search: Optional[str] = Query(None, description="Search in details"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get activity logs with filtering and pagination (admin only)
    """
    # Base query
    query = db.query(ActivityLog)
    
    # Apply filters
    filters = []
    
    if user_id is not None:
        filters.append(ActivityLog.user_id == user_id)
    
    if action:
        filters.append(ActivityLog.action == action)
    
    if resource_type:
        filters.append(ActivityLog.resource_type == resource_type)
    
    if date_from:
        try:
            date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            filters.append(ActivityLog.created_at >= date_from_dt)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            filters.append(ActivityLog.created_at <= date_to_dt)
        except ValueError:
            pass
    
    if search:
        filters.append(
            or_(
                ActivityLog.details.contains(search),
                ActivityLog.ip_address.contains(search)
            )
        )
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Count total
    total = query.count()
    
    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size
    skip = (page - 1) * page_size
    
    # Get logs with user info
    logs = query.order_by(desc(ActivityLog.created_at)).offset(skip).limit(page_size).all()
    
    # Format response
    log_infos = []
    for log in logs:
        log_info = ActivityLogInfo(
            id=log.id,
            user_id=log.user_id,
            username=log.user.username if log.user else "System",
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            details=log.details,
            ip_address=log.ip_address,
            created_at=log.created_at.isoformat()
        )
        log_infos.append(log_info)
    
    return ActivityLogListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        logs=log_infos
    )


@router.get("/stats", response_model=dict)
def get_activity_stats(
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get activity statistics (admin only)
    """
    from_date = datetime.utcnow() - timedelta(days=days)
    
    # Total activities
    total = db.query(ActivityLog).filter(ActivityLog.created_at >= from_date).count()
    
    # By action
    actions = db.query(
        ActivityLog.action,
        func.count(ActivityLog.id)
    ).filter(
        ActivityLog.created_at >= from_date
    ).group_by(ActivityLog.action).all()
    
    # By resource
    resources = db.query(
        ActivityLog.resource_type,
        func.count(ActivityLog.id)
    ).filter(
        ActivityLog.created_at >= from_date
    ).group_by(ActivityLog.resource_type).all()
    
    # Most active users
    top_users = db.query(
        ActivityLog.user_id,
        User.username,
        func.count(ActivityLog.id).label('count')
    ).join(
        User, ActivityLog.user_id == User.id
    ).filter(
        ActivityLog.created_at >= from_date
    ).group_by(
        ActivityLog.user_id, User.username
    ).order_by(
        desc('count')
    ).limit(5).all()
    
    return {
        "total_activities": total,
        "days_analyzed": days,
        "by_action": {action: count for action, count in actions},
        "by_resource": {resource: count for resource, count in resources},
        "top_users": [
            {"user_id": uid, "username": uname, "activity_count": count}
            for uid, uname, count in top_users
        ]
    }
