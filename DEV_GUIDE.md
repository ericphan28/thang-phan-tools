# 🚀 Hướng dẫn khởi động Development Server

## Cách 1: Sử dụng Script tự động (Đơn giản nhất) ⭐

### Windows CMD/PowerShell:
```cmd
start-dev.bat
```

Hoặc:
```powershell
.\start-dev.ps1
```

Script sẽ tự động:
- ✅ Mở 2 terminal riêng cho Backend và Frontend
- ✅ Khởi động Backend trên port 8000
- ✅ Khởi động Frontend trên port 5173
- ✅ Hiển thị thông tin truy cập

---

## Cách 2: Khởi động thủ công (Chi tiết)

### Bước 1: Khởi động Backend

Mở **Terminal 1** (PowerShell hoặc CMD):

```powershell
# Di chuyển vào thư mục backend
cd D:\thang\utility-server\backend

# Set PYTHONPATH (PowerShell)
$env:PYTHONPATH="D:\thang\utility-server\backend"

# Hoặc (CMD)
set PYTHONPATH=D:\thang\utility-server\backend

# Khởi động server
python -m uvicorn app.main_simple:app --host 127.0.0.1 --port 8000 --reload
```

**Đợi đến khi thấy:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### Bước 2: Khởi động Frontend

Mở **Terminal 2** (PowerShell hoặc CMD):

```powershell
# Di chuyển vào thư mục frontend
cd D:\thang\utility-server\frontend

# Khởi động Vite dev server
npm run dev
```

**Đợi đến khi thấy:**
```
VITE v7.2.2  ready in xxx ms
➜  Local:   http://localhost:5173/
```

---

## 📍 Truy cập ứng dụng

Sau khi cả hai servers đã khởi động thành công:

| Service | URL | Mô tả |
|---------|-----|-------|
| 🎨 Frontend | http://localhost:5173 | Giao diện quản trị React |
| 🔧 Backend API | http://127.0.0.1:8000 | FastAPI REST API |
| 📚 API Docs (Swagger) | http://127.0.0.1:8000/docs | Interactive API documentation |
| 📖 ReDoc | http://127.0.0.1:8000/redoc | Alternative API docs |

---

## 🔐 Đăng nhập

**Tài khoản mặc định:**
- **Username:** `admin`
- **Password:** `admin123`

**Các tài khoản test khác:**
- `john_viewer` / `password123` (Vai trò: viewer)
- `jane_editor` / `password123` (Vai trò: editor)

---

## 🛑 Dừng Servers

### Nếu dùng Script:
- Đóng các cửa sổ terminal đã mở
- Hoặc nhấn `Ctrl+C` trong từng terminal

### Nếu khởi động thủ công:
- Nhấn `Ctrl+C` trong từng terminal
- Hoặc đóng cửa sổ terminal

### Dừng toàn bộ process (nếu cần):
```powershell
# Dừng Backend
Get-Process python | Stop-Process -Force

# Dừng Frontend
Get-Process node | Where-Object {$_.MainWindowTitle -like "*Vite*"} | Stop-Process -Force
```

---

## ❗ Xử lý lỗi thường gặp

### Lỗi: Port đã được sử dụng

**Backend (Port 8000):**
```powershell
# Tìm process đang dùng port 8000
netstat -ano | findstr ":8000"

# Kill process (thay PID bằng số thực tế)
taskkill /PID <PID> /F
```

**Frontend (Port 5173):**
```powershell
# Tìm process đang dùng port 5173
netstat -ano | findstr ":5173"

# Kill process
taskkill /PID <PID> /F
```

### Lỗi: Module not found (Backend)

```powershell
cd D:\thang\utility-server\backend
pip install -r requirements.txt
```

### Lỗi: Dependencies missing (Frontend)

```powershell
cd D:\thang\utility-server\frontend
npm install
```

### Lỗi: CORS blocked

- Đảm bảo Backend đang chạy trên `127.0.0.1:8000`
- Đảm bảo Frontend đang chạy trên `localhost:5173`
- Refresh trình duyệt (F5)
- Xóa cache và cookies nếu cần

### Lỗi: Database locked

```powershell
# Dừng tất cả Python processes
Get-Process python | Stop-Process -Force

# Khởi động lại Backend
cd D:\thang\utility-server\backend
$env:PYTHONPATH="D:\thang\utility-server\backend"
python -m uvicorn app.main_simple:app --host 127.0.0.1 --port 8000 --reload
```

---

## 🔧 Development Tips

### Hot Reload
- **Backend:** Tự động reload khi sửa file Python (nhờ `--reload` flag)
- **Frontend:** Tự động reload khi sửa file React/TypeScript (Vite HMR)

### Debug Backend
```powershell
# Chạy với debug mode
python -m uvicorn app.main_simple:app --host 127.0.0.1 --port 8000 --reload --log-level debug
```

### Build Frontend cho Production
```powershell
cd D:\thang\utility-server\frontend
npm run build
# Output: dist/ folder
```

---

## 📝 Cấu trúc thư mục

```
D:\thang\utility-server\
├── backend/               # FastAPI Backend
│   ├── app/
│   │   ├── main_simple.py    # Entry point
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Config, database, security
│   │   └── models/           # Database models
│   ├── requirements.txt
│   └── utility.db           # SQLite database
│
├── frontend/              # React Frontend
│   ├── src/
│   │   ├── pages/           # Page components
│   │   ├── components/      # Reusable components
│   │   ├── services/        # API services
│   │   └── contexts/        # React contexts
│   ├── package.json
│   └── vite.config.ts
│
├── start-dev.bat          # Script khởi động (Windows CMD)
├── start-dev.ps1          # Script khởi động (PowerShell)
└── DEV_GUIDE.md          # File này
```

---

## 🎯 Next Steps

1. Mở http://localhost:5173 trong trình duyệt
2. Đăng nhập với `admin` / `admin123`
3. Khám phá các tính năng:
   - 📊 Dashboard: Thống kê tổng quan
   - 👥 Quản lý người dùng: Thêm, sửa, xóa, kích hoạt
   - 🛡️ Quản lý vai trò: Xem roles và permissions
4. Test API tại http://127.0.0.1:8000/docs

---

**Happy Coding! 🚀**
