# 🎨 Frontend UX Improvements - PDF Operations

## ❌ Vấn Đề Hiện Tại

Nhìn vào UI hiện tại, có **nhiều vấn đề về UX** làm giảm trải nghiệm người dùng:

### 1. **Buttons bị Disabled không rõ lý do**
```tsx
// Hiện tại: TẤT CẢ buttons đều disabled khi loading
<Button
  onClick={handleExtractPdfText}
  disabled={loading}  // ❌ Chỉ check loading, KHÔNG check có file hay không
  className="w-full"
  variant="outline"
>
  📝 Trích xuất Text
</Button>
```

**Vấn đề:**
- ❌ User KHÔNG BIẾT tại sao button bị disabled
- ❌ Không có tooltip hoặc error message
- ❌ Buttons vẫn disabled ngay cả khi ĐÃ upload file PDF
- ❌ User nghĩ feature bị lỗi hoặc chưa implement

### 2. **Thiếu Technology Badges**
- ✅ Top 4 buttons CÓ technology badges (Adobe, Gotenberg, pdf2docx, pdfplumber)
- ❌ Các PDF operations khác KHÔNG CÓ badges
- ❌ User không biết tool nào được dùng để xử lý

### 3. **Không có File Validation**
```tsx
// ❌ Không check xem file có phải PDF hay không
const handleExtractPdfText = async () => {
  // Directly process without checking file type
  // What if user uploaded a Word file?
}
```

### 4. **Loading State không rõ ràng**
```tsx
// ❌ Global loading state - không biết operation nào đang chạy
const [loading, setLoading] = useState(false);

// ✅ Đã có loadingOperation nhưng chưa dùng hết
const [loadingOperation, setLoadingOperation] = useState<string | null>(null);
```

---

## ✅ Giải Pháp: Cải Thiện UX

### **Phase 1: Smart Button States** (30 phút)

#### 1.1. Tạo Helper Functions
```tsx
// Helper: Check if file is PDF
const isPdfSelected = (): boolean => {
  return selectedFile !== null && getFileType(selectedFile) === 'pdf';
};

// Helper: Check if file is uploaded
const isFileSelected = (): boolean => {
  return selectedFile !== null;
};

// Helper: Get button disabled state with reason
const getButtonState = (requiredFileType: 'pdf' | 'word' | 'excel' | 'any'): {
  disabled: boolean;
  reason: string | null;
} => {
  // Operation đang chạy
  if (isAnyOperationLoading()) {
    return { disabled: true, reason: 'Đang xử lý...' };
  }
  
  // Chưa upload file
  if (!isFileSelected()) {
    return { disabled: true, reason: 'Vui lòng upload file trước' };
  }
  
  // Check file type
  if (requiredFileType !== 'any') {
    const fileType = getFileType(selectedFile);
    if (fileType !== requiredFileType) {
      return { 
        disabled: true, 
        reason: `Cần file ${requiredFileType.toUpperCase()}, bạn đã upload ${fileType?.toUpperCase() || 'UNKNOWN'}` 
      };
    }
  }
  
  return { disabled: false, reason: null };
};
```

#### 1.2. Apply to Buttons với Tooltips
```tsx
<Tooltip content={buttonState.reason || ''}>
  <Button
    onClick={handleExtractPdfText}
    disabled={buttonState.disabled}
    className="w-full"
    variant="outline"
  >
    {isOperationLoading('extract-text') ? (
      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
    ) : (
      '📝'
    )}
    <span className="ml-2">Trích xuất Text</span>
  </Button>
</Tooltip>
```

---

### **Phase 2: Technology Badges cho PDF Operations** (1 giờ)

#### 2.1. Map PDF Operations → Technologies
```tsx
// Technology mapping for PDF operations
const PDF_OPERATION_TECH: Record<string, {
  primary: TechnologyType;
  fallback?: TechnologyType;
  quality: string;
  description: string;
}> = {
  'extract-text': {
    primary: 'pdfplumber',
    quality: '8/10',
    description: 'Extract text với layout detection'
  },
  'pdf-info': {
    primary: 'pdfplumber',
    quality: '10/10',
    description: 'Get metadata từ PDF'
  },
  'compress': {
    primary: 'adobe',
    fallback: 'pdfplumber',
    quality: '10/10',
    description: 'Nén PDF với Adobe AI hoặc pypdf'
  },
  'split': {
    primary: 'pypdf',
    quality: '10/10',
    description: 'Tách PDF pages'
  },
  'rotate': {
    primary: 'pypdf',
    quality: '10/10',
    description: 'Xoay PDF pages'
  },
  'watermark': {
    primary: 'adobe',
    fallback: 'pypdf',
    quality: '10/10',
    description: 'Thêm watermark'
  },
  'protect': {
    primary: 'adobe',
    fallback: 'pypdf',
    quality: '10/10',
    description: 'Bảo vệ bằng password'
  },
  'unlock': {
    primary: 'pypdf',
    quality: '10/10',
    description: 'Gỡ password protection'
  },
  'to-images': {
    primary: 'pdf2image',
    quality: '10/10',
    description: 'Convert PDF → PNG/JPG'
  }
};
```

#### 2.2. Add Badges to Buttons
```tsx
<div className="space-y-2">
  <h3 className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
    Công cụ PDF
  </h3>
  
  {/* Extract Text */}
  <div className="space-y-1">
    <Button
      onClick={handleExtractPdfText}
      disabled={!isPdfSelected() || isAnyOperationLoading()}
      className="w-full"
      variant="outline"
    >
      {isOperationLoading('extract-text') ? (
        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
      ) : (
        '📝'
      )}
      <span className="ml-2">Trích xuất Text</span>
    </Button>
    <div className="text-xs text-gray-500 ml-2">
      Powered by: <TechnologyBadge type="pdfplumber" showQuality={true} />
    </div>
  </div>
  
  {/* PDF Info */}
  <div className="space-y-1">
    <Button
      onClick={handlePdfInfo}
      disabled={!isPdfSelected() || isAnyOperationLoading()}
      className="w-full"
      variant="outline"
    >
      {isOperationLoading('pdf-info') ? (
        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
      ) : (
        'ℹ️'
      )}
      <span className="ml-2">Xem Thông Tin PDF</span>
    </Button>
    <div className="text-xs text-gray-500 ml-2">
      Powered by: <TechnologyBadge type="pdfplumber" showQuality={true} />
    </div>
  </div>
  
  {/* Compress PDF */}
  <div className="space-y-1">
    <Button
      onClick={handleCompressPdf}
      disabled={!isPdfSelected() || isAnyOperationLoading()}
      className="w-full"
      variant="outline"
    >
      {isOperationLoading('compress') ? (
        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
      ) : (
        '📦'
      )}
      <span className="ml-2">Nén PDF</span>
    </Button>
    <div className="text-xs text-gray-500 ml-2">
      Powered by: 
      <TechnologyBadge type="adobe" showQuality={true} />
      <span className="mx-1">→</span>
      <TechnologyBadge type="pdfplumber" showQuality={true} />
    </div>
  </div>
  
  {/* ... other operations ... */}
</div>
```

---

### **Phase 3: Unified Conversion Handler** (2 giờ)

#### 3.1. Generic Conversion Function
```tsx
/**
 * Universal conversion handler - REUSE logic for all operations
 */
const handleConversion = async (options: {
  operation: string;
  endpoint: string;
  file: File;
  additionalData?: Record<string, any>;
  outputFilename?: string;
  technology: TechnologyType;
  onProgress?: (progress: number) => void;
}) => {
  const { operation, endpoint, file, additionalData, outputFilename, technology } = options;
  
  // Set loading state
  setLoadingOperation(operation);
  setLoading(true);
  setUploadProgress(0);
  setProcessingProgress(0);
  setCurrentOperation(operation);
  setCurrentTechnology(technology);
  
  const startTime = Date.now();
  const controller = new AbortController();
  setAbortController(controller);
  
  try {
    // Upload progress simulation
    const uploadInterval = setInterval(() => {
      setUploadProgress(prev => Math.min(prev + 10, 100));
    }, 100);
    
    // Prepare form data
    const formData = new FormData();
    formData.append('file', file);
    
    // Add additional data if provided
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, String(value));
      });
    }
    
    // Make API request
    const response = await axios.post(
      `${API_BASE}${endpoint}`,
      formData,
      {
        responseType: 'blob',
        signal: controller.signal,
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percent);
          }
        },
      }
    );
    
    clearInterval(uploadInterval);
    setUploadProgress(100);
    
    // Processing progress animation
    for (let i = 0; i <= 100; i += 20) {
      setProcessingProgress(i);
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    
    const processingTimeMs = Date.now() - startTime;
    
    // Extract technology metadata from headers
    const techEngine = response.headers['x-technology-engine'] || technology;
    const techQuality = response.headers['x-technology-quality'] || '10/10';
    
    // Download file
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.download = outputFilename || `output_${Date.now()}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    // Set result
    setResult({
      success: true,
      operation,
      technology: techEngine,
      quality: techQuality,
      processingTime: processingTimeMs,
      originalSize: file.size,
      outputSize: response.data.size,
    });
    
    toast.success(`✅ ${operation} thành công!`);
    
  } catch (error: any) {
    if (error.name === 'CanceledError') {
      toast('❌ Đã hủy thao tác');
    } else {
      const errorMsg = error.response?.data?.message || error.message || 'Lỗi không xác định';
      toast.error(`❌ Lỗi: ${errorMsg}`);
      setResult({ success: false, error: errorMsg });
    }
  } finally {
    setLoadingOperation(null);
    setLoading(false);
    setAbortController(null);
  }
};
```

#### 3.2. Refactor Existing Handlers
```tsx
// ❌ Before: Duplicate code
const handlePdfToWord = async () => {
  setLoading(true);
  setUploadProgress(0);
  // ... 50 lines of duplicate code ...
};

const handleWordToPdf = async () => {
  setLoading(true);
  setUploadProgress(0);
  // ... 50 lines of duplicate code ...
};

// ✅ After: Reuse handleConversion
const handlePdfToWord = async () => {
  if (!selectedFile) return;
  
  await handleConversion({
    operation: 'PDF → Word',
    endpoint: '/documents/convert/pdf-to-word',
    file: selectedFile,
    outputFilename: selectedFile.name.replace('.pdf', '.docx'),
    technology: 'adobe', // Will fallback to pdf2docx if Adobe fails
  });
};

const handleWordToPdf = async () => {
  if (!selectedFile) return;
  
  await handleConversion({
    operation: 'Word → PDF',
    endpoint: '/documents/convert/word-to-pdf',
    file: selectedFile,
    outputFilename: selectedFile.name.replace(/\.(docx?|doc)$/, '.pdf'),
    technology: 'gotenberg',
  });
};

const handleCompressPdf = async () => {
  if (!selectedFile) return;
  
  await handleConversion({
    operation: 'Compress PDF',
    endpoint: '/documents/compress',
    file: selectedFile,
    additionalData: { level: 'medium' },
    outputFilename: selectedFile.name.replace('.pdf', '_compressed.pdf'),
    technology: 'adobe',
  });
};

const handleExtractPdfText = async () => {
  if (!selectedFile) return;
  
  await handleConversion({
    operation: 'Extract Text',
    endpoint: '/documents/extract-text',
    file: selectedFile,
    outputFilename: selectedFile.name.replace('.pdf', '.txt'),
    technology: 'pdfplumber',
  });
};
```

---

### **Phase 4: Better Error Handling** (30 phút)

#### 4.1. File Validation Before Upload
```tsx
const validateFile = (file: File, requiredType?: 'pdf' | 'word' | 'excel'): {
  valid: boolean;
  error?: string;
} => {
  // Check file size (max 50MB)
  const maxSize = 50 * 1024 * 1024; // 50MB
  if (file.size > maxSize) {
    return {
      valid: false,
      error: `File quá lớn (${(file.size / 1024 / 1024).toFixed(2)}MB). Tối đa 50MB.`
    };
  }
  
  // Check file type
  if (requiredType) {
    const fileType = getFileType(file);
    if (fileType !== requiredType) {
      return {
        valid: false,
        error: `File không đúng định dạng. Cần ${requiredType.toUpperCase()}, bạn upload ${fileType?.toUpperCase() || 'UNKNOWN'}.`
      };
    }
  }
  
  return { valid: true };
};

// Apply validation
const handleExtractPdfText = async () => {
  if (!selectedFile) {
    toast.error('❌ Vui lòng upload file PDF trước!');
    return;
  }
  
  const validation = validateFile(selectedFile, 'pdf');
  if (!validation.valid) {
    toast.error(validation.error);
    return;
  }
  
  await handleConversion({
    operation: 'Extract Text',
    endpoint: '/documents/extract-text',
    file: selectedFile,
    outputFilename: selectedFile.name.replace('.pdf', '.txt'),
    technology: 'pdfplumber',
  });
};
```

#### 4.2. Network Error Handling
```tsx
const handleNetworkError = (error: any): string => {
  if (error.code === 'ECONNABORTED') {
    return 'Timeout! File quá lớn hoặc mạng chậm.';
  }
  
  if (error.code === 'ERR_NETWORK') {
    return 'Lỗi kết nối. Vui lòng kiểm tra mạng.';
  }
  
  if (error.response?.status === 413) {
    return 'File quá lớn! Server không chấp nhận.';
  }
  
  if (error.response?.status === 415) {
    return 'Định dạng file không được hỗ trợ.';
  }
  
  if (error.response?.status === 500) {
    return 'Lỗi server. Vui lòng thử lại sau.';
  }
  
  return error.message || 'Lỗi không xác định';
};
```

---

## 📊 So Sánh Before/After

### ❌ **BEFORE: Unfriendly UX**
```
User workflow:
1. Upload PDF ✅
2. Click "Trích xuất Text" → Button disabled (màu xám) ❌
3. User confused: "Tại sao không click được?" 🤔
4. No error message, no tooltip ❌
5. User thinks feature is broken ❌
```

### ✅ **AFTER: User-Friendly UX**
```
User workflow:
1. Click "Trích xuất Text" WITHOUT file → Toast: "Vui lòng upload file PDF" ✅
2. Upload Word file → Button disabled with tooltip: "Cần file PDF, bạn upload WORD" ✅
3. Upload PDF ✅ → Button enabled (có màu) ✅
4. Click "Trích xuất Text" → Show technology badge: "pdfplumber (8/10)" ✅
5. Processing with progress bar ✅
6. Success! Download file .txt ✅
```

---

## 🎯 Implementation Priority

### **Giai đoạn 1 (CRITICAL) - 2 giờ:**
✅ Fix button states (enable when có file PDF)  
✅ Add file validation  
✅ Add error messages

**Impact:** Từ "feature bị lỗi" → "feature hoạt động tốt"

### **Giai đoạn 2 (HIGH) - 2 giờ:**
✅ Add technology badges cho all operations  
✅ Unified conversion handler  
✅ Reduce code duplication (từ 500 lines → 200 lines)

**Impact:** Professional UI + maintainable code

### **Giai đoạn 3 (MEDIUM) - 1 giờ:**
✅ Better error handling  
✅ Network timeout handling  
✅ Retry logic

**Impact:** Robust application

---

## 📝 Code Changes Summary

### Files to Modify:
1. **`frontend/src/pages/ToolsPage.tsx`** (main changes)
   - Add helper functions: `isPdfSelected()`, `validateFile()`, `handleConversion()`
   - Update all button `disabled` attributes
   - Add technology badges
   - Refactor handlers to use unified logic

2. **`frontend/src/components/TechnologyBadge.tsx`** (minor)
   - Add `showQuality` prop to toggle quality display
   - Add compact mode for small badges

### Estimated Time:
- **Phase 1:** 2 hours
- **Phase 2:** 2 hours  
- **Phase 3:** 2 hours
- **Phase 4:** 1 hour
- **Total:** ~7 hours

### Lines of Code:
- **Before:** ~3545 lines  
- **After:** ~2800 lines (-745 lines, -21% code reduction)
- **Reason:** Unified conversion handler eliminates duplication

---

## 🚀 Next Steps

1. **Review this document** với team
2. **Approve changes**
3. **Implement Phase 1** (most critical)
4. **Test thoroughly**
5. **Deploy to production**
6. **Monitor user feedback**

---

**Benefits:**
- ✅ Better UX (users understand what's happening)
- ✅ Less code (easier maintenance)
- ✅ Consistent behavior (all operations work the same way)
- ✅ Technology transparency (users know which tool is used)
- ✅ Professional UI (badges, progress, error messages)

---

**Last Updated:** November 23, 2025  
**Author:** GitHub Copilot  
**Status:** Ready for implementation
