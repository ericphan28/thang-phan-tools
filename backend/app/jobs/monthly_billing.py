"""
Monthly billing job to reset premium_requests_used counter
Run this on the 1st of every month
"""
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.subscription import Subscription, SubscriptionStatus
import logging

logger = logging.getLogger(__name__)


def reset_premium_requests():
    """
    Reset premium_requests_used to 0 for all active/trial subscriptions
    Run this at the start of each month (e.g., via cron job)
    """
    db: Session = SessionLocal()
    try:
        # Get all active/trial subscriptions
        subscriptions = db.query(Subscription).filter(
            Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
        ).all()
        
        reset_count = 0
        for sub in subscriptions:
            if sub.premium_requests_used and sub.premium_requests_used > 0:
                old_value = sub.premium_requests_used
                sub.premium_requests_used = 0
                reset_count += 1
                logger.info(
                    f"Reset premium requests: subscription_id={sub.id}, "
                    f"user_id={sub.user_id}, old_value={old_value}"
                )
        
        db.commit()
        
        logger.info(
            f"✅ Monthly reset completed: {reset_count} subscriptions reset, "
            f"{len(subscriptions)} total active subscriptions"
        )
        
        return {
            "success": True,
            "total_subscriptions": len(subscriptions),
            "reset_count": reset_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error resetting premium requests: {e}")
        db.rollback()
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
    finally:
        db.close()


if __name__ == "__main__":
    """Run manually for testing"""
    print("=" * 60)
    print("MONTHLY BILLING JOB - Reset Premium Requests")
    print("=" * 60)
    result = reset_premium_requests()
    print(f"\nResult: {result}")
