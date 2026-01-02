"""
AI Provider Admin API - Manage API keys and track usage
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, Integer
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timedelta
from pydantic import BaseModel
import json

from app.core.database import get_db

# Lazy import to avoid circular dependency
if TYPE_CHECKING:
    from app.models.models import AIProviderKey, AIUsageLog, AIBillingSummary

router = APIRouter(tags=["🔑 AI Admin"])

# Add CORS headers for development
from fastapi.middleware.cors import CORSMiddleware


# ==================== Pydantic Models ====================

class AIProviderKeyCreate(BaseModel):
    provider: str  # gemini, claude, adobe
    key_name: str
    api_key: str
    org_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    monthly_limit: Optional[float] = None
    rate_limit_rpm: Optional[int] = None
    is_primary: bool = False


class AIProviderKeyUpdate(BaseModel):
    key_name: Optional[str] = None
    api_key: Optional[str] = None
    org_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    monthly_limit: Optional[float] = None
    rate_limit_rpm: Optional[int] = None
    is_active: Optional[bool] = None
    is_primary: Optional[bool] = None


class AIProviderKeyResponse(BaseModel):
    id: int
    provider: str
    key_name: str
    api_key_masked: str  # Only show last 4 chars
    org_id: Optional[str]
    is_active: bool
    is_primary: bool
    monthly_limit: Optional[float]
    rate_limit_rpm: Optional[int]
    last_used_at: Optional[datetime]
    last_error: Optional[str]
    error_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UsageStatsResponse(BaseModel):
    provider: str
    period: str
    total_requests: int
    total_tokens: int
    total_cost: float
    avg_response_time_ms: Optional[float]
    error_count: int
    success_rate: float


class BalanceResponse(BaseModel):
    provider: str
    monthly_limit: Optional[float]
    current_spend: float
    remaining: Optional[float]
    usage_percentage: Optional[float]


# ==================== API Key Management ====================

@router.get("/providers")
async def get_supported_providers():
    """Get list of supported AI providers"""
    return {
        "providers": [
            {
                "id": "gemini",
                "name": "Google Gemini",
                "models": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
                "pricing": {
                    "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
                    "gemini-2.5-pro": {"input": 1.25, "output": 5.00}
                },
                "features": ["vision", "text", "multimodal"],
                "supports_vietnamese": True
            },
            {
                "id": "claude",
                "name": "Anthropic Claude",
                "models": ["claude-sonnet-4-20250514", "claude-3-5-sonnet", "claude-3-opus"],
                "pricing": {
                    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
                    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00}
                },
                "features": ["vision", "text", "coding"],
                "supports_vietnamese": True
            },
            {
                "id": "adobe",
                "name": "Adobe PDF Services",
                "models": ["pdf-services-api"],
                "pricing": {"pdf-services-api": {"per_document": 0.05}},
                "features": ["ocr", "pdf_convert", "extract"],
                "supports_vietnamese": False,
                "warning": "Adobe OCR không hỗ trợ tiếng Việt"
            }
        ]
    }


@router.get("/keys", response_model=List[AIProviderKeyResponse])
async def list_api_keys(
    provider: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """List all AI provider API keys"""
    from app.models.models import AIProviderKey
    
    query = db.query(AIProviderKey)
    
    if provider:
        query = query.filter(AIProviderKey.provider == provider)
    if active_only:
        query = query.filter(AIProviderKey.is_active == True)
    
    keys = query.order_by(AIProviderKey.provider, desc(AIProviderKey.is_primary)).all()
    
    # Mask API keys for security
    result = []
    for key in keys:
        result.append(AIProviderKeyResponse(
            id=key.id,
            provider=key.provider,
            key_name=key.key_name,
            api_key_masked=f"****{key.api_key[-4:]}" if len(key.api_key) > 4 else "****",
            org_id=key.org_id,
            is_active=key.is_active,
            is_primary=key.is_primary,
            monthly_limit=key.monthly_limit,
            rate_limit_rpm=key.rate_limit_rpm,
            last_used_at=key.last_used_at,
            last_error=key.last_error,
            error_count=key.error_count,
            created_at=key.created_at
        ))
    
    return result


@router.post("/keys", response_model=AIProviderKeyResponse)
async def create_api_key(
    key_data: AIProviderKeyCreate,
    db: Session = Depends(get_db)
):
    """Create a new AI provider API key"""
    # Validate provider
    valid_providers = ["gemini", "claude", "adobe"]
    if key_data.provider not in valid_providers:
        raise HTTPException(status_code=400, detail=f"Invalid provider. Must be one of: {valid_providers}")
    
    # If this is set as primary, unset other primary keys for this provider
    if key_data.is_primary:
        db.query(AIProviderKey).filter(
            AIProviderKey.provider == key_data.provider,
            AIProviderKey.is_primary == True
        ).update({"is_primary": False})
    
    # Create new key
    new_key = AIProviderKey(
        provider=key_data.provider,
        key_name=key_data.key_name,
        api_key=key_data.api_key,
        org_id=key_data.org_id,
        client_id=key_data.client_id,
        client_secret=key_data.client_secret,
        monthly_limit=key_data.monthly_limit,
        rate_limit_rpm=key_data.rate_limit_rpm,
        is_primary=key_data.is_primary
    )
    
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    
    return AIProviderKeyResponse(
        id=new_key.id,
        provider=new_key.provider,
        key_name=new_key.key_name,
        api_key_masked=f"****{new_key.api_key[-4:]}",
        org_id=new_key.org_id,
        is_active=new_key.is_active,
        is_primary=new_key.is_primary,
        monthly_limit=new_key.monthly_limit,
        rate_limit_rpm=new_key.rate_limit_rpm,
        last_used_at=new_key.last_used_at,
        last_error=new_key.last_error,
        error_count=new_key.error_count,
        created_at=new_key.created_at
    )


@router.put("/keys/{key_id}", response_model=AIProviderKeyResponse)
async def update_api_key(
    key_id: int,
    key_data: AIProviderKeyUpdate,
    db: Session = Depends(get_db)
):
    """Update an AI provider API key"""
    from app.models.models import AIProviderKey
    
    key = db.query(AIProviderKey).filter(AIProviderKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # If setting as primary, unset others
    if key_data.is_primary:
        db.query(AIProviderKey).filter(
            AIProviderKey.provider == key.provider,
            AIProviderKey.is_primary == True,
            AIProviderKey.id != key_id
        ).update({"is_primary": False})
    
    # Update fields
    update_data = key_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(key, field, value)
    
    key.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(key)
    
    return AIProviderKeyResponse(
        id=key.id,
        provider=key.provider,
        key_name=key.key_name,
        api_key_masked=f"****{key.api_key[-4:]}",
        org_id=key.org_id,
        is_active=key.is_active,
        is_primary=key.is_primary,
        monthly_limit=key.monthly_limit,
        rate_limit_rpm=key.rate_limit_rpm,
        last_used_at=key.last_used_at,
        last_error=key.last_error,
        error_count=key.error_count,
        created_at=key.created_at
    )


@router.delete("/keys/{key_id}")
async def delete_api_key(key_id: int, db: Session = Depends(get_db)):
    """Delete an AI provider API key"""
    from app.models.models import AIProviderKey
    
    key = db.query(AIProviderKey).filter(AIProviderKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    db.delete(key)
    db.commit()
    
    return {"message": f"API key '{key.key_name}' deleted successfully"}


@router.post("/keys/{key_id}/test")
async def test_api_key(key_id: int, db: Session = Depends(get_db)):
    """Test if an API key is valid"""
    from app.models.models import AIProviderKey
    
    key = db.query(AIProviderKey).filter(AIProviderKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    result = {"provider": key.provider, "key_name": key.key_name, "status": "unknown"}
    
    try:
        if key.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=key.api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content("Say 'OK' if you can read this.")
            result["status"] = "valid"
            result["response"] = response.text[:50]
            
        elif key.provider == "claude":
            import anthropic
            client = anthropic.Anthropic(api_key=key.api_key)
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                messages=[{"role": "user", "content": "Say OK"}]
            )
            result["status"] = "valid"
            result["response"] = message.content[0].text
            
        elif key.provider == "adobe":
            # Adobe requires more complex validation
            result["status"] = "not_testable"
            result["message"] = "Adobe API requires full document processing to validate"
    
    except Exception as e:
        result["status"] = "invalid"
        result["error"] = str(e)
        
        # Update error count
        key.error_count += 1
        key.last_error = str(e)
        db.commit()
    
    return result


# ==================== Usage Tracking ====================

@router.get("/usage/stats")
async def get_usage_stats(
    provider: Optional[str] = None,
    period: str = "current_month",  # current_month, last_month, last_7_days, all
    db: Session = Depends(get_db)
):
    """Get usage statistics"""
    from app.models.models import AIProviderKey, AIUsageLog
    
    # Determine date range
    now = datetime.utcnow()
    if period == "current_month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "last_month":
        first_of_this_month = now.replace(day=1)
        start_date = (first_of_this_month - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        now = first_of_this_month - timedelta(seconds=1)
    elif period == "last_7_days":
        start_date = now - timedelta(days=7)
    else:
        start_date = datetime(2000, 1, 1)
    
    # Build query
    query = db.query(
        AIUsageLog.model,
        func.count(AIUsageLog.id).label("total_requests"),
        func.sum(AIUsageLog.input_tokens).label("total_input_tokens"),
        func.sum(AIUsageLog.output_tokens).label("total_output_tokens"),
        func.sum(AIUsageLog.total_tokens).label("total_tokens"),
        func.sum(AIUsageLog.total_cost).label("total_cost"),
        func.avg(AIUsageLog.processing_time_ms).label("avg_response_time"),
        func.sum(func.cast(AIUsageLog.status != "success", Integer)).label("error_count")
    ).filter(
        AIUsageLog.created_at >= start_date,
        AIUsageLog.created_at <= now
    )
    
    if provider:
        query = query.join(AIProviderKey).filter(AIProviderKey.provider == provider)
    
    query = query.group_by(AIUsageLog.model)
    
    results = query.all()
    
    stats = []
    for r in results:
        total = r.total_requests or 0
        errors = r.error_count or 0
        stats.append({
            "model": r.model,
            "total_requests": total,
            "total_input_tokens": r.total_input_tokens or 0,
            "total_output_tokens": r.total_output_tokens or 0,
            "total_tokens": r.total_tokens or 0,
            "total_cost_usd": round(r.total_cost or 0, 4),
            "avg_response_time_ms": round(r.avg_response_time or 0, 2),
            "error_count": errors,
            "success_rate": round((total - errors) / total * 100, 2) if total > 0 else 100
        })
    
    # Calculate totals
    total_cost = sum(s["total_cost_usd"] for s in stats)
    total_requests = sum(s["total_requests"] for s in stats)
    total_tokens = sum(s["total_tokens"] for s in stats)
    
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": now.isoformat(),
        "summary": {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "total_cost_vnd": round(total_cost * 25000, 0)  # Approximate VND
        },
        "by_model": stats
    }


@router.get("/usage/balance")
async def get_balance_status(db: Session = Depends(get_db)):
    """Get current balance/spend status for all providers"""
    from app.models.models import AIProviderKey, AIUsageLog
    
    now = datetime.utcnow()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get all active keys with their monthly spend
    keys = db.query(AIProviderKey).filter(AIProviderKey.is_active == True).all()
    
    balances = []
    for key in keys:
        # Calculate current month spend for this key
        monthly_spend = db.query(func.sum(AIUsageLog.total_cost)).filter(
            AIUsageLog.provider_key_id == key.id,
            AIUsageLog.created_at >= start_of_month
        ).scalar() or 0
        
        remaining = None
        usage_pct = None
        if key.monthly_limit:
            remaining = key.monthly_limit - monthly_spend
            usage_pct = (monthly_spend / key.monthly_limit) * 100
        
        balances.append({
            "provider": key.provider,
            "key_name": key.key_name,
            "is_primary": key.is_primary,
            "monthly_limit_usd": key.monthly_limit,
            "current_spend_usd": round(monthly_spend, 4),
            "remaining_usd": round(remaining, 4) if remaining else None,
            "usage_percentage": round(usage_pct, 2) if usage_pct else None,
            "status": "warning" if usage_pct and usage_pct > 80 else "ok",
            "last_used": key.last_used_at.isoformat() if key.last_used_at else None
        })
    
    return {
        "month": now.strftime("%Y-%m"),
        "balances": balances
    }


@router.get("/usage/recent")
async def get_recent_usage(
    limit: int = Query(default=50, le=500),
    provider: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get recent API usage logs"""
    from app.models.models import AIProviderKey, AIUsageLog
    
    query = db.query(AIUsageLog).join(AIProviderKey)
    
    if provider:
        query = query.filter(AIProviderKey.provider == provider)
    
    logs = query.order_by(desc(AIUsageLog.created_at)).limit(limit).all()
    
    return {
        "count": len(logs),
        "logs": [
            {
                "id": log.id,
                "provider": log.provider_key.provider,
                "model": log.model,
                "operation": log.operation,
                "input_tokens": log.input_tokens,
                "output_tokens": log.output_tokens,
                "total_cost_usd": round(log.total_cost, 6),
                "processing_time_ms": log.processing_time_ms,
                "status": log.status,
                "error": log.error_message,
                "request_metadata": log.request_metadata if log.request_metadata else {},
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ]
    }


# ==================== Dashboard Summary ====================

@router.get("/dashboard")
async def get_admin_dashboard(db: Session = Depends(get_db)):
    """Get comprehensive admin dashboard data"""
    from app.models.models import AIProviderKey, AIUsageLog
    
    now = datetime.utcnow()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Active keys count by provider
    keys_by_provider = db.query(
        AIProviderKey.provider,
        func.count(AIProviderKey.id).label("count")
    ).filter(
        AIProviderKey.is_active == True
    ).group_by(AIProviderKey.provider).all()
    
    # Today's usage
    today_usage = db.query(
        func.count(AIUsageLog.id).label("requests"),
        func.sum(AIUsageLog.total_tokens).label("tokens"),
        func.sum(AIUsageLog.total_cost).label("cost")
    ).filter(
        AIUsageLog.created_at >= start_of_today
    ).first()
    
    # This month's usage
    month_usage = db.query(
        func.count(AIUsageLog.id).label("requests"),
        func.sum(AIUsageLog.total_tokens).label("tokens"),
        func.sum(AIUsageLog.total_cost).label("cost")
    ).filter(
        AIUsageLog.created_at >= start_of_month
    ).first()
    
    # Top models by usage
    top_models = db.query(
        AIUsageLog.model,
        func.count(AIUsageLog.id).label("requests"),
        func.sum(AIUsageLog.total_cost).label("cost")
    ).filter(
        AIUsageLog.created_at >= start_of_month
    ).group_by(AIUsageLog.model).order_by(desc("cost")).limit(5).all()
    
    return {
        "timestamp": now.isoformat(),
        "api_keys": {
            "by_provider": {p: c for p, c in keys_by_provider},
            "total_active": sum(c for _, c in keys_by_provider)
        },
        "today": {
            "requests": today_usage.requests or 0,
            "tokens": today_usage.tokens or 0,
            "cost_usd": round(today_usage.cost or 0, 4),
            "cost_vnd": round((today_usage.cost or 0) * 25000, 0)
        },
        "this_month": {
            "requests": month_usage.requests or 0,
            "tokens": month_usage.tokens or 0,
            "cost_usd": round(month_usage.cost or 0, 4),
            "cost_vnd": round((month_usage.cost or 0) * 25000, 0)
        },
        "top_models": [
            {"model": m, "requests": r, "cost_usd": round(c or 0, 4)}
            for m, r, c in top_models
        ]
    }


@router.get("/providers/live-status")
async def get_providers_live_status(db: Session = Depends(get_db)):
    """
    Get real-time balance and limits from AI providers
    
    This fetches actual balance, credits, and rate limits from provider APIs
    (not just our database tracking)
    
    For Gemini: Shows remaining daily quota based on actual usage
    """
    from app.models.models import AIProviderKey
    from app.services.provider_balance_service import ProviderBalanceService
    
    # Get primary API keys
    keys = db.query(AIProviderKey).filter(
        AIProviderKey.is_active == True,
        AIProviderKey.is_primary == True
    ).all()
    
    # Prepare API key config
    api_keys_config = {}
    for key in keys:
        if key.provider == "claude":
            api_keys_config["claude"] = {"api_key": key.api_key}
        elif key.provider == "gemini":
            api_keys_config["gemini"] = {"api_key": key.api_key}
        elif key.provider == "adobe":
            api_keys_config["adobe"] = {
                "client_id": key.client_id or key.api_key,
                "client_secret": key.client_secret
            }
    
    # Fetch live data from providers (pass db session for Gemini quota tracking)
    live_data = await ProviderBalanceService.get_all_balances(api_keys_config, db)
    
    return {
        "success": True,
        "providers": live_data,
        "fetched_at": datetime.utcnow().isoformat(),
        "note": "Real-time data from provider APIs + database usage tracking"
    }
