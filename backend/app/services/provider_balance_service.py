"""
Service to fetch balance and usage information from AI providers
"""
import httpx
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProviderBalanceService:
    """Fetch real-time balance and limits from AI providers"""
    
    @staticmethod
    async def get_anthropic_balance(api_key: str) -> Optional[Dict]:
        """
        Get Claude (Anthropic) organization usage and balance
        
        Returns:
            {
                "credits_remaining": float,
                "credits_used": float,
                "rate_limit": {
                    "requests_per_minute": int,
                    "tokens_per_minute": int
                },
                "billing_period": {
                    "start": str,
                    "end": str
                }
            }
        """
        try:
            async with httpx.AsyncClient() as client:
                # Check organization usage
                response = await client.get(
                    "https://api.anthropic.com/v1/organization/usage",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "provider": "claude",
                        "status": "success",
                        "credits_remaining": data.get("balance", {}).get("remaining", 0),
                        "credits_used": data.get("balance", {}).get("used", 0),
                        "currency": "USD",
                        "last_updated": datetime.utcnow().isoformat()
                    }
                else:
                    logger.warning(f"Anthropic API returned {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching Anthropic balance: {e}")
            return None
    
    @staticmethod
    async def get_adobe_balance(client_id: str, client_secret: str) -> Optional[Dict]:
        """
        Get Adobe PDF Services transaction credits
        
        Note: Adobe doesn't provide a direct balance API.
        This returns estimated info based on plan type.
        """
        try:
            # Adobe uses OAuth2, need to get access token first
            async with httpx.AsyncClient() as client:
                # Get access token
                token_response = await client.post(
                    "https://ims-na1.adobelogin.com/ims/token/v3",
                    data={
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "grant_type": "client_credentials",
                        "scope": "openid,AdobeID,read_organizations"
                    },
                    timeout=10.0
                )
                
                if token_response.status_code != 200:
                    logger.warning(f"Adobe auth failed: {token_response.status_code}")
                    return None
                
                access_token = token_response.json().get("access_token")
                
                # Adobe doesn't have public balance API
                # Return static plan info
                return {
                    "provider": "adobe",
                    "status": "limited_info",
                    "message": "Adobe doesn't provide public balance API",
                    "plan_type": "Standard",
                    "estimated_monthly_quota": 5000,
                    "last_updated": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error fetching Adobe balance: {e}")
            return None
    
    @staticmethod
    async def get_gemini_info(api_key: str, db_session=None) -> Optional[Dict]:
        """
        Get Gemini (Google) rate limits and quota info
        
        Checks actual usage from database to show remaining daily quota.
        
        FREE TIER LIMITS (from Google):
        - 15 requests per minute
        - 1,500 requests per day (main limit)
        - 1M tokens per minute (rarely hit)
        - UNLIMITED total tokens (free forever)
        
        PAY-AS-YOU-GO:
        - Charged per TOKEN (not per request)
        - Gemini 2.5 Flash: $0.50/1M input + $2.00/1M output
        """
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        try:
            # Test if API key is valid
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://generativelanguage.googleapis.com/v1beta/models",
                    params={"key": api_key},
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    logger.warning(f"Gemini API returned {response.status_code}")
                    return None
            
            # Get today's usage from database if session provided
            requests_today = 0
            tokens_today = 0
            models_used = {}
            if db_session:
                from app.models.models import AIProviderKey, AIUsageLog
                
                # Get Gemini provider key
                gemini_key = db_session.query(AIProviderKey).filter(
                    AIProviderKey.provider == "gemini",
                    AIProviderKey.is_active == True
                ).first()
                
                if gemini_key:
                    # Count requests and tokens today
                    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    requests_today = db_session.query(func.count(AIUsageLog.id)).filter(
                        AIUsageLog.provider_key_id == gemini_key.id,
                        AIUsageLog.created_at >= today_start
                    ).scalar() or 0
                    
                    tokens_today = db_session.query(func.sum(AIUsageLog.total_tokens)).filter(
                        AIUsageLog.provider_key_id == gemini_key.id,
                        AIUsageLog.created_at >= today_start
                    ).scalar() or 0
                    
                    # Get breakdown by model
                    model_stats = db_session.query(
                        AIUsageLog.model,
                        func.count(AIUsageLog.id).label('requests'),
                        func.sum(AIUsageLog.input_tokens).label('input_tokens'),
                        func.sum(AIUsageLog.output_tokens).label('output_tokens')
                    ).filter(
                        AIUsageLog.provider_key_id == gemini_key.id,
                        AIUsageLog.created_at >= today_start
                    ).group_by(AIUsageLog.model).all()
                    
                    # Calculate cost per model
                    from app.services.ai_usage_service import PRICING
                    for model, req_count, input_tok, output_tok in model_stats:
                        pricing = PRICING.get(model, {"input": 0.5, "output": 2.0})
                        cost = ((input_tok or 0) / 1_000_000 * pricing["input"]) + \
                               ((output_tok or 0) / 1_000_000 * pricing["output"])
                        models_used[model] = {
                            "requests": req_count,
                            "input_tokens": input_tok or 0,
                            "output_tokens": output_tok or 0,
                            "total_tokens": (input_tok or 0) + (output_tok or 0),
                            "estimated_cost": round(cost, 4),
                            "pricing": {
                                "input": f"${pricing['input']}/1M",
                                "output": f"${pricing['output']}/1M"
                            }
                        }
            
            daily_request_limit = 1500
            remaining_requests = daily_request_limit - requests_today
            usage_pct = (requests_today / daily_request_limit) * 100
            
            # Total estimated cost across all models
            estimated_cost = sum(m["estimated_cost"] for m in models_used.values())
            
            return {
                "provider": "gemini",
                "status": "success",
                "plan_type": "Free Tier",
                "rate_limits": {
                    "requests_per_minute": 15,
                    "requests_per_day": daily_request_limit,
                    "tokens_per_minute": 1_000_000
                },
                "daily_usage": {
                    "requests_today": requests_today,
                    "remaining_requests": remaining_requests,
                    "usage_percentage": round(usage_pct, 2),
                    "tokens_today": tokens_today,
                    "tokens_per_minute_limit": 1_000_000,
                    "resets_in_hours": 24 - datetime.utcnow().hour
                },
                "models_breakdown": models_used,
                "pricing_info": {
                    "current_plan": "Free",
                    "total_estimated_cost_if_paid": round(estimated_cost, 4),
                    "note": "Mỗi model có giá khác nhau - xem chi tiết ở models_breakdown"
                },
                "message": "Free tier - 100% miễn phí" if remaining_requests > 100 else f"⚠️ Chỉ còn {remaining_requests} requests hôm nay!",
                "note": "FREE TIER: Giới hạn 1,500 requests/day (dùng chung cho TẤT CẢ models). Nếu upgrade lên PAID: Tính tiền theo TOKENS, mỗi model giá khác nhau.",
                "last_updated": datetime.utcnow().isoformat()
            }
                    
        except Exception as e:
            logger.error(f"Error checking Gemini API: {e}")
            return None
    
    @staticmethod
    async def get_all_balances(api_keys: Dict[str, Dict], db_session=None) -> Dict[str, Optional[Dict]]:
        """
        Fetch balance info for all configured providers
        
        Args:
            api_keys: {
                "claude": {"api_key": "sk-..."},
                "adobe": {"client_id": "...", "client_secret": "..."},
                "gemini": {"api_key": "..."}
            }
            db_session: SQLAlchemy session for database queries
        
        Returns:
            {
                "claude": {...balance info...},
                "adobe": {...balance info...},
                "gemini": {...info...}
            }
        """
        results = {}
        
        # Fetch Claude balance
        if "claude" in api_keys and api_keys["claude"].get("api_key"):
            results["claude"] = await ProviderBalanceService.get_anthropic_balance(
                api_keys["claude"]["api_key"]
            )
        
        # Fetch Adobe balance
        if "adobe" in api_keys:
            adobe_config = api_keys["adobe"]
            if adobe_config.get("client_id") and adobe_config.get("client_secret"):
                results["adobe"] = await ProviderBalanceService.get_adobe_balance(
                    adobe_config["client_id"],
                    adobe_config["client_secret"]
                )
        
        # Fetch Gemini info (with database session for usage tracking)
        if "gemini" in api_keys and api_keys["gemini"].get("api_key"):
            results["gemini"] = await ProviderBalanceService.get_gemini_info(
                api_keys["gemini"]["api_key"],
                db_session
            )
        
        return results
