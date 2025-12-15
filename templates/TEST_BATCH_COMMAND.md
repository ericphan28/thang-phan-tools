# Testing Batch Document Generation

## The Problem

You're getting a 400 error because:
- ❌ You're using the **single** endpoint `/pdf/generate`
- ❌ But uploading `thiep_khai_truong_batch.json` which is an **array**
- ✅ Single endpoint expects a **single JSON object**, not an array

## Quick Fixes

### Fix 1: Test Single Endpoint with Single Sample

In your frontend, upload these files **individually**:
- `thiep_khai_truong_sample1.json` ✅
- `thiep_khai_truong_sample2.json` ✅
- `thiep_khai_truong_sample3.json` ✅

**NOT** the batch file (`thiep_khai_truong_batch.json`) ❌

---

### Fix 2: Test Batch Endpoint with PowerShell

Since your frontend doesn't have a batch UI yet, use PowerShell:

```powershell
# Navigate to templates folder
cd d:\thang\utility-server\templates

# Test 1: Generate 5 invitations → MERGE into 1 PDF (5 pages)
curl.exe -X POST "http://localhost:8000/api/v1/documents/pdf/generate-batch" `
  -F "template_file=@thiep_khai_truong.docx" `
  -F "json_data=@thiep_khai_truong_batch.json" `
  -F "output_format=pdf" `
  -F "merge_output=true" `
  -o test_batch_merged_5pages.pdf

# Check the result
if (Test-Path "test_batch_merged_5pages.pdf") {
    Write-Host "✅ SUCCESS! Check test_batch_merged_5pages.pdf" -ForegroundColor Green
    Write-Host "📄 Should have 5 pages (one per guest)" -ForegroundColor Cyan
} else {
    Write-Host "❌ FAILED! Check server logs" -ForegroundColor Red
}

# Test 2: Generate 5 invitations → ZIP with 5 separate PDFs
curl.exe -X POST "http://localhost:8000/api/v1/documents/pdf/generate-batch" `
  -F "template_file=@thiep_khai_truong.docx" `
  -F "json_data=@thiep_khai_truong_batch.json" `
  -F "output_format=pdf" `
  -F "merge_output=false" `
  -o test_batch_separate.zip

# Check the result
if (Test-Path "test_batch_separate.zip") {
    Write-Host "✅ SUCCESS! Check test_batch_separate.zip" -ForegroundColor Green
    Write-Host "📦 Should contain 5 individual PDF files" -ForegroundColor Cyan
    # Extract to check
    Expand-Archive -Path "test_batch_separate.zip" -DestinationPath "test_batch_output" -Force
    Write-Host "📂 Extracted to: test_batch_output/" -ForegroundColor Yellow
} else {
    Write-Host "❌ FAILED! Check server logs" -ForegroundColor Red
}

# Test 3: Birthday batch (3 invitations merged)
curl.exe -X POST "http://localhost:8000/api/v1/documents/pdf/generate-batch" `
  -F "template_file=@thiep_sinh_nhat.docx" `
  -F "json_data=@thiep_sinh_nhat_batch.json" `
  -F "output_format=pdf" `
  -F "merge_output=true" `
  -o test_birthday_batch_3pages.pdf

if (Test-Path "test_birthday_batch_3pages.pdf") {
    Write-Host "✅ Birthday batch SUCCESS! 3 pages" -ForegroundColor Green
} else {
    Write-Host "❌ Birthday batch FAILED!" -ForegroundColor Red
}
```

---

## Alternative: Use curl for Single Document

If you want to test via command line with single JSON:

```powershell
cd d:\thang\utility-server\templates

# Read single JSON (not array)
$jsonContent = Get-Content "thiep_khai_truong_sample1.json" -Raw

# Test single endpoint
curl.exe -X POST "http://localhost:8000/api/v1/documents/pdf/generate" `
  -F "template_file=@thiep_khai_truong.docx" `
  -F "json_data=$jsonContent" `
  -F "output_format=pdf" `
  -o test_single.pdf

if (Test-Path "test_single.pdf") {
    Write-Host "✅ Single document SUCCESS!" -ForegroundColor Green
} else {
    Write-Host "❌ FAILED! Check server logs" -ForegroundColor Red
}
```

---

## Understanding the Difference

### Single Endpoint: `/pdf/generate`
- **Expects:** Single JSON object `{...}`
- **Returns:** One PDF file
- **Example JSON:**
  ```json
  {
    "guest": {"name": "Ông A", "title": "Giám Đốc"},
    "business": {"name": "Showroom", "slogan": "..."}
  }
  ```

### Batch Endpoint: `/pdf/generate-batch`
- **Expects:** JSON array `[{...}, {...}, {...}]`
- **Returns:** Merged PDF or ZIP with multiple files
- **Example JSON:**
  ```json
  [
    {"guest": {"name": "Ông A", ...}},
    {"guest": {"name": "Bà B", ...}},
    {"guest": {"name": "Ông C", ...}}
  ]
  ```

---

## Your Current Error

```
errorCode=BAD_REQUEST
statusCode=400
```

This happens because:
1. Frontend calls `/pdf/generate` (single)
2. You upload `thiep_khai_truong_batch.json` (array)
3. Adobe API receives: `[{...}, {...}]` instead of `{...}`
4. Adobe rejects: "Bad Request" ❌

---

## Quick Solution NOW

**In your frontend:**
1. Click "Choose JSON file"
2. Select `thiep_khai_truong_sample1.json` (NOT the batch file!)
3. Upload template `thiep_khai_truong.docx`
4. Click Generate
5. Should work! ✅

---

## To Use Batch Feature

You need to either:
1. Use PowerShell commands above (recommended for now)
2. Or add batch UI to frontend (future enhancement)

---

## Server Status Check

Make sure backend is running:
```powershell
# Check if server responds
curl.exe http://localhost:8000/health
```

Expected: `{"status":"healthy"}`
