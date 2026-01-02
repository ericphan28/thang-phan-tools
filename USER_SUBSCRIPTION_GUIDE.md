# 💳 USER SUBSCRIPTION & PRICING SYSTEM

Hệ thống tính phí cho user theo mô hình GitHub Copilot (Individual & Organization plans)

## 🎯 Tổng quan

Hệ thống cung cấp:
- **4 gói dịch vụ**: Free, Individual ($10/month), Organization ($19/user/month), Pay-as-you-go
- **Usage tracking**: Theo dõi chi tiết việc sử dụng AI (Gemini, Claude, Adobe)
- **Billing system**: Lịch sử hóa đơn, invoice tự động
- **Organization support**: Quản lý team, chia sẻ chi phí

## 📊 Pricing Plans

### 1️⃣ Free Plan
- **Giá**: $0/tháng
- **Giới hạn**: 100 requests/tháng, 10 requests/ngày
- **Tính năng**: Gemini Flash, OCR cơ bản
- **Phù hợp**: Dùng thử, học tập

### 2️⃣ Individual Plan (Giống GitHub Copilot Individual)
- **Giá**: $10/tháng (hoặc $100/năm)
- **Giới hạn**: 5,000 requests/tháng, 500 requests/ngày
- **AI Credits**: $20 included/tháng
- **Tính năng**:
  - Tất cả AI models (Gemini, Claude)
  - Adobe PDF Services
  - OCR tiếng Việt
  - Priority support
  - Usage analytics
  - API access
- **Trial**: 14 ngày miễn phí

### 3️⃣ Organization Plan (Giống GitHub Copilot Business)
- **Giá**: $19/user/tháng (hoặc $190/user/năm)
- **Giới hạn**: Unlimited requests
- **AI Credits**: $50/user/tháng included
- **Tính năng**:
  - Tất cả tính năng Individual
  - Team management
  - Organization dashboard
  - Usage analytics per user
  - Centralized billing
  - Custom integrations
  - SLA guarantee
- **Trial**: 30 ngày miễn phí

### 4️⃣ Pay-as-you-go
- **Giá**: $0 monthly fee, trả theo usage thực tế
- **Giới hạn**: 100 requests/ngày
- **Pricing**:
  - Gemini Flash: $0.075/1M input tokens, $0.30/1M output tokens
  - Claude Sonnet: $3.00/1M input tokens, $15.00/1M output tokens
  - Adobe PDF: $0.05/document
- **Minimum**: $5/tháng nếu có sử dụng

---

## 🗄️ Database Schema

### Tables Created

#### `organizations` - Tổ chức/Công ty
```sql
- id (PK)
- name (Tên organization)
- slug (URL-friendly name)
- description
- owner_id (FK to users)
- max_members (Số lượng thành viên tối đa)
- billing_email
- is_active
- created_at, updated_at
```

#### `organization_members` - Thành viên của organization
```sql
- id (PK)
- organization_id (FK)
- user_id (FK)
- role (owner, admin, member)
- is_active
- invited_at, joined_at
```

#### `pricing_plans` - Các gói dịch vụ
```sql
- id (PK)
- plan_type (free, individual, organization, pay_as_you_go)
- name, description
- monthly_price, annual_price
- monthly_requests_limit, daily_requests_limit
- monthly_spending_limit (AI credits)
- features (JSON)
- trial_days
- is_active, is_public
- created_at, updated_at
```

#### `subscriptions` - Đăng ký của user/organization
```sql
- id (PK)
- user_id (FK) hoặc organization_id (FK)
- plan_type, status (active, trial, cancelled, expired, suspended)
- monthly_price, monthly_limit_usd
- monthly_requests_limit, daily_requests_limit
- current_period_start, current_period_end
- trial_start, trial_end
- cancel_at_period_end, cancelled_at
- created_at, updated_at
```

#### `user_usage_records` - Chi tiết sử dụng AI
```sql
- id (PK)
- subscription_id (FK)
- user_id (FK - người thực hiện request)
- ai_usage_log_id (FK - link to AI usage log)
- provider (gemini, claude, adobe)
- operation, model
- input_tokens, output_tokens, total_tokens
- total_cost (USD)
- billing_month (YYYY-MM format)
- created_at
```

#### `billing_history` - Lịch sử hóa đơn
```sql
- id (PK)
- subscription_id (FK)
- billing_month (YYYY-MM)
- period_start, period_end
- total_requests, total_tokens
- gemini_cost, claude_cost, adobe_cost, total_cost
- subscription_fee
- total_amount (subscription_fee + total_cost)
- status (pending, paid, overdue)
- invoice_number, invoice_url
- paid_at
- created_at, updated_at
```

---

## 🚀 Setup Instructions

### 1. Initialize Database Tables

```bash
# Chạy migration script để tạo tables
cd backend
python scripts/init_pricing.py
```

Script sẽ:
- Tạo tất cả tables mới (organizations, subscriptions, pricing_plans, etc.)
- Insert 4 pricing plans mặc định
- Display summary của các plans

### 2. Update AIUsageLog (Optional)

Để track usage theo user, cần thêm `user_id` vào `ai_usage_logs`:

```python
# backend/app/models/models.py - AIUsageLog class
user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
```

### 3. Restart Backend Server

```bash
# Backend sẽ tự động load router mới
# Kiểm tra logs xem có lỗi không
```

### 4. Test API Endpoints

```bash
# Get pricing plans
curl http://localhost:8000/api/v1/subscription/pricing-plans

# Get my subscription
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/subscription/my-subscription

# Get usage summary
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/subscription/my-usage
```

---

## 📱 Frontend Pages

### 1. User Subscription Dashboard (`/subscription`)
- Overview của subscription hiện tại
- Usage summary (requests, tokens, costs)
- Budget tracking với progress bar
- Provider breakdown (Gemini, Claude, Adobe)
- Daily usage chart
- Top operations by cost

### 2. Pricing Plans (`/pricing`)
- Hiển thị 4 pricing plans
- So sánh features
- Monthly/Annual toggle
- Subscribe/Switch plan buttons
- Trial information

### 3. Billing History (`/billing`)
- List tất cả hóa đơn
- Filter by status
- Download invoice
- Payment status tracking

---

## 🔧 API Endpoints

### Pricing Plans
```
GET  /api/v1/subscription/pricing-plans
GET  /api/v1/subscription/pricing-plans/{plan_type}
```

### User Subscription
```
GET    /api/v1/subscription/my-subscription
POST   /api/v1/subscription/subscribe
PUT    /api/v1/subscription/my-subscription
DELETE /api/v1/subscription/my-subscription  # Cancel
```

### Usage Statistics
```
GET /api/v1/subscription/my-usage
GET /api/v1/subscription/my-usage/detailed?days=30
```

### Billing
```
GET /api/v1/subscription/my-billing?page=1&page_size=12
GET /api/v1/subscription/my-billing/{billing_id}
```

### Organizations
```
POST /api/v1/subscription/organizations
GET  /api/v1/subscription/organizations/my
GET  /api/v1/subscription/organizations/{org_id}
```

---

## 💡 Usage Tracking Flow

### Cách track AI usage cho billing:

1. **Khi user gọi AI API**:
   ```python
   # Trong AI service (Gemini, Claude, etc.)
   # Log usage to ai_usage_logs (already exists)
   usage_log = AIUsageLog(
       provider_key_id=key.id,
       user_id=current_user.id,  # <- Thêm user_id
       operation="ocr",
       model="gemini-2.5-flash",
       input_tokens=1000,
       output_tokens=500,
       total_cost=0.15
   )
   
   # Create user usage record for billing
   user_usage = UserUsageRecord(
       subscription_id=subscription.id,
       user_id=current_user.id,
       ai_usage_log_id=usage_log.id,
       provider="gemini",
       operation="ocr",
       model="gemini-2.5-flash",
       input_tokens=1000,
       output_tokens=500,
       total_tokens=1500,
       total_cost=0.15,
       billing_month=datetime.now().strftime("%Y-%m")
   )
   ```

2. **Monthly Billing Job** (Cron job):
   ```python
   # scripts/generate_monthly_billing.py
   # Chạy vào đầu mỗi tháng để tạo hóa đơn
   for subscription in active_subscriptions:
       # Aggregate usage from user_usage_records
       # Create billing_history record
       # Send invoice email
   ```

---

## 🎨 Frontend Components

### Key Features Implemented:

1. **Usage Visualization**:
   - Progress bars cho budget usage
   - Pie chart cho provider breakdown
   - Bar chart cho daily usage trend

2. **Real-time Updates**:
   - React Query auto-refetch
   - Optimistic updates
   - Toast notifications

3. **Responsive Design**:
   - Mobile-friendly cards
   - Collapsible sections
   - Adaptive layouts

---

## ⚠️ TODO - Next Steps

### Backend:
1. ✅ Create database models (DONE)
2. ✅ Create API endpoints (DONE)
3. ⏳ Add `user_id` to AIUsageLog
4. ⏳ Create usage tracking middleware
5. ⏳ Create monthly billing job
6. ⏳ Implement payment gateway (Stripe?)
7. ⏳ Create invoice PDF generator

### Frontend:
1. ✅ Create User Subscription page (DONE)
2. ✅ Create Pricing page (DONE)
3. ✅ Create Billing History page (DONE)
4. ⏳ Add Organization management page
5. ⏳ Add Team members page
6. ⏳ Add Payment method management

### Features:
1. ⏳ Email notifications (trial ending, over budget, invoice)
2. ⏳ Webhook for payment events
3. ⏳ Admin panel for managing subscriptions
4. ⏳ Organization invite system
5. ⏳ Usage alerts & limits enforcement

---

## 📝 Testing Checklist

- [ ] Create free subscription for new user
- [ ] Subscribe to Individual plan
- [ ] View usage statistics
- [ ] Check budget limits
- [ ] Switch plans
- [ ] Cancel subscription
- [ ] View billing history
- [ ] Create organization
- [ ] Add organization members
- [ ] Track organization usage

---

## 🔗 Integration Points

### With AI Admin:
- Sử dụng `AIUsageLog` existing để track usage
- Pricing dựa trên actual AI provider costs
- Admin có thể view all users usage

### With User Management:
- Each user automatically gets Free subscription
- Superusers can manage all subscriptions
- Activity logs track subscription changes

---

## 📚 References

- GitHub Copilot Pricing: https://github.com/features/copilot/plans
- Stripe Billing: https://stripe.com/docs/billing
- SaaS Pricing Best Practices: https://www.priceintelligently.com/

---

**Created**: December 26, 2025  
**Status**: ✅ Backend API Ready | ✅ Frontend Pages Ready | ⏳ Usage Tracking Pending  
**Next**: Implement usage tracking middleware & monthly billing job
