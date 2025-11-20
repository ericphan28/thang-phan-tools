# 🚀 UTILITY SERVER - PROJECT OVERVIEW

## 📋 Tổng quan dự án

**Utility Server** là hệ thống quản trị full-stack với authentication, authorization và các công cụ tiện ích.

### 🎯 Mục đích
- Hệ thống quản lý người dùng và phân quyền (RBAC)
- Admin dashboard để quản trị
- API backend với FastAPI
- Frontend React với TypeScript
- Các công cụ tiện ích (document conversion, OCR, face recognition)

### 🏗️ Kiến trúc
```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Browser   │─────▶│    Nginx    │─────▶│   Backend   │
│  (React)    │      │  (Reverse   │      │  (FastAPI)  │
│             │      │   Proxy)    │      │             │
└─────────────┘      └─────────────┘      └──────┬──────┘
                                                  │
                                         ┌────────┴────────┐
                                         │                 │
                                    ┌────▼────┐      ┌────▼────┐
                                    │PostgreSQL│      │  Redis  │
                                    └─────────┘      └─────────┘
```

---

## 🌐 Deployment Information

### Production Server
- **IP**: 165.99.59.47
- **URL**: http://165.99.59.47
- **Hostname**: giakiemso
- **OS**: Ubuntu 22.04 LTS

### Docker Containers
- `utility_nginx` - Nginx reverse proxy (port 80, 443)
- `utility_backend` - FastAPI backend (port 8000 internal)
- `utility_postgres` - PostgreSQL 15 database
- `utility_redis` - Redis cache
- `utility_gotenberg` - Document conversion service

### Credentials
- **Admin User**: `admin` / `admin123`
- **Database**: `utility_db`
- **DB User**: `utility_user`

---

## 📁 Cấu trúc thư mục

```
utility-server/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Main application entry
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py      # Settings & environment
│   │   │   ├── database.py    # Database connection
│   │   │   └── security.py    # JWT, password hashing
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── auth_models.py # User, Role, Permission, ActivityLog
│   │   │   └── models.py      # APIKey, Face, ProcessedFile
│   │   ├── api/v1/endpoints/  # API routes
│   │   │   ├── auth.py        # Login, register, logout
│   │   │   ├── users.py       # User management
│   │   │   ├── roles.py       # Role & permission management
│   │   │   ├── activity_logs.py # Activity logging
│   │   │   ├── documents.py   # Document conversion
│   │   │   ├── images.py      # Image processing
│   │   │   └── ocr.py         # OCR functionality
│   │   └── services/          # Business logic
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── main.tsx          # Entry point
│   │   ├── App.tsx           # App component with routing
│   │   ├── config.ts         # API configuration
│   │   ├── components/
│   │   │   ├── layout/       # Layout components
│   │   │   │   ├── Layout.tsx       # Main layout with sidebar
│   │   │   │   └── Sidebar.tsx      # Navigation sidebar (responsive)
│   │   │   ├── ui/           # Reusable UI components
│   │   │   └── modals/       # Modal dialogs
│   │   ├── pages/            # Page components
│   │   │   ├── LoginPage.tsx        # Login screen
│   │   │   ├── DashboardPage.tsx    # Dashboard with stats
│   │   │   ├── UsersPage.tsx        # User management
│   │   │   ├── RolesPage.tsx        # Role management
│   │   │   ├── ActivityLogsPage.tsx # Activity logs
│   │   │   └── ToolsPage.tsx        # Utility tools
│   │   ├── services/         # API service layer
│   │   │   ├── api.ts        # Axios instance with interceptors
│   │   │   └── index.ts      # Service functions
│   │   ├── contexts/         # React contexts
│   │   │   └── AuthContext.tsx # Authentication context
│   │   └── types/            # TypeScript types
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── nginx/
│   └── nginx.conf            # Nginx configuration
│
├── docker-compose.yml        # Docker orchestration
└── .env                      # Environment variables

```

---

## 🔌 API Endpoints

### Authentication (`/api/auth`)
- `POST /login` - Đăng nhập (JSON body: username, password)
- `POST /register` - Đăng ký user mới
- `GET /me` - Lấy thông tin user hiện tại
- `POST /logout` - Đăng xuất
- `POST /change-password` - Đổi mật khẩu

### Users (`/api/users`)
- `GET /` - Danh sách users (có pagination, search)
- `POST /` - Tạo user mới
- `GET /{id}` - Chi tiết user
- `PUT /{id}` - Cập nhật user
- `DELETE /{id}` - Xóa user
- `GET /stats` - Thống kê users
- `PUT /{id}/toggle-active` - Kích hoạt/vô hiệu hóa user

### Roles (`/api/roles`)
- `GET /` - Danh sách roles
- `POST /` - Tạo role mới
- `GET /{id}` - Chi tiết role với permissions
- `PUT /{id}` - Cập nhật role
- `DELETE /{id}` - Xóa role

### Activity Logs (`/api/logs`)
- `GET /` - Danh sách activity logs (có filter, pagination)
- `GET /stats` - Thống kê hoạt động

### Documents (`/api/documents`)
- `POST /convert` - Convert document (PDF, Word, etc.)

### Images (`/api/images`)
- `POST /upload` - Upload và xử lý ảnh

---

## 🗄️ Database Schema

### Users Table (`users`)
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email
- `hashed_password` - Bcrypt hashed password
- `full_name` - Tên đầy đủ
- `is_active` - Trạng thái hoạt động
- `is_superuser` - Superuser flag
- `created_at`, `updated_at` - Timestamps

### Roles Table (`roles`)
- `id` - Primary key
- `name` - Tên role (admin, editor, viewer)
- `description` - Mô tả role

### Permissions Table (`permissions`)
- `id` - Primary key
- `role_id` - Foreign key to roles
- `resource` - Resource name (user, document, etc.)
- `action` - Action (read, write, delete)

### User_Roles Table (`user_roles`)
- `user_id` - Foreign key to users
- `role_id` - Foreign key to roles
- Many-to-many relationship

### Activity_Logs Table (`activity_logs`)
- `id` - Primary key
- `user_id` - Foreign key to users
- `action` - Action performed (login, create, update, delete)
- `resource_type` - Resource type
- `resource_id` - Resource ID
- `details` - JSON details
- `ip_address` - Client IP
- `user_agent` - Client user agent
- `created_at` - Timestamp

### API_Keys Table (`api_keys`)
- `id` - Primary key
- `user_id` - Foreign key to users
- `key` - API key hash
- `name` - Key name/description
- `is_active` - Active status
- `expires_at` - Expiration date

### Faces Table (`faces`)
- `id` - Primary key
- `user_id` - Foreign key to users
- `encoding` - Face encoding vector
- `image_path` - Path to image

### Processed_Files Table (`processed_files`)
- `id` - Primary key
- `user_id` - Foreign key to users
- `original_filename` - Original filename
- `file_type` - File type
- `status` - Processing status
- `result_path` - Result file path

---

## 🔐 Authentication Flow

1. **Login**: User gửi username/password → Backend verify → Trả về JWT token
2. **Store Token**: Frontend lưu token vào localStorage
3. **API Calls**: Axios interceptor tự động thêm `Authorization: Bearer {token}`
4. **Token Expiry**: Token expires sau 7 ngày
5. **Auto Logout**: Nếu 401 → Xóa token → Redirect to login

---

## 🎨 Frontend Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Routing
- **TanStack Query** - Data fetching & caching
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Shadcn/ui** - Component library

### Important Frontend Configs

**API Configuration (`config.ts`)**:
```typescript
export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';
```

**Build Command**:
```bash
$env:VITE_API_URL="/api"; npm run build
```

**Responsive Design**:
- Mobile: Hamburger menu, collapsible sidebar
- Tablet: 2-column grid
- Desktop: Full layout with fixed sidebar

---

## 🐳 Docker Setup

### Services
1. **Nginx** - Reverse proxy
   - Routes `/api/*` → backend:8000
   - Serves frontend static files
   - Port 80 (HTTP), 443 (HTTPS ready)

2. **Backend** - FastAPI
   - Internal port 8000
   - Auto-reload in development
   - Uvicorn ASGI server

3. **PostgreSQL** - Database
   - Port 5432
   - Volume: `postgres_data`

4. **Redis** - Cache & queue
   - Port 6379
   - Volume: `redis_data`

5. **Gotenberg** - Document conversion
   - Port 3000
   - Chromium-based conversion

### Environment Variables (`.env`)
```env
DB_PASSWORD=your_db_password
REDIS_PASSWORD=your_redis_password
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here
```

---

## 🚢 Deployment Process

### 1. Backend Changes
```bash
# Upload backend files
scp -r backend/app root@165.99.59.47:/opt/utility-server/backend/

# Restart container
ssh root@165.99.59.47 "docker restart utility_backend"
```

### 2. Frontend Changes
```bash
# Build with production API URL
cd frontend
$env:VITE_API_URL="/api"
npm run build

# Deploy to server
ssh root@165.99.59.47 "rm -rf /opt/utility-server/frontend/dist/*"
scp -r dist/* root@165.99.59.47:/opt/utility-server/frontend/dist/

# Add cache buster (optional)
ssh root@165.99.59.47 "sed -i 's|index-HASH.js|index-HASH.js?v=VERSION|' /opt/utility-server/frontend/dist/index.html"

# Reload nginx
ssh root@165.99.59.47 "docker exec utility_nginx nginx -s reload"
```

### 3. Database Migrations
```bash
# Create migration script on server
ssh root@165.99.59.47 "cat > /tmp/migrate.py << 'EOF'
from app.core.database import Base, engine
Base.metadata.create_all(bind=engine)
print('Migration completed')
EOF"

# Run migration
ssh root@165.99.59.47 "docker cp /tmp/migrate.py utility_backend:/app/ && docker exec utility_backend python migrate.py"
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Frontend calls localhost:8000
**Cause**: Vite build cache hoặc env variable không set
**Solution**: 
```bash
cd frontend
Remove-Item -Recurse -Force node_modules, dist
npm install
$env:VITE_API_URL="/api"
npm run build
```

### Issue 2: Database table not found
**Cause**: Migration chưa chạy
**Solution**: Run migration script (see deployment process)

### Issue 3: 401 Unauthorized
**Cause**: Token expired hoặc không có trong request
**Solution**: Check localStorage, login lại

### Issue 4: Nginx 404 for API
**Cause**: Nginx config sai hoặc backend chưa chạy
**Solution**: 
```bash
ssh root@165.99.59.47 "docker logs utility_backend"
ssh root@165.99.59.47 "docker exec utility_nginx cat /etc/nginx/nginx.conf"
```

### Issue 5: Mobile không responsive
**Cause**: CSS breakpoints chưa đúng
**Solution**: Đã fix với Tailwind responsive classes (md:, sm:)

---

## 📝 Important Notes

1. **LUÔN build với VITE_API_URL="/api"** - Không để localhost:8000
2. **Cache busting** - Thêm ?v=version vào JS files khi deploy
3. **Database models** - Import tất cả trong `models/__init__.py` để SQLAlchemy detect
4. **JWT Token** - Expires sau 7 ngày, lưu trong localStorage
5. **Activity Logs** - Tự động log mọi action (login, create, update, delete)
6. **RBAC** - 3 roles mặc định: admin (full access), editor (read/write), viewer (read only)
7. **Responsive Design** - Mobile-first với Tailwind breakpoints

---

## 🔗 Useful Commands

```bash
# Check container status
ssh root@165.99.59.47 "docker ps"

# View logs
ssh root@165.99.59.47 "docker logs --tail=50 utility_backend"

# Database access
ssh root@165.99.59.47 "docker exec utility_postgres psql -U utility_user -d utility_db"

# List tables
ssh root@165.99.59.47 "docker exec utility_postgres psql -U utility_user -d utility_db -c '\dt'"

# Restart all services
ssh root@165.99.59.47 "cd /opt/utility-server && docker-compose restart"

# Check disk space
ssh root@165.99.59.47 "df -h"
```

---

## 📚 Documentation Files

- `PROJECT_STRUCTURE.md` - Chi tiết cấu trúc code
- `AUTHENTICATION_SETUP.md` - Setup authentication system
- `DEPLOY.md` - Deployment guide
- `QUICKSTART.md` - Quick start guide
- `README.md` - General overview

---

**Last Updated**: November 21, 2025
**Version**: 1.0.0
**Maintainer**: Admin Team
