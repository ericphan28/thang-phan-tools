# 🔧 TROUBLESHOOTING & DEBUGGING GUIDE

## 📋 Quick Reference

### Most Common Issues (đã fix thành công)

| Issue | Symptom | Solution | Status |
|-------|---------|----------|--------|
| Frontend calls localhost:8000 | ERR_CONNECTION_REFUSED | Build với `VITE_API_URL="/api"` | ✅ FIXED |
| Table activity_logs not found | 500 Internal Server Error | Run migration script | ✅ FIXED |
| Browser cache old JS file | Old UI, features broken | Hard refresh + cache buster | ✅ FIXED |
| Mobile not responsive | Layout broken on mobile | Added responsive classes | ✅ FIXED |
| Login 500 error | Cannot login | Created activity_logs table | ✅ FIXED |

---

## 🎨 FRONTEND ISSUES

### Issue #1: API calls localhost:8000

**Root Cause**: Vite build cache hoặc env variable không set

**Solution**:
```powershell
cd frontend
Remove-Item -Recurse -Force node_modules, dist, node_modules/.vite
npm install
$env:VITE_API_URL="/api"
npm run build

# Deploy
ssh root@165.99.59.47 "rm -rf /opt/utility-server/frontend/dist/*"
scp -r dist/* root@165.99.59.47:/opt/utility-server/frontend/dist/

# Cache buster
$timestamp = Get-Date -Format "yyyyMMddHHmm"
$jsFile = (Get-ChildItem dist/assets/*.js).Name
ssh root@165.99.59.47 "sed -i 's|$jsFile|${jsFile}?v=$timestamp|' /opt/utility-server/frontend/dist/index.html"
ssh root@165.99.59.47 "docker exec utility_nginx nginx -s reload"
```

**Browser**: CTRL + SHIFT + R (hard refresh)

---

### Issue #2: Browser loading old file

**Check current file**:
```bash
# Server
ssh root@165.99.59.47 "ls -lh /opt/utility-server/frontend/dist/assets/*.js"

# Browser DevTools → Network tab → look for index-*.js
```

**Solution**: Add/update cache buster
```bash
ssh root@165.99.59.47 "sed -i 's|index-OLD.js|index-NEW.js?v=VERSION|' /opt/utility-server/frontend/dist/index.html"
```

---

## 🔙 BACKEND ISSUES

### Issue #3: 500 Internal Server Error on login

**Check logs**:
```bash
ssh root@165.99.59.47 "docker logs --tail=50 utility_backend"
```

**Common causes**:

**A. Table not found (activity_logs)**
```bash
# Create migration script
ssh root@165.99.59.47 "cat > /tmp/migrate.py << 'EOF'
import sys
sys.path.insert(0, '/app')
from app.models import auth_models
from app.core.database import Base, engine
Base.metadata.create_all(bind=engine)
print('Tables created')
from sqlalchemy import inspect
tables = inspect(engine).get_table_names()
print(f'Tables: {tables}')
EOF"

# Run
ssh root@165.99.59.47 "docker cp /tmp/migrate.py utility_backend:/app/ && docker exec utility_backend python migrate.py"

# Verify
ssh root@165.99.59.47 "docker exec utility_postgres psql -U utility_user -d utility_db -c '\dt'"
```

**B. Import error (ModuleNotFoundError)**
```bash
# Keep models/__init__.py EMPTY to avoid circular imports
ssh root@165.99.59.47 "echo '# Empty init file' > /opt/utility-server/backend/app/models/__init__.py"
ssh root@165.99.59.47 "docker restart utility_backend"
```

**C. Environment variables missing**
```bash
ssh root@165.99.59.47 "cat /opt/utility-server/.env"
ssh root@165.99.59.47 "docker restart utility_backend"
```

---

### Issue #4: Backend container keeps restarting

**Check logs**:
```bash
ssh root@165.99.59.47 "docker logs utility_backend --tail=100"
```

**Common causes**:
- Import errors → Fix models/__init__.py
- Database connection failed → Check postgres container
- Port conflict → Check if 8000 already used

---

## 🗄️ DATABASE ISSUES

### Issue #5: Cannot connect to database

```bash
# Check postgres
ssh root@165.99.59.47 "docker ps | grep postgres"
ssh root@165.99.59.47 "docker logs utility_postgres --tail=30"

# Test connection
ssh root@165.99.59.47 "docker exec utility_postgres psql -U utility_user -d utility_db -c 'SELECT 1;'"

# Restart if needed
ssh root@165.99.59.47 "docker restart utility_postgres"
ssh root@165.99.59.47 "sleep 5 && docker restart utility_backend"
```

---

### Issue #6: Missing table

**List all tables**:
```bash
ssh root@165.99.59.47 "docker exec utility_postgres psql -U utility_user -d utility_db -c '\dt'"
```

**Expected tables**:
- users
- roles
- permissions
- user_roles
- activity_logs
- api_keys
- api_logs
- faces
- processed_files

**If missing**: Run migration (see Issue #3A)

---

## 🚢 DEPLOYMENT ISSUES

### Issue #7: Changes not reflecting

**Backend changes**:
```bash
# Upload files
scp -r backend/app root@165.99.59.47:/opt/utility-server/backend/

# Restart
ssh root@165.99.59.47 "docker restart utility_backend"

# Check logs
ssh root@165.99.59.47 "docker logs utility_backend --tail=30"
```

**Frontend changes**:
```bash
# Build
cd frontend
$env:VITE_API_URL="/api"
npm run build

# Deploy
ssh root@165.99.59.47 "rm -rf /opt/utility-server/frontend/dist/*"
scp -r dist/* root@165.99.59.47:/opt/utility-server/frontend/dist/

# Cache buster
$jsFile = (Get-ChildItem dist/assets/*.js).Name
$timestamp = Get-Date -Format "yyyyMMddHHmm"
ssh root@165.99.59.47 "sed -i 's|$jsFile|${jsFile}?v=$timestamp|' /opt/utility-server/frontend/dist/index.html"

# Reload nginx
ssh root@165.99.59.47 "docker exec utility_nginx nginx -s reload"
```

**Browser**: Hard refresh (CTRL + SHIFT + R)

---

### Issue #8: Nginx 502 Bad Gateway

**Cause**: Backend not running

**Solution**:
```bash
# Check backend
ssh root@165.99.59.47 "docker ps | grep backend"

# If not running, check why
ssh root@165.99.59.47 "docker logs utility_backend --tail=100"

# Restart
ssh root@165.99.59.47 "docker restart utility_backend"
```

---

## 🔍 DEBUG CHECKLIST

Always check in this order:

1. **Logs**
```bash
ssh root@165.99.59.47 "docker logs utility_backend --tail=50"
ssh root@165.99.59.47 "docker logs utility_nginx --tail=50"
```

2. **Container status**
```bash
ssh root@165.99.59.47 "docker ps -a"
```

3. **Database**
```bash
ssh root@165.99.59.47 "docker exec utility_postgres psql -U utility_user -d utility_db -c '\dt'"
```

4. **Browser**
- F12 → Console (check errors)
- F12 → Network (check requests)
- localStorage.getItem('access_token')

---

## 🛠️ USEFUL COMMANDS

### System Status
```bash
# All containers
ssh root@165.99.59.47 "docker ps"

# Container logs
ssh root@165.99.59.47 "docker logs CONTAINER_NAME --tail=50"

# Disk usage
ssh root@165.99.59.47 "df -h"
ssh root@165.99.59.47 "docker system df"
```

### Database
```bash
# Connect
ssh root@165.99.59.47 "docker exec -it utility_postgres psql -U utility_user -d utility_db"

# List tables
ssh root@165.99.59.47 "docker exec utility_postgres psql -U utility_user -d utility_db -c '\dt'"

# Count records
ssh root@165.99.59.47 "docker exec utility_postgres psql -U utility_user -d utility_db -c 'SELECT COUNT(*) FROM users;'"

# Show users
ssh root@165.99.59.47 "docker exec utility_postgres psql -U utility_user -d utility_db -c 'SELECT id, username, email, is_active FROM users;'"
```

### Restart Services
```bash
# Individual
ssh root@165.99.59.47 "docker restart utility_backend"
ssh root@165.99.59.47 "docker restart utility_nginx"
ssh root@165.99.59.47 "docker restart utility_postgres"

# All
ssh root@165.99.59.47 "cd /opt/utility-server && docker-compose restart"
```

### Clean Up
```bash
# Remove unused images
ssh root@165.99.59.47 "docker image prune -a"

# Remove stopped containers
ssh root@165.99.59.47 "docker container prune"

# Clean all
ssh root@165.99.59.47 "docker system prune -a"
```

---

## 📞 Getting Help

**Information to collect**:
```bash
# System
ssh root@165.99.59.47 "uname -a && docker --version"

# Containers
ssh root@165.99.59.47 "docker ps -a"

# Logs
ssh root@165.99.59.47 "docker logs utility_backend --tail=100"
ssh root@165.99.59.47 "docker logs utility_nginx --tail=100"

# Database
ssh root@165.99.59.47 "docker exec utility_postgres psql -U utility_user -d utility_db -c '\dt'"
```

**What to include**:
- What you were trying to do
- What happened instead
- Error messages (exact text)
- Browser console errors
- Backend logs
- When it started
- What changed recently

---

**Last Updated**: November 21, 2025
