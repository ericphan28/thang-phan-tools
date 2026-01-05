# 🚀 VPS Deployment - Quick Guide

**GitHub:** https://github.com/ericphan28/thang-phan-tools  
**VPS IP:** 165.99.59.47

---

## 📦 Deploy Mới Nhất

SSH vào VPS và chạy:

```bash
ssh root@165.99.59.47

cd /root/thang-phan-tools
git pull origin main
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build backend
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

---

## ✅ Sau Khi Deploy

### 1. Thêm Gemini Keys vào Database

Mở browser: **http://165.99.59.47/admin/gemini-keys**

Click "+ Add Key" và thêm 3 keys:
- **orc-xa-gia-kiem-02** | ericphan28@gmail.com | Priority 10 | Quota 1500000
- **orc-xa-gia-kiem-03** | ericphan28@gmail.com | Priority 10 | Quota 1500000
- **orc-xa-gia-kiem-04** | ericphan28@gmail.com | Priority 10 | Quota 1500000

### 2. Xóa GEMINI_API_KEY khỏi .env

```bash
ssh root@165.99.59.47
cd /root/thang-phan-tools/backend
nano .env

# XÓA dòng: GEMINI_API_KEY=AIza...
# Giữ lại: GEMINI_ENCRYPTION_KEY (QUAN TRỌNG!)

# Save: Ctrl+O, Enter, Ctrl+X

cd ..
docker-compose -f docker-compose.prod.yml restart backend
```

### 3. Verify

```bash
# Check backend logs
docker-compose -f docker-compose.prod.yml logs backend | tail -20

# Should see:
# ✅ Loaded .env
# 💻 Running in Docker
# ✅ Keys managed via database

# Test health
curl http://localhost:8000/health
# {"status":"healthy","version":"2.1.5"}

# Test keys API
curl http://localhost:8000/api/v1/admin/gemini-keys/dashboard \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
# Should return dashboard data
```

---

## 🐛 Troubleshooting

**Backend crashes on start:**
```bash
docker-compose -f docker-compose.prod.yml logs backend
# Look for errors
```

**"Không tìm thấy Gemini API key" error:**
```bash
# Add keys in UI: http://165.99.59.47/admin/gemini-keys
# OR check database:
docker exec -it thang-phan-tools-postgres-1 psql -U utility_user -d utility_db
\c utility_db
SELECT id, key_name, status FROM gemini_api_keys;
\q
```

**Database connection failed:**
```bash
docker-compose -f docker-compose.prod.yml ps
# postgres must be running

docker-compose -f docker-compose.prod.yml restart postgres
```

---

## 📊 Monitor

```bash
# Real-time logs
docker-compose -f docker-compose.prod.yml logs -f backend frontend postgres

# Container status
docker-compose -f docker-compose.prod.yml ps

# Disk usage
df -h
docker system df

# Cleanup old images
docker system prune -a
```

---

## 🔄 Rollback

Nếu có lỗi, rollback:

```bash
cd /root/thang-phan-tools
git log --oneline -5  # Find commit hash before deploy

git checkout <PREVIOUS_COMMIT_HASH>
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

---

**Last Deploy:** 6/1/2026  
**Commit:** feat: Gemini Keys Management System
