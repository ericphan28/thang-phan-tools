"""
TEST SCRIPT - Phase 1: Quota System
Verify quota implementation works correctly
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import SessionLocal
from app.models.auth_models import User
from app.services.quota_service import QuotaService
from app.core.security import get_password_hash
from datetime import datetime, timedelta

def test_quota_system():
    """Test quota system với user thực tế"""
    db = SessionLocal()
    
    print("=" * 80)
    print("🧪 TESTING PHASE 1: QUOTA SYSTEM")
    print("=" * 80)
    
    try:
        # Test 1: Tạo FREE user mới
        print("\n📝 Test 1: Tạo FREE user với 3 quota")
        test_user = db.query(User).filter(User.email == "test_quota@test.com").first()
        
        if test_user:
            print(f"   ℹ️  User đã tồn tại: {test_user.email}")
            db.delete(test_user)
            db.commit()
            print("   🗑️  Đã xóa user cũ")
        
        # Tạo user mới
        new_user = User(
            username="test_quota",
            email="test_quota@test.com",
            hashed_password=get_password_hash("test123"),
            full_name="Test Quota User",
            is_active=True,
            subscription_tier="FREE",
            ai_quota_monthly=3,
            ai_usage_this_month=0,
            quota_reset_date=datetime.utcnow() + timedelta(days=30)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"   ✅ Created user: {new_user.email}")
        print(f"   📊 Tier: {new_user.subscription_tier}")
        print(f"   📊 Quota: {new_user.ai_usage_this_month}/{new_user.ai_quota_monthly}")
        
        # Test 2: Check quota info
        print("\n📝 Test 2: Get quota info")
        quota_info = QuotaService.get_user_quota_info(new_user)
        print(f"   ✅ Quota info: {quota_info}")
        assert quota_info['remaining'] == 3, "Initial quota should be 3"
        
        # Test 3: Use quota 3 lần (OK)
        print("\n📝 Test 3: Dùng quota 3 lần (should succeed)")
        for i in range(3):
            quota_check = QuotaService.check_ai_quota(new_user, db)
            db.commit()
            print(f"   ✅ Request {i+1}/3: Used={new_user.ai_usage_this_month}, Remaining={quota_check['remaining']}")
        
        assert new_user.ai_usage_this_month == 3, "Should have used 3 quota"
        
        # Test 4: Dùng lần thứ 4 (should fail với 403)
        print("\n📝 Test 4: Dùng lần thứ 4 (should raise HTTPException)")
        try:
            QuotaService.check_ai_quota(new_user, db)
            print("   ❌ FAILED: Should have raised HTTPException")
        except Exception as e:
            if "403" in str(e) or "QUOTA_EXCEEDED" in str(e):
                print(f"   ✅ PASSED: Raised HTTPException as expected")
                print(f"   📄 Error: {e}")
            else:
                print(f"   ❌ FAILED: Wrong exception: {e}")
        
        # Test 5: Upgrade to PRO
        print("\n📝 Test 5: Upgrade to PRO (100 quota)")
        upgraded_user = QuotaService.upgrade_subscription(new_user, "PRO", db)
        print(f"   ✅ Upgraded to: {upgraded_user.subscription_tier}")
        print(f"   📊 New quota: {upgraded_user.ai_usage_this_month}/{upgraded_user.ai_quota_monthly}")
        assert upgraded_user.ai_quota_monthly == 100, "PRO should have 100 quota"
        assert upgraded_user.ai_usage_this_month == 0, "Usage should reset after upgrade"
        
        # Test 6: Use quota as PRO (should work)
        print("\n📝 Test 6: Dùng quota với PRO tier")
        quota_check = QuotaService.check_ai_quota(upgraded_user, db)
        db.commit()
        print(f"   ✅ Request OK: Used={upgraded_user.ai_usage_this_month}, Remaining={quota_check['remaining']}")
        
        # Test 7: Warning level
        print("\n📝 Test 7: Test warning level (>80%)")
        upgraded_user.ai_usage_this_month = 85  # 85/100 = 85%
        db.commit()
        is_warning = QuotaService.is_quota_warning_level(upgraded_user)
        print(f"   ✅ Usage: 85/100 (85%) → Warning: {is_warning}")
        assert is_warning == True, "Should show warning at 85%"
        
        # Test 8: Reset quota
        print("\n📝 Test 8: Test auto reset quota")
        upgraded_user.quota_reset_date = datetime.utcnow() - timedelta(days=1)  # Past date
        upgraded_user.ai_usage_this_month = 50
        db.commit()
        print(f"   📅 Old reset date: {upgraded_user.quota_reset_date}")
        print(f"   📊 Old usage: {upgraded_user.ai_usage_this_month}")
        
        QuotaService.check_and_reset_quota(upgraded_user, db)
        db.refresh(upgraded_user)
        
        print(f"   📅 New reset date: {upgraded_user.quota_reset_date}")
        print(f"   📊 New usage: {upgraded_user.ai_usage_this_month}")
        assert upgraded_user.ai_usage_this_month == 0, "Usage should reset to 0"
        
        # Cleanup
        print("\n🧹 Cleanup: Xóa test user")
        db.delete(upgraded_user)
        db.commit()
        print("   ✅ Cleaned up")
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_quota_system()
