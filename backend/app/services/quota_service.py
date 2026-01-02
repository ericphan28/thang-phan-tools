"""
Quota Management Service - Phase 1 Implementation
Kiểm tra và quản lý AI quota cho users
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.auth_models import User
from app.models.subscription import Subscription, SubscriptionStatus, PlanType


class QuotaService:
    """Service để quản lý AI quota"""
    
    # Quota limits theo tier
    QUOTA_LIMITS = {
        "FREE": 3,
        "PRO": 100,
        "TEAM": 500,  # Per user trong team
        "ENTERPRISE": 999999  # Unlimited (số lớn)
    }

    @staticmethod
    def _get_active_subscription(user: User, db: Session) -> Subscription | None:
        """Return the most relevant active/trial subscription for a user (if any)."""
        if not user or not getattr(user, "id", None):
            return None

        now = datetime.utcnow()
        subscription = (
            db.query(Subscription)
            .filter(
                Subscription.user_id == user.id,
                Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]),
            )
            .order_by(Subscription.current_period_end.desc().nullslast(), Subscription.id.desc())
            .first()
        )
        if not subscription:
            return None

        # If a subscription has an end date in the past, treat it as inactive for quota purposes
        # NOTE: NULL current_period_end means "no expiry set" → treat as active
        if subscription.current_period_end is not None and subscription.current_period_end < now:
            return None

        return subscription

    @staticmethod
    def _subscription_to_tier(subscription: Subscription) -> str:
        """Map subscription plan types into the legacy tier labels used by Phase-1 quota."""
        if not subscription:
            return "FREE"

        plan = subscription.plan_type
        if plan == PlanType.FREE:
            return "FREE"

        # Today we treat all paid plans as PRO to avoid blocking paid users.
        # (Organization 299k is a paid plan with premium_requests_limit in the DB.)
        return "PRO"
    
    @staticmethod
    def get_user_quota_info(user: User, db: Session | None = None) -> dict:
        """Lấy thông tin quota của user (ưu tiên subscription nếu có)."""
        if db is not None:
            subscription = QuotaService._get_active_subscription(user, db)
            if subscription and subscription.plan_type != PlanType.FREE:
                limit = int(subscription.premium_requests_limit or 0)
                used = int(subscription.premium_requests_used or 0)
                remaining = max(0, limit - used) if limit > 0 else 0
                return {
                    "subscription_tier": QuotaService._subscription_to_tier(subscription),
                    "quota_monthly": limit,
                    "usage_this_month": used,
                    "remaining": remaining,
                    "reset_date": subscription.current_period_end,
                    "percentage_used": round((used / limit * 100), 1) if limit > 0 else 0,
                }

        quota = int(getattr(user, "ai_quota_monthly", 0) or 0)
        used = int(getattr(user, "ai_usage_this_month", 0) or 0)
        return {
            "subscription_tier": getattr(user, "subscription_tier", "FREE"),
            "quota_monthly": quota,
            "usage_this_month": used,
            "remaining": max(0, quota - used),
            "reset_date": getattr(user, "quota_reset_date", None),
            "percentage_used": round((used / quota * 100), 1) if quota > 0 else 0,
        }
    
    @staticmethod
    def check_and_reset_quota(user: User, db: Session) -> None:
        """Kiểm tra và reset quota nếu đã qua tháng mới"""
        now = datetime.utcnow()

        # Subscription-based quota reset (preferred for paid plans)
        try:
            subscription = QuotaService._get_active_subscription(user, db)
        except Exception:
            subscription = None

        if subscription and subscription.plan_type != PlanType.FREE:
            # If billing period ended, reset usage and roll period forward (simple 30-day window)
            if subscription.current_period_end and subscription.current_period_end <= now:
                subscription.premium_requests_used = 0
                subscription.current_period_start = now
                subscription.current_period_end = now + timedelta(days=30)
                db.commit()

            # Mirror subscription limits/usage onto legacy User fields to keep existing endpoints consistent
            limit = int(subscription.premium_requests_limit or 0)
            user.subscription_tier = QuotaService._subscription_to_tier(subscription)
            if limit > 0:
                user.ai_quota_monthly = limit
                user.ai_usage_this_month = int(subscription.premium_requests_used or 0)
                user.quota_reset_date = subscription.current_period_end
                db.commit()
            return
        
        # Nếu chưa có quota_reset_date, set ngày đầu tiên
        if not user.quota_reset_date:
            user.quota_reset_date = now + timedelta(days=30)
            db.commit()
            return
        
        # Nếu đã qua ngày reset, reset quota
        if user.quota_reset_date <= now:
            user.ai_usage_this_month = 0
            user.quota_reset_date = now + timedelta(days=30)
            db.commit()
    
    @staticmethod
    def check_ai_quota(user: User, db: Session) -> dict:
        """
        Kiểm tra AI quota trước khi gọi AI API
        
        Raises:
            HTTPException: Nếu hết quota
            
        Returns:
            dict: Thông tin quota sau khi check
        """
        # Reset quota nếu cần
        QuotaService.check_and_reset_quota(user, db)

        subscription = None
        try:
            subscription = QuotaService._get_active_subscription(user, db)
        except Exception:
            subscription = None

        # Prefer paid subscription quotas when available
        if subscription and subscription.plan_type != PlanType.FREE:
            limit = int(subscription.premium_requests_limit or 0)
            used = int(subscription.premium_requests_used or 0)

            if limit > 0 and used >= limit:
                quota_info = QuotaService.get_user_quota_info(user, db)
                # Estimate days until reset using billing period end
                reset_date = subscription.current_period_end
                days_until_reset = (reset_date - datetime.utcnow()).days + 1 if reset_date else 30

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error_code": "QUOTA_EXCEEDED",
                        "message": "Bạn đã hết quota AI cho tháng này 😢",
                        "suggestion": f"Vui lòng đợi {days_until_reset} ngày nữa hoặc nâng cấp gói.",
                        "quota_info": quota_info,
                        "upgrade_url": "/pricing",
                        "reset_in_days": days_until_reset,
                    },
                )

            # Increment usage (commit happens after the AI call succeeds)
            subscription.premium_requests_used = used + 1

            # Mirror into legacy User fields so existing UI/headers don't show FREE
            user.subscription_tier = QuotaService._subscription_to_tier(subscription)
            if limit > 0:
                user.ai_quota_monthly = limit
                user.ai_usage_this_month = subscription.premium_requests_used
                user.quota_reset_date = subscription.current_period_end

            return QuotaService.get_user_quota_info(user, db)

        # Legacy user-based quota
        db.refresh(user)
        if user.ai_usage_this_month >= user.ai_quota_monthly:
            quota_info = QuotaService.get_user_quota_info(user)
            days_until_reset = (user.quota_reset_date - datetime.utcnow()).days + 1
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error_code": "QUOTA_EXCEEDED",
                    "message": "Bạn đã hết quota AI cho tháng này 😢",
                    "suggestion": f"Nâng cấp lên PRO để có 100 lần/tháng, hoặc đợi {days_until_reset} ngày nữa",
                    "quota_info": quota_info,
                    "upgrade_url": "/pricing",
                    "reset_in_days": days_until_reset,
                },
            )

        user.ai_usage_this_month += 1
        return QuotaService.get_user_quota_info(user)
    
    @staticmethod
    def rollback_quota_increment(user: User, db: Session) -> None:
        """
        Rollback quota increment nếu AI call thất bại
        Gọi trong exception handler
        """
        subscription = None
        try:
            subscription = QuotaService._get_active_subscription(user, db)
        except Exception:
            subscription = None

        if subscription and subscription.plan_type != PlanType.FREE:
            used = int(subscription.premium_requests_used or 0)
            if used > 0:
                subscription.premium_requests_used = used - 1
            # Mirror back
            limit = int(subscription.premium_requests_limit or 0)
            user.subscription_tier = QuotaService._subscription_to_tier(subscription)
            if limit > 0:
                user.ai_quota_monthly = limit
                user.ai_usage_this_month = int(subscription.premium_requests_used or 0)
                user.quota_reset_date = subscription.current_period_end
            db.commit()
            return

        if user.ai_usage_this_month > 0:
            user.ai_usage_this_month -= 1
            db.commit()
    
    @staticmethod
    def upgrade_subscription(user: User, new_tier: str, db: Session) -> User:
        """
        Nâng cấp subscription tier
        
        Args:
            user: User object
            new_tier: FREE/PRO/TEAM/ENTERPRISE
            db: Database session
            
        Returns:
            Updated user
        """
        if new_tier not in QuotaService.QUOTA_LIMITS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid subscription tier: {new_tier}"
            )
        
        user.subscription_tier = new_tier
        user.ai_quota_monthly = QuotaService.QUOTA_LIMITS[new_tier]
        
        # Reset quota về 0 khi upgrade (tặng full quota mới)
        user.ai_usage_this_month = 0
        user.quota_reset_date = datetime.utcnow() + timedelta(days=30)
        
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def is_quota_warning_level(user: User) -> bool:
        """
        Kiểm tra xem quota đã ở mức cảnh báo chưa (>80%)
        Dùng để hiển thị warning message
        """
        if user.ai_quota_monthly == 0:
            return False
        
        percentage = (user.ai_usage_this_month / user.ai_quota_monthly) * 100
        return percentage >= 80
