# 📚 CONTEXT FOR NEW CHAT SESSION

## 🎯 Mục đích file này
File này chứa TẤT CẢ thông tin cần thiết để AI hiểu TOÀN BỘ project trong chat session mới.
Khi bắt đầu chat mới, chỉ cần attach file này và AI sẽ có đầy đủ context.

---

## 📊 PROJECT SUMMARY

**Project Name**: Utility Server  
**Type**: Full-stack web application  
**Tech Stack**: FastAPI (Backend) + React/TypeScript (Frontend) + PostgreSQL + Redis + Nginx + Docker  
**Deployment**: Production on VPS 165.99.59.47  
**Status**: ✅ DEPLOYED & WORKING  

---

## 🏗️ ARCHITECTURE

```
Internet → Nginx (Port 80/443) → FastAPI Backend (Port 8000) → PostgreSQL + Redis
                  ↓
            React Frontend (SPA)
```

**Key Points**:
- Nginx reverse proxy: `/api/*` → `backend:8000`
- Frontend: Vite build, served as static files
- Auth: JWT tokens, 7 days expiry
- Database: PostgreSQL 15 with 9 tables
- Containerized: 5 Docker containers

---

## 🌐 PRODUCTION INFO

**Server**:
- IP: `165.99.59.47`
- URL: `http://165.99.59.47`
- OS: Ubuntu 22.04
- Hostname: giakiemso

**Credentials**:
- Admin: `admin` / `admin123`
- Database: `utility_db` / `utility_user`

**Docker Containers**:
- `utility_nginx` - Nginx
- `utility_backend` - FastAPI
- `utility_postgres` - PostgreSQL
- `utility_redis` - Redis
- `utility_gotenberg` - Document conversion

---

## 📁 PROJECT STRUCTURE

```
utility-server/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry
│   │   ├── core/
│   │   │   ├── config.py        # Settings
│   │   │   ├── database.py      # SQLAlchemy
│   │   │   └── security.py      # JWT, bcrypt
│   │   ├── models/
│   │   │   ├── auth_models.py   # User, Role, Permission, ActivityLog
│   │   │   └── models.py        # APIKey, Face, ProcessedFile
│   │   ├── api/v1/endpoints/
│   │   │   ├── auth.py          # /api/auth/*
│   │   │   ├── users.py         # /api/users/*
│   │   │   ├── roles.py         # /api/roles/*
│   │   │   ├── activity_logs.py # /api/logs/*
│   │   │   ├── documents.py     # /api/documents/*
│   │   │   ├── images.py        # /api/images/*
│   │   │   └── ocr.py           # /api/ocr/*
│   │   └── services/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Routes
│   │   ├── config.ts            # API_BASE_URL = '/api'
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Layout.tsx   # Main layout
│   │   │   │   └── Sidebar.tsx  # Responsive sidebar
│   │   │   ├── ui/              # Shadcn components
│   │   │   └── modals/
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── UsersPage.tsx    # Responsive table/cards
│   │   │   ├── RolesPage.tsx
│   │   │   ├── ActivityLogsPage.tsx
│   │   │   └── ToolsPage.tsx
│   │   ├── services/
│   │   │   ├── api.ts           # Axios with interceptors
│   │   │   └── index.ts         # Service functions
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx  # Auth state
│   │   └── types/
│   ├── package.json
│   └── vite.config.ts
│
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
└── .env
```

---

## 🔌 API ENDPOINTS

### Auth (`/api/auth`)
- `POST /login` - Login (returns JWT)
- `POST /register` - Register
- `GET /me` - Current user
- `POST /logout` - Logout
- `POST /change-password` - Change password

### Users (`/api/users`)
- `GET /` - List users (pagination, search)
- `POST /` - Create user
- `GET /{id}` - Get user
- `PUT /{id}` - Update user
- `DELETE /{id}` - Delete user
- `GET /stats` - User stats
- `PUT /{id}/toggle-active` - Toggle active status

### Roles (`/api/roles`)
- `GET /` - List roles
- `POST /` - Create role
- `GET /{id}` - Get role with permissions
- `PUT /{id}` - Update role
- `DELETE /{id}` - Delete role

### Activity Logs (`/api/logs`)
- `GET /` - List logs (filter, pagination)
- `GET /stats` - Activity stats

---

## 🗄️ DATABASE SCHEMA

**9 Tables**:
1. `users` - User accounts
2. `roles` - Role definitions (admin, editor, viewer)
3. `permissions` - Fine-grained permissions
4. `user_roles` - Many-to-many user↔role
5. `activity_logs` - Audit trail (all actions logged)
6. `api_keys` - API keys for programmatic access
7. `api_logs` - API usage logs
8. `faces` - Face recognition data
9. `processed_files` - File processing tracking

**Key Relationships**:
- User ↔ Role (many-to-many via user_roles)
- Role → Permissions (one-to-many)
- User → ActivityLog (one-to-many)
- User → APIKey (one-to-many)

---

## 🔐 AUTHENTICATION FLOW

1. User sends `{username, password}` to `/api/auth/login`
2. Backend verifies → generates JWT token (expires 7 days)
3. Frontend stores token in `localStorage`
4. All subsequent API calls include `Authorization: Bearer {token}`
5. If 401 → auto logout → redirect to login

**Important**: 
- Token in `localStorage.getItem('access_token')`
- User info in `localStorage.getItem('user')`
- Axios interceptor auto-adds token to headers

---

## 🎨 FRONTEND KEY FEATURES

**Tech**:
- React 18 + TypeScript
- Vite build tool
- TanStack Query (data fetching)
- Tailwind CSS
- Shadcn/ui components
- Lucide icons

**Responsive Design**:
- Mobile: Hamburger menu, collapsible sidebar
- Tablet: 2-column grid
- Desktop: Fixed sidebar, 4-column grid

**Config**:
```typescript
// config.ts
export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';
```

**Build Command**:
```powershell
$env:VITE_API_URL="/api"
npm run build
```

---

## 🚀 DEPLOYMENT PROCESS

### Backend Deploy
```powershell
scp -r backend/app root@165.99.59.47:/opt/utility-server/backend/
ssh root@165.99.59.47 "docker restart utility_backend"
```

### Frontend Deploy
```powershell
cd frontend
$env:VITE_API_URL="/api"
npm run build
ssh root@165.99.59.47 "rm -rf /opt/utility-server/frontend/dist/*"
scp -r dist/* root@165.99.59.47:/opt/utility-server/frontend/dist/
$jsFile = (Get-ChildItem dist/assets/*.js).Name
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
ssh root@165.99.59.47 "sed -i 's|$jsFile|${jsFile}?v=$timestamp|' /opt/utility-server/frontend/dist/index.html"
ssh root@165.99.59.47 "docker exec utility_nginx nginx -s reload"
```

### Database Migration
```bash
ssh root@165.99.59.47 "cat > /tmp/migrate.py << 'EOF'
import sys
sys.path.insert(0, '/app')
from app.models import auth_models
from app.core.database import Base, engine
Base.metadata.create_all(bind=engine)
print('Migration done')
EOF"

ssh root@165.99.59.47 "docker cp /tmp/migrate.py utility_backend:/app/ && docker exec utility_backend python migrate.py"
```

---

## 🐛 COMMON ISSUES (ĐÃ FIX)

### Issue 1: Frontend calls localhost:8000 ❌
**Cause**: Vite build cache hoặc không set `VITE_API_URL`  
**Solution**: 
```powershell
cd frontend
Remove-Item -Recurse -Force node_modules, dist
npm install
$env:VITE_API_URL="/api"
npm run build
# Then deploy
```

### Issue 2: Table 'activity_logs' not found ❌
**Cause**: Migration chưa chạy  
**Solution**: Run migration script (see above)

### Issue 3: Browser loading old JS file ❌
**Cause**: Browser cache  
**Solution**: 
- Add cache buster `?v=timestamp` to index.html
- User: Hard refresh (CTRL + SHIFT + R)

### Issue 4: Mobile layout broken ❌
**Cause**: Missing responsive classes  
**Solution**: ✅ Fixed với Tailwind breakpoints (md:, sm:)

### Issue 5: Backend 500 on login ❌
**Cause**: activity_logs table missing  
**Solution**: ✅ Fixed - table created

---

## 🔍 DEBUG COMMANDS

```bash
# Container status
ssh root@165.99.59.47 "docker ps"

# Backend logs
ssh root@165.99.59.47 "docker logs utility_backend --tail=50"

# Nginx logs
ssh root@165.99.59.47 "docker logs utility_nginx --tail=50"

# Database tables
ssh root@165.99.59.47 "docker exec utility_postgres psql -U utility_user -d utility_db -c '\dt'"

# Database users
ssh root@165.99.59.47 "docker exec utility_postgres psql -U utility_user -d utility_db -c 'SELECT id, username, email, is_active FROM users;'"

# Test backend
curl http://165.99.59.47/api/health

# Test login
$body = @{username='admin'; password='admin123'} | ConvertTo-Json
Invoke-WebRequest -Uri "http://165.99.59.47/api/auth/login" -Method POST -Body $body -ContentType "application/json"
```

---

## 📝 IMPORTANT NOTES

### Critical Points:
1. **ALWAYS build frontend với `VITE_API_URL="/api"`** - Không để localhost:8000
2. **Cache busting** - Thêm `?v=timestamp` khi deploy frontend
3. **models/__init__.py** - Giữ EMPTY để tránh circular imports
4. **JWT Token** - Expires sau 7 ngày
5. **Activity Logs** - Tự động log mọi action
6. **RBAC** - 3 roles: admin (full), editor (read/write), viewer (read)
7. **Responsive** - Mobile-first design

### File Locations:
- Frontend build: `/opt/utility-server/frontend/dist/`
- Backend code: `/opt/utility-server/backend/app/`
- Nginx config: `/opt/utility-server/nginx/nginx.conf`
- Database data: Docker volume `postgres_data`

---

## 🔗 DOCUMENTATION FILES

- `PROJECT_OVERVIEW.md` - Tổng quan chi tiết
- `DEBUG_GUIDE.md` - Troubleshooting guide
- `DEPLOYMENT_CHECKLIST.md` - Deploy step-by-step
- `AUTHENTICATION_SETUP.md` - Auth system setup
- `PROJECT_STRUCTURE.md` - Code structure
- `DEPLOY.md` - Deployment details

---

## 🎯 CURRENT STATUS

### ✅ Hoạt động tốt:
- Login/logout ✅
- User management (CRUD) ✅
- Role management ✅
- Activity logging ✅
- Responsive mobile UI ✅
- API authentication ✅
- Database migrations ✅

### 🚧 Cần phát triển:
- Document conversion tools
- Image processing
- OCR functionality
- Face recognition
- API rate limiting
- Email notifications

---

## 💡 WHEN STARTING NEW CHAT

**Attach this file và nói:**
> "Đây là context đầy đủ của project Utility Server. Vui lòng đọc và hiểu toàn bộ architecture, issues đã fix, và deployment process. Tôi cần [your task]."

**AI sẽ biết:**
- Project structure
- Tech stack
- Deployment process
- Common issues và solutions
- Database schema
- API endpoints
- Authentication flow
- Debug commands

---

**Last Updated**: November 21, 2025  
**Version**: 1.0.0  
**Status**: Production Ready ✅
