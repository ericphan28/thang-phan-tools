"""
Delete old keys that cannot be decrypted
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.core.database import engine

print("🗑️  Xóa 3 keys cũ (không decrypt được)...")

with engine.connect() as conn:
    # Delete keys
    result = conn.execute(text("DELETE FROM gemini_api_keys WHERE id IN (1, 2, 3)"))
    conn.commit()
    
    print(f"✅ Đã xóa {result.rowcount} keys")
    print("\n📝 Bây giờ hãy:")
    print("1. Vào http://localhost:5173/admin/gemini-keys")
    print("2. Click 'Add Key'")
    print("3. Nhập lại 3 keys với account_email = ericphan28@gmail.com")
    print("\nKeys mới sẽ được mã hóa với GEMINI_ENCRYPTION_KEY hiện tại!")
