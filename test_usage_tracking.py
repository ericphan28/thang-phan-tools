"""
Test AI Usage Tracking
"""
from sqlalchemy import desc
from backend.app.core.database import SessionLocal
from backend.app.models.models import AIUsageLog

db = SessionLocal()

try:
    # Get recent AI usage logs
    logs = db.query(AIUsageLog).order_by(desc(AIUsageLog.created_at)).limit(5).all()
    
    print("📊 Recent AI Usage Logs (Last 5):")
    print("=" * 80)
    
    for log in logs:
        print(f"\n🤖 {log.operation}")
        print(f"   Provider: {log.model}")
        print(f"   Tokens: {log.input_tokens} → {log.output_tokens} (total: {log.total_tokens})")
        print(f"   Cost: ${log.total_cost:.6f}")
        print(f"   Status: {log.status}")
        print(f"   Time: {log.created_at}")
        
finally:
    db.close()
