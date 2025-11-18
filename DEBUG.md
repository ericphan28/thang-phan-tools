# 🔧 DEBUG GUIDE - Hướng dẫn debug lỗi hiện tại

## ❌ Vấn đề hiện tại:
- Update User gặp lỗi 422 hoặc CORS error
- Backend có thể crash khi nhận request

## ✅ Servers đã chạy:
Đã mở 2 CMD windows riêng cho:
- Backend (Port 8000)  
- Frontend (Port 5173)

## 🧪 CÁCH DEBUG:

### Bước 1: Kiểm tra Backend logs
Mở **CMD window Backend** (màu đen) và xem logs khi bạn click Save ở frontend.

**Tìm kiếm:**
- `PUT /api/users/4` - Request đã đến backend chưa?
- `422 Unprocessable Entity` - Lỗi validation?
- `Traceback` hoặc `Error` - Backend crash?

### Bước 2: Kiểm tra Frontend request
Mở **Browser Console** (F12) → Tab **Network**:
1. Click Save để update user
2. Tìm request `PUT /api/users/4`
3. Click vào request đó
4. Xem tab **Payload** - Data gửi đi là gì?
5. Xem tab **Response** - Backend trả về lỗi gì?

### Bước 3: Test Login lại
Có thể token hết hạn:
1. Logout
2. Login lại bằng `admin` / `admin123`
3. Thử update user lại

### Bước 4: Test bằng API Docs
Mở http://localhost:8000/docs:
1. Click "Authorize" → Nhập token từ localStorage
2. Thử PUT /api/users/{user_id} với payload:
```json
{
  "email": "test@example.com",
  "full_name": "Test User",
  "is_active": true,
  "is_superuser": false,
  "role_ids": [1]
}
```
3. Xem response

## 📋 NHỮNG GÌ TÔI ĐÃ FIX:

### ✅ Fix 1: Update User thiếu xử lý role_ids
**File**: `backend/app/services/user_service.py`
**Đã thêm**:
```python
# Update roles if provided
if user_data.role_ids is not None:
    roles = db.query(Role).filter(Role.id.in_(user_data.role_ids)).all()
    if len(roles) != len(user_data.role_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more role IDs are invalid"
        )
    user.roles = roles
```

### ✅ Fix 2: Update Role permissions an toàn hơn
**File**: `backend/app/api/v1/endpoints/roles.py`
**Đã thêm type check**:
```python
for spec in role_data.permission_specs:
    resource = spec.get('resource', '') if isinstance(spec, dict) else ''
    action = spec.get('action', '') if isinstance(spec, dict) else ''
```

## 🎯 NEXT STEPS:

1. **Xem Backend logs** trong CMD window
2. **Xem Network tab** trong browser
3. **Báo cho tôi**:
   - Backend log có gì? (copy paste vài dòng)
   - Request payload là gì?
   - Response error message là gì?

---

## 🚀 CÁCH RESTART SERVERS:

**Stop tất cả**:
```powershell
Stop-Process -Name python,node -Force
```

**Start lại**:
- Chạy `START.bat` (tự động mở 2 windows)
- Hoặc manual trong 2 terminals riêng:
  - Terminal 1: `start-backend.bat`
  - Terminal 2: `start-frontend.bat`
