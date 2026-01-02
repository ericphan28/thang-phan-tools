# 🏛️ Công cụ Hỗ trợ Xử lý Văn bản - Document AI Assistant

**FastAPI (8000) + React/TS (5173) + PostgreSQL + Redis + Gotenberg + Gemini AI**

**Phục vụ:** Cán bộ, chuyên viên các cơ quan Nhà nước Việt Nam  
**Mục đích:** Công cụ hỗ trợ xử lý văn bản (convert, OCR, extract, analyze, optimize)  
**Công nghệ:** AI OCR tiếng Việt, PDF processing, Text extraction, Data visualization

## � Business Model & Growth Strategy

**Target Users:** Vietnamese government officials (cán bộ nhà nước) who handle large volumes of documents daily

**Monetization Funnel:**
1. **Public Demo** (no login) → Hook users with 3 free AI requests
2. **Free Tier** (after signup) → 10 AI requests/month to build habit
3. **Pro Plan** (299k VNĐ/month) → Unlimited AI, target 10,000 users = 2.99B VNĐ/month revenue
4. **Enterprise** (custom pricing) → Government agency contracts with volume discounts

**Why Users Pay:**
- Traditional tools (Adobe, MS Office): Complex, expensive, no Vietnamese support
- Our tool: 1-click OCR, 98% Vietnamese accuracy, auto-format government documents
- Time savings: 2 hours/day → 40 hours/month saved = Worth 299k easily

**Key Metrics to Track:**
- Demo → Signup conversion rate (target: 30%)
- Free → Pro conversion rate (target: 10%)
- Monthly churn rate (target: <5%)
- Average revenue per user (ARPU)
- AI cost per request vs subscription price (maintain 80%+ margin)

**Growth Tactics:**
- Public demo with instant value (no signup friction)
- Upgrade prompts after successful demo OCR
- Usage-based notifications ("Bạn đã dùng 8/10 requests miễn phí")
- Testimonials from government officials

---

## �🏗️ Stack & Architecture

**Backend:** FastAPI + SQLAlchemy + Pydantic + JWT Auth + async/await  
**Frontend:** React 18 + TypeScript + Vite + Radix UI + Tailwind + react-hot-toast  
**Services:** PostgreSQL, Redis, Gotenberg (Office→PDF), Gemini AI (10+ models), Tesseract OCR

**Core Features (AI-First Approach):**
- **AI OCR:** Gemini 2.0 Flash Vision (98% accuracy, context-aware Vietnamese)
- **AI Writing:** Formal style optimization, grammar check (Gemini 2.5 Flash <2s)
- **AI Analysis:** Data conflict detection, semantic extraction (Gemini 2.5 Pro)
- **AI Generation:** Auto-report writing, chart creation from data
- **Legacy Convert:** Word↔PDF, Excel↔PDF via Gotenberg (fallback only)
- **Edit:** Merge, Split, Rotate, Compress, Watermark, Protect/Unlock

**Why AI-First:**
- Traditional tools (Tesseract, PyPDF): 70-80% accuracy, no context
- Gemini AI: 98% accuracy, understands Vietnamese semantics, self-improving
- ROI: Save 97% time, 81% profit margin on AI API costs

**Key Pattern - Smart DB Detection** (`backend/app/core/config.py`):
```python
is_docker = os.path.exists('/.dockerenv')
db_host = "postgres" if is_docker else "165.99.59.47"  # Zero-config deployment
```

## 🚀 Development Workflow

**CRITICAL: Use VS Code tasks - NEVER manual commands**
- `Ctrl+Shift+P` → "Run Task" → "Start All Servers" (sets PYTHONPATH, cwd, manages lifecycle)
- Backend: `backend/app/main_simple.py` (FastAPI entry)
- Frontend: Auto-reloads on change

**Structure:**
```
backend/app/
  api/v1/endpoints/   # auth, users, documents, ai_admin
  routers/            # mau_2c (Vietnamese forms)
  services/           # document_service (5360 lines), gemini_service, ocr_service
  models/             # SQLAlchemy (User, Role, AIUsageLog)
  schemas/            # Pydantic validation
frontend/src/
  pages/              # Mau2CPage, OCRDemoPage, AIAdminDashboardPage
  components/ui/      # Radix UI wrappers
  services/api.ts     # Axios + JWT interceptor
```

## 📐 Critical Patterns

**1. File Upload Lifecycle** - Always cleanup in `finally`:
```python
temp_path = None
try:
    temp_path = await save_upload_file(upload_file)
    output = await document_service.convert(temp_path)
    return FileResponse(output)
finally:
    if temp_path and temp_path.exists(): temp_path.unlink()
```

**2. AI Service Auto-Logging** - NEVER call APIs directly:
```python
# ✅ CORRECT - Auto-logs tokens, cost, time
from app.services.gemini_service import GeminiService
gemini = GeminiService(db, user_id=current_user.id)
response = gemini.generate_content(prompt, model="gemini-2.5-flash")
```

**3. Vietnamese Error Messages** - User-friendly, not technical:
```python
raise HTTPException(400, "File quá lớn. Giới hạn 10MB.")
# NOT: "Request entity too large"
```

**4. Database Sessions** - Use `Depends(get_db)` dependency

**5. Frontend API** - Use `services/api.ts` (auto JWT + 401 redirect):
```typescript
import api from '../services/api';
const response = await api.post('/api/v1/documents/convert', formData);
```

---

## 💳 Subscription & Quota System (CRITICAL)

**Dual-System Architecture** - Must understand both:

### 1. Legacy User Fields (backward compatibility)
```python
# models/auth_models.py - User model
subscription_tier: str = "FREE"  # FREE/PRO/TEAM/ENTERPRISE
ai_quota_monthly: int = 3        # Số request AI/tháng
ai_usage_this_month: int = 0     # Đã dùng bao nhiêu
```

### 2. New Subscription System (authoritative)
```python
# models/subscription.py
class Subscription:
    plan_type: PlanType              # FREE/INDIVIDUAL/ORGANIZATION/PAY_AS_YOU_GO
    status: SubscriptionStatus       # ACTIVE/TRIAL/CANCELLED/EXPIRED
    monthly_price: float             # Giá gói (VNĐ hoặc USD)
    monthly_limit_usd: float         # Giới hạn chi tiêu
    premium_requests_limit: int      # Số request AI cho phép
    premium_requests_used: int       # Đã dùng bao nhiêu
    current_period_start: datetime
    current_period_end: datetime     # NULL = không hết hạn
```

### QuotaService Logic (services/quota_service.py)
```python
# CRITICAL: Luôn check subscriptions table trước, sau đó mirror sang User fields
@staticmethod
def check_quota(db: Session, user_id: int) -> QuotaStatus:
    # 1. Tìm active subscription trong subscriptions table
    subscription = QuotaService._get_active_subscription(db, user_id)
    
    if subscription:
        # 2. Map subscription → tier (PRO, TEAM, etc.)
        tier = QuotaService._subscription_to_tier(subscription)
        
        # 3. Mirror sang User fields (legacy support)
        user = db.query(User).filter(User.id == user_id).first()
        user.subscription_tier = tier
        user.ai_quota_monthly = subscription.premium_requests_limit
        db.commit()
        
        # 4. Return quota từ subscription
        return QuotaStatus(
            has_quota=(subscription.premium_requests_used < subscription.premium_requests_limit),
            tier=tier,
            used=subscription.premium_requests_used,
            limit=subscription.premium_requests_limit
        )
    else:
        # Fallback to User fields nếu không có subscription
        return check_user_legacy_quota(db, user_id)
```

### Common Quota Issues & Fixes

**Problem 1: User có subscription nhưng bị 403 "hết quota"**
```bash
# Symptom: subscriptions table có plan ACTIVE, nhưng User.subscription_tier = FREE
# Root cause: User fields không sync với subscriptions table
# Fix: Run sync script
cd backend
python scripts/sync_user_quota.py --all
# Or for single user:
python scripts/sync_user_quota.py dcthoan
```

**Problem 2: Subscription period_end = NULL**
```python
# CRITICAL: NULL current_period_end = ACTIVE (không hết hạn), NOT expired
# QuotaService logic:
if subscription.current_period_end is None:
    return True  # Active forever
elif subscription.current_period_end > datetime.now():
    return True  # Still in period
else:
    return False  # Expired
```

**Problem 3: Schema validation error - missing fields**
```python
# Error: ResponseValidationError: Field required: monthly_requests_limit
# Cause: Schema expects field X but model has field Y
# Fix: Update schema to match model OR add migration
# Example (Dec 2025 fix):
class SubscriptionResponse(BaseModel):
    # WRONG: monthly_requests_limit, daily_requests_limit (không tồn tại)
    # RIGHT: premium_requests_limit, premium_requests_used (model fields)
    premium_requests_limit: Optional[int] = None
    premium_requests_used: Optional[int] = None
```

### Database Schema Overview
```sql
-- Core tables
users (id, email, subscription_tier, ai_quota_monthly, ai_usage_this_month)
subscriptions (id, user_id, plan_type, status, premium_requests_limit, current_period_end)
pricing_plans (plan_type, monthly_price, premium_requests_limit)
user_usage_records (subscription_id, user_id, provider, total_cost, billing_month)

-- Relationships
User 1:1 Subscription (via user_id)
Subscription 1:N UserUsageRecord (via subscription_id)
```

---

## 🔧 SQLAlchemy 2.x Common Issues

**Problem: `TypeError: Function.__init__() got an unexpected keyword argument 'else_'`**
```python
# ❌ WRONG (SQLAlchemy 1.x syntax)
from sqlalchemy import func
func.case((condition, value), else_=default)

# ✅ CORRECT (SQLAlchemy 2.x)
from sqlalchemy import case
case((condition, value), else_=default)

# Real example from subscription.py:
usage = db.query(
    func.sum(
        case(
            (UserUsageRecord.provider == 'gemini', UserUsageRecord.total_cost),
            else_=0
        )
    ).label('gemini_cost')
)
```

**Problem: Stale cache after code changes**
```bash
# Symptom: Code changed but backend still runs old code
# Fix 1: Clear __pycache__
Get-ChildItem -Path backend -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

# Fix 2: Kill all Python processes
Get-Process python | Stop-Process -Force

# Fix 3: Start WITHOUT --reload flag (reload unreliable on Windows)
python -m uvicorn app.main_simple:app --host 0.0.0.0 --port 8000
```

---

## 🔌 Integrations

**Gemini AI** (Primary - AI-First Strategy) → `.env`: `GEMINI_API_KEY`
- **2.0 Flash**: Multimodal vision OCR, 98% Vietnamese accuracy, $0.10/doc
- **2.5 Flash**: Real-time writing coach <2s response, $0.02/doc
- **2.5 Pro**: Advanced reasoning, data analysis, $0.50/doc
- **Use cases:** OCR scan→Word, formal writing optimization, conflict detection, report generation

**Traditional Fallbacks** (Legacy support only):
- **Tesseract OCR**: 70% accuracy, slow (25s/page), no context → Use only if Gemini fails
- **Gotenberg**: Office→PDF at `http://gotenberg:3000` (Docker) → Use for simple conversions
- **Adobe PDF**: Premium OCR (no Vietnamese) → Deprecated in favor of Gemini

**Mẫu 2C Forms**: `routers/mau_2c.py` → POST `/api/mau-2c/generate` → .docx (python-docx)

**Business Model:**
- Free tier: 10 AI requests/month (hook users)
- Pro: 299k VNĐ/month unlimited (target 10k users = 2.99B VNĐ/month)
- Enterprise: Custom pricing for government agencies

---

## 🐳 Deployment

**GitHub Actions**: `.github/workflows/backend-image-ghcr.yml` → Push to `main` → Builds `ghcr.io/.../thang-phan-tools-backend:latest`  
**VPS**: `docker-compose -f docker-compose.prod.yml pull && up -d`  
**DB Migration**: `init_db()` auto-creates tables (SQLAlchemy models)

## 🛠️ Common Tasks

**New Endpoint**: `api/v1/endpoints/<feature>.py` + schema + service → register in `main_simple.py`  
**New Page**: `pages/<Page>.tsx` → add route in `App.tsx`  
**Debug**: Backend (task terminal), Frontend (browser console), DB (`165.99.59.47:5432` dev / `postgres:5432` prod)

---

## ⚠️ Common Pitfalls

**Backend:**
- ❌ Direct AI calls → ✅ Use `GeminiService(db, user_id)` wrapper
- ❌ No cleanup → ✅ `finally: temp_path.unlink()`
- ❌ Technical errors → ✅ Vietnamese messages with emoji
- ❌ Hardcoded DB host → ✅ Smart Docker detection
- ❌ Manual python commands → ✅ VS Code tasks only

**Frontend:**
- ❌ Direct fetch → ✅ Use `api.ts` (auto JWT)
- ❌ No loading states → ✅ Show `<Skeleton />` + error states
- ❌ Generic toasts → ✅ `toast.error('Không thể tải file lên. Vui lòng thử lại.')`
- ❌ Fixed widths → ✅ Responsive classes (`w-full md:w-1/2`)

---

## 🎯 Model Selection (Gemini)

| Model | Quality | Speed | Cost/1M | Use Case |
|-------|---------|-------|---------|----------|
| `gemini-2.5-flash` | 9/10 | 9/10 | $0.30/$2.50 | ⭐ Default production |
| `gemini-2.5-flash-lite` | 8/10 | 10/10 | $0.10/$0.40 | 💰 High volume |
| `gemini-2.5-pro` | 10/10 | 7/10 | $1.25/$10.00 | 🎯 Complex docs |

**Decision:** Vietnamese PDF? → Gemini (Adobe doesn't support). Scanned? → Enable OCR.

---

## 🌍 Vietnamese Localization

**System Language:** 100% Vietnamese for government officials (cán bộ nhà nước)
- Error messages: `get_friendly_error_message()` in `document_service.py`
- Toasts: `toast.success('✅ Đã upload 3 tài liệu')`
- Forms: `<Input label="Họ và tên *" placeholder="Nguyễn Văn A" />`
- Encoding: UTF-8 everywhere (see `main_simple.py` lines 3-7 for Windows fix)

**User Roles:**
- **Admin**: Full system access, manage users, view AI usage analytics
- **User**: Access document processing tools, AI features (quota-based)
- **Free**: Limited features, upgrade prompts

**Common Use Cases (Vietnamese Government Officials):**
- Convert Word báo cáo → PDF for official distribution
- OCR scanned công văn → Extract text → Edit in Word
- Extract tables from PDF reports → Excel for analysis
- Generate Mẫu 2C (personnel form) from JSON data
- Optimize writing style for formal government documents
- Create charts from statistical tables in reports
- Merge multiple PDF documents into single file
- Add watermarks/passwords to confidential documents

---

# 🎨 UI/UX GUIDELINES (CRITICAL)

## 📱 Responsive Design - ALWAYS REQUIRED

### Mobile-First Approach
```tsx
// ✅ CORRECT - Always use responsive classes
<div className="flex flex-col md:flex-row gap-4">
  <div className="w-full md:w-1/2">...</div>
</div>

// ✅ CORRECT - Responsive text sizes
<h1 className="text-2xl md:text-3xl lg:text-4xl font-bold">

// ✅ CORRECT - Responsive padding/margin
<section className="p-4 md:p-6 lg:p-8">

// ❌ WRONG - Fixed widths without responsive
<div className="w-[800px]">...</div>

// ❌ WRONG - Only one breakpoint
<div className="grid grid-cols-3">...</div>
```

### Breakpoint Strategy
```tsx
// Use Tailwind breakpoints consistently:
// sm: 640px   - Mobile landscape
// md: 768px   - Tablet
// lg: 1024px  - Desktop
// xl: 1280px  - Large desktop
// 2xl: 1536px - Extra large

// Example pattern for all layouts:
<div className="
  grid 
  grid-cols-1 
  sm:grid-cols-2 
  lg:grid-cols-3 
  xl:grid-cols-4 
  gap-4 
  md:gap-6
">
```

### Container & Max Width
```tsx
// ✅ ALWAYS use container with max-width
<div className="container mx-auto px-4 max-w-7xl">
  {/* Content */}
</div>

// For full-width sections with constrained content:
<section className="w-full bg-gray-50">
  <div className="container mx-auto px-4 max-w-6xl py-8">
    {/* Content */}
  </div>
</section>
```

### Touch-Friendly Targets (Mobile)
```tsx
// ✅ Minimum tap target: 44x44px (iOS) / 48x48dp (Android)
<Button 
  size="lg"  // At least 'default' size, prefer 'lg' for primary actions
  className="min-h-[44px] min-w-[44px]"
>

// ✅ Adequate spacing between interactive elements
<div className="flex gap-3">  {/* Minimum 12px gap */}
  <Button>Action 1</Button>
  <Button>Action 2</Button>
</div>
```

## 💬 Toast Notifications (react-hot-toast)

```tsx
// ✅ SUCCESS - Clear, actionable
toast.success('✅ Đã upload 3 tài liệu');

// ✅ ERROR - Helpful, not technical  
toast.error('Không thể tải file lên. Vui lòng thử lại.');

// ✅ LOADING - Shows progress
const loadingId = toast.loading('Đang xử lý văn bản...');
toast.success('Hoàn thành!', { id: loadingId });

// ❌ WRONG - Technical/generic
toast.error('Error 500'); toast.success('OK');
```

## 🎯 Common UI Patterns

**Loading States:**
```tsx
{isLoading ? <Skeleton className="h-12 w-full" /> : <DataTable data={data} />}
```

**Error States:**
```tsx
{error && (
  <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
    <h3>Không thể tải dữ liệu</h3>
    <Button onClick={refetch}>Thử lại</Button>
  </div>
)}
```

**Empty States:**
```tsx
{items.length === 0 && (
  <div className="text-center py-12">
    <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
    <h3>Chưa có dự án nào</h3>
    <Button onClick={createProject}>Tạo dự án mới</Button>
  </div>
)}
```

**Form Validation:**
```tsx
<Input
  className={errors.name ? 'border-red-500' : ''}
/>
{errors.name && <p className="text-sm text-red-600">{errors.name}</p>}
```

**Modal/Dialog:**
```tsx
<DialogContent className="max-w-[95vw] sm:max-w-[500px] max-h-[90vh] overflow-y-auto">
```

---

## ✅ CHECKLIST - Before Committing UI Code

- [ ] Works on mobile (320px - 768px)
- [ ] Works on tablet (768px - 1024px)
- [ ] Works on desktop (1024px+)
- [ ] All buttons have adequate size (min 44x44px)
- [ ] Touch targets have proper spacing (min 12px gap)
- [ ] Forms have clear validation messages
- [ ] Loading states are shown during async operations
- [ ] Error states are user-friendly with retry options
- [ ] Empty states provide guidance and actions
- [ ] Toast messages are clear and actionable
- [ ] Modals/dialogs work on small screens
- [ ] Text is readable (proper contrast, size, line-height)
- [ ] Images/icons are not stretched or pixelated
- [ ] Horizontal scroll is avoided
- [ ] Focus states are visible for keyboard navigation

---

## 🚀 Performance & Optimization

### Backend Performance

**File Processing:**
```python
# ✅ Use async operations for I/O
async with aiofiles.open(file_path, 'rb') as f:
    content = await f.read()

# ✅ Stream large files instead of loading into memory
return StreamingResponse(
    file_stream_generator(file_path),
    media_type="application/pdf"
)

# ✅ Use httpx.AsyncClient for external APIs
async with httpx.AsyncClient(timeout=60.0) as client:
    response = await client.post(url, files=files)
```

**Database Queries:**
```python
# ✅ Use database indexes (see models)
class AIUsageLog(Base):
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    provider = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)

# ✅ Limit query results
db.query(APILog).order_by(desc(APILog.created_at)).limit(100).all()

# ❌ AVOID - Loading all records
db.query(APILog).all()  # Could be millions of rows!
```

**Caching Strategy:**
```python
# Redis cache for expensive operations
# Example in ai_usage_service.py:
cache_key = f"usage:summary:{user_id}:{date}"
cached = redis_client.get(cache_key)
if cached:
    return json.loads(cached)
# ... compute result ...
redis_client.setex(cache_key, 3600, json.dumps(result))
```

### Frontend Performance

```typescript
// ✅ Lazy load heavy components
const DocumentEditor = lazy(() => import('./DocumentEditor'));
const AIAdminDashboard = lazy(() => import('./AIAdminDashboardPage'));

// ✅ Memoize expensive computations
const processedData = useMemo(() => {
  return heavyComputation(data);
}, [data]);

// ✅ Debounce search inputs
const [searchTerm, setSearchTerm] = useState('');
const debouncedSearch = useDebounce(searchTerm, 500);

useEffect(() => {
  if (debouncedSearch) {
    performSearch(debouncedSearch);
  }
}, [debouncedSearch]);

// ✅ Use React.memo for expensive renders
export const ExpensiveComponent = React.memo(({ data }) => {
  return <ComplexVisualization data={data} />;
});
```

---

## 🔧 Environment Setup

### Backend `.env` (Required)
```bash
# Database
DB_USER=utility_user
DB_PASSWORD=your_secure_password
DB_NAME=utility_db
DB_PORT=5432

# Security
SECRET_KEY=your-secret-key-change-this
JWT_SECRET_KEY=jwt-secret-key-change-this

# Redis
REDIS_PASSWORD=your_redis_password

# AI (Optional)
GEMINI_API_KEY=your_key  # Recommended for Vietnamese
PDF_SERVICES_CLIENT_ID=your_id  # Adobe premium
USE_ADOBE_PDF_API=false
```

### Frontend `.env`
```bash
VITE_API_URL=http://localhost:8000
```

---

## 🐛 Troubleshooting

### Backend Issues

**`ModuleNotFoundError: 'app'`**
```bash
# Cause: PYTHONPATH not set
# Fix: Use VS Code tasks (auto-sets PYTHONPATH)
Ctrl+Shift+P → Run Task → Backend Server
```

**`Database connection failed`**
```bash
# Dev: Check remote DB at 165.99.59.47:5432
Test-NetConnection -ComputerName 165.99.59.47 -Port 5432

# Docker: Check postgres container
docker ps | grep postgres
docker-compose up -d postgres
```

**`403 Quota exceeded` but user has paid plan**
```bash
# Check dual system sync
python scripts/check_quota_users.py dcthoan
# Output: subscription (PRO, 1000) vs user fields (FREE, 3)

# Fix: Sync subscription → user fields
python scripts/sync_user_quota.py dcthoan
# Or bulk sync all paid users:
python scripts/sync_user_quota.py --all
```

**`Server starts then immediately crashes`**
```bash
# Check if port 8000 is occupied
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

# Kill port 8000 processes
Get-NetTCPConnection -LocalPort 8000 | 
  Select-Object -ExpandProperty OwningProcess | 
  ForEach-Object { Stop-Process -Id $_ -Force }

# Check for import errors
cd backend
$env:PYTHONPATH="$PWD"
python -c "from app.main_simple import app; print('✅ OK')"
```

**`Gotenberg conversion failed`**
```bash
# Check Gotenberg service (Docker)
curl http://localhost:3000/health

# Fallback: Use local LibreOffice (dev only)
# System uses Gotenberg in prod, LibreOffice in dev fallback
```

**`SQLAlchemy validation error: Field required`**
```python
# Symptom: ResponseValidationError with missing fields
# Cause: Pydantic schema doesn't match SQLAlchemy model
# Fix: Update schema in backend/app/schemas/*.py

# Example: SubscriptionResponse expected monthly_requests_limit
# but model has premium_requests_limit
# Solution: Change schema to match model fields
```

### Frontend Issues

**`401 Unauthorized` on all requests**
```typescript
// Check token in browser console
localStorage.getItem('access_token')

// If null or expired → re-login
// Frontend automatically redirects on 401 (api.ts interceptor)
```

**`Network Error` - Cannot reach backend**
```bash
# Check backend is running on port 8000
curl http://localhost:8000/health

# Check VITE_API_URL in frontend/.env
VITE_API_URL=http://localhost:8000
```

**`FormData not sent correctly (403 or 400)`**
```typescript
// ❌ WRONG - Manual Content-Type breaks FormData
const formData = new FormData();
formData.append('file', file);
api.post('/endpoint', formData, {
  headers: { 'Content-Type': 'multipart/form-data' } // Don't do this!
});

// ✅ CORRECT - Let browser set Content-Type with boundary
const formData = new FormData();
formData.append('file', file);
api.post('/endpoint', formData);  // No headers needed
// api.ts interceptor auto-removes Content-Type for FormData
```

**`Styles not applying`**
```bash
# Tailwind not watching files
cd frontend
npm run dev  # Starts Vite + Tailwind watch mode

# Hard refresh browser: Ctrl+Shift+R
```

### Database Query Issues

**Check user's subscription status**
```sql
-- Connect to DB: 165.99.59.47:5432 / utility_db / utility_user
SELECT 
  u.email,
  u.subscription_tier AS user_tier,
  u.ai_quota_monthly AS user_quota,
  u.ai_usage_this_month AS user_used,
  s.plan_type AS sub_plan,
  s.status AS sub_status,
  s.premium_requests_limit AS sub_limit,
  s.premium_requests_used AS sub_used,
  s.current_period_end
FROM users u
LEFT JOIN subscriptions s ON u.id = s.user_id
WHERE u.email = 'dcthoan@example.com';

-- Red flags:
-- 1. sub_plan = ORGANIZATION but user_tier = FREE → Need sync
-- 2. sub_status = ACTIVE but current_period_end < NOW() → Expired
-- 3. sub_used >= sub_limit → Quota exhausted
```

**Reset user quota for testing**
```sql
-- Reset usage counters (BE CAREFUL - production data!)
UPDATE subscriptions 
SET premium_requests_used = 0
WHERE user_id = (SELECT id FROM users WHERE email = 'test@example.com');

UPDATE users
SET ai_usage_this_month = 0
WHERE email = 'test@example.com';
```

---

## 📚 Key Files

**Backend:** `main_simple.py` (FastAPI entry), `config.py` (smart DB), `document_service.py` (5360 lines), `gemini_service.py` (auto-log), `mau_2c.py` (forms)  
**Frontend:** `App.tsx` (routes), `api.ts` (JWT client), `AuthContext.tsx` (auth state), `components/ui/*` (Radix wrappers)  
**Config:** `docker-compose.yml`, `.github/workflows/backend-image-ghcr.yml`

---

## 💡 Best Practices Summary

### DO ✅
- Always use VS Code tasks to start servers
- Use wrapper services (GeminiService) for AI calls
- Cleanup temp files in `finally` blocks
- Write Vietnamese error messages with emojis
- Use responsive Tailwind classes for all UI
- Auto-redirect to `/login` on 401 errors
- Log all AI usage to database
- Test on mobile (320px) before committing UI

### DON'T ❌
- Never call AI APIs directly without logging
- Don't hardcode database hosts (use smart detection)
- Don't use manual commands (python, npm) - use tasks
- Don't show technical errors to users
- Don't forget to add JWT token to API calls
- Don't create fixed-width layouts without responsive
- Don't batch cleanup - always cleanup immediately in finally
- Don't use generic toast messages

---

## ⚠️ Known Issues & In-Progress Fixes (Dec 30, 2025)

**Issue 1: Backend crashes immediately after start**
- **Symptom:** Uvicorn starts then "Shutting down" right away
- **Status:** Investigating (likely database connection or import error)
- **Workaround:** Check logs, verify DB connectivity, clear `__pycache__`

**Issue 2: Frontend FormData showing wrong Content-Type**
- **Symptom:** Browser dev tools show `Content-Type: application/x-www-form-urlencoded` and `data: {}`
- **Expected:** `Content-Type: multipart/form-data; boundary=...`
- **Status:** Frontend code looks correct (api.ts removes Content-Type for FormData)
- **Action:** Need to test end-to-end after backend stabilizes

**Issue 3: Subscription schema mismatch (FIXED)**
- **Was:** `SubscriptionResponse` expected `monthly_requests_limit`, `daily_requests_limit`
- **Model has:** `premium_requests_limit`, `premium_requests_used`
- **Fix applied:** Updated schema to match model fields
- **Date:** Dec 30, 2025

**Issue 4: SQLAlchemy func.case syntax error (FIXED)**
- **Was:** `func.case()` syntax from SQLAlchemy 1.x
- **Should be:** Import `case` directly, not as `func.case`
- **Fix applied:** Changed `from sqlalchemy import func` to `from sqlalchemy import func, case`
- **Date:** Dec 30, 2025

---

**Last Updated:** December 30, 2025  
**Version:** 2.2.0  
**Major Updates:**
- Added comprehensive Subscription/Quota System documentation (dual-system architecture)
- SQLAlchemy 2.x migration notes (func.case → case)
- Troubleshooting guide expansion (backend crashes, FormData issues, DB queries)
- Schema validation error resolution patterns

**For questions:** Check README.md or existing code patterns
