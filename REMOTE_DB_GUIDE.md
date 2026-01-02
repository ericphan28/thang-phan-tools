# 🌐 KẾT NỐI LOCALHOST → VPS DATABASE

## 💡 Ý Tưởng
**1 database duy nhất trên VPS** - cả localhost và production đều kết nối vào đó.

### ✅ Ưu điểm:
- Chỉ 1 database → Không cần sync
- Đơn giản - không cần Docker local
- Data luôn real-time
- Team share chung database
- Test với production data thật

### ⚠️ Nhược điểm:
- Phụ thuộc internet
- Latency cao hơn (50-200ms)
- Cần bảo mật connection
- Nếu VPS down → không dev được

---

## 🚀 2 CÁCH KẾT NỐI

### 🔐 Option 1: SSH Tunnel (Khuyến nghị ⭐)

**Bảo mật cao:**
- Không expose port PostgreSQL ra internet
- Tất cả traffic đi qua SSH (encrypted)
- Chỉ cần SSH access

**Cách dùng:**
```powershell
# Tạo SSH tunnel
.\connect-remote-db.ps1 -Mode ssh-tunnel

# Tunnel sẽ chạy background:
# localhost:5432 → VPS:5432

# Ngắt kết nối
.\connect-remote-db.ps1 -Mode disconnect
```

**Cách hoạt động:**
```
localhost:5432 → SSH tunnel → VPS:5432 → PostgreSQL
```

---

### 🌐 Option 2: Direct Connection

**Đơn giản hơn:**
- Kết nối trực tiếp qua internet
- Không cần SSH tunnel

**Rủi ro bảo mật:**
- PostgreSQL port exposed ra internet
- Có thể bị brute-force attack
- Cần firewall rules chặt chẽ

**Setup trên VPS:**
```bash
ssh root@165.99.59.47

# 1. Update docker-compose.prod.yml
nano docker-compose.prod.yml
# Sửa postgres ports: "0.0.0.0:5432:5432"

# 2. Allow firewall (chỉ IP của bạn)
sudo ufw allow from YOUR_IP to any port 5432

# 3. Update PostgreSQL config
docker exec utility-postgres-prod bash -c \
  "echo 'host all all 0.0.0.0/0 md5' >> /var/lib/postgresql/data/pg_hba.conf"

docker exec utility-postgres-prod bash -c \
  "echo \"listen_addresses = '*'\" >> /var/lib/postgresql/data/postgresql.conf"

# 4. Restart
docker-compose restart postgres
```

**Update backend/.env:**
```dotenv
DATABASE_URL=postgresql://utility_user:PASSWORD@165.99.59.47:5432/utility_db
```

---

## 📋 SETUP NHANH (SSH Tunnel - Khuyến nghị)

### Bước 1: Tạo SSH Tunnel
```powershell
.\connect-remote-db.ps1 -Mode ssh-tunnel
```

### Bước 2: Lấy Password từ VPS
```bash
ssh root@165.99.59.47
cat /opt/utility-server/.env | grep DB_PASSWORD
# hoặc
docker-compose -f /opt/utility-server/docker-compose.prod.yml exec postgres env | grep POSTGRES_PASSWORD
```

### Bước 3: Update backend/.env
```dotenv
# Remote PostgreSQL via SSH Tunnel
DATABASE_URL=postgresql://utility_user:YOUR_PASSWORD@localhost:5432/utility_db
```

### Bước 4: Test Connection
```powershell
.\connect-remote-db.ps1 -Mode test
```

### Bước 5: Start Backend
```powershell
cd backend
python -m uvicorn app.main_simple:app --reload
```

✅ Done! Backend giờ kết nối trực tiếp tới VPS database!

---

## 🔧 QUẢN LÝ SSH TUNNEL

### Start Tunnel
```powershell
.\connect-remote-db.ps1 -Mode ssh-tunnel
```

### Check Status
```powershell
# Check SSH process
Get-Process | Where-Object { $_.ProcessName -eq "ssh" }

# Test connection
.\connect-remote-db.ps1 -Mode test
```

### Stop Tunnel
```powershell
.\connect-remote-db.ps1 -Mode disconnect
```

### Auto-start on Boot (Optional)
Tạo Windows Task Scheduler để tự động start SSH tunnel khi boot.

---

## 🧪 TESTING

### Test từ PowerShell
```powershell
.\connect-remote-db.ps1 -Mode test
```

### Test từ pgAdmin
```
Host:     localhost (nếu dùng SSH tunnel) hoặc 165.99.59.47 (direct)
Port:     5432
Database: utility_db
User:     utility_user
Password: (lấy từ VPS)
```

### Test từ Python
```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://utility_user:PASSWORD@localhost:5432/utility_db"
)

with engine.connect() as conn:
    result = conn.execute("SELECT version();")
    print(result.fetchone()[0])
```

---

## 🔒 BẢO MẬT

### SSH Tunnel (Option 1)
- ✅ Không expose port
- ✅ Traffic encrypted qua SSH
- ✅ Chỉ cần SSH key authentication
- ✅ VPS không cần mở thêm port

### Direct Connection (Option 2)
**Cần làm thêm:**
1. **Strong password:** Tối thiểu 20 ký tự, random
2. **Firewall:** Chỉ allow IP của bạn
   ```bash
   sudo ufw allow from YOUR_IP to any port 5432
   sudo ufw deny 5432  # Deny all others
   ```
3. **SSL/TLS:** Enable SSL trong PostgreSQL
4. **Fail2ban:** Auto-ban sau nhiều lần login fail
5. **Monitor logs:** Check unauthorized access attempts

---

## 🚦 WORKFLOW MỚI

### Development Flow
```
1. Start SSH tunnel (nếu dùng option 1)
2. Code trên localhost
3. Backend tự động kết nối VPS database
4. Mọi thay đổi data đều real-time
5. Team khác cũng thấy ngay
```

### Team Collaboration
```
Developer A (localhost) ─┐
                         ├──→ VPS PostgreSQL (duy nhất)
Developer B (localhost) ─┤
                         │
Production Frontend    ──┘
```

Tất cả đều dùng **1 database duy nhất!**

---

## 📊 SO SÁNH

| Phương án | Setup | Bảo mật | Tốc độ | Phụ thuộc |
|-----------|-------|---------|--------|-----------|
| **SQLite Local** | Dễ | Cao | Nhanh | Không |
| **PostgreSQL Local** | Trung bình | Cao | Nhanh | Docker |
| **SSH Tunnel → VPS** | Trung bình | Cao | Trung bình | Internet + VPS |
| **Direct → VPS** | Dễ | Thấp | Trung bình | Internet + VPS |

---

## 🎯 KHUYẾN NGHỊ

### Cho 1 người dev:
✅ **SSH Tunnel → VPS** (Option 1)
- Đơn giản
- Bảo mật
- 1 database duy nhất

### Cho team:
✅ **PostgreSQL Local + Sync script**
- Mỗi người 1 DB local (không conflict)
- Sync khi cần
- Không phụ thuộc VPS

### Cho production testing:
✅ **SSH Tunnel + Staging DB**
- Tạo DB staging riêng trên VPS
- Test trên staging trước khi production

---

## ⚙️ TROUBLESHOOTING

### Lỗi: "Connection refused"
```powershell
# Check SSH tunnel running
Get-Process | Where-Object { $_.ProcessName -eq "ssh" }

# Restart tunnel
.\connect-remote-db.ps1 -Mode disconnect
.\connect-remote-db.ps1 -Mode ssh-tunnel
```

### Lỗi: "Password authentication failed"
```bash
# Get correct password from VPS
ssh root@165.99.59.47
cat /opt/utility-server/.env | grep DB_PASSWORD
```

### Lỗi: "Timeout"
- Check internet connection
- Check VPS is running
- Check firewall rules

### Tunnel bị ngắt khi máy sleep
Tạo script tự động reconnect:
```powershell
# auto-reconnect.ps1
while ($true) {
    $tunnel = Get-Process | Where-Object { $_.ProcessName -eq "ssh" }
    if (-not $tunnel) {
        .\connect-remote-db.ps1 -Mode ssh-tunnel
    }
    Start-Sleep -Seconds 60
}
```

---

## 📋 CHECKLIST

### Setup lần đầu:
- [ ] Quyết định dùng SSH Tunnel hay Direct
- [ ] Nếu SSH Tunnel: Test SSH access tới VPS
- [ ] Nếu Direct: Setup firewall trên VPS
- [ ] Chạy script connect-remote-db.ps1
- [ ] Lấy password từ VPS
- [ ] Update backend/.env
- [ ] Test connection
- [ ] Start backend và test

### Hàng ngày:
- [ ] Start SSH tunnel (nếu dùng option 1)
- [ ] Start backend (sẽ tự connect VPS)
- [ ] Code như bình thường
- [ ] Disconnect tunnel khi done

---

## 🎉 KẾT LUẬN

**1 database duy nhất trên VPS:**
- ✅ Đơn giản nhất
- ✅ Không cần sync
- ✅ Real-time data
- ⚠️ Cần internet
- ⚠️ Cần bảo mật tốt

**Khuyến nghị:** Dùng **SSH Tunnel** để kết nối - vừa đơn giản vừa bảo mật!
