# 🔧 BLOB RESPONSE ERROR HANDLING - FIXED!

**Ngày**: 25/11/2024  
**Issue**: Frontend không hiển thị được error message từ backend khi dùng `responseType: 'blob'`

---

## 🐛 Root Cause

### Problem
Khi axios request có `responseType: 'blob'`, **cả success và error responses đều trở thành Blob**:

```typescript
const response = await axios.post(url, formData, {
  responseType: 'blob',  // ← Vấn đề ở đây!
});
```

**Kết quả**:
- ✅ Success (200): Blob chứa PDF file → OK
- ❌ Error (400): Blob chứa JSON error → Không parse được!

### Error Log
```
Split error: AxiosError {
  response: {
    data: Blob,           // ← Error message ở trong Blob này!
    status: 400,
    statusText: 'Bad Request'
  }
}
```

Backend đã trả về friendly message:
```
😔 Rất tiếc! File PDF này có chữ ký điện tử...
```

Nhưng frontend không đọc được vì nó là **Blob**, không phải JSON!

---

## ✅ Solution

### 1. Parse Blob to JSON

**Before** (Không đọc được Blob):
```typescript
const getErrorMessage = (error: any): string => {
  const detail = error.response?.data?.detail;  // ← undefined (vì data là Blob)
  return detail || 'Lỗi...';
};
```

**After** (Parse Blob thành JSON):
```typescript
const getErrorMessage = async (error: any): Promise<string> => {
  // Handle Blob error responses
  if (error.response?.data instanceof Blob) {
    try {
      const text = await error.response.data.text();  // Blob → text
      const json = JSON.parse(text);                  // text → JSON
      if (json.detail) {
        return json.detail;  // ← Lấy được friendly message!
      }
    } catch (e) {
      // Parsing failed, use fallback
    }
  }
  
  // Handle normal JSON responses
  const detail = error.response?.data?.detail;
  if (detail) return detail;
  
  // Fallback messages
  if (error.response?.status === 400) {
    return '❌ Yêu cầu không hợp lệ...';
  }
  
  return error.message || 'Đã có lỗi xảy ra';
};
```

### 2. Async Wrapper for Toast

Vì `getErrorMessage` giờ là async, cần wrapper:

```typescript
const showErrorToast = async (error: any) => {
  const errorMsg = await getErrorMessage(error);
  toast.error(errorMsg, { duration: 6000 });
};
```

### 3. Update All Catch Blocks

**Before**:
```typescript
catch (error: any) {
  const errorMsg = getErrorMessage(error);  // ← Promise!
  toast.error(errorMsg, { duration: 6000 });  // ❌ Type error
}
```

**After**:
```typescript
catch (error: any) {
  await showErrorToast(error);  // ✅ Works!
}
```

---

## 📝 Code Changes

### File: `frontend/src/pages/AdobePdfPage.tsx`

#### Lines 13-49: Helper Functions
```typescript
// Parse Blob/JSON error responses
const getErrorMessage = async (error: any): Promise<string> => {
  // Handle Blob error responses (from responseType: 'blob')
  if (error.response?.data instanceof Blob) {
    try {
      const text = await error.response.data.text();
      const json = JSON.parse(text);
      if (json.detail) {
        return json.detail;
      }
    } catch (e) {
      // If parsing fails, fall through to generic messages
    }
  }
  
  // Handle JSON error responses
  const detail = error.response?.data?.detail;
  if (detail) {
    return detail;
  }
  
  // Fallback messages...
};

// Async wrapper for toast
const showErrorToast = async (error: any) => {
  const errorMsg = await getErrorMessage(error);
  toast.error(errorMsg, { duration: 6000 });
};
```

#### All 8 Catch Blocks Updated:
1. `handleWatermark` - Line 144
2. `handleCombine` - Line 185
3. `handleSplit` - Line 224
4. `handleProtect` - Line 273
5. `handleLinearize` - Line 314
6. `handleAutoTag` - Line 355
7. `handleGenerateDocument` - Line 406
8. `handleElectronicSeal` - Line 454

**All now use**: `await showErrorToast(error);`

---

## 🧪 Test Results

### Test Case: Signed PDF (25-bnn-kem1.pdf)

**Backend Log**:
```
[ERROR] Adobe Split error: errorCode=PDF_SIGNED
INFO: 127.0.0.1 - "POST /api/v1/documents/pdf/split HTTP/1.1" 400 Bad Request
```

Backend trả về JSON:
```json
{
  "detail": "😔 Rất tiếc! File PDF này có chữ ký điện tử.\n\n💡 Giải pháp:\n• Adobe API không xử lý được file có chữ ký số\n• Vui lòng remove signature trước\n• Hoặc dùng bản PDF gốc chưa ký"
}
```

**Frontend (BEFORE FIX)**:
```
❌ Toast shows: "Yêu cầu không hợp lệ. Vui lòng kiểm tra lại thông tin."
```

**Frontend (AFTER FIX)**:
```
✅ Toast shows:
😔 Rất tiếc! File PDF này có chữ ký điện tử.

💡 Giải pháp:
• Adobe API không xử lý được file có chữ ký số
• Vui lòng remove signature trước
• Hoặc dùng bản PDF gốc chưa ký
```

---

## 📊 Coverage

| Feature | Response Type | Error Handling | Status |
|---------|---------------|----------------|--------|
| Split PDF | `blob` | ✅ Blob parsing | Fixed |
| Combine PDF | `blob` | ✅ Blob parsing | Fixed |
| Watermark | `blob` | ✅ Blob parsing | Fixed |
| Protect PDF | `blob` | ✅ Blob parsing | Fixed |
| Linearize | `blob` | ✅ Blob parsing | Fixed |
| Auto-Tag | `blob` | ✅ Blob parsing | Fixed |
| Doc Gen | `blob` | ✅ Blob parsing | Fixed |
| E-Seal | `blob` | ✅ Blob parsing | Fixed |

**All 8 features fixed!** ✅

---

## 💡 Why This Happened

### Axios Behavior with `responseType: 'blob'`

When you set `responseType: 'blob'`:
- Axios **always** converts response body to Blob
- This applies to **both success AND error** responses
- Error responses with JSON are wrapped in Blob

### Solution Pattern
```typescript
// ✅ Correct way to handle Blob error responses
if (error.response?.data instanceof Blob) {
  const text = await error.response.data.text();
  const json = JSON.parse(text);
  // Now you can access json.detail
}
```

---

## 🎯 Key Takeaways

1. **`responseType: 'blob'` affects error responses too!**
   - Not just success responses
   - Error JSON gets wrapped in Blob

2. **Always check response type before parsing**
   ```typescript
   if (error.response?.data instanceof Blob) {
     // Parse as Blob
   } else {
     // Parse as JSON
   }
   ```

3. **Async error handling is OK**
   - Functions can be async
   - Just need to await in catch blocks

4. **Toast.error accepts promises if awaited**
   ```typescript
   const msg = await getErrorMessage(error);
   toast.error(msg);
   ```

---

## ✅ Verification

### Test Commands
```bash
# 1. Start servers
npm run dev (frontend)
python -m uvicorn app.main_simple:app --reload (backend)

# 2. Upload a signed PDF (25-bnn-kem1.pdf)
# 3. Try Split PDF
# 4. Check toast message
```

### Expected Result
Toast should display:
```
😔 Rất tiếc! File PDF này có chữ ký điện tử.

💡 Giải pháp:
• Adobe API không xử lý được file có chữ ký số
• Vui lòng remove signature trước
• Hoặc dùng bản PDF gốc chưa ký
```

---

## 🚀 Impact

**Before**:
- Generic fallback messages
- Users không biết lý do cụ thể
- Phải check browser console

**After**:
- Detailed friendly messages
- Clear explanation + solutions
- No need to check console
- Better user experience! 😊

---

**Fixed by**: GitHub Copilot  
**Date**: November 25, 2024  
**Issue Type**: Frontend error parsing  
**Impact**: All 8 Adobe PDF features
