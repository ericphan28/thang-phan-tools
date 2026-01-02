"""
Initialize Pricing Plans
Run this script once to setup default pricing plans in the database
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, engine, Base
from app.models.subscription import PricingPlan, PlanType
# Import all models to ensure they're registered with Base.metadata
from app.models import auth_models, models, subscription
import json

def init_pricing_plans():
    """Initialize default pricing plans"""
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")
    
    db = SessionLocal()
    
    try:
        # Check if plans already exist
        existing = db.query(PricingPlan).count()
        if existing > 0:
            print(f"⚠ Found {existing} existing pricing plans. Skipping initialization.")
            return
        
        plans_data = [
            {
                "plan_type": PlanType.FREE,
                "name": "Miễn phí",
                "description": "Dùng thử miễn phí - Đủ cho nhu cầu cơ bản",
                "monthly_price": 0.0,
                "premium_requests_limit": 0,
                "monthly_spending_limit": None,
                "trial_days": 0,
                "features": json.dumps({
                    "features": [
                        "✅ Chuyển đổi file Word, Excel, PDF không giới hạn",
                        "✅ Đọc chữ từ ảnh (OCR) không giới hạn",
                        "✅ Xử lý file cơ bản miễn phí",
                        "❌ Chưa có AI phân tích nâng cao"
                    ]
                })
            },
            {
                "plan_type": PlanType.INDIVIDUAL,
                "name": "Cá nhân",
                "description": "Dành cho freelancer và cá nhân - Đủ dùng cho hầu hết mọi người",
                "monthly_price": 99000.0,
                "annual_price": 990000.0,
                "premium_requests_limit": 300,
                "monthly_spending_limit": 50000.0,
                "trial_days": 7,
                "features": json.dumps({
                    "features": [
                        "✅ Mọi tính năng cơ bản không giới hạn",
                        "🤖 300 lượt dùng AI thông minh mỗi tháng",
                        "📝 Phân tích văn bản bằng AI",
                        "📄 Xử lý PDF nâng cao",
                        "🇻🇳 Đọc chữ Việt từ ảnh chuẩn xác",
                        "💰 Tặng thêm 50,000đ dùng AI",
                        "⚡ Hỗ trợ ưu tiên",
                        "🎁 Dùng thử 7 ngày miễn phí"
                    ]
                })
            },
            {
                "plan_type": PlanType.ORGANIZATION,
                "name": "Doanh nghiệp",
                "description": "Dành cho team và công ty - Nhiều tính năng hơn cho nhóm",
                "monthly_price": 299000.0,
                "annual_price": 2990000.0,
                "premium_requests_limit": 1000,
                "monthly_spending_limit": 200000.0,
                "trial_days": 14,
                "features": json.dumps({
                    "features": [
                        "✅ Mọi tính năng cơ bản không giới hạn",
                        "🚀 1,000 lượt AI mỗi tháng (cho mỗi người)",
                        "🤖 Dùng đầy đủ các AI thông minh nhất",
                        "💰 Tặng thêm 200,000đ dùng AI/người",
                        "👥 Quản lý thành viên trong team",
                        "📊 Xem báo cáo sử dụng chi tiết",
                        "💳 Thanh toán tập trung, dễ quản lý",
                        "🎯 Hỗ trợ ưu tiên 24/7",
                        "🧾 Xuất hóa đơn đỏ VAT",
                        "🎁 Dùng thử 14 ngày miễn phí"
                    ]
                })
            },
            {
                "plan_type": PlanType.PAY_AS_YOU_GO,
                "name": "Trả theo dùng",
                "description": "Dùng ít thì trả ít - Linh hoạt, không ràng buộc",
                "monthly_price": 0.0,
                "premium_requests_limit": 0,
                "monthly_spending_limit": None,
                "trial_days": 7,
                "features": json.dumps({
                    "features": [
                        "✅ Tính năng cơ bản miễn phí mãi mãi",
                        "💰 Chỉ trả tiền khi dùng AI nâng cao",
                        "📦 Mua gói AI khi cần: 100 lượt = 39k, 300 lượt = 99k",
                        "🎯 Phù hợp người dùng thỉnh thoảng",
                        "🚫 Không phí cố định hàng tháng",
                        "🎁 Dùng thử 7 ngày miễn phí"
                    ]
                })
            }
        ]
        
        # Create pricing plans
        for plan_data in plans_data:
            plan = PricingPlan(**plan_data)
            db.add(plan)
            price_display = "MIỄN PHÍ" if plan_data['monthly_price'] == 0 else f"{int(plan_data['monthly_price']):,}đ/tháng"
            print(f"✓ Tạo gói: {plan_data['name']} ({price_display})")
        
        db.commit()
        print(f"\n✅ Successfully initialized {len(plans_data)} pricing plans!")
        
        # Display summary
        print("\n" + "="*60)
        print("📊 BẢNG GIÁ DỊCH VỤ - GITHUB COPILOT MODEL")
        print("="*60)
        plans = db.query(PricingPlan).all()
        for plan in plans:
            if plan.monthly_price == 0:
                print(f"\n📦 {plan.name} - MIỄN PHÍ")
            else:
                print(f"\n📦 {plan.name} - {int(plan.monthly_price):,}đ/tháng")
            print(f"   Loại: {plan.plan_type.value}")
            print(f"   Trial: {plan.trial_days} ngày")
            print(f"   Basic features: UNLIMITED (Word/Excel/PDF, OCR)")
            if plan.premium_requests_limit:
                print(f"   Premium AI requests: {plan.premium_requests_limit:,} requests/tháng")
            else:
                print(f"   Premium AI requests: 0 (cần mua thêm)")
            if plan.monthly_spending_limit:
                print(f"   AI Credits tặng kèm: {int(plan.monthly_spending_limit):,}đ")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("INITIALIZING PRICING PLANS")
    print("="*60)
    init_pricing_plans()
