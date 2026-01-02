from __future__ import annotations

from datetime import datetime

from sqlalchemy import text

from app.core.database import SessionLocal
from app.models.auth_models import User


def user_row(u: User) -> dict:
    return {
        "id": u.id,
        "username": u.username,
        "is_superuser": bool(u.is_superuser),
        "subscription_tier": u.subscription_tier,
        "ai_quota_monthly": u.ai_quota_monthly,
        "ai_usage_this_month": u.ai_usage_this_month,
        "quota_reset_date": u.quota_reset_date.isoformat() if u.quota_reset_date else None,
    }


def main() -> None:
    with SessionLocal() as db:
        # Avoid hanging on slow queries / table scans
        try:
            db.execute(text("SET statement_timeout = 5000"))
        except Exception:
            pass

        print("=== USER: dcthoan ===")
        target = db.query(User).filter(User.username == "dcthoan").first()
        print(user_row(target) if target else None)

        print("\n=== USERS (potential quota issues) ===")
        users = (
            db.query(User)
            .order_by(User.ai_quota_monthly.asc(), User.ai_usage_this_month.desc())
            .limit(50)
            .all()
        )
        for u in users:
            # Show rows that are likely misconfigured or already blocked
            if u.ai_quota_monthly <= 3 or u.ai_usage_this_month >= u.ai_quota_monthly:
                print(user_row(u))

        print("\n=== SUBSCRIPTIONS TABLE (if exists) ===")
        try:
            # Fast existence check (no full scan)
            exists = db.execute(text("select to_regclass('public.subscriptions')")).scalar()
            print("subscriptions_table:", exists)
            if not exists:
                return

            if target:
                rows = db.execute(
                    text(
                        """
                        select id, user_id, plan_type, status, monthly_price, created_at
                        from subscriptions
                        where user_id = :user_id
                        order by id desc
                        limit 20
                        """
                    ),
                    {"user_id": target.id},
                ).fetchall()
                print("subscriptions(for dcthoan, last 20):")
                for r in rows:
                    print(dict(r._mapping))

            rows_299 = db.execute(
                text(
                    """
                    select id, user_id, plan_type, status, monthly_price, created_at
                    from subscriptions
                    where monthly_price in (299000, 299000.0)
                    order by id desc
                    limit 20
                    """
                )
            ).fetchall()
            print("subscriptions(299k candidates, last 20):")
            for r in rows_299:
                print(dict(r._mapping))
        except Exception as e:
            print("subscriptions table check failed:", type(e).__name__, str(e)[:250])


if __name__ == "__main__":
    main()
