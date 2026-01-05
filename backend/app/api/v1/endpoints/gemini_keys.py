"""
Admin API endpoints for Gemini API Keys Management
CHXI superuser mới được access
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.dependencies import get_current_superuser
from app.models.auth_models import User
from app.models.gemini_keys import KeyStatus, QuotaType, UsageStatus
from app.schemas.gemini_keys import (
    GeminiAPIKeyCreate,
    GeminiAPIKeyUpdate,
    GeminiAPIKeyResponse,
    QuotaResponse,
    UsageLogResponse,
    RotationLogResponse,
    DashboardMetrics,
    KeyHealthOverview,
    UsageTrend,
    ModelUsageStats,
    UserUsageStats,
    KeyStatusEnum
)
from app.services.gemini_key_service import GeminiKeyService

router = APIRouter(prefix="/gemini-keys", tags=["Gemini Keys Management (Admin)"])


# ========== KEY CRUD ==========

@router.post("/keys", response_model=GeminiAPIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_gemini_key(
    key_data: GeminiAPIKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    **Tạo Gemini API key mới (Admin only)**
    
    - Validate key (test call API)
    - Encrypt key trước khi lưu
    - Initialize quota
    """
    service = GeminiKeyService(db)
    
    try:
        db_key = service.create_key(key_data, created_by_user_id=current_user.id)
        
        # Build response với quota info
        monthly_quota = next(
            (q for q in db_key.quotas if q.quota_type == QuotaType.MONTHLY),
            None
        )
        
        return GeminiAPIKeyResponse(
            id=db_key.id,
            key_name=db_key.key_name,
            account_email=db_key.account_email,
            api_key_masked=service.mask_api_key(service.decrypt_api_key(db_key.api_key_encrypted)),
            provider=db_key.provider,
            status=db_key.status,
            priority=db_key.priority,
            created_at=db_key.created_at,
            last_used_at=db_key.last_used_at,
            notes=db_key.notes,
            monthly_quota_limit=monthly_quota.quota_limit if monthly_quota else None,
            monthly_quota_used=monthly_quota.quota_used if monthly_quota else None,
            monthly_quota_remaining=monthly_quota.quota_remaining if monthly_quota else None,
            monthly_usage_percentage=monthly_quota.usage_percentage if monthly_quota else None,
            is_near_limit=monthly_quota.is_near_limit if monthly_quota else None
        )
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/keys", response_model=List[GeminiAPIKeyResponse])
async def list_gemini_keys(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    **Liệt kê tất cả Gemini API keys (Admin only)**
    
    - include_inactive=True: Hiển thị cả keys inactive/revoked
    """
    service = GeminiKeyService(db)
    keys = service.get_all_keys(include_inactive=include_inactive)
    
    result = []
    for key in keys:
        monthly_quota = next(
            (q for q in key.quotas if q.quota_type == QuotaType.MONTHLY),
            None
        )
        
        result.append(GeminiAPIKeyResponse(
            id=key.id,
            key_name=key.key_name,
            account_email=key.account_email,
            api_key_masked=service.mask_api_key(service.decrypt_api_key(key.api_key_encrypted)),
            provider=key.provider,
            status=key.status,
            priority=key.priority,
            created_at=key.created_at,
            last_used_at=key.last_used_at,
            notes=key.notes,
            monthly_quota_limit=monthly_quota.quota_limit if monthly_quota else None,
            monthly_quota_used=monthly_quota.quota_used if monthly_quota else None,
            monthly_quota_remaining=monthly_quota.quota_remaining if monthly_quota else None,
            monthly_usage_percentage=monthly_quota.usage_percentage if monthly_quota else None,
            is_near_limit=monthly_quota.is_near_limit if monthly_quota else None
        ))
    
    return result


@router.get("/keys/{key_id}", response_model=GeminiAPIKeyResponse)
async def get_gemini_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """**Chi tiết 1 key (Admin only)**"""
    service = GeminiKeyService(db)
    key = service.get_key_by_id(key_id)
    
    if not key:
        raise HTTPException(status_code=404, detail=f"Key ID {key_id} không tồn tại")
    
    monthly_quota = next(
        (q for q in key.quotas if q.quota_type == QuotaType.MONTHLY),
        None
    )
    
    return GeminiAPIKeyResponse(
        id=key.id,
        key_name=key.key_name,
        account_email=key.account_email,
        api_key_masked=service.mask_api_key(service.decrypt_api_key(key.api_key_encrypted)),
        provider=key.provider,
        status=key.status,
        priority=key.priority,
        created_at=key.created_at,
        last_used_at=key.last_used_at,
        notes=key.notes,
        monthly_quota_limit=monthly_quota.quota_limit if monthly_quota else None,
        monthly_quota_used=monthly_quota.quota_used if monthly_quota else None,
        monthly_quota_remaining=monthly_quota.quota_remaining if monthly_quota else None,
        monthly_usage_percentage=monthly_quota.usage_percentage if monthly_quota else None,
        is_near_limit=monthly_quota.is_near_limit if monthly_quota else None
    )


@router.patch("/keys/{key_id}", response_model=GeminiAPIKeyResponse)
async def update_gemini_key(
    key_id: int,
    update_data: GeminiAPIKeyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """**Update key (tên, account_email, status, priority, notes)**"""
    service = GeminiKeyService(db)
    key = service.get_key_by_id(key_id)
    
    if not key:
        raise HTTPException(status_code=404, detail=f"Key ID {key_id} không tồn tại")
    
    # Update fields
    if update_data.key_name:
        key.key_name = update_data.key_name
    if update_data.account_email is not None:
        key.account_email = update_data.account_email
    if update_data.status:
        key.status = KeyStatus(update_data.status.value)
    if update_data.priority:
        key.priority = update_data.priority
    if update_data.notes is not None:
        key.notes = update_data.notes
    
    db.commit()
    db.refresh(key)
    
    monthly_quota = next(
        (q for q in key.quotas if q.quota_type == QuotaType.MONTHLY),
        None
    )
    
    return GeminiAPIKeyResponse(
        id=key.id,
        key_name=key.key_name,
        account_email=key.account_email,
        api_key_masked=service.mask_api_key(service.decrypt_api_key(key.api_key_encrypted)),
        provider=key.provider,
        status=key.status,
        priority=key.priority,
        created_at=key.created_at,
        last_used_at=key.last_used_at,
        notes=key.notes,
        monthly_quota_limit=monthly_quota.quota_limit if monthly_quota else None,
        monthly_quota_used=monthly_quota.quota_used if monthly_quota else None,
        monthly_quota_remaining=monthly_quota.quota_remaining if monthly_quota else None,
        monthly_usage_percentage=monthly_quota.usage_percentage if monthly_quota else None,
        is_near_limit=monthly_quota.is_near_limit if monthly_quota else None
    )


@router.delete("/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gemini_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    **Xóa key (Admin only)**
    
    ⚠️ Cascade delete tất cả quota & usage logs liên quan
    """
    service = GeminiKeyService(db)
    success = service.delete_key(key_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Key ID {key_id} không tồn tại")
    
    return None


# ========== QUOTA & USAGE ==========

@router.get("/keys/{key_id}/quotas", response_model=List[QuotaResponse])
async def get_key_quotas(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """**Xem quotas của 1 key (monthly/daily/per_minute)**"""
    service = GeminiKeyService(db)
    key = service.get_key_by_id(key_id)
    
    if not key:
        raise HTTPException(status_code=404, detail=f"Key ID {key_id} không tồn tại")
    
    result = []
    for quota in key.quotas:
        result.append(QuotaResponse(
            id=quota.id,
            key_id=quota.key_id,
            quota_type=quota.quota_type,
            quota_limit=quota.quota_limit,
            quota_used=quota.quota_used,
            quota_remaining=quota.quota_remaining,
            usage_percentage=quota.usage_percentage,
            is_near_limit=quota.is_near_limit,
            reset_at=quota.reset_at,
            last_updated=quota.last_updated
        ))
    
    return result


@router.get("/usage-logs", response_model=List[UsageLogResponse])
async def get_usage_logs(
    key_id: Optional[int] = None,
    user_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    **Xem usage logs (Admin only)**
    
    - Filter theo key_id hoặc user_id
    - Mặc định trả về 100 records gần nhất
    """
    from app.models.gemini_keys import GeminiKeyUsageLog, GeminiAPIKey
    from app.models.auth_models import User as UserModel
    from sqlalchemy import desc
    
    query = db.query(
        GeminiKeyUsageLog,
        GeminiAPIKey.key_name,
        UserModel.username
    ).outerjoin(
        GeminiAPIKey, GeminiKeyUsageLog.key_id == GeminiAPIKey.id
    ).outerjoin(
        UserModel, GeminiKeyUsageLog.user_id == UserModel.id
    )
    
    if key_id:
        query = query.filter(GeminiKeyUsageLog.key_id == key_id)
    if user_id:
        query = query.filter(GeminiKeyUsageLog.user_id == user_id)
    
    results = query.order_by(desc(GeminiKeyUsageLog.created_at)).limit(limit).all()
    
    return [
        UsageLogResponse(
            id=log.id,
            key_id=log.key_id,
            key_name=key_name,
            user_id=log.user_id,
            username=username,
            model=log.model,
            total_tokens=log.total_tokens,
            cost_usd=float(log.cost_usd),
            request_type=log.request_type,
            status=log.status,
            error_message=log.error_message,
            response_time_ms=log.response_time_ms,
            created_at=log.created_at
        )
        for log, key_name, username in results
    ]


@router.get("/rotation-logs", response_model=List[RotationLogResponse])
async def get_rotation_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """**Xem lịch sử rotation (Admin only)**"""
    from app.models.gemini_keys import GeminiKeyRotationLog, GeminiAPIKey
    from sqlalchemy import desc, alias
    
    FromKey = alias(GeminiAPIKey, name="from_key")
    ToKey = alias(GeminiAPIKey, name="to_key")
    
    results = (
        db.query(
            GeminiKeyRotationLog,
            FromKey.c.key_name.label("from_key_name"),
            ToKey.c.key_name.label("to_key_name")
        )
        .outerjoin(FromKey, GeminiKeyRotationLog.from_key_id == FromKey.c.id)
        .outerjoin(ToKey, GeminiKeyRotationLog.to_key_id == ToKey.c.id)
        .order_by(desc(GeminiKeyRotationLog.rotated_at))
        .limit(limit)
        .all()
    )
    
    return [
        RotationLogResponse(
            id=log.id,
            from_key_id=log.from_key_id,
            from_key_name=from_name,
            to_key_id=log.to_key_id,
            to_key_name=to_name,
            reason=log.reason,
            rotated_at=log.rotated_at,
            rotated_by=log.rotated_by
        )
        for log, from_name, to_name in results
    ]


# ========== DASHBOARD & ANALYTICS ==========

@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    **Dashboard tổng hợp (Admin only)**
    
    - Overview: Tổng số keys, status, quota
    - Trends: Usage 7 ngày gần nhất
    - Top models: Model nào được dùng nhiều nhất
    - Top users: User nào tiêu thụ quota cao nhất
    - Recent rotations: 10 rotations gần nhất
    """
    from app.models.gemini_keys import GeminiAPIKey, GeminiKeyQuota, GeminiKeyUsageLog, GeminiKeyRotationLog
    from app.models.auth_models import User as UserModel
    from sqlalchemy import func, desc, case, alias
    
    # ===== OVERVIEW =====
    total_keys = db.query(func.count(GeminiAPIKey.id)).scalar()
    active_keys = db.query(func.count(GeminiAPIKey.id)).filter(GeminiAPIKey.status == KeyStatus.ACTIVE).scalar()
    inactive_keys = db.query(func.count(GeminiAPIKey.id)).filter(GeminiAPIKey.status == KeyStatus.INACTIVE).scalar()
    quota_exceeded_keys = db.query(func.count(GeminiAPIKey.id)).filter(GeminiAPIKey.status == KeyStatus.QUOTA_EXCEEDED).scalar()
    revoked_keys = db.query(func.count(GeminiAPIKey.id)).filter(GeminiAPIKey.status == KeyStatus.REVOKED).scalar()
    
    total_quota_remaining = db.query(func.sum(GeminiKeyQuota.quota_remaining)).filter(
        GeminiKeyQuota.quota_type == QuotaType.MONTHLY
    ).scalar() or 0
    
    # Keys gần hết quota (> 80%)
    keys_near_limit = (
        db.query(GeminiAPIKey.key_name)
        .join(GeminiKeyQuota)
        .filter(
            GeminiKeyQuota.quota_type == QuotaType.MONTHLY,
            (GeminiKeyQuota.quota_used * 100.0 / GeminiKeyQuota.quota_limit) > 80
        )
        .all()
    )
    
    overview = KeyHealthOverview(
        total_keys=total_keys,
        active_keys=active_keys,
        inactive_keys=inactive_keys,
        quota_exceeded_keys=quota_exceeded_keys,
        revoked_keys=revoked_keys,
        total_quota_remaining=int(total_quota_remaining),
        keys_near_limit=[k[0] for k in keys_near_limit]
    )
    
    # ===== USAGE TRENDS 7D =====
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    trends_data = (
        db.query(
            func.date(GeminiKeyUsageLog.created_at).label("date"),
            func.count(GeminiKeyUsageLog.id).label("total_requests"),
            func.sum(GeminiKeyUsageLog.total_tokens).label("total_tokens"),
            func.sum(GeminiKeyUsageLog.cost_usd).label("total_cost"),
            (func.count(case((GeminiKeyUsageLog.status == UsageStatus.SUCCESS, 1))) * 100.0 / func.count(GeminiKeyUsageLog.id)).label("success_rate")
        )
        .filter(GeminiKeyUsageLog.created_at >= seven_days_ago)
        .group_by(func.date(GeminiKeyUsageLog.created_at))
        .order_by(func.date(GeminiKeyUsageLog.created_at))
        .all()
    )
    
    usage_trends = [
        UsageTrend(
            date=str(row.date),
            total_requests=row.total_requests,
            total_tokens=row.total_tokens or 0,
            total_cost_usd=float(row.total_cost or 0),
            success_rate=round(row.success_rate or 0, 2)
        )
        for row in trends_data
    ]
    
    # ===== TOP MODELS =====
    top_models_data = (
        db.query(
            GeminiKeyUsageLog.model,
            func.count(GeminiKeyUsageLog.id).label("total_requests"),
            func.sum(GeminiKeyUsageLog.total_tokens).label("total_tokens"),
            func.sum(GeminiKeyUsageLog.cost_usd).label("total_cost"),
            func.avg(GeminiKeyUsageLog.response_time_ms).label("avg_response_time")
        )
        .filter(GeminiKeyUsageLog.created_at >= seven_days_ago)
        .group_by(GeminiKeyUsageLog.model)
        .order_by(desc("total_requests"))
        .limit(5)
        .all()
    )
    
    top_models = [
        ModelUsageStats(
            model=row.model,
            total_requests=row.total_requests,
            total_tokens=row.total_tokens or 0,
            total_cost_usd=float(row.total_cost or 0),
            avg_response_time_ms=round(row.avg_response_time, 2) if row.avg_response_time else None
        )
        for row in top_models_data
    ]
    
    # ===== TOP USERS =====
    top_users_data = (
        db.query(
            UserModel.id,
            UserModel.username,
            func.count(GeminiKeyUsageLog.id).label("total_requests"),
            func.sum(GeminiKeyUsageLog.total_tokens).label("total_tokens"),
            func.sum(GeminiKeyUsageLog.cost_usd).label("total_cost")
        )
        .join(UserModel, GeminiKeyUsageLog.user_id == UserModel.id)
        .filter(GeminiKeyUsageLog.created_at >= seven_days_ago)
        .group_by(UserModel.id, UserModel.username)
        .order_by(desc("total_cost"))
        .limit(10)
        .all()
    )
    
    top_users = [
        UserUsageStats(
            user_id=row.id,
            username=row.username,
            total_requests=row.total_requests,
            total_tokens=row.total_tokens or 0,
            total_cost_usd=float(row.total_cost or 0)
        )
        for row in top_users_data
    ]
    
    # ===== RECENT ROTATIONS =====
    FromKey = alias(GeminiAPIKey, name="from_key")
    ToKey = alias(GeminiAPIKey, name="to_key")
    
    recent_rotations_data = (
        db.query(
            GeminiKeyRotationLog,
            FromKey.c.key_name.label("from_key_name"),
            ToKey.c.key_name.label("to_key_name")
        )
        .outerjoin(FromKey, GeminiKeyRotationLog.from_key_id == FromKey.c.id)
        .outerjoin(ToKey, GeminiKeyRotationLog.to_key_id == ToKey.c.id)
        .order_by(desc(GeminiKeyRotationLog.rotated_at))
        .limit(10)
        .all()
    )
    
    recent_rotations = [
        RotationLogResponse(
            id=log.id,
            from_key_id=log.from_key_id,
            from_key_name=from_name,
            to_key_id=log.to_key_id,
            to_key_name=to_name,
            reason=log.reason,
            rotated_at=log.rotated_at,
            rotated_by=log.rotated_by
        )
        for log, from_name, to_name in recent_rotations_data
    ]
    
    return DashboardMetrics(
        overview=overview,
        usage_trends_7d=usage_trends,
        top_models=top_models,
        top_users=top_users,
        recent_rotations=recent_rotations
    )


# ========== MANUAL ACTIONS ==========

@router.post("/keys/{key_id}/rotate")
async def manual_rotate_key(
    key_id: int,
    reason: str = "manual_rotation",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    **Rotate key thủ công (Admin only)**
    
    - Chuyển sang key khác ngay lập tức
    - Log rotation với admin username
    """
    service = GeminiKeyService(db)
    
    next_key = service.rotate_key(
        current_key_id=key_id,
        reason=reason,
        rotated_by=f"admin:{current_user.username}"
    )
    
    if not next_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Không còn key khả dụng để rotate!"
        )
    
    return {
        "message": f"✅ Đã rotate sang key: {next_key.key_name}",
        "new_key_id": next_key.id,
        "new_key_name": next_key.key_name,
        "quota_remaining": next_key.quota_remaining
    }


@router.post("/quotas/reset-monthly")
async def reset_monthly_quotas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    **Reset tất cả monthly quotas (Admin only)**
    
    ⚠️ Chỉ dùng để test hoặc fix lỗi
    Trong production, cronjob sẽ tự động chạy đầu tháng
    """
    service = GeminiKeyService(db)
    reset_count = service.reset_monthly_quotas()
    
    return {
        "message": f"✅ Đã reset {reset_count} monthly quotas",
        "reset_count": reset_count
    }

