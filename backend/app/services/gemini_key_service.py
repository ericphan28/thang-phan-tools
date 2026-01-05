"""
Gemini API Keys Service
Core logic: Key selection, rotation, quota tracking, encryption
"""
import os
import logging
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from cryptography.fernet import Fernet
import base64

from app.models.gemini_keys import (
    GeminiAPIKey, 
    GeminiKeyQuota, 
    GeminiKeyUsageLog,
    GeminiKeyRotationLog,
    KeyStatus,
    QuotaType,
    UsageStatus
)
from app.schemas.gemini_keys import (
    GeminiAPIKeyCreate,
    UsageLogCreate,
    SelectedKeyInfo
)

logger = logging.getLogger(__name__)


class GeminiKeyService:
    """
    Service quản lý Gemini API keys
    - Encryption/Decryption keys
    - Select best available key
    - Auto-rotation khi hết quota
    - Track usage & update quotas
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.encryption_key = self._get_encryption_key()
        self.cipher = Fernet(self.encryption_key)
    
    def _get_encryption_key(self) -> bytes:
        """
        Lấy encryption key từ ENV
        CRITICAL: Phải set GEMINI_ENCRYPTION_KEY trong .env
        Generate key: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
        """
        key_str = os.getenv("GEMINI_ENCRYPTION_KEY")
        if not key_str:
            logger.warning("GEMINI_ENCRYPTION_KEY not set! Using default (INSECURE for dev only)")
            # Default key CHỈ dùng dev - KHÔNG dùng production
            key_str = "3FJX8qQXYZ0-_N8vF5x8dGKZ9pW_T2xC8qN9vF5x8dE="
        
        return key_str.encode()
    
    # ========== ENCRYPTION ==========
    
    def encrypt_api_key(self, plaintext_key: str) -> str:
        """Mã hóa API key trước khi lưu DB"""
        try:
            encrypted = self.cipher.encrypt(plaintext_key.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Failed to encrypt API key: {e}")
            raise ValueError("Không thể mã hóa API key")
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Giải mã API key khi cần dùng"""
        try:
            decrypted = self.cipher.decrypt(encrypted_key.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt API key: {e}")
            raise ValueError("Không thể giải mã API key")
    
    def mask_api_key(self, plaintext_key: str) -> str:
        """
        Mask API key để hiển thị (chỉ show 4 ký tự đầu/cuối)
        VD: AIzaSyABC...XYZ → AIza***************XYZ
        """
        if len(plaintext_key) <= 8:
            return "****"
        return f"{plaintext_key[:4]}{'*' * (len(plaintext_key) - 8)}{plaintext_key[-4:]}"
    
    # ========== KEY MANAGEMENT ==========
    
    def create_key(
        self, 
        key_data: GeminiAPIKeyCreate, 
        created_by_user_id: Optional[int] = None
    ) -> GeminiAPIKey:
        """
        Tạo key mới
        1. Validate key (test call API)
        2. Encrypt key
        3. Insert to DB
        4. Initialize quota
        """
        # TODO: Validate key bằng cách test call Gemini API
        # from google import generativeai as genai
        # genai.configure(api_key=key_data.api_key)
        # try:
        #     model = genai.GenerativeModel('gemini-2.5-flash')
        #     model.generate_content("test")
        # except Exception as e:
        #     raise ValueError(f"API key không hợp lệ: {e}")
        
        # Encrypt key
        encrypted_key = self.encrypt_api_key(key_data.api_key)
        
        # Create key record
        db_key = GeminiAPIKey(
            key_name=key_data.key_name,
            api_key_encrypted=encrypted_key,
            provider="gemini",
            status=KeyStatus.ACTIVE,
            priority=key_data.priority,
            notes=key_data.notes,
            created_by=created_by_user_id
        )
        self.db.add(db_key)
        self.db.flush()  # Để lấy db_key.id
        
        # Initialize monthly quota
        monthly_quota = GeminiKeyQuota(
            key_id=db_key.id,
            quota_type=QuotaType.MONTHLY,
            quota_limit=key_data.monthly_quota_limit,
            quota_used=0,
            quota_remaining=key_data.monthly_quota_limit,
            reset_at=self._get_next_month_start()
        )
        self.db.add(monthly_quota)
        
        # Initialize daily quota (10% of monthly)
        daily_quota = GeminiKeyQuota(
            key_id=db_key.id,
            quota_type=QuotaType.DAILY,
            quota_limit=key_data.monthly_quota_limit // 30,
            quota_used=0,
            quota_remaining=key_data.monthly_quota_limit // 30,
            reset_at=self._get_next_day_start()
        )
        self.db.add(daily_quota)
        
        self.db.commit()
        self.db.refresh(db_key)
        
        logger.info(f"✅ Created new Gemini key: {key_data.key_name} (ID: {db_key.id})")
        return db_key
    
    def get_all_keys(self, include_inactive: bool = False) -> List[GeminiAPIKey]:
        """Lấy danh sách tất cả keys"""
        query = self.db.query(GeminiAPIKey)
        if not include_inactive:
            query = query.filter(GeminiAPIKey.status != KeyStatus.INACTIVE)
        return query.order_by(GeminiAPIKey.priority.asc()).all()
    
    def get_key_by_id(self, key_id: int) -> Optional[GeminiAPIKey]:
        """Lấy key theo ID"""
        return self.db.query(GeminiAPIKey).filter(GeminiAPIKey.id == key_id).first()
    
    def update_key_status(self, key_id: int, new_status: KeyStatus) -> GeminiAPIKey:
        """Update trạng thái của key"""
        db_key = self.get_key_by_id(key_id)
        if not db_key:
            raise ValueError(f"Key ID {key_id} không tồn tại")
        
        old_status = db_key.status
        db_key.status = new_status
        self.db.commit()
        
        logger.info(f"Updated key {db_key.key_name}: {old_status} → {new_status}")
        return db_key
    
    def delete_key(self, key_id: int) -> bool:
        """Xóa key (cascade delete quotas & logs)"""
        db_key = self.get_key_by_id(key_id)
        if not db_key:
            return False
        
        self.db.delete(db_key)
        self.db.commit()
        
        logger.info(f"🗑️ Deleted key: {db_key.key_name}")
        return True
    
    # ========== KEY SELECTION ==========
    
    def select_best_key(self) -> Optional[SelectedKeyInfo]:
        """
        Chọn key tốt nhất để dùng
        Tiêu chí:
        1. status = ACTIVE
        2. quota_remaining > threshold (10,000 tokens)
        3. priority ASC (key có priority thấp = ưu tiên cao)
        4. quota_remaining DESC (key còn nhiều quota nhất)
        5. last_used_at ASC (cân bằng tải)
        """
        THRESHOLD = 10_000  # Tối thiểu 10k tokens
        
        # Query với join quota table
        result = (
            self.db.query(
                GeminiAPIKey,
                GeminiKeyQuota.quota_remaining
            )
            .join(GeminiKeyQuota, GeminiAPIKey.id == GeminiKeyQuota.key_id)
            .filter(
                and_(
                    GeminiAPIKey.status == KeyStatus.ACTIVE,
                    GeminiKeyQuota.quota_type == QuotaType.MONTHLY,
                    GeminiKeyQuota.quota_remaining > THRESHOLD
                )
            )
            .order_by(
                GeminiAPIKey.priority.asc(),
                GeminiKeyQuota.quota_remaining.desc(),
                GeminiAPIKey.last_used_at.asc().nulls_first()
            )
            .first()
        )
        
        if not result:
            logger.warning("⚠️ NO AVAILABLE KEYS! All keys exhausted or inactive")
            
            # Fallback: Tìm key sắp reset (trong 1 giờ tới)
            fallback = (
                self.db.query(GeminiAPIKey, GeminiKeyQuota)
                .join(GeminiKeyQuota)
                .filter(
                    and_(
                        GeminiAPIKey.status == KeyStatus.ACTIVE,
                        GeminiKeyQuota.quota_type == QuotaType.MONTHLY,
                        GeminiKeyQuota.reset_at < datetime.utcnow() + timedelta(hours=1)
                    )
                )
                .order_by(GeminiAPIKey.priority.asc())
                .first()
            )
            
            if not fallback:
                return None
            
            result = fallback
        
        db_key, quota_remaining = result
        
        # Decrypt key
        api_key_decrypted = self.decrypt_api_key(db_key.api_key_encrypted)
        
        logger.info(f"✅ Selected key: {db_key.key_name} (quota remaining: {quota_remaining:,})")
        
        return SelectedKeyInfo(
            id=db_key.id,
            key_name=db_key.key_name,
            api_key_decrypted=api_key_decrypted,
            priority=db_key.priority,
            quota_remaining=quota_remaining
        )
    
    # ========== AUTO ROTATION ==========
    
    def rotate_key(
        self, 
        current_key_id: int, 
        reason: str,
        rotated_by: str = "system_auto"
    ) -> Optional[SelectedKeyInfo]:
        """
        Tự động chuyển sang key khác
        1. Mark current key (quota_exceeded hoặc revoked)
        2. Select next best key
        3. Log rotation
        """
        current_key = self.get_key_by_id(current_key_id)
        if not current_key:
            logger.error(f"Key ID {current_key_id} not found for rotation")
            return None
        
        # Update current key status
        if reason == "quota_exceeded":
            self.update_key_status(current_key_id, KeyStatus.QUOTA_EXCEEDED)
        elif reason in ["key_error", "revoked"]:
            self.update_key_status(current_key_id, KeyStatus.REVOKED)
        
        # Select next key
        next_key = self.select_best_key()
        
        if not next_key:
            logger.critical("🚨 CRITICAL: No available keys after rotation!")
            # TODO: Send alert to admin (email/Slack)
            return None
        
        # Log rotation
        rotation_log = GeminiKeyRotationLog(
            from_key_id=current_key_id,
            to_key_id=next_key.id,
            reason=reason,
            rotated_by=rotated_by
        )
        self.db.add(rotation_log)
        self.db.commit()
        
        logger.warning(f"🔄 Rotated key: {current_key.key_name} → {next_key.key_name} (reason: {reason})")
        
        return next_key
    
    # ========== QUOTA TRACKING ==========
    
    def track_usage(self, usage_data: UsageLogCreate) -> GeminiKeyUsageLog:
        """
        Track usage sau mỗi API call
        1. Insert usage log
        2. Update quota (monthly & daily)
        3. Check threshold → Auto-rotate if needed
        """
        # Insert log
        usage_log = GeminiKeyUsageLog(**usage_data.model_dump())
        self.db.add(usage_log)
        
        # Update monthly quota
        monthly_quota = (
            self.db.query(GeminiKeyQuota)
            .filter(
                and_(
                    GeminiKeyQuota.key_id == usage_data.key_id,
                    GeminiKeyQuota.quota_type == QuotaType.MONTHLY
                )
            )
            .first()
        )
        
        if monthly_quota:
            monthly_quota.quota_used += usage_data.total_tokens
            monthly_quota.quota_remaining = monthly_quota.quota_limit - monthly_quota.quota_used
            monthly_quota.last_updated = datetime.utcnow()
            
            # Check threshold (< 5% → rotate)
            if monthly_quota.quota_remaining < monthly_quota.quota_limit * 0.05:
                logger.warning(f"⚠️ Key {usage_data.key_id} gần hết quota: {monthly_quota.quota_remaining:,} tokens")
                self.rotate_key(usage_data.key_id, "quota_exceeded")
        
        # Update daily quota
        daily_quota = (
            self.db.query(GeminiKeyQuota)
            .filter(
                and_(
                    GeminiKeyQuota.key_id == usage_data.key_id,
                    GeminiKeyQuota.quota_type == QuotaType.DAILY
                )
            )
            .first()
        )
        
        if daily_quota:
            daily_quota.quota_used += usage_data.total_tokens
            daily_quota.quota_remaining = daily_quota.quota_limit - daily_quota.quota_used
            daily_quota.last_updated = datetime.utcnow()
        
        # Update last_used_at
        db_key = self.get_key_by_id(usage_data.key_id)
        if db_key:
            db_key.last_used_at = datetime.utcnow()
        
        self.db.commit()
        
        return usage_log
    
    # ========== QUOTA RESET (Cronjob) ==========
    
    def reset_monthly_quotas(self) -> int:
        """
        Reset tất cả monthly quotas (chạy đầu tháng)
        Return: số quotas đã reset
        """
        quotas = (
            self.db.query(GeminiKeyQuota)
            .filter(
                and_(
                    GeminiKeyQuota.quota_type == QuotaType.MONTHLY,
                    GeminiKeyQuota.reset_at <= datetime.utcnow()
                )
            )
            .all()
        )
        
        reset_count = 0
        for quota in quotas:
            quota.quota_used = 0
            quota.quota_remaining = quota.quota_limit
            quota.reset_at = self._get_next_month_start()
            quota.last_updated = datetime.utcnow()
            
            # Reactive key if it was quota_exceeded
            if quota.key.status == KeyStatus.QUOTA_EXCEEDED:
                quota.key.status = KeyStatus.ACTIVE
                logger.info(f"✅ Reactivated key: {quota.key.key_name}")
            
            reset_count += 1
        
        self.db.commit()
        logger.info(f"🔄 Reset {reset_count} monthly quotas")
        
        return reset_count
    
    def reset_daily_quotas(self) -> int:
        """Reset tất cả daily quotas (chạy mỗi đêm)"""
        quotas = (
            self.db.query(GeminiKeyQuota)
            .filter(
                and_(
                    GeminiKeyQuota.quota_type == QuotaType.DAILY,
                    GeminiKeyQuota.reset_at <= datetime.utcnow()
                )
            )
            .all()
        )
        
        for quota in quotas:
            quota.quota_used = 0
            quota.quota_remaining = quota.quota_limit
            quota.reset_at = self._get_next_day_start()
            quota.last_updated = datetime.utcnow()
        
        self.db.commit()
        return len(quotas)
    
    # ========== HELPER METHODS ==========
    
    def _get_next_month_start(self) -> datetime:
        """Lấy thời điểm đầu tháng sau"""
        now = datetime.utcnow()
        if now.month == 12:
            return datetime(now.year + 1, 1, 1)
        else:
            return datetime(now.year, now.month + 1, 1)
    
    def _get_next_day_start(self) -> datetime:
        """Lấy thời điểm đầu ngày mai"""
        now = datetime.utcnow()
        return datetime(now.year, now.month, now.day) + timedelta(days=1)
