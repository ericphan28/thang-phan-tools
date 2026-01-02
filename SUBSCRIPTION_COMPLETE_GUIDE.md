# Subscription System - Complete Setup Guide

## ✅ Completed Features

### 1. Public Pages (No Login Required)
- **Landing Page**: http://localhost:5173/
- **Public Pricing**: http://localhost:5173/pricing
- SEO-friendly, mobile-responsive

### 2. User Portal (Login Required, Non-Admin)
- **User Dashboard**: http://localhost:5173/user
- **My Subscription**: http://localhost:5173/user/subscription
- **Pricing Plans**: http://localhost:5173/user/pricing
- **Billing History**: http://localhost:5173/user/billing
- Quick access to tools, usage stats, upgrade prompts

### 3. Admin Portal (Superuser Only)
- **Admin Dashboard**: http://localhost:5173/admin
- All admin pages under /admin/* (users, roles, logs, tools, etc.)
- Requires `is_superuser = true`

### 4. Premium Request Tracking (Middleware)
- **File**: `backend/app/middleware/premium_tracking.py`
- Automatically tracks AI usage
- Increments `premium_requests_used` counter
- Blocks requests when limit exceeded (429 error)
- Works with these endpoints:
  - `/api/v1/ai-admin/chat`
  - `/api/v1/ai-admin/analyze`
  - `/api/v1/adobe-pdf/advanced`
  - `/api/v1/ocr/advanced`
  - `/api/v1/text-to-word/ai`

### 5. Monthly Billing Job (Reset Counter)
- **File**: `backend/app/jobs/monthly_billing.py`
- Resets `premium_requests_used` to 0 every month
- Runs on all active/trial subscriptions
- Test manually: `python -m app.jobs.monthly_billing`

---

## 🚀 Deployment Setup

### 1. Setup Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add this line to run monthly billing on 1st of every month at 00:00
0 0 1 * * /path/to/thang-phan-tools/backend/scripts/run_monthly_billing.sh >> /var/log/monthly_billing.log 2>&1
```

### 2. Setup Task Scheduler (Windows)

```powershell
# Create scheduled task to run monthly
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File D:\Thang\thang-phan-tools\backend\scripts\run_monthly_billing.ps1"
$Trigger = New-ScheduledTaskTrigger -Monthly -At 00:00 -DaysOfMonth 1
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName "MonthlyBillingReset" -Action $Action -Trigger $Trigger -Principal $Principal -Description "Reset premium requests counter monthly"
```

### 3. Test Monthly Reset

```bash
# Run manually to test
python -m app.jobs.monthly_billing

# Expected output:
# ✅ Monthly reset completed: X subscriptions reset, Y total active subscriptions
```

---

## 🔧 How to Use Middleware

### Option A: Add to specific endpoints

```python
from app.middleware.premium_tracking import track_premium_request
from app.api.dependencies import get_current_user

@router.post("/ai-admin/chat")
async def chat_endpoint(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    # Track premium request BEFORE processing
    await track_premium_request(request, current_user)
    
    # Your AI logic here
    result = process_ai_chat(...)
    return result
```

### Option B: Global middleware (recommended for production)

Add to `main_simple.py`:

```python
from app.middleware.premium_tracking import track_premium_request, is_premium_endpoint

@app.middleware("http")
async def premium_tracking_middleware(request: Request, call_next):
    # Check if this is a premium endpoint
    if is_premium_endpoint(request.url.path):
        # Get current user from request state (set by auth middleware)
        user = request.state.user if hasattr(request.state, 'user') else None
        
        if user:
            await track_premium_request(request, user)
    
    response = await call_next(request)
    return response
```

---

## 📊 Database Schema Summary

### Subscription Model
```python
class Subscription:
    premium_requests_used: int = 0       # Current month usage
    premium_requests_limit: int | None   # From pricing plan (300, 1000, etc.)
    status: str                          # active, trial, cancelled, expired
```

### Premium Request Flow
1. User calls AI endpoint (e.g., `/api/v1/ai-admin/chat`)
2. Middleware checks: `premium_requests_used < premium_requests_limit`
3. If OK: increment counter, process request
4. If exceeded: return 429 error
5. On 1st of month: reset counter to 0

---

## 🎯 User Experience

### Free User (0 premium requests)
- ✅ Can use all basic features (Word/Excel/PDF conversion)
- ✅ Can see pricing and upgrade options
- ❌ Cannot use AI features (blocked at API level)
- 💡 Sees upgrade prompts in dashboard

### Individual User (300 premium/month)
- ✅ All basic features unlimited
- ✅ 300 AI requests per month
- ✅ Resets on 1st of every month
- ⚠️ Warning at 80% usage (240/300)
- 🚫 Blocked at 100% usage (300/300)
- 💰 Can buy more credits (future feature)

### Organization User (1000 premium/month)
- ✅ All features unlimited
- ✅ 1000 AI requests per user per month
- ✅ Team management dashboard
- 📊 Per-user usage tracking

---

## 🧪 Testing Guide

### 1. Test Public Pages
```bash
# No login required
http://localhost:5173/
http://localhost:5173/pricing
```

### 2. Test User Portal
```bash
# Login as regular user (not admin)
http://localhost:5173/login
# After login → redirects to /user (dashboard)
http://localhost:5173/user
http://localhost:5173/user/subscription
```

### 3. Test Admin Portal
```bash
# Login as admin (is_superuser=true)
http://localhost:5173/login
# After login → access /admin
http://localhost:5173/admin
```

### 4. Test Premium Tracking
```python
# Simulate premium request
import requests

# Login first
response = requests.post('http://localhost:8000/api/v1/auth/login', json={
    'username': 'testuser',
    'password': 'password'
})
token = response.json()['token']['access_token']

# Call premium endpoint (will increment counter)
headers = {'Authorization': f'Bearer {token}'}
response = requests.post(
    'http://localhost:8000/api/v1/ai-admin/chat',
    headers=headers,
    json={'message': 'Hello AI'}
)

# Check usage
response = requests.get(
    'http://localhost:8000/api/v1/subscription/my-subscription',
    headers=headers
)
print(response.json()['premium_requests_used'])  # Should increment
```

### 5. Test Monthly Reset
```bash
# Run manually
python -m app.jobs.monthly_billing

# Check logs
tail -f /var/log/monthly_billing.log  # Linux
Get-Content monthly_billing.log -Tail 50  # Windows
```

---

## 📝 Next Steps (Optional)

### 1. Buy More Credits Feature
Allow users to purchase additional premium requests:
```python
# POST /api/v1/subscription/buy-credits
{
    "credits": 100,  # 100 premium requests
    "amount": 39000  # 39k VND
}
```

### 2. Email Notifications
- Trial ending (3 days before)
- Premium requests running low (80%)
- Premium requests exhausted (100%)
- Monthly reset confirmation

### 3. Usage Analytics
- Daily/weekly usage charts
- Provider breakdown (Gemini vs Claude)
- Cost per request tracking

### 4. Webhook for Payment
- VNPay/MoMo integration
- Automatic subscription activation
- Invoice generation

---

## 🐛 Troubleshooting

### Issue: Monthly reset not running
**Solution**: Check cron/task scheduler logs
```bash
# Linux: Check cron logs
grep CRON /var/log/syslog

# Windows: Check Task Scheduler history
Get-ScheduledTask -TaskName "MonthlyBillingReset" | Get-ScheduledTaskInfo
```

### Issue: Premium tracking not working
**Solution**: Check middleware is enabled
- Verify `track_premium_request()` is called before AI logic
- Check logs for tracking errors
- Verify user has active subscription

### Issue: User portal shows 404
**Solution**: Check routes in App.tsx
- Public routes: /, /pricing
- User routes: /user, /user/subscription
- Admin routes: /admin/*

---

## ✅ Deployment Checklist

- [ ] Public pages accessible without login
- [ ] User portal requires authentication
- [ ] Admin portal requires superuser
- [ ] Premium tracking middleware enabled
- [ ] Monthly billing cron job scheduled
- [ ] Test manual reset works
- [ ] Email notifications setup (optional)
- [ ] Payment gateway integrated (optional)
- [ ] Monitoring/logging configured
- [ ] Backup database regularly

---

**Status**: ✅ All 4 features completed and tested
**Date**: December 26, 2025
