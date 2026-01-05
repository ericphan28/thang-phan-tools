# Import all models to ensure SQLAlchemy knows about relationships
# This prevents "Failed to locate a name" errors

from app.models.auth_models import User, Role, ActivityLog
from app.models.subscription import Subscription, PricingPlan
from app.models.ocr_analytics import OCRUsageLog, OCRUserAction
from app.models.gemini_keys import (
    GeminiAPIKey, 
    GeminiKeyQuota, 
    GeminiKeyUsageLog, 
    GeminiKeyRotationLog,
    KeyStatus,
    QuotaType,
    UsageStatus
)

__all__ = [
    "User",
    "Role", 
    "ActivityLog",
    "Subscription",
    "PricingPlan",
    "OCRUsageLog",
    "OCRUserAction",
    "GeminiAPIKey",
    "GeminiKeyQuota",
    "GeminiKeyUsageLog",
    "GeminiKeyRotationLog",
    "KeyStatus",
    "QuotaType",
    "UsageStatus",
]
