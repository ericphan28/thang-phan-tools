# 🚀 Hướng Dẫn Chạy Servers

## ⚡ Cách Sử Dụng Nhanh

### 1️⃣ Khởi động cả Backend + Frontend
```powershell
.\start.ps1
```
✅ Tự động dọn dẹp ports cũ  
✅ Khởi động Backend (Port 8000)  
✅ Khởi động Frontend (Port 5173)  
✅ Hiển thị logs real-time  
✅ Nhấn **Ctrl+C** để dừng  

### 2️⃣ Dừng tất cả servers
```powershell
.\stop.ps1
```

### 3️⃣ Restart servers
```powershell
.\restart.ps1
```

## 🌐 URLs sau khi chạy

| Service | URL | Mô tả |
|---------|-----|-------|
| Frontend | http://localhost:5173 | React Admin Dashboard |
| Backend API | http://localhost:8000 | FastAPI Server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Login | admin / admin123 | Default credentials |

## 💡 Lưu Ý

### ✅ Ưu điểm của script tự động:
- **Không lo server bị tắt** khi Copilot sửa code
- **Auto-cleanup** ports trước khi start
- **Logs có màu** dễ theo dõi
- **Dừng sạch sẽ** với Ctrl+C

### 🔧 Nếu gặp lỗi:
1. **Port đang bị chiếm**: Chạy `.\stop.ps1` trước
2. **Backend không start**: Kiểm tra Python đã cài đặt chưa
3. **Frontend không start**: Chạy `npm install` trong folder `frontend`
4. **Script không chạy**: Mở PowerShell as Administrator

### 📝 Chạy riêng từng server (cách cũ):

**Backend:**
```powershell
cd backend
$env:PYTHONPATH="D:\thang\utility-server\backend"
python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```powershell
cd frontend
npm run dev
```

## 🎯 Workflow Khuyên Dùng

1. **Bật servers một lần**: `.\start.ps1`
2. **Để terminal chạy ngầm**, mở terminal mới để làm việc khác
3. **Copilot sửa code** → Servers tự động reload (hot-reload)
4. **Xong việc**: Quay lại terminal đang chạy servers → Nhấn Ctrl+C

---

**Tác giả**: Utility Server Team  
**Update**: Nov 2025
