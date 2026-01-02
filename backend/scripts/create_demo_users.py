"""
Script to create demo users for testing subscription system
Run: python scripts/create_demo_users.py
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.core.database import SessionLocal
from app.models.auth_models import User
from app.models.subscription import Subscription, PricingPlan, SubscriptionStatus, PlanType

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_demo_users():
    """Create demo users for testing"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("CREATING DEMO USERS FOR TESTING")
        print("="*70 + "\n")
        
        # Get pricing plans
        plans = db.query(PricingPlan).all()
        plan_dict = {p.name: p for p in plans}
        
        if not plans:
            print("❌ No pricing plans found! Please create pricing plans first.")
            return
        
        # Demo users data
        demo_users = [
            {
                "email": "admin@demo.com",
                "username": "admin",
                "full_name": "Admin User",
                "is_superuser": True,
                "subscription": None,
                "description": "👑 ADMIN - Full system access"
            },
            {
                "email": "free@demo.com",
                "username": "free_user",
                "full_name": "Free User",
                "is_superuser": False,
                "subscription": None,
                "description": "🆓 FREE - No subscription, limited features"
            },
            {
                "email": "basic@demo.com",
                "username": "basic_user",
                "full_name": "Basic User",
                "is_superuser": False,
                "subscription": {
                    "plan_name": "Cá nhân",
                    "status": SubscriptionStatus.ACTIVE,
                    "premium_requests_used": 0,
                    "days_offset": 5  # Started 5 days ago
                },
                "description": "✨ BASIC - 99k/month, 50 AI requests/month, just started"
            },
            {
                "email": "basic-trial@demo.com",
                "username": "basic_trial",
                "full_name": "Basic Trial User",
                "is_superuser": False,
                "subscription": {
                    "plan_name": "Cá nhân",
                    "status": SubscriptionStatus.TRIAL,
                    "premium_requests_used": 12,
                    "days_offset": 25  # Trial ending soon
                },
                "description": "⏰ TRIAL - 7-day trial almost expired (2 days left)"
            },
            {
                "email": "pro@demo.com",
                "username": "pro_user",
                "full_name": "Pro User",
                "is_superuser": False,
                "subscription": {
                    "plan_name": "Doanh nghiệp",
                    "status": SubscriptionStatus.ACTIVE,
                    "premium_requests_used": 87,
                    "days_offset": 15  # Mid-month
                },
                "description": "🚀 PRO - 299k/month, 200 AI requests/month, 87 used (43%)"
            },
            {
                "email": "pro-full@demo.com",
                "username": "pro_full",
                "full_name": "Pro Full Usage",
                "is_superuser": False,
                "subscription": {
                    "plan_name": "Doanh nghiệp",
                    "status": SubscriptionStatus.ACTIVE,
                    "premium_requests_used": 200,
                    "days_offset": 20  # Almost at limit
                },
                "description": "⚠️ PRO FULL - 200/200 AI requests used, will be blocked"
            },
            {
                "email": "expired@demo.com",
                "username": "expired_user",
                "full_name": "Expired User",
                "is_superuser": False,
                "subscription": {
                    "plan_name": "Cá nhân",
                    "status": SubscriptionStatus.EXPIRED,
                    "premium_requests_used": 45,
                    "days_offset": 35,  # Expired 5 days ago
                    "end_date_offset": -5
                },
                "description": "❌ EXPIRED - Subscription ended 5 days ago"
            },
        ]
        
        created_users = []
        
        for user_data in demo_users:
            # Check if user exists (by email or username)
            existing_user = db.query(User).filter(
                (User.email == user_data["email"]) | (User.username == user_data["username"])
            ).first()
            
            if existing_user:
                print(f"⚠️  User already exists: {user_data['email']}")
                # Update password and info for testing
                existing_user.hashed_password = hash_password("demo123")
                existing_user.full_name = user_data["full_name"]
                existing_user.is_superuser = user_data["is_superuser"]
                db.commit()
                db.refresh(existing_user)
                print(f"   ✅ Updated password to: demo123")
                
                # Check if should update subscription
                if user_data["subscription"]:
                    existing_sub = db.query(Subscription).filter(
                        Subscription.user_id == existing_user.id
                    ).first()
                    
                    if existing_sub:
                        print(f"   📦 Subscription already exists, skipping")
                    else:
                        print(f"   📦 Creating subscription...")
                        sub_data = user_data["subscription"]
                        plan = plan_dict.get(sub_data["plan_name"])
                        
                        if plan:
                            start_date = datetime.utcnow() - timedelta(days=sub_data["days_offset"])
                            
                            if sub_data["status"] == SubscriptionStatus.TRIAL:
                                end_date = start_date + timedelta(days=7)
                            elif "end_date_offset" in sub_data:
                                end_date = datetime.utcnow() + timedelta(days=sub_data["end_date_offset"])
                            else:
                                end_date = start_date + timedelta(days=30)
                            
                            # Map plan type
                            plan_type_map = {
                                "Miễn phí": PlanType.FREE,
                                "Cá nhân": PlanType.INDIVIDUAL,
                                "Doanh nghiệp": PlanType.ORGANIZATION,
                                "Trả theo dùng": PlanType.PAY_AS_YOU_GO
                            }
                            
                            subscription = Subscription(
                                user_id=existing_user.id,
                                plan_type=plan_type_map.get(plan.name, PlanType.INDIVIDUAL),
                                status=sub_data["status"],
                                monthly_price=plan.monthly_price,
                                premium_requests_limit=plan.premium_requests_limit,
                                premium_requests_used=sub_data["premium_requests_used"],
                                current_period_start=start_date,
                                current_period_end=end_date,
                                cancel_at_period_end=False
                            )
                            
                            db.add(subscription)
                            db.commit()
                            print(f"   ✅ Subscription created")
                
                created_users.append((existing_user, user_data["description"]))
                print()
                continue
            
            # Create new user
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                hashed_password=hash_password("demo123"),
                is_active=True,
                is_superuser=user_data["is_superuser"]
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            print(f"✅ Created user: {user.email}")
            print(f"   Password: demo123")
            print(f"   Description: {user_data['description']}")
            
            # Create subscription if specified
            if user_data["subscription"]:
                sub_data = user_data["subscription"]
                plan = plan_dict.get(sub_data["plan_name"])
                
                if not plan:
                    print(f"   ⚠️  Plan not found: {sub_data['plan_name']}")
                    continue
                
                start_date = datetime.utcnow() - timedelta(days=sub_data["days_offset"])
                
                if sub_data["status"] == SubscriptionStatus.TRIAL:
                    end_date = start_date + timedelta(days=7)  # 7-day trial
                elif "end_date_offset" in sub_data:
                    end_date = datetime.utcnow() + timedelta(days=sub_data["end_date_offset"])
                else:
                    end_date = start_date + timedelta(days=30)  # 1 month
                
                # Map plan type
                plan_type_map = {
                    "Miễn phí": PlanType.FREE,
                    "Cá nhân": PlanType.INDIVIDUAL,
                    "Doanh nghiệp": PlanType.ORGANIZATION,
                    "Trả theo dùng": PlanType.PAY_AS_YOU_GO
                }
                
                subscription = Subscription(
                    user_id=user.id,
                    plan_type=plan_type_map.get(plan.name, PlanType.INDIVIDUAL),
                    status=sub_data["status"],
                    monthly_price=plan.monthly_price,
                    premium_requests_limit=plan.premium_requests_limit,
                    premium_requests_used=sub_data["premium_requests_used"],
                    current_period_start=start_date,
                    current_period_end=end_date,
                    cancel_at_period_end=False
                )
                
                db.add(subscription)
                db.commit()
                
                print(f"   📦 Subscription: {plan.name}")
                print(f"   📊 AI Usage: {sub_data['premium_requests_used']}/{plan.premium_requests_limit}")
                print(f"   📅 Period: {start_date.date()} → {end_date.date()}")
            
            created_users.append((user, user_data["description"]))
            print()
        
        # Print summary
        print("="*70)
        print("DEMO USERS SUMMARY")
        print("="*70 + "\n")
        
        for user, description in created_users:
            print(f"📧 Email: {user.email:<25} | Password: demo123")
            print(f"   {description}")
            print()
        
        print("="*70)
        print("✅ Demo users created successfully!")
        print(f"🌐 Frontend: http://localhost:5173")
        print(f"🔐 All passwords: demo123")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_users()
