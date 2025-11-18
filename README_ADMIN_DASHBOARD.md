# 🎯 ADMIN DASHBOARD - HỆ THỐNG QUẢN TRỊ

## 📦 Tổng Quan

Hệ thống Admin Dashboard hoàn chỉnh với quản lý người dùng, vai trò, phân quyền và nhật ký hoạt động.

### ✨ Tính Năng

**🔐 Xác Thực & Bảo Mật**
- Đăng nhập JWT authentication
- Session management với auto-refresh tokens
- Role-based access control (RBAC)
- Password hashing với bcrypt

**👥 Quản Lý Người Dùng**
- Tạo, sửa, xóa người dùng
- Gán nhiều vai trò cho mỗi người dùng
- Active/Inactive user status
- Superuser designation

**🎭 Quản Lý Vai Trò**
- Tạo, sửa, xóa vai trò
- Định nghĩa permissions chi tiết (resource + action)
- Kiểm tra số lượng users trước khi xóa
- 3 vai trò mặc định: Admin, Editor, Viewer

**📊 Nhật Ký Hoạt Động**
- Tự động log tất cả operations (CRUD User/Role, Auth)
- Timeline view với filters (action, resource type)
- Statistics dashboard (total, create, update, delete)
- Hiển thị thời gian tương đối (vừa xong, X phút trước, ...)
- Track IP address và user agent

---

## 🚀 CÁCH CHẠY

### 🔧 Yêu Cầu

- **Python**: 3.13+
- **Node.js**: 20+
- **Database**: SQLite (development) / PostgreSQL (production)

### 📥 Cài Đặt

**Backend:**
```powershell
cd backend
pip install -r requirements.txt
```

**Frontend:**
```powershell
cd frontend
npm install
```

### ▶️ Chạy Development

**Cách 1: VS Code Tasks (Khuyên dùng)**
1. Nhấn `Ctrl+Shift+P`
2. Chọn "Tasks: Run Task"
3. Chọn "🚀 Start All Servers"
4. Backend chạy ở port 8000, Frontend ở port 5173

**Cách 2: Manual**

Terminal 1 - Backend:
```powershell
cd backend
$env:PYTHONPATH="D:\thang\utility-server\backend"
python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Frontend:
```powershell
cd frontend
npm run dev
```

### 🌐 Truy Cập

- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs
- **Default Login**: 
  - Username: `admin`
  - Password: `admin123`

---

## 📂 Cấu Trúc Project

```
utility-server/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # API endpoints
│   │   │   ├── auth.py          # Đăng nhập, logout
│   │   │   ├── users.py         # User CRUD
│   │   │   ├── roles.py         # Role CRUD
│   │   │   └── activity_logs.py # Activity logs
│   │   ├── core/
│   │   │   ├── config.py        # App configuration
│   │   │   ├── database.py      # Database connection
│   │   │   └── security.py      # JWT, password hashing
│   │   ├── models/
│   │   │   └── models.py        # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── role.py
│   │   │   └── activity_log.py
│   │   ├── services/            # Business logic
│   │   │   ├── user_service.py
│   │   │   ├── role_service.py
│   │   │   ├── activity_logger.py
│   │   │   └── face_service.py
│   │   └── main_simple.py       # FastAPI app
│   ├── requirements.txt
│   └── utility.db               # SQLite database
│
├── frontend/
│   ├── src/
│   │   ├── pages/               # Page components
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── UsersPage.tsx
│   │   │   ├── RolesPage.tsx
│   │   │   └── ActivityLogsPage.tsx
│   │   ├── components/          # Reusable components
│   │   │   ├── ui/              # shadcn/ui components
│   │   │   ├── Sidebar.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── services/            # API services
│   │   │   ├── api.ts           # Axios config
│   │   │   ├── authService.ts
│   │   │   ├── userService.ts
│   │   │   ├── roleService.ts
│   │   │   └── activityLogService.ts
│   │   ├── types/               # TypeScript types
│   │   ├── contexts/            # React contexts
│   │   │   └── AuthContext.tsx
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
└── .vscode/
    └── tasks.json               # VS Code tasks for easy startup
```

---

## 🎨 Tech Stack

### Backend
- **FastAPI** 0.115+ - Modern Python web framework
- **SQLAlchemy** 2.0 - ORM
- **SQLite** - Development database
- **Pydantic** 2.0 - Data validation
- **JWT** - Authentication
- **bcrypt** - Password hashing
- **python-multipart** - File uploads

### Frontend
- **React** 19.2 + **TypeScript** 5.9
- **Vite** 7.2 - Build tool
- **TanStack Query** 5.90 - Server state management
- **Axios** 1.13 - HTTP client
- **React Router** 7.9 - Routing
- **TailwindCSS** 3.4 - Styling
- **Lucide React** 0.554 - Icons
- **react-hot-toast** 2.6 - Notifications

---

## 📊 Database Schema

### Users Table
```sql
- id (PK)
- username (unique)
- email (unique)
- hashed_password
- full_name
- is_active
- is_superuser
- created_at
- updated_at
```

### Roles Table
```sql
- id (PK)
- name (unique)
- description
- permissions (JSON)
- created_at
- updated_at
```

### User-Role Association (Many-to-Many)
```sql
- user_id (FK)
- role_id (FK)
```

### Activity Logs Table
```sql
- id (PK)
- user_id (FK)
- username
- action (create/update/delete/login)
- resource_type (user/role/auth)
- resource_id
- details (JSON)
- ip_address
- user_agent
- created_at
```

---

## 🔐 API Endpoints

### Authentication
- `POST /api/auth/login` - Đăng nhập
- `POST /api/auth/logout` - Đăng xuất
- `GET /api/auth/me` - Thông tin user hiện tại

### Users
- `GET /api/users/` - Danh sách users (phân trang)
- `POST /api/users/` - Tạo user mới
- `GET /api/users/{id}` - Chi tiết user
- `PUT /api/users/{id}` - Cập nhật user
- `DELETE /api/users/{id}` - Xóa user

### Roles
- `GET /api/roles/` - Danh sách roles
- `POST /api/roles/` - Tạo role mới
- `GET /api/roles/{id}` - Chi tiết role
- `PUT /api/roles/{id}` - Cập nhật role
- `DELETE /api/roles/{id}` - Xóa role

### Activity Logs
- `GET /api/logs/` - Danh sách logs (phân trang, filters)
- `GET /api/logs/stats` - Thống kê logs

---

## 🧪 Testing

### Test Backend
```powershell
cd backend
pytest
```

### Test Frontend
```powershell
cd frontend
npm test
```

### Manual Testing
1. Đăng nhập với admin/admin123
2. Tạo user mới → Kiểm tra activity logs
3. Gán role cho user → Kiểm tra update hoạt động
4. Tạo role mới → Kiểm tra permissions
5. Xóa user → Kiểm tra confirmation dialog

---

## 🐛 Đã Sửa Các Bug

1. ✅ **Update user không save role_ids** - Thêm role_ids handling vào user_service
2. ✅ **Duplicate UserUpdate schemas** - Consolidate về user.py
3. ✅ **ImportError schemas** - Fix imports trong __init__.py
4. ✅ **Timezone display bug** - Activity logs hiển thị "7 giờ trước" thay vì "Vừa xong"
5. ✅ **Type error update_role** - Thêm isinstance() check

---

## 📝 TODO / Improvements

- [ ] Add pagination for users list
- [ ] Add search/filter for users
- [ ] Add user avatar upload
- [ ] Export activity logs to CSV/PDF
- [ ] Email notifications
- [ ] Two-factor authentication (2FA)
- [ ] Dark mode toggle
- [ ] API rate limiting
- [ ] Backup/restore database
- [ ] Deploy to production (Docker)

---

## 🚢 Production Deployment

**Docker Compose:**
```bash
docker-compose up -d
```

**Environment Variables:**
```env
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
CORS_ORIGINS=https://yourdomain.com
```

**Nginx Config:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5173;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

---

## 🤝 Contributing

1. Fork the project
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

MIT License

---

## 👤 Contact

- **Developer**: Thang
- **Project**: Admin Dashboard
- **Date**: November 2025

---

**🎉 Chúc mừng! Dashboard đã hoàn thiện 100%!**
