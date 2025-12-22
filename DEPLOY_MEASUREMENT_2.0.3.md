# ĐO THỜI GIAN DEPLOY - VERSION 2.0.3

**Ngày test:** 22/12/2025 21:10  
**Commit:** 3452f9d  
**Image:** ghcr.io/ericphan28/thang-phan-tools-backend:sha-3452f9d

---

## 📊 KẾT QUẢ ĐO THỜI GIAN

### Giai đoạn 1: Build & Push (GitHub Actions)
```
1. Commit code:          0.3 giây
2. Push lên GitHub:      2.5 giây  
3. GitHub Actions build: ~240 giây (4 phút)
-----------------------------------
TỔNG GD1:                ~243 giây (4 phút)
```

### Giai đoạn 2: Deploy lên VPS

**Đang đo...**

Chạy script để đo chính xác:
```bash
cd /opt/utility-server

# Step 1: Pull image
time docker pull ghcr.io/ericphan28/thang-phan-tools-backend:sha-3452f9d

# Step 2: Tag latest  
time docker tag ghcr.io/ericphan28/thang-phan-tools-backend:sha-3452f9d ghcr.io/ericphan28/thang-phan-tools-backend:latest

# Step 3-5: Restart
time (docker compose -f docker-compose.prod.yml down backend && \
      docker compose -f docker-compose.prod.yml up -d backend)

# Step 6: Verify
curl http://localhost:8000/health
```

---

## 📝 GHI CHÚ

- Lần này là **incremental pull** (chỉ thay đổi 1 file nhỏ)
- Nên pull sẽ nhanh hơn nhiều so với lần đầu
- Docker chỉ pull layer thay đổi, không pull lại toàn bộ
