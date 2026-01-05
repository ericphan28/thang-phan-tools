"""
Gemini API Keys Management Models
Quản lý nhiều Gemini API keys với auto-rotation khi hết quota
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, BigInteger, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from enum import Enum

from app.core.database import Base


class KeyStatus(str, Enum):
    """Trạng thái của API key"""
    ACTIVE = "active"  # Đang hoạt động bình thường
    INACTIVE = "inactive"  # Tạm dừng (admin disable)
    REVOKED = "revoked"  # Bị thu hồi (key invalid)
    QUOTA_EXCEEDED = "quota_exceeded"  # Hết quota (tự động chuyển sang key khác)


class QuotaType(str, Enum):
    """Loại quota"""
    MONTHLY = "monthly"  # Quota reset hàng tháng
    DAILY = "daily"  # Quota reset hàng ngày
    PER_MINUTE = "per_minute"  # Rate limit (60 requests/minute)


class UsageStatus(str, Enum):
    """Trạng thái của request"""
    SUCCESS = "success"
    FAILED = "failed"
    QUOTA_EXCEEDED = "quota_exceeded"
    RATE_LIMITED = "rate_limited"
    KEY_ERROR = "key_error"


class GeminiAPIKey(Base):
    """
    Quản lý danh sách Gemini API keys
    Mỗi key có priority, quota, status riêng
    """
    __tablename__ = "gemini_api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String(100), nullable=False, unique=True)  # "Production Key 1"
    account_email = Column(String(255), nullable=True, index=True)  # Email tài khoản Google tạo key
    api_key_encrypted = Column(Text, nullable=False)  # Encrypted với AES-256
    provider = Column(String(20), default="gemini", nullable=False)  # Mở rộng: openai, claude
    
    status = Column(
        SQLEnum(KeyStatus),
        default=KeyStatus.ACTIVE,
        nullable=False,
        index=True
    )
    
    priority = Column(Integer, default=10, nullable=False, index=True)  # 1 = cao nhất
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)  # Ghi chú admin
    
    # Relationships
    quotas = relationship("GeminiKeyQuota", back_populates="key", cascade="all, delete-orphan")
    usage_logs = relationship("GeminiKeyUsageLog", back_populates="key", cascade="all, delete-orphan")
    rotations_from = relationship(
        "GeminiKeyRotationLog",
        foreign_keys="GeminiKeyRotationLog.from_key_id",
        back_populates="from_key"
    )
    rotations_to = relationship(
        "GeminiKeyRotationLog",
        foreign_keys="GeminiKeyRotationLog.to_key_id",
        back_populates="to_key"
    )
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<GeminiAPIKey(name='{self.key_name}', status='{self.status}', priority={self.priority})>"


class GeminiKeyQuota(Base):
    """
    Tracking quota của từng API key
    Mỗi key có quota monthly, daily, per_minute riêng
    """
    __tablename__ = "gemini_key_quotas"
    
    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(Integer, ForeignKey("gemini_api_keys.id", ondelete="CASCADE"), nullable=False, index=True)
    
    quota_type = Column(
        SQLEnum(QuotaType),
        nullable=False,
        index=True
    )
    
    quota_limit = Column(BigInteger, nullable=False)  # VD: 1,500,000 tokens/month
    quota_used = Column(BigInteger, default=0, nullable=False)
    quota_remaining = Column(BigInteger, nullable=False)  # Computed: limit - used
    
    reset_at = Column(DateTime, nullable=False, index=True)  # Thời điểm reset quota
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    key = relationship("GeminiAPIKey", back_populates="quotas")
    
    def __repr__(self):
        return f"<GeminiKeyQuota(key={self.key_id}, type='{self.quota_type}', remaining={self.quota_remaining}/{self.quota_limit})>"
    
    @property
    def usage_percentage(self) -> float:
        """Tỷ lệ % đã dùng"""
        if self.quota_limit == 0:
            return 0.0
        return (self.quota_used / self.quota_limit) * 100
    
    @property
    def is_near_limit(self) -> bool:
        """Kiểm tra có gần hết quota không (< 20%)"""
        return self.usage_percentage > 80


class GeminiKeyUsageLog(Base):
    """
    Log chi tiết mỗi request dùng Gemini API
    Dùng để analytics, billing, debugging
    """
    __tablename__ = "gemini_key_usage_log"
    
    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(Integer, ForeignKey("gemini_api_keys.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    model = Column(String(50), nullable=False, index=True)  # gemini-2.5-flash, gemini-2.0-flash-vision
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    
    cost_usd = Column(Numeric(10, 6), default=0.0, nullable=False)  # Chi phí tính theo token
    
    request_type = Column(String(50), nullable=True, index=True)  # ocr, writing, analysis, generation
    
    status = Column(
        SQLEnum(UsageStatus),
        default=UsageStatus.SUCCESS,
        nullable=False,
        index=True
    )
    
    error_message = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)  # Thời gian response (milliseconds)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    key = relationship("GeminiAPIKey", back_populates="usage_logs")
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<GeminiKeyUsageLog(key={self.key_id}, model='{self.model}', tokens={self.total_tokens}, status='{self.status}')>"


class GeminiKeyRotationLog(Base):
    """
    Lịch sử chuyển đổi giữa các API keys
    Track khi nào, tại sao rotate key
    """
    __tablename__ = "gemini_key_rotation_log"
    
    id = Column(Integer, primary_key=True, index=True)
    from_key_id = Column(Integer, ForeignKey("gemini_api_keys.id", ondelete="SET NULL"), nullable=True)
    to_key_id = Column(Integer, ForeignKey("gemini_api_keys.id", ondelete="SET NULL"), nullable=True)
    
    reason = Column(String(100), nullable=False, index=True)  # quota_exceeded, manual_rotation, key_error
    
    rotated_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    rotated_by = Column(String(50), nullable=False)  # "system_auto" hoặc "admin:username"
    
    # Relationships
    from_key = relationship("GeminiAPIKey", foreign_keys=[from_key_id], back_populates="rotations_from")
    to_key = relationship("GeminiAPIKey", foreign_keys=[to_key_id], back_populates="rotations_to")
    
    def __repr__(self):
        return f"<GeminiKeyRotationLog(from={self.from_key_id}, to={self.to_key_id}, reason='{self.reason}')>"
