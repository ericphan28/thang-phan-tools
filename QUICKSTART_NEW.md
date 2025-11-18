# 🚀 QUICK START - Hướng dẫn siêu nhanh

## Cách ĐƠN GIẢN NHẤT (3 bước):

### 1️⃣ Mở VS Code
```
Mở folder: D:\thang\utility-server
```

### 2️⃣ Chạy servers
**Nhấn:** `Ctrl+Shift+P`  
**Gõ:** `Run Task`  
**Chọn:** `🚀 Start All Servers`

**Hoặc nhấn phím tắt:** `Ctrl+Shift+S`

### 3️⃣ Mở browser
```
http://localhost:5173
```

**Login:** `admin` / `admin123`

---

## 🎯 Bạn sẽ thấy:

VS Code tự động mở 2 terminal panels:
- **Panel 1 (Backend)**: Logs của FastAPI server
- **Panel 2 (Frontend)**: Logs của Vite dev server

## ⚡ Phím tắt hữu ích:

| Phím | Chức năng |
|------|-----------|
| `Ctrl+Shift+S` | Start All Servers |
| `Ctrl+Shift+K` | Stop All Servers |
| `Ctrl+Shift+P` | Command Palette |
| `Ctrl+` ` | Toggle Terminal |

## 🛑 Dừng servers:

**Cách 1:** Nhấn `Ctrl+Shift+K`

**Cách 2:** Click vào icon **thùng rác** 🗑️ ở góc phải Terminal panel

**Cách 3:** Nhấn `Ctrl+C` trong mỗi terminal

---

## 🔧 Nếu gặp lỗi "Port đang được sử dụng":

Chạy trong PowerShell:
```powershell
Stop-Process -Name python,node -Force
```

Rồi start lại servers.

---

## 📝 Các tính năng đã implement:

### ✅ Option A - UX/UI Improvements
- Loading skeletons
- Confirmation dialogs
- Animations (fade-in, zoom-in)
- Empty states
- Form validation
- Toast notifications (Vietnamese)

### ✅ Option B - Roles Management
- Create/Edit/Delete roles
- Multi-select permissions
- Real-time permission updates
- Default roles protection

### ✅ Option C - Activity Logs
- Timeline UI với icons
- Filters (action, resource type, search)
- Stats dashboard (7 days)
- Pagination
- Vietnamese timestamps
- Automatic logging cho tất cả CRUD operations

---

## 🎨 Tech Stack:

**Backend:**
- FastAPI 0.115+
- SQLAlchemy 2.0+
- Python 3.13
- SQLite database

**Frontend:**
- React 18 + TypeScript
- Vite 7.2
- TanStack Query
- TailwindCSS
- Lucide Icons

---

**Tác giả:** Utility Server Team  
**Update:** November 2025
