"""
ADMIN SCRIPT - Manage User Subscriptions
Tạo user và assign subscription tier (thay thế payment gateway)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import SessionLocal
from app.models.auth_models import User
from app.services.quota_service import QuotaService
from app.core.security import get_password_hash
from datetime import datetime, timedelta

def create_user_with_subscription(
    email: str,
    username: str,
    password: str,
    full_name: str,
    tier: str = "PRO"
):
    """
    Tạo user mới với subscription tier
    
    Args:
        email: Email của user
        username: Username
        password: Password (will be hashed)
        full_name: Tên đầy đủ
        tier: FREE/PRO/TEAM/ENTERPRISE (default: PRO)
    """
    db = SessionLocal()
    
    try:
        # Check if user exists
        existing = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing:
            print(f"❌ User đã tồn tại: {existing.email}")
            
            # Update subscription instead
            print(f"🔄 Updating subscription to {tier}...")
            upgraded = QuotaService.upgrade_subscription(existing, tier, db)
            print(f"✅ Upgraded {existing.email} to {tier}")
            print(f"   📊 Quota: {upgraded.ai_quota_monthly}/month")
            return existing
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_superuser=False,
            subscription_tier=tier,
            ai_quota_monthly=QuotaService.QUOTA_LIMITS[tier],
            ai_usage_this_month=0,
            quota_reset_date=datetime.utcnow() + timedelta(days=30)
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ Created user: {new_user.email}")
        print(f"   👤 Username: {new_user.username}")
        print(f"   🎟️  Tier: {new_user.subscription_tier}")
        print(f"   📊 Quota: {new_user.ai_quota_monthly}/month")
        print(f"   📅 Reset: {new_user.quota_reset_date.strftime('%Y-%m-%d')}")
        
        return new_user
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def upgrade_existing_user(email: str, new_tier: str):
    """Nâng cấp tier cho user hiện tại"""
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ Không tìm thấy user: {email}")
            return
        
        old_tier = user.subscription_tier
        upgraded = QuotaService.upgrade_subscription(user, new_tier, db)
        
        print(f"✅ Upgraded user: {email}")
        print(f"   📈 {old_tier} → {new_tier}")
        print(f"   📊 Quota: {upgraded.ai_quota_monthly}/month (reset to 0)")
        
        return upgraded
        
    finally:
        db.close()


def list_all_users():
    """Liệt kê tất cả users với subscription"""
    db = SessionLocal()
    
    try:
        users = db.query(User).order_by(User.created_at.desc()).all()
        
        print("\n" + "=" * 100)
        print(f"{'Email':<30} {'Tier':<15} {'Quota':<20} {'Active':<10} {'Created':<20}")
        print("=" * 100)
        
        for user in users:
            quota_str = f"{user.ai_usage_this_month}/{user.ai_quota_monthly}"
            created = user.created_at.strftime('%Y-%m-%d %H:%M')
            active = "✅ Yes" if user.is_active else "❌ No"
            
            print(f"{user.email:<30} {user.subscription_tier:<15} {quota_str:<20} {active:<10} {created:<20}")
        
        print("=" * 100)
        print(f"Total: {len(users)} users")
        
    finally:
        db.close()


def batch_create_government_users():
    """
    Batch create users cho cán bộ nhà nước (VD: Sở KH-ĐT)
    Modify danh sách này theo nhu cầu
    """
    users = [
        {
            "email": "canbo1@sokhdt.gov.vn",
            "username": "canbo_sokhdt_1",
            "password": "ChangeMe123!",
            "full_name": "Nguyễn Văn A - Sở KH-ĐT",
            "tier": "PRO"
        },
        {
            "email": "canbo2@sokhdt.gov.vn",
            "username": "canbo_sokhdt_2",
            "password": "ChangeMe123!",
            "full_name": "Trần Thị B - Sở KH-ĐT",
            "tier": "PRO"
        },
        # Add more users here...
    ]
    
    print(f"🚀 Creating {len(users)} government users...")
    
    for user_data in users:
        try:
            create_user_with_subscription(**user_data)
        except Exception as e:
            print(f"   ⚠️  Failed to create {user_data['email']}: {e}")
    
    print(f"\n✅ Batch creation completed!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("""
╔════════════════════════════════════════════════════════════════╗
║          ADMIN SUBSCRIPTION MANAGEMENT TOOL                    ║
╚════════════════════════════════════════════════════════════════╝

Usage:
  python admin_subscription.py create <email> <username> <password> <full_name> [tier]
  python admin_subscription.py upgrade <email> <tier>
  python admin_subscription.py list
  python admin_subscription.py batch

Examples:
  # Tạo user PRO
  python admin_subscription.py create canbo@sokhdt.gov.vn canbo_sokhdt Pass123! "Nguyễn Văn A" PRO
  
  # Nâng cấp user hiện tại
  python admin_subscription.py upgrade canbo@sokhdt.gov.vn ENTERPRISE
  
  # Liệt kê tất cả users
  python admin_subscription.py list
  
  # Tạo batch users (edit script first)
  python admin_subscription.py batch

Tiers: FREE (3/month), PRO (100/month), TEAM (500/month), ENTERPRISE (unlimited)
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) < 6:
            print("❌ Usage: create <email> <username> <password> <full_name> [tier]")
            sys.exit(1)
        
        email = sys.argv[2]
        username = sys.argv[3]
        password = sys.argv[4]
        full_name = sys.argv[5]
        tier = sys.argv[6] if len(sys.argv) > 6 else "PRO"
        
        create_user_with_subscription(email, username, password, full_name, tier)
    
    elif command == "upgrade":
        if len(sys.argv) < 4:
            print("❌ Usage: upgrade <email> <tier>")
            sys.exit(1)
        
        email = sys.argv[2]
        tier = sys.argv[3]
        upgrade_existing_user(email, tier)
    
    elif command == "list":
        list_all_users()
    
    elif command == "batch":
        batch_create_government_users()
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
