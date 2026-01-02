"""
Subscription & Billing Pydantic Schemas
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ===== ENUMS =====

class PlanType(str, Enum):
    FREE = "free"
    INDIVIDUAL = "individual"
    ORGANIZATION = "organization"
    PAY_AS_YOU_GO = "pay_as_you_go"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"
    SUSPENDED = "suspended"


# ===== ORGANIZATION SCHEMAS =====

class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    slug: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    billing_email: Optional[EmailStr] = None


class OrganizationCreate(OrganizationBase):
    max_members: int = Field(default=10, ge=1, le=1000)


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    billing_email: Optional[EmailStr] = None
    max_members: Optional[int] = Field(None, ge=1, le=1000)
    is_active: Optional[bool] = None


class OrganizationResponse(OrganizationBase):
    id: int
    owner_id: int
    max_members: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ===== ORGANIZATION MEMBER SCHEMAS =====

class OrganizationMemberAdd(BaseModel):
    user_id: int
    role: str = Field(default="member", pattern="^(owner|admin|member)$")


class OrganizationMemberResponse(BaseModel):
    id: int
    organization_id: int
    user_id: int
    role: str
    is_active: bool
    invited_at: datetime
    joined_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ===== PRICING PLAN SCHEMAS =====

class PricingPlanBase(BaseModel):
    plan_type: PlanType
    name: str
    description: Optional[str] = None
    monthly_price: float = Field(ge=0)
    annual_price: Optional[float] = Field(None, ge=0)


class PricingPlanCreate(PricingPlanBase):
    premium_requests_limit: Optional[int] = None  # AI requests/month
    monthly_spending_limit: Optional[float] = None  # AI credits
    features: Optional[str] = None  # JSON string
    trial_days: int = Field(default=14, ge=0, le=365)


class PricingPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    monthly_price: Optional[float] = Field(None, ge=0)
    annual_price: Optional[float] = Field(None, ge=0)
    premium_requests_limit: Optional[int] = None  # AI requests
    monthly_spending_limit: Optional[float] = None  # AI credits
    features: Optional[str] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None
    trial_days: Optional[int] = Field(None, ge=0, le=365)


class PricingPlanResponse(PricingPlanBase):
    id: int
    premium_requests_limit: Optional[int]  # AI requests/month
    monthly_spending_limit: Optional[float]  # AI credits
    features: Optional[str]
    is_active: bool
    is_public: bool
    trial_days: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ===== SUBSCRIPTION SCHEMAS =====

class SubscriptionBase(BaseModel):
    plan_type: PlanType
    monthly_limit_usd: Optional[float] = Field(None, ge=0)


class SubscriptionCreate(SubscriptionBase):
    organization_id: Optional[int] = None


class SubscriptionUpdate(BaseModel):
    plan_type: Optional[PlanType] = None
    monthly_limit_usd: Optional[float] = Field(None, ge=0)
    cancel_at_period_end: Optional[bool] = None


class SubscriptionResponse(BaseModel):
    id: int
    user_id: Optional[int]
    organization_id: Optional[int]
    plan_type: PlanType
    status: SubscriptionStatus
    monthly_price: float
    monthly_limit_usd: Optional[float]
    # Map từ model fields (premium_requests_limit)
    premium_requests_limit: Optional[int] = None
    premium_requests_used: Optional[int] = None
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    trial_start: Optional[datetime]
    trial_end: Optional[datetime]
    cancel_at_period_end: bool
    cancelled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ===== USAGE SCHEMAS =====

class UsageSummary(BaseModel):
    """Current period usage summary"""
    period_start: datetime
    period_end: datetime
    total_requests: int
    total_tokens: int
    total_cost: float
    
    # Breakdown by provider
    gemini_cost: float
    claude_cost: float
    adobe_cost: float
    
    # Limits
    monthly_limit: Optional[float]
    remaining_budget: Optional[float]
    usage_percentage: Optional[float]


class DailyUsage(BaseModel):
    """Daily usage statistics"""
    date: str  # YYYY-MM-DD
    requests: int
    tokens: int
    cost: float


class ProviderUsage(BaseModel):
    """Usage by provider"""
    provider: str
    requests: int
    tokens: int
    cost: float
    percentage: float


class UsageStatsResponse(BaseModel):
    """Detailed usage statistics"""
    summary: UsageSummary
    daily_usage: List[DailyUsage]
    provider_breakdown: List[ProviderUsage]
    top_operations: List[dict]  # Top 5 operations by cost


# ===== BILLING SCHEMAS =====

class BillingHistoryResponse(BaseModel):
    id: int
    subscription_id: int
    billing_month: str
    period_start: datetime
    period_end: datetime
    total_requests: int
    total_tokens: int
    gemini_cost: float
    claude_cost: float
    adobe_cost: float
    total_cost: float
    subscription_fee: float
    total_amount: float
    status: str
    paid_at: Optional[datetime]
    invoice_number: Optional[str]
    invoice_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class BillingListResponse(BaseModel):
    """List of billing records with pagination"""
    total: int
    page: int
    page_size: int
    total_pages: int
    records: List[BillingHistoryResponse]


# ===== DASHBOARD SCHEMAS =====

class UserDashboardResponse(BaseModel):
    """User dashboard overview"""
    user_id: int
    username: str
    email: str
    
    # Subscription info
    subscription: SubscriptionResponse
    
    # Current period usage
    current_usage: UsageSummary
    
    # Alerts
    alerts: List[dict]  # Budget warnings, limit warnings, etc.


class OrganizationDashboardResponse(BaseModel):
    """Organization dashboard overview"""
    organization: OrganizationResponse
    subscription: SubscriptionResponse
    current_usage: UsageSummary
    member_count: int
    top_users: List[dict]  # Top users by usage
    alerts: List[dict]
