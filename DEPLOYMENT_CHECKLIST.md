# 🚀 DEPLOYMENT CHECKLIST - Step by Step Guide

## 📋 Pre-Deployment Checklist

- [ ] Code changes tested locally
- [ ] Database migrations prepared (if needed)
- [ ] Environment variables checked
- [ ] Backup database (if needed)
- [ ] No hardcoded localhost URLs
- [ ] All dependencies in requirements.txt/package.json

---

## 🔙 BACKEND DEPLOYMENT

### Step 1: Test Changes Locally
```powershell
cd D:\thang\utility-server\backend
# Test with local server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Upload Backend Files
```powershell
# Upload specific files
scp backend/app/api/v1/endpoints/FILE.py root@165.99.59.47:/opt/utility-server/backend/app/api/v1/endpoints/

# Or upload entire app folder
scp -r backend/app root@165.99.59.47:/opt/utility-server/backend/
```

### Step 3: Update Requirements (if needed)
```powershell
scp backend/requirements.txt root@165.99.59.47:/opt/utility-server/backend/
ssh root@165.99.59.47 "cd /opt/utility-server && docker-compose build backend"
```

### Step 4: Run Database Migrations (if needed)
```bash
# Create migration script
ssh root@165.99.59.47 "cat > /tmp/migrate.py << 'EOF'
import sys
sys.path.insert(0, '/app')
from app.models import auth_models  # Import all model files
from app.core.database import Base, engine
Base.metadata.create_all(bind=engine)
print('Migration completed')
EOF"

# Run migration
ssh root@165.99.59.47 "docker cp /tmp/migrate.py utility_backend:/app/ && docker exec utility_backend python migrate.py"

# Verify
ssh root@165.99.59.47 "docker exec utility_postgres psql -U utility_user -d utility_db -c '\dt'"
```

### Step 5: Restart Backend
```bash
ssh root@165.99.59.47 "docker restart utility_backend"

# Wait for startup
Start-Sleep -Seconds 5

# Check logs
ssh root@165.99.59.47 "docker logs utility_backend --tail=30"
```

### Step 6: Test Backend API
```bash
# Health check
curl http://165.99.59.47/api/health

# Test login
$body = @{username='admin'; password='admin123'} | ConvertTo-Json
Invoke-WebRequest -Uri "http://165.99.59.47/api/auth/login" -Method POST -Body $body -ContentType "application/json"
```

**Backend Deployment: ✅ COMPLETE**

---

## 🎨 FRONTEND DEPLOYMENT

### Step 1: Build Frontend
```powershell
cd D:\thang\utility-server\frontend

# CRITICAL: Set API URL
$env:VITE_API_URL="/api"

# Build
npm run build

# Verify build output
Get-ChildItem dist/assets/*.js
# Should see: index-HASH.js

# IMPORTANT: Verify no localhost:8000
Select-String -Pattern "localhost:8000" -Path "dist/assets/*.js"
# Should return: NO MATCHES
```

### Step 2: Backup Old Build (optional)
```bash
ssh root@165.99.59.47 "cp -r /opt/utility-server/frontend/dist /opt/utility-server/frontend/dist.backup.$(date +%Y%m%d)"
```

### Step 3: Deploy New Build
```powershell
# Remove old files
ssh root@165.99.59.47 "rm -rf /opt/utility-server/frontend/dist/*"

# Upload new files
scp -r dist/* root@165.99.59.47:/opt/utility-server/frontend/dist/

# Verify upload
ssh root@165.99.59.47 "ls -lh /opt/utility-server/frontend/dist/assets/"
```

### Step 4: Add Cache Buster
```powershell
# Get JS filename
$jsFile = (Get-ChildItem dist/assets/*.js).Name

# Generate timestamp
$timestamp = Get-Date -Format "yyyyMMddHHmmss"

# Add cache buster to index.html
ssh root@165.99.59.47 "sed -i 's|$jsFile|${jsFile}?v=$timestamp|' /opt/utility-server/frontend/dist/index.html"

# Verify
ssh root@165.99.59.47 "cat /opt/utility-server/frontend/dist/index.html | grep script"
# Should see: index-HASH.js?v=TIMESTAMP
```

### Step 5: Reload Nginx
```bash
ssh root@165.99.59.47 "docker exec utility_nginx nginx -s reload"
```

### Step 6: Test Frontend
1. Open browser in **Incognito mode** (CTRL + SHIFT + N)
2. Go to: http://165.99.59.47
3. Open DevTools (F12) → Network tab
4. Hard refresh (CTRL + SHIFT + R)
5. Verify:
   - Loading index-HASH.js?v=TIMESTAMP
   - No errors in Console
   - API calls going to /api/*, NOT localhost:8000

### Step 7: Clear User Cache (inform users)
```
Ask users to:
1. Press CTRL + SHIFT + R (hard refresh)
2. Or use Incognito mode
3. Or clear browser cache
```

**Frontend Deployment: ✅ COMPLETE**

---

## 🔧 NGINX CONFIGURATION CHANGES

### Update nginx.conf
```powershell
# Edit local file
code nginx/nginx.conf

# Upload to server
scp nginx/nginx.conf root@165.99.59.47:/opt/utility-server/nginx/

# Test config
ssh root@165.99.59.47 "docker exec utility_nginx nginx -t"

# Reload if OK
ssh root@165.99.59.47 "docker exec utility_nginx nginx -s reload"
```

---

## 🗄️ DATABASE CHANGES

### Creating New Tables
```bash
# 1. Add model in backend/app/models/
# 2. Create migration script
ssh root@165.99.59.47 "cat > /tmp/add_table.py << 'EOF'
import sys
sys.path.insert(0, '/app')
from app.models import YOUR_MODEL_FILE
from app.core.database import Base, engine
Base.metadata.create_all(bind=engine)
print('Table created')
EOF"

# 3. Run migration
ssh root@165.99.59.47 "docker cp /tmp/add_table.py utility_backend:/app/ && docker exec utility_backend python add_table.py"

# 4. Verify
ssh root@165.99.59.47 "docker exec utility_postgres psql -U utility_user -d utility_db -c '\dt'"
```

### Backup Database
```bash
# Create backup
ssh root@165.99.59.47 "docker exec utility_postgres pg_dump -U utility_user utility_db > /tmp/backup_$(date +%Y%m%d_%H%M%S).sql"

# Copy to local
scp root@165.99.59.47:/tmp/backup_*.sql D:\backups\
```

### Restore Database
```bash
# Upload backup
scp D:\backups\backup_YYYYMMDD.sql root@165.99.59.47:/tmp/

# Restore
ssh root@165.99.59.47 "docker exec -i utility_postgres psql -U utility_user utility_db < /tmp/backup_YYYYMMDD.sql"
```

---

## 🐳 DOCKER CHANGES

### Rebuild Container
```bash
# Backend
ssh root@165.99.59.47 "cd /opt/utility-server && docker-compose build backend"
ssh root@165.99.59.47 "cd /opt/utility-server && docker-compose up -d backend"

# All services
ssh root@165.99.59.47 "cd /opt/utility-server && docker-compose build"
ssh root@165.99.59.47 "cd /opt/utility-server && docker-compose up -d"
```

### Update docker-compose.yml
```powershell
scp docker-compose.yml root@165.99.59.47:/opt/utility-server/
ssh root@165.99.59.47 "cd /opt/utility-server && docker-compose up -d"
```

---

## ✅ POST-DEPLOYMENT VERIFICATION

### 1. Container Health
```bash
ssh root@165.99.59.47 "docker ps"
# All containers should be "Up" and healthy
```

### 2. Backend Health
```bash
# Health endpoint
curl http://165.99.59.47/api/health

# Login test
$body = @{username='admin'; password='admin123'} | ConvertTo-Json
Invoke-WebRequest -Uri "http://165.99.59.47/api/auth/login" -Method POST -Body $body -ContentType "application/json"
```

### 3. Frontend Check
- [ ] Open http://165.99.59.47 (Incognito)
- [ ] Can see login page
- [ ] Can login successfully
- [ ] Dashboard loads
- [ ] No console errors
- [ ] Network tab shows /api/* calls (not localhost)

### 4. Database Check
```bash
ssh root@165.99.59.47 "docker exec utility_postgres psql -U utility_user -d utility_db -c 'SELECT COUNT(*) FROM users;'"
```

### 5. Check Logs
```bash
# Backend
ssh root@165.99.59.47 "docker logs utility_backend --tail=50"

# Nginx
ssh root@165.99.59.47 "docker logs utility_nginx --tail=50"

# Look for errors or warnings
```

---

## 🚨 ROLLBACK PROCEDURE

### If Backend Fails
```bash
# Restore old files from backup
ssh root@165.99.59.47 "cp -r /opt/utility-server/backend.backup/* /opt/utility-server/backend/"

# Restart
ssh root@165.99.59.47 "docker restart utility_backend"
```

### If Frontend Fails
```bash
# Restore old build
ssh root@165.99.59.47 "rm -rf /opt/utility-server/frontend/dist && mv /opt/utility-server/frontend/dist.backup.YYYYMMDD /opt/utility-server/frontend/dist"

# Reload nginx
ssh root@165.99.59.47 "docker exec utility_nginx nginx -s reload"
```

### If Database Fails
```bash
# Restore from backup
ssh root@165.99.59.47 "docker exec -i utility_postgres psql -U utility_user utility_db < /tmp/backup_YYYYMMDD.sql"
```

---

## 📝 DEPLOYMENT LOG TEMPLATE

```
Date: YYYY-MM-DD HH:MM
Deployed by: [Your Name]
Branch/Commit: [git branch/commit hash]

Changes:
- [ ] Backend: [describe changes]
- [ ] Frontend: [describe changes]
- [ ] Database: [describe changes]
- [ ] Config: [describe changes]

Deployment Steps:
- [ ] Backend deployed
- [ ] Frontend built and deployed
- [ ] Database migrated
- [ ] Nginx reloaded
- [ ] Verified working

Issues Encountered:
- [Any issues and how resolved]

Rollback Plan:
- [Steps if rollback needed]

Notes:
- [Any special notes]
```

---

## 🎯 QUICK DEPLOY COMMANDS

### Full Stack Deploy
```powershell
# Backend
scp -r backend/app root@165.99.59.47:/opt/utility-server/backend/
ssh root@165.99.59.47 "docker restart utility_backend"

# Frontend
cd frontend
$env:VITE_API_URL="/api"
npm run build
ssh root@165.99.59.47 "rm -rf /opt/utility-server/frontend/dist/*"
scp -r dist/* root@165.99.59.47:/opt/utility-server/frontend/dist/
$jsFile = (Get-ChildItem dist/assets/*.js).Name
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
ssh root@165.99.59.47 "sed -i 's|$jsFile|${jsFile}?v=$timestamp|' /opt/utility-server/frontend/dist/index.html"
ssh root@165.99.59.47 "docker exec utility_nginx nginx -s reload"

# Verify
ssh root@165.99.59.47 "docker ps"
ssh root@165.99.59.47 "docker logs utility_backend --tail=20"
```

---

## 🔗 Related Documents

- `PROJECT_OVERVIEW.md` - Project architecture
- `DEBUG_GUIDE.md` - Troubleshooting
- `DEPLOY.md` - Detailed deployment guide

---

**Last Updated**: November 21, 2025
**Version**: 1.0.0
