"""
Middleware to track premium AI requests usage
"""
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.subscription import Subscription
from app.models.auth_models import User
import logging

logger = logging.getLogger(__name__)

# Premium endpoints that consume premium requests
PREMIUM_ENDPOINTS = {
    '/api/v1/ai-admin/chat',  # Gemini/Claude chat
    '/api/v1/ai-admin/analyze',  # AI analysis
    '/api/v1/adobe-pdf/advanced',  # Adobe advanced features
    '/api/v1/ocr/advanced',  # Advanced OCR
    '/api/v1/text-to-word/ai',  # AI text processing
}

async def track_premium_request(request: Request, user: User):
    """
    Track premium request usage for a user
    Increment premium_requests_used counter
    Check if user has exceeded their limit
    """
    # Check if this endpoint uses premium features
    path = request.url.path
    if path not in PREMIUM_ENDPOINTS:
        return  # Not a premium endpoint, skip tracking
    
    db: Session = SessionLocal()
    try:
        # Get user's subscription
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.status.in_(['active', 'trial'])
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=403,
                detail="Bạn cần đăng ký gói dịch vụ để sử dụng tính năng này"
            )
        
        # Check if user has premium requests available
        limit = subscription.premium_requests_limit or 0
        used = subscription.premium_requests_used or 0
        
        if limit > 0 and used >= limit:
            raise HTTPException(
                status_code=429,
                detail=f"Bạn đã dùng hết {limit} lượt AI tháng này. Vui lòng nâng cấp gói hoặc đợi tháng sau."
            )
        
        # Increment counter
        subscription.premium_requests_used = used + 1
        db.commit()
        
        logger.info(
            f"Premium request tracked: user_id={user.id}, "
            f"used={subscription.premium_requests_used}/{limit}, "
            f"endpoint={path}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking premium request: {e}")
        db.rollback()
    finally:
        db.close()


def is_premium_endpoint(path: str) -> bool:
    """Check if an endpoint requires premium requests"""
    return path in PREMIUM_ENDPOINTS
