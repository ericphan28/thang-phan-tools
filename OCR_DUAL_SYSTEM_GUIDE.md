# 🎯 Dual OCR System - Tesseract + Adobe

## ✅ CONFIGURED! Pick Your OCR Strategy

Your system now supports **BOTH** OCR engines with intelligent fallback:

```
┌─────────────────────────────────────────┐
│   🔍 Image with Text                    │
│   ↓                                     │
│   ┌──────────────────┐                 │
│   │  Primary OCR     │                 │
│   │  (User Choice)   │                 │
│   └──────────────────┘                 │
│          ↓                              │
│     ✅ Success?                         │
│          ↓ No                           │
│   ┌──────────────────┐                 │
│   │  Fallback OCR    │                 │
│   │  (Auto Backup)   │                 │
│   └──────────────────┘                 │
│          ↓                              │
│     📝 Result                           │
└─────────────────────────────────────────┘
```

---

## 🎮 Control Panel: `backend/.env`

```env
# Choose your OCR priority:
OCR_PRIORITY="tesseract,adobe"    # FREE first, premium backup
# OR
OCR_PRIORITY="adobe,tesseract"    # BEST QUALITY first, free backup
```

---

## 🆚 Engine Comparison

| Feature | **Tesseract** | **Adobe PDF Services** |
|---------|---------------|------------------------|
| **Quality** | ⭐⭐⭐ 7/10 | ⭐⭐⭐⭐⭐ 10/10 |
| **Cost** | ✅ FREE | 💰 500/month free |
| **Speed** | ⚡ Fast (local) | 🌐 Medium (API) |
| **Accuracy** | Good | Excellent |
| **Layout** | Basic | Perfect |
| **Vietnamese** | ✅ Good | ✅ Perfect |
| **Languages** | 100+ | 50+ |
| **Internet** | ❌ Not needed | ✅ Required |
| **Installation** | 📥 Required | ☁️ Cloud-based |
| **Limit** | ♾️ Unlimited | 500/month |

---

## 🎯 Recommended Strategies

### Strategy 1: **FREE FIRST** (Default) ✨ RECOMMENDED
```env
OCR_PRIORITY="tesseract,adobe"
```

**When to use**: Personal projects, high volume, budget-conscious

**Flow**:
1. ✅ Tesseract tries first (free, unlimited)
2. ⚠️ If fails → Adobe kicks in (backup quality)
3. 💡 Saves Adobe quota for when you really need it

**Best for**:
- Testing & development
- High volume OCR (100+ images/day)
- Budget-conscious projects
- Offline processing

---

### Strategy 2: **QUALITY FIRST**
```env
OCR_PRIORITY="adobe,tesseract"
```

**When to use**: Production, critical documents, business

**Flow**:
1. ✅ Adobe tries first (best quality)
2. ⚠️ If quota exhausted → Tesseract continues (still works)
3. 💡 Never stops working, even after Adobe quota runs out

**Best for**:
- Production applications
- Business documents
- Vietnamese text (diacritics critical)
- Layout-sensitive documents
- Low volume (<500 docs/month)

---

### Strategy 3: **TESSERACT ONLY**
```env
OCR_PRIORITY="tesseract"
```

**When to use**: 100% free, unlimited

**Flow**:
1. ✅ Tesseract only (no Adobe fallback)
2. ⚠️ If Tesseract fails → Error returned
3. 💡 Zero cloud dependency

**Best for**:
- No internet access
- Unlimited volume needed
- Adobe not configured

---

### Strategy 4: **ADOBE ONLY**
```env
OCR_PRIORITY="adobe"
```

**When to use**: Premium quality only

**Flow**:
1. ✅ Adobe only (no Tesseract fallback)
2. ⚠️ If quota exhausted → Error returned
3. 💡 Guaranteed quality

**Best for**:
- Critical documents only
- Quality over availability
- Low volume (<500/month)

---

## 🚀 Quick Setup

### Option A: Tesseract (FREE) - 5 minutes

```powershell
# Method 1: Chocolatey (fastest)
choco install tesseract

# Method 2: Batch script
.\install-tesseract.bat

# Method 3: Manual
# Download: https://github.com/UB-Mannheim/tesseract/wiki
```

**Then set**:
```env
OCR_PRIORITY="tesseract,adobe"
```

✅ **Done!** OCR works with unlimited free usage.

---

### Option B: Adobe (PREMIUM) - Already configured! ✅

Your Adobe credentials are already in `.env`:
```env
USE_ADOBE_PDF_API=true
PDF_SERVICES_CLIENT_ID="d46f7e349fe44f7ca933c216eaa9bd48"
PDF_SERVICES_CLIENT_SECRET="p8e-Bg7-Ce-***"
```

**Just set**:
```env
OCR_PRIORITY="adobe,tesseract"
```

✅ **Done!** You get premium quality OCR.

---

### Option C: BOTH (BEST) - Recommended ⭐

1. Install Tesseract: `choco install tesseract`
2. Adobe already configured ✅
3. Set priority: `OCR_PRIORITY="tesseract,adobe"`
4. Restart backend

**Result**: 
- ✅ Unlimited free OCR (Tesseract)
- ✅ Premium backup (Adobe kicks in if needed)
- ✅ Never fails (dual redundancy)
- ✅ Best of both worlds!

---

## 📊 Real-World Examples

### Example 1: Startup (500 docs/day)
```env
OCR_PRIORITY="tesseract,adobe"
```
- Day 1-30: Tesseract handles all 15,000 docs (free)
- Adobe: Unused, available as emergency backup
- **Cost**: $0

---

### Example 2: Enterprise (100 critical docs/month)
```env
OCR_PRIORITY="adobe,tesseract"
```
- Critical docs: Adobe (perfect quality)
- Non-critical: Adobe
- After quota: Tesseract continues
- **Cost**: $0 (within free tier)

---

### Example 3: Mixed Volume (1000 docs/month)
```env
OCR_PRIORITY="tesseract,adobe"
```
- Tesseract: 1000 docs (free)
- Adobe: Standby backup (unused = saved quota)
- **Cost**: $0

---

## 🔧 Current Configuration

### ✅ What You Have Now:

```env
# Tesseract: Not installed yet
# Adobe: ✅ Configured with valid credentials
# Default: "tesseract,adobe"
```

**Recommendation**: 
1. Install Tesseract (5 min): `choco install tesseract`
2. Keep `OCR_PRIORITY="tesseract,adobe"`
3. Enjoy unlimited free OCR with premium backup! 🎉

---

## 🧪 Testing

```powershell
# After setup, test OCR:
python test_ocr_simple.py

# Should show:
# ✅ OCR Extract (vi,en) - PASS (ocr_engine: tesseract)
# ✅ OCR Vietnamese - PASS (ocr_engine: tesseract)
# ✅ OCR Auto-Detect - PASS (ocr_engine: tesseract)
```

---

## 🎛️ How to Change Strategy

Edit `backend/.env`, change ONE line:

```env
# Current (FREE FIRST):
OCR_PRIORITY="tesseract,adobe"

# Change to QUALITY FIRST:
OCR_PRIORITY="adobe,tesseract"
```

**Restart backend** → Done! ✅

---

## 📈 Usage Tracking

Each OCR response includes `ocr_engine` field:

```json
{
  "text": "Extracted text...",
  "confidence": 0.95,
  "ocr_engine": "tesseract"  // or "adobe"
}
```

Track which engine was used for each request!

---

## 🆘 Troubleshooting

### ❌ "No OCR provider available"
**Solution**: Install Tesseract OR configure Adobe credentials

### ❌ "Tesseract not found"
**Solution**: Run `choco install tesseract`, restart backend

### ❌ "Adobe quota exceeded"
**Solution**: 
- Wait for next month (quota resets)
- OR change to `OCR_PRIORITY="tesseract"` (unlimited)

### ⚠️ "Tesseract failed, trying adobe..."
**This is normal!** Fallback working as expected.

---

## 🎯 TL;DR

**Best Setup (Recommended)**:
1. Install Tesseract: `choco install tesseract`
2. Keep Adobe credentials (already configured)
3. Use: `OCR_PRIORITY="tesseract,adobe"`
4. Restart backend

**Result**: Unlimited free OCR + premium backup! 🚀

---

## 📞 More Info

- Tesseract install guide: `install-tesseract.bat`
- Adobe setup guide: `ADOBE_CREDENTIALS_GUIDE.md`
- OCR test script: `test_ocr_simple.py`
- General OCR info: `OCR_SETUP_GUIDE.md`

---

**Status**: ✅ Adobe configured, Tesseract pending (optional)
