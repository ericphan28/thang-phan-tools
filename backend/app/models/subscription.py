"""
User Subscription & Billing Models
- Subscription plans (Individual, Organization, Pay-as-you-go)
- User subscriptions
- Organizations
- Usage tracking per user
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.core.database import Base

# Import User from auth_models to establish relationships
from app.models.auth_models import User

# Forward declaration for AIUsageLog (avoid circular import)
# The actual AIUsageLog model is in models.py
# We'll use string reference for FK



class PlanType(str, Enum):
    """Subscription plan types"""
    FREE = "free"
    INDIVIDUAL = "individual"
    ORGANIZATION = "organization"
    PAY_AS_YOU_GO = "pay_as_you_go"


class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"
    SUSPENDED = "suspended"


class Organization(Base):
    """Organizations for team/company subscriptions"""
    __tablename__ = "organizations"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Settings
    max_members = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    
    # Billing
    billing_email = Column(String(200), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("OrganizationMember", back_populates="organization")
    subscription = relationship("Subscription", back_populates="organization", uselist=False)


class OrganizationMember(Base):
    """Members of an organization"""
    __tablename__ = "organization_members"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Role in organization
    role = Column(String(50), default="member")  # owner, admin, member
    
    # Status
    is_active = Column(Boolean, default=True)
    invited_at = Column(DateTime, default=datetime.utcnow)
    joined_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="members")
    user = relationship("User")


class Subscription(Base):
    """User/Organization subscriptions"""
    __tablename__ = "subscriptions"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Subscription owner (user or organization)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Plan details
    plan_type = Column(SQLEnum(PlanType), nullable=False, default=PlanType.FREE)
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.TRIAL)
    
    # Pricing
    monthly_price = Column(Float, default=0.0)  # USD
    monthly_limit_usd = Column(Float, nullable=True)  # Spending limit
    
    # Usage limits
    # Basic features = UNLIMITED (Word/Excel/PDF, basic OCR)
    # Premium requests = AI calls (Gemini, Claude, Adobe Advanced)
    premium_requests_used = Column(Integer, default=0)  # Premium requests used this period
    premium_requests_limit = Column(Integer, nullable=True)  # From pricing plan
    
    # Billing period
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    
    # Trial
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    
    # Cancel
    cancel_at_period_end = Column(Boolean, default=False)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    organization = relationship("Organization", back_populates="subscription", foreign_keys=[organization_id])
    usage_records = relationship("UserUsageRecord", back_populates="subscription")


class UserUsageRecord(Base):
    """Track AI usage per user/organization for billing"""
    __tablename__ = "user_usage_records"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Owner
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Who made the request
    
    # Usage details
    ai_usage_log_id = Column(Integer, ForeignKey("ai_usage_logs.id"), nullable=True)  # Link to AI usage
    
    # Aggregated data (for quick queries)
    provider = Column(String(50), nullable=False, index=True)  # gemini, claude, adobe
    operation = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    
    # Tokens & Cost
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)  # USD
    
    # Period tracking
    billing_month = Column(String(7), nullable=False, index=True)  # YYYY-MM format
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="usage_records")
    user = relationship("User")


class BillingHistory(Base):
    """Monthly billing records"""
    __tablename__ = "billing_history"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Subscription
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    
    # Billing period
    billing_month = Column(String(7), nullable=False, index=True)  # YYYY-MM
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Usage summary
    total_requests = Column(Integer, default=0)
    total_input_tokens = Column(Integer, default=0)
    total_output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Cost breakdown
    gemini_cost = Column(Float, default=0.0)
    claude_cost = Column(Float, default=0.0)
    adobe_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Subscription fee
    subscription_fee = Column(Float, default=0.0)
    
    # Total amount
    total_amount = Column(Float, default=0.0)  # subscription_fee + total_cost
    
    # Status
    status = Column(String(50), default="pending")  # pending, paid, overdue
    paid_at = Column(DateTime, nullable=True)
    
    # Invoice
    invoice_number = Column(String(100), unique=True, nullable=True)
    invoice_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscription = relationship("Subscription")


class PricingPlan(Base):
    """Available pricing plans configuration"""
    __tablename__ = "pricing_plans"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Plan details
    plan_type = Column(SQLEnum(PlanType), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Pricing
    monthly_price = Column(Float, default=0.0)
    annual_price = Column(Float, nullable=True)  # Discounted annual price
    
    # Limits
    # Basic features (Word/Excel/PDF conversion, basic OCR) = UNLIMITED (included)
    # Premium requests = AI providers (Gemini, Claude, Adobe Advanced) = LIMITED
    premium_requests_limit = Column(Integer, nullable=True)  # Premium AI requests/month
    monthly_spending_limit = Column(Float, nullable=True)  # USD - AI credits for pay-as-you-go
    
    # Features (JSON string)
    features = Column(Text, nullable=True)  # Store as JSON
    
    # Visibility
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    
    # Trial
    trial_days = Column(Integer, default=14)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
