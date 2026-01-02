# Demo Users for Testing

All demo users have password: **demo123**

## How to Run

```powershell
# Create/update demo users
cd backend
$env:PYTHONPATH="D:\Thang\thang-phan-tools\backend"
python scripts/create_demo_users.py
```

## Test Accounts

### 1. 👑 Admin (Superuser)
- **Email**: `admin@example.com`
- **Password**: `demo123`
- **Access**: Full system access, all admin pages
- **Use case**: Test admin features, manage all subscriptions

---

### 2. 🆓 Free User (No Subscription)
- **Email**: `free@demo.com`
- **Password**: `demo123`
- **Subscription**: None
- **Access**: Basic tools only (Word/Excel/PDF, basic OCR)
- **Limits**: No premium AI requests
- **Use case**: Test free tier experience, upgrade flow

---

### 3. ✨ Basic User (Active)
- **Email**: `basic@demo.com`
- **Password**: `demo123`
- **Plan**: Cá nhân (99,000đ/month)
- **Status**: ACTIVE (started 5 days ago)
- **AI Usage**: 0/50 premium requests
- **Use case**: Test active subscription with no usage yet

---

### 4. ⏰ Basic Trial (Ending Soon)
- **Email**: `basic-trial@demo.com`
- **Password**: `demo123`
- **Plan**: Cá nhân (7-day trial)
- **Status**: TRIAL (25 days ago, expires in 2 days!)
- **AI Usage**: 12/50 premium requests
- **Use case**: Test trial ending warnings, conversion to paid

---

### 5. 🚀 Pro User (Active with Usage)
- **Email**: `pro@demo.com`
- **Password**: `demo123`
- **Plan**: Doanh nghiệp (299,000đ/month)
- **Status**: ACTIVE (started 15 days ago, mid-month)
- **AI Usage**: 87/200 premium requests (43% used)
- **Use case**: Test typical pro user experience, usage tracking

---

### 6. ⚠️ Pro Full (Quota Exceeded)
- **Email**: `pro-full@demo.com`
- **Password**: `demo123`
- **Plan**: Doanh nghiệp (299,000đ/month)
- **Status**: ACTIVE
- **AI Usage**: 200/200 premium requests (100% used!)
- **Use case**: Test quota exceeded warnings, blocking AI requests (HTTP 429)

---

### 7. ❌ Expired User
- **Email**: `expired@demo.com`
- **Password**: `demo123`
- **Plan**: Cá nhân (was 99,000đ/month)
- **Status**: EXPIRED (ended 5 days ago)
- **AI Usage**: 45/50 premium requests (from last period)
- **Use case**: Test expired subscription handling, renewal flow

---

## Testing Scenarios

### Public Pages (No Login Required)
1. Open http://localhost:5173
2. View landing page with features and pricing preview
3. Click "Xem bảng giá" → see full pricing page
4. Click "Đăng nhập" → login page

### User Portal (Regular Users)
1. Login as any non-admin user
2. View dashboard at `/user` with:
   - Current subscription status
   - AI usage progress bar
   - Total spending
   - Quick action buttons
3. Navigate to `/user/subscription` to see detailed subscription info
4. Navigate to `/user/pricing` to upgrade plan
5. Navigate to `/user/billing` for billing history

### Admin Pages (Superuser Only)
1. Login as `admin@example.com`
2. Access admin routes at `/admin/*`
3. Manage all users' subscriptions
4. View system-wide analytics

### Premium Request Tracking
1. Login as `pro@demo.com` (87/200 used)
2. Make AI requests (chat, analyze, etc.)
3. Watch counter increment automatically
4. Login as `pro-full@demo.com` (200/200 used)
5. Try making AI request → should get HTTP 429 error

### Trial Expiration
1. Login as `basic-trial@demo.com`
2. Should see trial expiring warning (2 days left)
3. Test upgrade flow to paid subscription

### Expired Subscription
1. Login as `expired@demo.com`
2. Should see "Subscription expired" message
3. Limited to basic features only
4. Test renewal/reactivation flow

---

## Quick Test Commands

```bash
# Test login with curl
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"pro@demo.com","password":"demo123"}'

# Check subscription status
curl http://localhost:8000/api/v1/subscriptions/my-subscription \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check AI usage
curl http://localhost:8000/api/v1/subscriptions/my-usage \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Notes

- All users are created/updated with password: `demo123`
- Users are created in remote database (165.99.59.47)
- Running script multiple times is safe - it updates existing users
- Subscriptions have realistic dates (trial ending, mid-month, expired)
- AI usage counters set to different levels for realistic testing
- Free user has NO subscription record (tests null handling)
- Script output shows detailed creation/update info

---

## Troubleshooting

**Can't login?**
- Check servers are running: Backend (8000), Frontend (5173)
- Verify database connection to 165.99.59.47
- Check `.env` file has correct DB credentials

**Subscription not showing?**
- Run script again to create subscriptions
- Check API response in browser DevTools
- Verify pricing plans exist in database

**Trial date wrong?**
- Script calculates dates relative to current time
- Trial set to expire in 2 days from script run date
- Re-run script to refresh dates

**Need different test data?**
- Edit `backend/scripts/create_demo_users.py`
- Modify `demo_users` array with desired data
- Change usage counters, dates, plans as needed
- Run script again to update

---

## Cleanup

To delete all demo users (keep admin):

```sql
-- Connect to database
DELETE FROM subscriptions WHERE user_id IN (
  SELECT id FROM users WHERE email LIKE '%@demo.com'
);

DELETE FROM users WHERE email LIKE '%@demo.com';
```
