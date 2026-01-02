"""
AI Usage Service - Track API usage and manage provider keys
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING
import json

# Lazy import to avoid circular dependency
if TYPE_CHECKING:
    from app.models.models import AIProviderKey, AIUsageLog

from app.core.database import SessionLocal

# Pricing per 1M tokens (USD) - Updated December 26, 2025
# Source: https://ai.google.dev/pricing
PRICING = {
    # Gemini 3 Series
    "gemini-3-pro-preview": {"input": 2.00, "output": 12.00},  # includes thinking tokens
    "gemini-3-flash-preview": {"input": 0.50, "output": 3.00},
    
    # Gemini 2.5 Series
    "gemini-2.5-flash": {"input": 0.30, "output": 2.50},
    "gemini-2.5-flash-preview-09-2025": {"input": 0.30, "output": 2.50},
    "gemini-2.5-flash-lite": {"input": 0.10, "output": 0.40},
    "gemini-2.5-flash-lite-preview-09-2025": {"input": 0.10, "output": 0.40},
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
    
    # Gemini 2.0 Series
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    "gemini-2.0-flash-exp": {"input": 0.075, "output": 0.30},
    "gemini-2.0-flash-lite": {"input": 0.075, "output": 0.30},
    
    # Claude Models
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
}

# Free tier configurations
FREE_TIER_LIMITS = {
    "gemini": {
        "requests_per_minute": 15,
        "requests_per_day": 1500,
        "tokens_per_minute": 1_000_000,
        "is_free": True  # Mark as free tier
    }
}


def get_primary_key(provider: str, db: Session = None):
    """Get primary API key for a provider"""
    from app.models.models import AIProviderKey
    
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    
    try:
        # First try to get primary key
        key = db.query(AIProviderKey).filter(
            AIProviderKey.provider == provider,
            AIProviderKey.is_active == True,
            AIProviderKey.is_primary == True
        ).first()
        
        # If no primary, get any active key
        if not key:
            key = db.query(AIProviderKey).filter(
                AIProviderKey.provider == provider,
                AIProviderKey.is_active == True
            ).first()
        
        return key
    finally:
        if close_db:
            db.close()


def get_api_key(provider: str, db: Session = None) -> Optional[str]:
    """Get API key string for a provider"""
    key = get_primary_key(provider, db)
    return key.api_key if key else None


def calculate_cost(model: str, input_tokens: int, output_tokens: int, provider: str = None) -> Dict[str, float]:
    """
    Calculate cost based on token usage
    
    Args:
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        provider: Provider name (gemini, claude, etc.) - used to check free tier
    
    Returns:
        Dict with input_cost, output_cost, total_cost
    """
    # Check if this is a free tier provider
    if provider and provider in FREE_TIER_LIMITS and FREE_TIER_LIMITS[provider].get("is_free"):
        return {
            "input_cost": 0.0,
            "output_cost": 0.0,
            "total_cost": 0.0
        }
    
    pricing = PRICING.get(model, {"input": 0.0, "output": 0.0})
    
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost
    
    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost
    }


def log_usage(
    db: Session,
    provider: str,
    model: str,
    endpoint: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    processing_time: float = None,
    status: str = "success",
    error_message: str = None,
    request_id: str = None,
    user_id: int = None,
    request_metadata: Dict[str, Any] = None
):
    """Log AI API usage"""
    from app.models.models import AIProviderKey, AIUsageLog
    
    try:
        # Get provider key
        key = get_primary_key(provider, db)
        if not key:
            return None
        
        # Calculate costs (pass provider to check free tier)
        costs = calculate_cost(model, input_tokens, output_tokens, provider)
        
        # Create log entry
        log = AIUsageLog(
            provider_key_id=key.id,
            user_id=user_id,
            operation=endpoint,
            model=model,
            request_id=request_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            input_cost=costs["input_cost"],
            output_cost=costs["output_cost"],
            total_cost=costs["total_cost"],
            processing_time_ms=processing_time * 1000 if processing_time else None,
            status=status,
            error_message=error_message,
            request_metadata=json.dumps(request_metadata) if request_metadata else None
        )
        
        db.add(log)
        
        # Update key's last_used_at
        key.last_used_at = datetime.utcnow()
        if status == "error":
            key.error_count += 1
            key.last_error = error_message
        
        db.commit()
        db.refresh(log)
        
        return log
    
    except Exception as e:
        db.rollback()
        print(f"Error logging AI usage: {e}")
        return None


def get_current_month_spend(provider: str, db: Session = None) -> float:
    """Get current month's total spend for a provider"""
    from app.models.models import AIProviderKey, AIUsageLog
    
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    
    try:
        from sqlalchemy import func
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        key = get_primary_key(provider, db)
        if not key:
            return 0.0
        
        total = db.query(func.sum(AIUsageLog.total_cost)).filter(
            AIUsageLog.provider_key_id == key.id,
            AIUsageLog.created_at >= start_of_month
        ).scalar()
        
        return total or 0.0
    
    finally:
        if close_db:
            db.close()


def check_budget_limit(provider: str, db: Session = None) -> Dict[str, Any]:
    """Check if provider is within budget"""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    
    try:
        key = get_primary_key(provider, db)
        if not key:
            return {"ok": False, "reason": "No API key configured"}
        
        if not key.monthly_limit:
            return {"ok": True, "unlimited": True}
        
        current_spend = get_current_month_spend(provider, db)
        remaining = key.monthly_limit - current_spend
        
        return {
            "ok": remaining > 0,
            "monthly_limit": key.monthly_limit,
            "current_spend": current_spend,
            "remaining": remaining,
            "usage_percent": (current_spend / key.monthly_limit) * 100
        }
    
    finally:
        if close_db:
            db.close()
