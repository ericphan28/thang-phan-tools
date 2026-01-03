"""
Adobe PDF Services Usage Tracking API
Endpoint để track & check Adobe API usage
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.models import APILog
from app.api.dependencies import get_current_user
from app.models.auth_models import User

router = APIRouter(tags=["Adobe Usage"])


class AdobeUsageResponse(BaseModel):
    """Adobe usage statistics response"""
    total_transactions: int
    transactions_this_month: int
    monthly_limit: int
    remaining: int
    percentage_used: float
    reset_date: str
    breakdown_by_operation: dict
    recent_transactions: list


@router.get("/adobe/usage", response_model=AdobeUsageResponse)
async def get_adobe_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📊 Kiểm tra Adobe PDF Services usage
    
    **Trả về:**
    - Total transactions (all time)
    - Transactions this month
    - Monthly limit (500 free tier)
    - Remaining quota
    - Breakdown by operation (OCR, Extract, etc.)
    - Recent 10 transactions
    
    **NOTE:** Adobe không có API check usage chính thức.
    Đây là local tracking dựa vào API logs của hệ thống.
    """
    
    # Get first day of current month
    now = datetime.utcnow()
    first_day_of_month = datetime(now.year, now.month, 1)
    
    # Query Adobe API calls (filter by endpoint pattern)
    adobe_endpoints = [
        '/documents/pdf/ocr',
        '/documents/pdf/extract',
        '/documents/pdf/split',
        '/documents/pdf/compress',
        '/documents/pdf/watermark',
        '/documents/pdf/protect',
        '/documents/pdf/unlock',
        '/documents/convert/pdf-to-word',
        '/documents/html-to-pdf'
    ]
    
    # Total transactions (all time)
    total_query = db.query(func.count(APILog.id)).filter(
        APILog.endpoint.in_(adobe_endpoints),
        APILog.status_code == 200  # Only successful calls count
    )
    total_transactions = total_query.scalar() or 0
    
    # Transactions this month
    monthly_query = db.query(func.count(APILog.id)).filter(
        APILog.endpoint.in_(adobe_endpoints),
        APILog.status_code == 200,
        APILog.created_at >= first_day_of_month
    )
    transactions_this_month = monthly_query.scalar() or 0
    
    # Monthly limit
    monthly_limit = 500  # Adobe free tier
    remaining = max(0, monthly_limit - transactions_this_month)
    percentage_used = (transactions_this_month / monthly_limit * 100) if monthly_limit > 0 else 0
    
    # Reset date (first day of next month)
    if now.month == 12:
        reset_date = datetime(now.year + 1, 1, 1)
    else:
        reset_date = datetime(now.year, now.month + 1, 1)
    
    # Breakdown by operation
    breakdown_query = db.query(
        APILog.endpoint,
        func.count(APILog.id).label('count')
    ).filter(
        APILog.endpoint.in_(adobe_endpoints),
        APILog.status_code == 200,
        APILog.created_at >= first_day_of_month
    ).group_by(APILog.endpoint)
    
    breakdown = {}
    for row in breakdown_query.all():
        # Extract operation name from endpoint
        op_name = row.endpoint.split('/')[-1]  # e.g., 'ocr', 'extract'
        breakdown[op_name] = row.count
    
    # Recent transactions (last 10)
    recent_query = db.query(APILog).filter(
        APILog.endpoint.in_(adobe_endpoints),
        APILog.status_code == 200
    ).order_by(desc(APILog.created_at)).limit(10)
    
    recent_transactions = []
    for log in recent_query.all():
        recent_transactions.append({
            "timestamp": log.created_at.isoformat(),
            "endpoint": log.endpoint,
            "operation": log.endpoint.split('/')[-1],
            "duration_ms": log.duration_ms,
            "user": log.user_email or "unknown"
        })
    
    return {
        "total_transactions": total_transactions,
        "transactions_this_month": transactions_this_month,
        "monthly_limit": monthly_limit,
        "remaining": remaining,
        "percentage_used": round(percentage_used, 2),
        "reset_date": reset_date.isoformat(),
        "breakdown_by_operation": breakdown,
        "recent_transactions": recent_transactions
    }


@router.get("/adobe/quota-status")
async def get_adobe_quota_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🚨 Quick check Adobe quota status (dùng cho alerts)
    
    **Trả về:**
    - status: "ok" | "warning" | "critical" | "exhausted"
    - used: số transactions đã dùng tháng này
    - limit: 500
    - message: thông báo
    """
    
    now = datetime.utcnow()
    first_day_of_month = datetime(now.year, now.month, 1)
    
    adobe_endpoints = [
        '/documents/pdf/ocr',
        '/documents/pdf/extract',
        '/documents/pdf/split',
        '/documents/pdf/compress',
        '/documents/pdf/watermark',
        '/documents/pdf/protect',
        '/documents/pdf/unlock',
        '/documents/convert/pdf-to-word',
        '/documents/html-to-pdf'
    ]
    
    monthly_query = db.query(func.count(APILog.id)).filter(
        APILog.endpoint.in_(adobe_endpoints),
        APILog.status_code == 200,
        APILog.created_at >= first_day_of_month
    )
    used = monthly_query.scalar() or 0
    limit = 500
    
    # Determine status
    if used >= limit:
        status = "exhausted"
        message = "❌ Đã hết quota Adobe! Vui lòng chờ đầu tháng sau hoặc nâng cấp."
    elif used >= limit * 0.9:  # 90%
        status = "critical"
        message = f"🚨 Sắp hết quota Adobe! Còn {limit - used} transactions."
    elif used >= limit * 0.7:  # 70%
        status = "warning"
        message = f"⚠️ Quota Adobe đang cao. Còn {limit - used} transactions."
    else:
        status = "ok"
        message = f"✅ Quota Adobe bình thường. Đã dùng {used}/{limit}."
    
    return {
        "status": status,
        "used": used,
        "limit": limit,
        "remaining": max(0, limit - used),
        "percentage": round(used / limit * 100, 2) if limit > 0 else 0,
        "message": message
    }


@router.post("/adobe/log-transaction")
async def log_adobe_transaction(
    operation: str,
    endpoint: str,
    duration_ms: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📝 Log a manual Adobe transaction (for operations not tracked by middleware)
    
    **Use case:** Nếu có operation mới chưa có trong APILog middleware
    """
    
    log_entry = APILog(
        endpoint=endpoint,
        method="POST",
        status_code=200,
        duration_ms=duration_ms or 0,
        user_id=current_user.id
    )
    
    db.add(log_entry)
    db.commit()
    
    return {"message": "Transaction logged successfully", "operation": operation}
