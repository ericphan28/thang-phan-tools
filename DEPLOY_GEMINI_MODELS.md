# 🚀 Deploy Gemini Model Selection to Production

**Server:** 165.99.59.47  
**Feature:** Gemini Model Selection (10 models)  
**Time:** ~10 minutes  
**Date:** December 3, 2025

---

## 📋 What's Being Deployed

### Backend Changes:
- ✅ 10 Gemini models configuration (GEMINI_MODELS)
- ✅ New API endpoint: GET `/api/v1/documents/gemini/models`
- ✅ Updated PDF conversion endpoint to accept `gemini_model` parameter
- ✅ Default model changed to `gemini-2.5-flash`

### Frontend Changes:
- ✅ New component: `GeminiModelSelector.tsx` (320 lines)
- ✅ New UI components: `select.tsx`
- ✅ Updated: `ToolsPage.tsx`, `App.tsx`
- ✅ New dependencies: @radix-ui/react-select, @radix-ui/react-tooltip

---

## ✅ Pre-Deploy Checklist

### Local Verification
- [x] Backend tested locally (port 8000)
- [x] Frontend tested locally (port 3000)
- [x] No compile errors
- [x] Dependencies installed
- [ ] Code committed to Git
- [ ] .env updated with production values

### Files to Deploy
**Backend (3 files):**
- `backend/app/services/document_service.py` (MODIFIED +180 lines)
- `backend/app/api/v1/endpoints/documents.py` (MODIFIED +25 lines)
- `backend/.env` (MODIFIED - GEMINI_MODEL updated)
- `backend/requirements.txt` (CHECK - should include google-generativeai)

**Frontend (All files):**
- Build entire frontend (npm run build)
- New components added
- New dependencies installed

---

## 🚀 Deployment Steps

### Option A: Quick Deploy (Recommended) ⚡

#### Step 1: Commit Changes to Git
```powershell
# On local machine (D:\thang\utility-server)
cd D:\thang\utility-server

# Check what changed
git status

# Add all changes
git add .

# Commit with descriptive message
git commit -m "feat: Add Gemini model selection feature with 10 models

- Added GEMINI_MODELS configuration (10 models)
- Created GeminiModelSelector component
- Added model selection to PDF to Word conversion
- Updated default model to gemini-2.5-flash
- Added GET /gemini/models API endpoint
- Installed @radix-ui/react-select and @radix-ui/react-tooltip"

# Push to GitHub
git push origin main
```

#### Step 2: SSH to Production Server
```bash
ssh root@165.99.59.47
```

#### Step 3: Run Deployment Script
```bash
cd /opt/utility-server

# Create deployment script
cat > deploy-gemini-models.sh << 'EOF'
#!/bin/bash
set -e

echo "========================================"
echo "🚀 DEPLOYING GEMINI MODEL SELECTION"
echo "========================================"
echo ""

cd /opt/utility-server

# Backup current code
echo "📦 Creating backup..."
tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz backend/app frontend/src 2>/dev/null || true

# Pull latest code
echo ""
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Update backend .env if needed
echo ""
echo "🔧 Checking backend .env..."
if ! grep -q "gemini-2.5-flash" backend/.env 2>/dev/null; then
    echo "⚠️  Updating GEMINI_MODEL to gemini-2.5-flash..."
    sed -i 's/GEMINI_MODEL=.*/GEMINI_MODEL="gemini-2.5-flash"/' backend/.env
    echo "✅ Updated"
else
    echo "✅ Already up to date"
fi

# Check Python dependencies
echo ""
echo "📦 Checking Python dependencies..."
if grep -q "google-generativeai" backend/requirements.txt; then
    echo "✅ google-generativeai found in requirements.txt"
else
    echo "⚠️  google-generativeai NOT in requirements.txt - adding..."
    echo "google-generativeai>=0.3.0" >> backend/requirements.txt
fi

# Rebuild backend (if dependencies changed)
echo ""
echo "🔨 Rebuilding backend container..."
docker-compose build backend --no-cache

# Install frontend dependencies
echo ""
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
echo "✅ Dependencies installed"

# Build frontend for production
echo ""
echo "🏗️  Building frontend for production..."
npm run build
echo "✅ Frontend built"

cd ..

# Restart services
echo ""
echo "🔄 Restarting services..."
docker-compose down
docker-compose up -d

# Wait for services to start
echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo ""
echo "📊 Service status:"
docker-compose ps

# Test backend API
echo ""
echo "🧪 Testing backend API..."
if curl -s http://localhost:8000/api/v1/health | grep -q "healthy"; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend health check failed"
fi

# Test Gemini models endpoint
echo ""
echo "🧪 Testing Gemini models endpoint..."
if curl -s http://localhost:8000/api/v1/documents/gemini/models | grep -q "gemini-2.5-flash"; then
    echo "✅ Gemini models endpoint working!"
    echo ""
    echo "Available models:"
    curl -s http://localhost:8000/api/v1/documents/gemini/models | python3 -m json.tool | grep '"name"' | head -5
else
    echo "⚠️  Gemini models endpoint check failed"
fi

echo ""
echo "========================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "========================================"
echo ""
echo "🌐 Frontend: http://165.99.59.47:3000"
echo "🔧 Backend:  http://165.99.59.47:8000"
echo "📚 API Docs: http://165.99.59.47:8000/docs"
echo ""
echo "🎯 New endpoint: GET /api/v1/documents/gemini/models"
echo "🎮 Test: Go to Tools page → PDF to Word → Enable Gemini → See model selector!"
echo ""
EOF

# Make executable
chmod +x deploy-gemini-models.sh

# Run deployment
./deploy-gemini-models.sh
```

#### Step 4: Verify Deployment
```bash
# Check logs
docker-compose logs -f backend --tail=50

# Look for:
# - "✅ Gemini API enabled - Model: Gemini 2.5 Flash (Quality: 9/10)"
# - No errors in startup

# Test API manually
curl http://localhost:8000/api/v1/documents/gemini/models | python3 -m json.tool

# Should return JSON with all 10 models
```

---

### Option B: Manual Deploy (If Git Not Used) 📤

#### Step 1: Build Frontend Locally
```powershell
# On local machine
cd D:\thang\utility-server\frontend

# Install dependencies
npm install

# Build for production
npm run build

# Result: frontend/dist folder created
```

#### Step 2: Upload Files via SCP

**Upload Backend Files:**
```powershell
# Upload modified service file
scp backend/app/services/document_service.py root@165.99.59.47:/opt/utility-server/backend/app/services/

# Upload modified endpoint file
scp backend/app/api/v1/endpoints/documents.py root@165.99.59.47:/opt/utility-server/backend/app/api/v1/endpoints/

# Upload .env (CAREFUL - contains secrets!)
scp backend/.env root@165.99.59.47:/opt/utility-server/backend/
```

**Upload Frontend Build:**
```powershell
# Upload entire dist folder
scp -r frontend/dist/* root@165.99.59.47:/opt/utility-server/frontend/dist/
```

#### Step 3: SSH and Restart Services
```bash
ssh root@165.99.59.47

cd /opt/utility-server

# Restart containers
docker-compose restart backend
docker-compose restart frontend

# Check status
docker-compose ps
```

---

## 🧪 Post-Deployment Testing

### 1. Backend API Test
```bash
# On server or from local machine
curl http://165.99.59.47:8000/api/v1/documents/gemini/models

# Should return JSON with 10 models
```

### 2. Frontend Test
```
Open browser: http://165.99.59.47:3000/tools

Steps:
1. Upload a PDF file
2. Click "PDF to Word"
3. Check ✅ "Sử dụng Gemini API"
4. 🆕 Verify model selector dropdown appears
5. 🆕 Click dropdown - should show 10 models
6. 🆕 See quality/speed bars and cost info
7. Select a model (try gemini-2.5-flash)
8. Click "Convert"
9. Verify conversion works
10. Check success message shows model name
```

### 3. Smoke Tests
```bash
# Test default model (no selection)
curl -X POST http://165.99.59.47:8000/api/v1/documents/convert/pdf-to-word \
  -F "file=@test.pdf" \
  -F "use_gemini=true"
# Should use gemini-2.5-flash (default)

# Test specific model selection
curl -X POST http://165.99.59.47:8000/api/v1/documents/convert/pdf-to-word \
  -F "file=@test.pdf" \
  -F "use_gemini=true" \
  -F "gemini_model=gemini-2.5-flash-lite"
# Should use flash-lite model
```

---

## ⚙️ Environment Configuration

### Production .env (Backend)
```env
# ================================
# Google Gemini API
# ================================
GEMINI_API_KEY=AIzaSyC3X92AYepFgVhIidH4QR0umGXZ5XFP27A

# 🆕 UPDATED: New default model (December 2025)
GEMINI_MODEL="gemini-2.5-flash"

# OLD (before this update):
# GEMINI_MODEL="gemini-2.0-flash-exp"
```

**Important:** Verify your production `.env` has the correct GEMINI_API_KEY!

---

## 🐛 Troubleshooting

### Issue: Model selector doesn't appear
**Cause:** Frontend not built/deployed correctly  
**Fix:**
```bash
cd /opt/utility-server/frontend
npm install
npm run build
docker-compose restart frontend
```

### Issue: "Model not found" error
**Cause:** Backend code not updated  
**Fix:**
```bash
# Verify backend file updated
cat backend/app/services/document_service.py | grep "GEMINI_MODELS ="

# Should see GEMINI_MODELS dictionary with 10+ models
# If not, re-upload the file
```

### Issue: Backend won't start
**Cause:** Python dependency missing  
**Fix:**
```bash
# Check requirements.txt
cat backend/requirements.txt | grep "google-generativeai"

# If missing, add it
echo "google-generativeai>=0.3.0" >> backend/requirements.txt

# Rebuild container
docker-compose build backend --no-cache
docker-compose up -d backend
```

### Issue: API returns 500 error
**Cause:** GEMINI_API_KEY not set or invalid  
**Fix:**
```bash
# Check .env file
cat backend/.env | grep GEMINI_API_KEY

# Test API key manually
python3 << EOF
import google.generativeai as genai
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-2.5-flash")
print("✅ API key valid!")
EOF
```

### Issue: Dropdown shows no models
**Cause:** API endpoint not returning data  
**Fix:**
```bash
# Test endpoint
curl http://localhost:8000/api/v1/documents/gemini/models

# Check backend logs
docker-compose logs backend | grep -i "gemini"

# Should see: "✅ Gemini API enabled - Model: Gemini 2.5 Flash"
```

---

## 📊 Monitoring

### After Deployment, Monitor:

**Backend Logs:**
```bash
docker-compose logs -f backend | grep -i "gemini"
```

**Look for:**
- ✅ "✅ Gemini API enabled - Model: Gemini 2.5 Flash (Quality: 9/10)"
- ✅ "Starting Gemini conversion with Gemini 2.5 Flash"
- ❌ Any errors about models not found

**Frontend Access:**
```bash
# Check Nginx is serving files
curl -I http://localhost:3000

# Should return 200 OK
```

**Resource Usage:**
```bash
docker stats

# Check CPU/Memory of backend container
# Model selection adds minimal overhead
```

---

## 🔄 Rollback Plan

If something goes wrong:

### Quick Rollback (Git)
```bash
cd /opt/utility-server

# See recent commits
git log --oneline -5

# Rollback to previous version
git reset --hard HEAD~1

# Rebuild and restart
docker-compose build backend
docker-compose up -d
```

### Manual Rollback
```bash
# Restore from backup
cd /opt/utility-server
tar -xzf backup-YYYYMMDD-HHMMSS.tar.gz

# Restart services
docker-compose restart
```

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Code tested locally
- [ ] Git committed and pushed
- [ ] .env checked (GEMINI_MODEL updated)
- [ ] Dependencies verified
- [ ] Backup created

### Deployment
- [ ] Code pulled/uploaded
- [ ] Backend rebuilt (if needed)
- [ ] Frontend rebuilt
- [ ] Services restarted
- [ ] Health check passed

### Post-Deployment
- [ ] API endpoint tested (`/gemini/models`)
- [ ] Frontend dropdown visible
- [ ] PDF conversion works with model selection
- [ ] Logs checked for errors
- [ ] User notification sent

---

## 📈 Success Metrics

**Feature is live if:**
- ✅ GET `/api/v1/documents/gemini/models` returns 10 models
- ✅ Frontend shows model selector when Gemini enabled
- ✅ Users can select different models
- ✅ PDF conversion works with selected model
- ✅ Success message shows model name used

---

## 🎉 Post-Deployment

### Notify Users
```
📢 NEW FEATURE DEPLOYED! 🚀

🎯 Gemini Model Selection
Users can now choose from 10 different Gemini AI models when converting PDF to Word!

✨ Features:
- 10 models to choose from
- Visual quality/speed indicators
- Cost transparency
- Smart defaults (gemini-2.5-flash)

🎮 Try it now:
1. Go to Tools page
2. Upload PDF
3. Click "PDF to Word"
4. Enable Gemini API
5. See the new model selector! 🎨

💡 Models available:
- Gemini 3 Pro (cutting-edge) 🚀
- Gemini 2.5 Flash (recommended) ⭐
- Gemini 2.5 Flash-Lite (budget) 💰
- And 7 more options!
```

---

## 📞 Support

**Issues?** Check:
1. Backend logs: `docker-compose logs backend`
2. Frontend console: Browser DevTools (F12)
3. API health: `curl http://localhost:8000/api/v1/health`
4. Gemini models: `curl http://localhost:8000/api/v1/documents/gemini/models`

**Still stuck?** Review:
- `GEMINI_MODEL_SELECTION_IMPLEMENTATION.md` (implementation details)
- `GEMINI_MODELS_COMPLETE_GUIDE_2025.md` (model reference)
- `DEPLOYMENT_CHECKLIST.md` (general deployment)

---

**Created:** December 3, 2025  
**Status:** ✅ Ready to Deploy  
**Estimated Time:** 10 minutes  
**Complexity:** Medium (frontend rebuild required)

🚀 **DEPLOY NOW!** Run Option A for fastest deployment.
