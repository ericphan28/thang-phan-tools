"""
User Subscription & Billing API Endpoints
Manage subscriptions, usage tracking, and billing for users and organizations
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_, extract, case
from typing import Optional, List
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_superuser
from app.models.auth_models import User
from app.models.subscription import (
    Subscription, Organization, OrganizationMember, 
    PricingPlan, UserUsageRecord, BillingHistory,
    PlanType, SubscriptionStatus
)
from app.schemas.subscription import (
    # Organization
    OrganizationCreate, OrganizationUpdate, OrganizationResponse,
    OrganizationMemberAdd, OrganizationMemberResponse,
    # Pricing Plans
    PricingPlanResponse,
    # Subscription
    SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse,
    # Usage & Billing
    UsageSummary, UsageStatsResponse, DailyUsage, ProviderUsage,
    BillingHistoryResponse, BillingListResponse,
    # Dashboard
    UserDashboardResponse
)

router = APIRouter(tags=["💳 User Subscription"])


# ==================== ADMIN: SYNC USER TIER (DEV/OPS) ====================

from pydantic import BaseModel


class AdminSetTierRequest(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    tier: str  # FREE/PRO/TEAM/ENTERPRISE


@router.post("/admin/set-user-tier")
async def admin_set_user_tier(
    payload: AdminSetTierRequest,
    admin_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Set a user's quota tier server-side. Use for syncing paid plans into DB."""
    from app.services.quota_service import QuotaService

    tier = (payload.tier or "").upper().strip()
    if tier not in QuotaService.QUOTA_LIMITS:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {tier}")

    user = None
    if payload.user_id is not None:
        user = db.query(User).filter(User.id == payload.user_id).first()
    elif payload.email:
        user = db.query(User).filter(User.email == payload.email).first()
    else:
        raise HTTPException(status_code=400, detail="Provide user_id or email")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    QuotaService.upgrade_subscription(user, tier, db)
    db.refresh(user)

    return {
        "ok": True,
        "user_id": user.id,
        "email": user.email,
        **QuotaService.get_user_quota_info(user),
    }


# ==================== HELPER FUNCTIONS ====================

def get_current_period(subscription: Subscription) -> tuple[datetime, datetime]:
    """Get current billing period for subscription"""
    if subscription.current_period_start and subscription.current_period_end:
        return subscription.current_period_start, subscription.current_period_end
    
    # Default to current month
    now = datetime.utcnow()
    start = datetime(now.year, now.month, 1)
    end = datetime(now.year, now.month, calendar.monthrange(now.year, now.month)[1], 23, 59, 59)
    return start, end


def calculate_usage_summary(
    db: Session,
    subscription_id: int,
    start_date: datetime,
    end_date: datetime
) -> UsageSummary:
    """Calculate usage summary for a billing period"""
    
    # Query usage records
    usage = db.query(
        func.count(UserUsageRecord.id).label('total_requests'),
        func.sum(UserUsageRecord.total_tokens).label('total_tokens'),
        func.sum(UserUsageRecord.total_cost).label('total_cost'),
        func.sum(
            case(
                (UserUsageRecord.provider == 'gemini', UserUsageRecord.total_cost),
                else_=0
            )
        ).label('gemini_cost'),
        func.sum(
            case(
                (UserUsageRecord.provider == 'claude', UserUsageRecord.total_cost),
                else_=0
            )
        ).label('claude_cost'),
        func.sum(
            case(
                (UserUsageRecord.provider == 'adobe', UserUsageRecord.total_cost),
                else_=0
            )
        ).label('adobe_cost')
    ).filter(
        UserUsageRecord.subscription_id == subscription_id,
        UserUsageRecord.created_at >= start_date,
        UserUsageRecord.created_at <= end_date
    ).first()
    
    # Get subscription limits
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    
    total_cost = float(usage.total_cost or 0)
    monthly_limit = subscription.monthly_limit_usd
    
    remaining_budget = None
    usage_percentage = None
    if monthly_limit:
        remaining_budget = max(0, monthly_limit - total_cost)
        usage_percentage = min(100, (total_cost / monthly_limit) * 100)
    
    return UsageSummary(
        period_start=start_date,
        period_end=end_date,
        total_requests=usage.total_requests or 0,
        total_tokens=int(usage.total_tokens or 0),
        total_cost=total_cost,
        gemini_cost=float(usage.gemini_cost or 0),
        claude_cost=float(usage.claude_cost or 0),
        adobe_cost=float(usage.adobe_cost or 0),
        monthly_limit=monthly_limit,
        remaining_budget=remaining_budget,
        usage_percentage=usage_percentage
    )


# ==================== PRICING PLANS ====================

@router.get("/pricing-plans", response_model=List[PricingPlanResponse])
async def get_pricing_plans(
    active_only: bool = True,
    public_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get available pricing plans"""
    query = db.query(PricingPlan)
    
    if active_only:
        query = query.filter(PricingPlan.is_active == True)
    if public_only:
        query = query.filter(PricingPlan.is_public == True)
    
    plans = query.order_by(PricingPlan.monthly_price).all()
    return plans


@router.get("/pricing-plans/{plan_type}", response_model=PricingPlanResponse)
async def get_pricing_plan(
    plan_type: PlanType,
    db: Session = Depends(get_db)
):
    """Get specific pricing plan details"""
    plan = db.query(PricingPlan).filter(PricingPlan.plan_type == plan_type).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Pricing plan not found")
    return plan


# ==================== USER SUBSCRIPTION ====================

@router.get("/my-subscription", response_model=SubscriptionResponse)
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription"""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        # Create free subscription by default
        subscription = Subscription(
            user_id=current_user.id,
            plan_type=PlanType.FREE,
            status=SubscriptionStatus.ACTIVE,
            monthly_price=0.0
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
    
    return subscription


@router.post("/subscribe", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Subscribe to a plan (Individual or Pay-as-you-go)"""
    
    # Check if user already has subscription
    existing = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="User already has a subscription. Use update endpoint instead."
        )
    
    # Get pricing plan
    plan = db.query(PricingPlan).filter(
        PricingPlan.plan_type == subscription_data.plan_type
    ).first()
    
    if not plan or not plan.is_active:
        raise HTTPException(status_code=400, detail="Invalid or inactive plan")
    
    # Organization subscriptions must be created separately
    if subscription_data.plan_type == PlanType.ORGANIZATION:
        raise HTTPException(
            status_code=400,
            detail="Organization subscriptions must be created through organization endpoint"
        )
    
    # Calculate billing period
    now = datetime.utcnow()
    trial_end = now + timedelta(days=plan.trial_days) if plan.trial_days > 0 else None
    period_start = now
    period_end = now + relativedelta(months=1)
    
    # Create subscription
    subscription = Subscription(
        user_id=current_user.id,
        plan_type=subscription_data.plan_type,
        status=SubscriptionStatus.TRIAL if trial_end else SubscriptionStatus.ACTIVE,
        monthly_price=plan.monthly_price,
        monthly_limit_usd=subscription_data.monthly_limit_usd or plan.monthly_spending_limit,
        monthly_requests_limit=plan.monthly_requests_limit,
        daily_requests_limit=plan.daily_requests_limit,
        current_period_start=period_start,
        current_period_end=period_end,
        trial_start=now if trial_end else None,
        trial_end=trial_end
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    return subscription


@router.put("/my-subscription", response_model=SubscriptionResponse)
async def update_my_subscription(
    subscription_data: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's subscription"""
    
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")
    
    # Update plan type
    if subscription_data.plan_type and subscription_data.plan_type != subscription.plan_type:
        plan = db.query(PricingPlan).filter(
            PricingPlan.plan_type == subscription_data.plan_type
        ).first()
        
        if not plan or not plan.is_active:
            raise HTTPException(status_code=400, detail="Invalid or inactive plan")
        
        subscription.plan_type = subscription_data.plan_type
        subscription.monthly_price = plan.monthly_price
        subscription.monthly_requests_limit = plan.monthly_requests_limit
        subscription.daily_requests_limit = plan.daily_requests_limit
    
    # Update limits
    if subscription_data.monthly_limit_usd is not None:
        subscription.monthly_limit_usd = subscription_data.monthly_limit_usd
    
    # Cancel subscription
    if subscription_data.cancel_at_period_end is not None:
        subscription.cancel_at_period_end = subscription_data.cancel_at_period_end
        if subscription_data.cancel_at_period_end:
            subscription.cancelled_at = datetime.utcnow()
    
    subscription.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(subscription)
    
    return subscription


@router.delete("/my-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel subscription (will be cancelled at period end)"""
    
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")
    
    subscription.cancel_at_period_end = True
    subscription.cancelled_at = datetime.utcnow()
    subscription.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Subscription will be cancelled at the end of current billing period",
        "cancellation_date": subscription.current_period_end
    }


# ==================== USAGE STATISTICS ====================

@router.get("/my-usage", response_model=UsageSummary)
async def get_my_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's usage summary for current period"""
    
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")
    
    start_date, end_date = get_current_period(subscription)
    return calculate_usage_summary(db, subscription.id, start_date, end_date)


@router.get("/my-usage/detailed", response_model=UsageStatsResponse)
async def get_my_usage_detailed(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed usage statistics with daily breakdown"""
    
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Summary
    summary = calculate_usage_summary(db, subscription.id, start_date, end_date)
    
    # Daily usage
    daily_data = db.query(
        func.date(UserUsageRecord.created_at).label('date'),
        func.count(UserUsageRecord.id).label('requests'),
        func.sum(UserUsageRecord.total_tokens).label('tokens'),
        func.sum(UserUsageRecord.total_cost).label('cost')
    ).filter(
        UserUsageRecord.subscription_id == subscription.id,
        UserUsageRecord.created_at >= start_date,
        UserUsageRecord.created_at <= end_date
    ).group_by(func.date(UserUsageRecord.created_at)).all()
    
    daily_usage = [
        DailyUsage(
            date=str(d.date),
            requests=d.requests,
            tokens=int(d.tokens or 0),
            cost=float(d.cost or 0)
        )
        for d in daily_data
    ]
    
    # Provider breakdown
    provider_data = db.query(
        UserUsageRecord.provider,
        func.count(UserUsageRecord.id).label('requests'),
        func.sum(UserUsageRecord.total_tokens).label('tokens'),
        func.sum(UserUsageRecord.total_cost).label('cost')
    ).filter(
        UserUsageRecord.subscription_id == subscription.id,
        UserUsageRecord.created_at >= start_date,
        UserUsageRecord.created_at <= end_date
    ).group_by(UserUsageRecord.provider).all()
    
    total_cost = sum(p.cost or 0 for p in provider_data)
    provider_breakdown = [
        ProviderUsage(
            provider=p.provider,
            requests=p.requests,
            tokens=int(p.tokens or 0),
            cost=float(p.cost or 0),
            percentage=float(p.cost or 0) / total_cost * 100 if total_cost > 0 else 0
        )
        for p in provider_data
    ]
    
    # Top operations
    top_ops = db.query(
        UserUsageRecord.operation,
        func.count(UserUsageRecord.id).label('count'),
        func.sum(UserUsageRecord.total_cost).label('cost')
    ).filter(
        UserUsageRecord.subscription_id == subscription.id,
        UserUsageRecord.created_at >= start_date,
        UserUsageRecord.created_at <= end_date
    ).group_by(UserUsageRecord.operation).order_by(desc('cost')).limit(5).all()
    
    top_operations = [
        {
            "operation": op.operation,
            "count": op.count,
            "cost": float(op.cost or 0)
        }
        for op in top_ops
    ]
    
    return UsageStatsResponse(
        summary=summary,
        daily_usage=daily_usage,
        provider_breakdown=provider_breakdown,
        top_operations=top_operations
    )


# ==================== BILLING HISTORY ====================

@router.get("/my-billing", response_model=BillingListResponse)
async def get_my_billing_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get billing history for current user"""
    
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")
    
    # Query billing records
    query = db.query(BillingHistory).filter(
        BillingHistory.subscription_id == subscription.id
    ).order_by(desc(BillingHistory.billing_month))
    
    total = query.count()
    records = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return BillingListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
        records=records
    )


@router.get("/my-billing/{billing_id}", response_model=BillingHistoryResponse)
async def get_billing_detail(
    billing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific billing record detail"""
    
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")
    
    billing = db.query(BillingHistory).filter(
        BillingHistory.id == billing_id,
        BillingHistory.subscription_id == subscription.id
    ).first()
    
    if not billing:
        raise HTTPException(status_code=404, detail="Billing record not found")
    
    return billing


# ==================== ORGANIZATION ENDPOINTS ====================

@router.post("/organizations", response_model=OrganizationResponse)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new organization"""
    
    # Check if slug is unique
    existing = db.query(Organization).filter(Organization.slug == org_data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organization slug already exists")
    
    # Create organization
    organization = Organization(
        name=org_data.name,
        slug=org_data.slug,
        description=org_data.description,
        billing_email=org_data.billing_email,
        owner_id=current_user.id,
        max_members=org_data.max_members
    )
    
    db.add(organization)
    db.commit()
    db.refresh(organization)
    
    # Add owner as member
    member = OrganizationMember(
        organization_id=organization.id,
        user_id=current_user.id,
        role="owner",
        joined_at=datetime.utcnow()
    )
    db.add(member)
    db.commit()
    
    return organization


@router.get("/organizations/my", response_model=List[OrganizationResponse])
async def get_my_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get organizations where user is a member"""
    
    memberships = db.query(OrganizationMember).filter(
        OrganizationMember.user_id == current_user.id,
        OrganizationMember.is_active == True
    ).all()
    
    org_ids = [m.organization_id for m in memberships]
    organizations = db.query(Organization).filter(
        Organization.id.in_(org_ids)
    ).all()
    
    return organizations


@router.get("/organizations/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get organization details"""
    
    # Check if user is member
    member = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.user_id == current_user.id,
        OrganizationMember.is_active == True
    ).first()
    
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    
    organization = db.query(Organization).filter(Organization.id == org_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return organization


# ==================== NEW: QUOTA MANAGEMENT (Phase 1) ====================

from app.services.quota_service import QuotaService
from pydantic import BaseModel

class QuotaResponse(BaseModel):
    """Quota information response"""
    subscription_tier: str
    quota_monthly: int
    usage_this_month: int
    remaining: int
    percentage_used: float
    reset_date: Optional[datetime]
    is_warning_level: bool  # >80%


@router.get("/quota")
async def get_my_quota(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📊 Lấy thông tin quota AI của user hiện tại
    
    **Returns:**
    - subscription_tier: FREE/PRO/TEAM/ENTERPRISE
    - quota_monthly: Tổng quota/tháng
    - usage_this_month: Đã dùng bao nhiêu
    - remaining: Còn lại bao nhiêu
    - percentage_used: % đã dùng (0-100)
    - reset_date: Ngày reset quota
    - is_warning_level: True nếu >80% quota
    """
    # Reset quota nếu đã qua tháng
    QuotaService.check_and_reset_quota(current_user, db)
    db.refresh(current_user)

    quota_info = QuotaService.get_user_quota_info(current_user, db)
    
    return {
        **quota_info,
        "is_warning_level": QuotaService.is_quota_warning_level(current_user)
    }


@router.get("/tiers")
async def get_subscription_tiers():
    """
    💰 Lấy danh sách tất cả subscription tiers với giá
    
    **Returns:** List of all available tiers with pricing
    """
    return {
        "tiers": [
            {
                "id": "FREE",
                "name": "Miễn phí",
                "price": 0,
                "price_display": "Miễn phí",
                "quota_monthly": 3,
                "features": [
                    "3 AI requests/month",
                    "Basic convert Word↔PDF",
                    "OCR đơn giản",
                    "Community support"
                ],
                "recommended": False
            },
            {
                "id": "PRO",
                "name": "Professional",
                "price": 399000,
                "price_display": "399,000 VNĐ/tháng",
                "quota_monthly": 100,
                "features": [
                    "100 AI requests/month",
                    "All AI tools",
                    "OCR tiếng Việt (Gemini)",
                    "Formal writing optimization",
                    "Data conflict detection",
                    "Chart generation",
                    "Priority support",
                    "No watermark"
                ],
                "recommended": True,
                "badge": "Phổ biến nhất"
            },
            {
                "id": "TEAM",
                "name": "Team",
                "price": 1990000,
                "price_display": "1,990,000 VNĐ/tháng",
                "quota_monthly": 500,
                "features": [
                    "500 AI requests/month (shared)",
                    "Up to 5 users",
                    "All PRO features",
                    "Team dashboard",
                    "Usage analytics",
                    "Priority support",
                    "Team training (1 session)"
                ],
                "recommended": False
            },
            {
                "id": "ENTERPRISE",
                "name": "Enterprise",
                "price": 0,
                "price_display": "Liên hệ",
                "quota_monthly": 999999,
                "features": [
                    "Unlimited AI requests",
                    "Unlimited users",
                    "On-premise deployment option",
                    "Custom integrations",
                    "Dedicated support",
                    "SLA 99.9%",
                    "Training & consulting",
                    "Custom workflows"
                ],
                "recommended": False,
                "badge": "Doanh nghiệp"
            }
        ]
    }
