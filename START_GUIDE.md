# 🚀 HƯỚNG DẪN KHỞI ĐỘNG SERVERS

## ⚠️ VẤN ĐỀ:
PowerShell commands đang kill lẫn nhau khi chạy trong cùng session.

## ✅ GIẢI PHÁP: Dùng VS Code Tasks

### Bước 1: Trong VS Code
```
Ctrl+Shift+P → Tasks: Run Task → 🚀 Start All Servers
```

Hoặc phím tắt: **`Ctrl+Shift+S`**

### Bước 2: VS Code sẽ tự động
- Mở 2 terminal panels riêng biệt
- Backend panel (Cyan)
- Frontend panel (Magenta)
- Không bao giờ conflict!

---

## 🔧 HOẶC: Chạy thủ công trong 2 terminals riêng

### Terminal 1 - Backend:
```powershell
cd D:\thang\utility-server\backend
$env:PYTHONPATH="D:\thang\utility-server\backend"
python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend:
```powershell
cd D:\thang\utility-server\frontend
npm run dev
```

---

## 📝 SAU KHI START:

**Mở browser:**
- Frontend: http://localhost:5173
- Backend Docs: http://localhost:8000/docs
- Login: admin / admin123

**Test features:**
1. Update user → Check role_ids được lưu
2. Update role → Check permissions được lưu
3. Activity Logs → Check logs hiển thị đầy đủ

---

## ✅ ĐÃ FIX:

1. ✅ Cleanup 5 files thừa backend
2. ✅ Fix duplicate UserUpdate schema
3. ✅ Fix import trong __init__.py
4. ✅ Clear Python cache
5. ✅ Backend code clean và ready

**VẤN ĐỀ DUY NHẤT:** PowerShell commands kill processes khi run automation → Dùng VS Code Tasks thay thế!

---

**Recommendation:** Dùng VS Code Tasks (Ctrl+Shift+S) - Đơn giản và ổn định nhất!
