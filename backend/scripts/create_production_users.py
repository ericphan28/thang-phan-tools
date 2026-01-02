"""
Script to create production users with subscriptions
Run: python scripts/create_production_users.py
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

def create_production_users():
    """Create production users with real subscriptions"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("CREATING PRODUCTION USERS")
        print("="*70 + "\n")
        
        # Get pricing plans
        plans = db.query(PricingPlan).all()
        plan_dict = {p.name: p for p in plans}
        
        if not plans:
            print("❌ No pricing plans found! Please create pricing plans first.")
            return
        
        # Get "Doanh nghiệp" plan (299k)
        pro_plan = plan_dict.get("Doanh nghiệp")
        if not pro_plan:
            print("❌ 'Doanh nghiệp' plan not found!")
            return
        
        # Production users data
        production_users = [
            {
                "email": "dcthoan@company.com",
                "username": "dcthoan",
                "full_name": "Đinh Công Thoàn",
                "phone": "0909967128",
                "password": "Thoan@2025",  # Strong default password - user should change
                "plan_name": "Doanh nghiệp",
            },
            {
                "email": "pnphuong@company.com",
                "username": "pnphuong",
                "full_name": "Phạm Ngọc Phượng",
                "phone": "0979443226",
                "password": "Phuong@2025",  # Strong default password - user should change
                "plan_name": "Doanh nghiệp",
            },
            {
                "email": "dnptrinh@company.com",
                "username": "dnptrinh",
                "full_name": "Đinh Ngọc Phương Trinh",
                "phone": "0354682712",
                "password": "Trinh@2025",  # Strong default password - user should change
                "plan_name": "Doanh nghiệp",
            },
        ]
        
        created_users = []
        
        for user_data in production_users:
            # Check if user exists
            existing_user = db.query(User).filter(
                (User.email == user_data["email"]) | (User.username == user_data["username"])
            ).first()
            
            if existing_user:
                print(f"⚠️  User already exists: {user_data['username']} ({user_data['email']})")
                print(f"   Skipping...\n")
                created_users.append((existing_user, user_data))
                continue
            
            # Create new user
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                phone=user_data["phone"],
                hashed_password=hash_password(user_data["password"]),
                is_active=True,
                is_superuser=False
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            print(f"✅ Created user: {user.full_name}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Phone: {user_data['phone']}")
            print(f"   Password: {user_data['password']}")
            
            # Create subscription for 299k plan
            plan = plan_dict.get(user_data["plan_name"])
            if not plan:
                print(f"   ⚠️  Plan not found: {user_data['plan_name']}")
                continue
            
            # Active subscription starting today, valid for 30 days
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=30)
            
            subscription = Subscription(
                user_id=user.id,
                plan_type=PlanType.ORGANIZATION,  # Doanh nghiệp
                status=SubscriptionStatus.ACTIVE,
                monthly_price=plan.monthly_price,
                premium_requests_limit=plan.premium_requests_limit,
                premium_requests_used=0,
                current_period_start=start_date,
                current_period_end=end_date,
                cancel_at_period_end=False
            )
            
            db.add(subscription)
            db.commit()
            
            print(f"   📦 Subscription: {plan.name} (299,000đ/month)")
            print(f"   📊 AI Limit: {plan.premium_requests_limit} requests/month")
            print(f"   📅 Valid: {start_date.date()} → {end_date.date()} (30 days)")
            print(f"   💳 Status: ACTIVE\n")
            
            created_users.append((user, user_data))
        
        # Print summary
        print("="*70)
        print("PRODUCTION USERS SUMMARY")
        print("="*70 + "\n")
        
        for user, data in created_users:
            print(f"👤 {user.full_name}")
            print(f"   📧 Email: {user.email}")
            print(f"   🆔 Username: {user.username}")
            print(f"   📱 Phone: {data['phone']}")
            print(f"   🔑 Password: {data['password']}")
            print(f"   💼 Plan: Doanh nghiệp (299,000đ/month)")
            print(f"   📊 AI: 200 requests/month")
            print()
        
        print("="*70)
        print("✅ Production users created successfully!")
        print("⚠️  IMPORTANT: Users should change their password after first login!")
        print(f"🌐 Login at: http://localhost:5173/login")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_production_users()
