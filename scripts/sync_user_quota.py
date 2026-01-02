from __future__ import annotations

import os
import sys

# Ensure backend imports work when running from repo root
sys.path.insert(0, os.path.abspath("backend"))

from app.core.database import SessionLocal
from app.models.auth_models import User
from app.services.quota_service import QuotaService
from app.models.subscription import Subscription, SubscriptionStatus, PlanType


def main() -> None:
    with SessionLocal() as db:
        args = sys.argv[1:]
        if args and args[0] == "--all":
            subs = (
                db.query(Subscription)
                .filter(
                    Subscription.user_id.isnot(None),
                    Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]),
                    Subscription.plan_type != PlanType.FREE,
                )
                .order_by(Subscription.id.asc())
                .all()
            )
            user_ids = sorted({s.user_id for s in subs if s.user_id})
            print(f"Found {len(user_ids)} users with active paid subscriptions")
            for user_id in user_ids:
                u = db.query(User).filter(User.id == user_id).first()
                if not u:
                    continue
                before = (u.subscription_tier, u.ai_quota_monthly, u.ai_usage_this_month)
                QuotaService.check_and_reset_quota(u, db)
                db.refresh(u)
                after = (u.subscription_tier, u.ai_quota_monthly, u.ai_usage_this_month)
                print(f"{u.username}: {before} -> {after}")
            return

        username = args[0] if args else "dcthoan"
        u = db.query(User).filter(User.username == username).first()
        if not u:
            print(f"User {username} not found")
            return

        print("before:", u.subscription_tier, u.ai_quota_monthly, u.ai_usage_this_month, u.quota_reset_date)
        QuotaService.check_and_reset_quota(u, db)
        db.refresh(u)
        print("after :", u.subscription_tier, u.ai_quota_monthly, u.ai_usage_this_month, u.quota_reset_date)
        print("effective:", QuotaService.get_user_quota_info(u, db))


if __name__ == "__main__":
    main()
