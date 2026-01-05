"""
Pydantic schemas for Gemini API Keys Management
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class KeyStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"
    QUOTA_EXCEEDED = "quota_exceeded"


class QuotaTypeEnum(str, Enum):
    MONTHLY = "monthly"
    DAILY = "daily"
    PER_MINUTE = "per_minute"


class UsageStatusEnum(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    QUOTA_EXCEEDED = "quota_exceeded"
    RATE_LIMITED = "rate_limited"
    KEY_ERROR = "key_error"


# ========== Gemini API Key Schemas ==========

class GeminiAPIKeyCreate(BaseModel):
    """Schema để tạo key mới"""
    key_name: str = Field(..., min_length=3, max_length=100, description="Tên gợi nhớ cho key")
    account_email: Optional[str] = Field(None, max_length=255, description="Email tài khoản Google (VD: ericphan28@gmail.com)")
    api_key: str = Field(..., min_length=30, description="Gemini API key từ Google AI Studio")
    priority: int = Field(10, ge=1, le=100, description="Thứ tự ưu tiên (1 = cao nhất)")
    monthly_quota_limit: int = Field(1_500_000, ge=0, description="Giới hạn quota hàng tháng (tokens)")
    notes: Optional[str] = Field(None, description="Ghi chú admin")
    
    @validator('api_key')
    def validate_api_key(cls, v):
        if not v.startswith('AIza'):
            raise ValueError('Gemini API key phải bắt đầu bằng "AIza"')
        return v


class GeminiAPIKeyUpdate(BaseModel):
    """Schema để update key"""
    key_name: Optional[str] = Field(None, min_length=3, max_length=100)
    account_email: Optional[str] = Field(None, max_length=255)
    status: Optional[KeyStatusEnum] = None
    priority: Optional[int] = Field(None, ge=1, le=100)
    notes: Optional[str] = None


class GeminiAPIKeyResponse(BaseModel):
    """Response schema - KHÔNG trả về full API key"""
    id: int
    key_name: str
    account_email: Optional[str] = None
    api_key_masked: str  # AIza***************xyz (chỉ show 4 ký tự đầu/cuối)
    provider: str
    status: KeyStatusEnum
    priority: int
    created_at: datetime
    last_used_at: Optional[datetime]
    notes: Optional[str]
    
    # Quota info (joined từ quotas table)
    monthly_quota_limit: Optional[int] = None
    monthly_quota_used: Optional[int] = None
    monthly_quota_remaining: Optional[int] = None
    monthly_usage_percentage: Optional[float] = None
    is_near_limit: Optional[bool] = None
    
    class Config:
        from_attributes = True


# ========== Quota Schemas ==========

class QuotaResponse(BaseModel):
    """Response quota của 1 key"""
    id: int
    key_id: int
    quota_type: QuotaTypeEnum
    quota_limit: int
    quota_used: int
    quota_remaining: int
    usage_percentage: float
    is_near_limit: bool
    reset_at: datetime
    last_updated: datetime
    
    class Config:
        from_attributes = True


# ========== Usage Log Schemas ==========

class UsageLogCreate(BaseModel):
    """Schema để log usage (internal use)"""
    key_id: int
    user_id: Optional[int] = None
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    request_type: Optional[str] = None
    status: UsageStatusEnum = UsageStatusEnum.SUCCESS
    error_message: Optional[str] = None
    response_time_ms: Optional[int] = None


class UsageLogResponse(BaseModel):
    """Response usage log"""
    id: int
    key_id: int
    key_name: Optional[str] = None  # Joined from key table
    user_id: Optional[int]
    username: Optional[str] = None  # Joined from user table
    model: str
    total_tokens: int
    cost_usd: float
    request_type: Optional[str]
    status: UsageStatusEnum
    error_message: Optional[str]
    response_time_ms: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== Rotation Log Schemas ==========

class RotationLogResponse(BaseModel):
    """Response rotation log"""
    id: int
    from_key_id: Optional[int]
    from_key_name: Optional[str]
    to_key_id: Optional[int]
    to_key_name: Optional[str]
    reason: str
    rotated_at: datetime
    rotated_by: str
    
    class Config:
        from_attributes = True


# ========== Dashboard & Analytics Schemas ==========

class KeyHealthOverview(BaseModel):
    """Tổng quan sức khỏe tất cả keys"""
    total_keys: int
    active_keys: int
    inactive_keys: int
    quota_exceeded_keys: int
    revoked_keys: int
    total_quota_remaining: int  # Tổng quota còn lại của tất cả keys active
    keys_near_limit: List[str]  # Danh sách tên keys gần hết quota


class UsageTrend(BaseModel):
    """Xu hướng sử dụng theo thời gian"""
    date: str  # YYYY-MM-DD
    total_requests: int
    total_tokens: int
    total_cost_usd: float
    success_rate: float  # % request thành công


class ModelUsageStats(BaseModel):
    """Thống kê usage theo model"""
    model: str
    total_requests: int
    total_tokens: int
    total_cost_usd: float
    avg_response_time_ms: Optional[float]


class UserUsageStats(BaseModel):
    """Thống kê usage theo user"""
    user_id: int
    username: str
    total_requests: int
    total_tokens: int
    total_cost_usd: float


class DashboardMetrics(BaseModel):
    """Metrics tổng hợp cho dashboard"""
    overview: KeyHealthOverview
    usage_trends_7d: List[UsageTrend]  # 7 ngày gần nhất
    top_models: List[ModelUsageStats]
    top_users: List[UserUsageStats]
    recent_rotations: List[RotationLogResponse]


# ========== Key Selection Response ==========

class SelectedKeyInfo(BaseModel):
    """Thông tin key được chọn (internal use, không trả về client)"""
    id: int
    key_name: str
    api_key_decrypted: str  # Full key để dùng call API
    priority: int
    quota_remaining: int
