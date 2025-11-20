# UI/UX Improvements - Operation Management

## 🎯 Vấn Đề Ban Đầu

**Trước khi cải tiến:**
- ❌ Khi 1 operation đang chạy → TẤT CẢ nút đều hiển thị loading spinner
- ❌ User không thể tương tác với bất kỳ tính năng nào khác
- ❌ Không có cách nào để hủy operation đang chạy
- ❌ UI không rõ ràng về operation nào đang thực thi
- ❌ Logic nghiệp vụ không hợp lý: tại sao convert Word lại khóa nút Excel?

**Ví dụ:**
```
User click "Word → PDF" 
  → Loading = true
    → NÚT WORD: [⏳ Loading...] ← Hợp lý
    → NÚT EXCEL: [⏳ Loading...] ← KHÔNG HỢP LÝ!
    → NÚT IMAGE: [⏳ Loading...] ← KHÔNG HỢP LÝ!
    → NÚT PDF: [⏳ Loading...] ← KHÔNG HỢP LÝ!
```

## ✅ Giải Pháp Mới

### 1. **Operation-Specific Loading State**

**Thay vì:**
```typescript
const [loading, setLoading] = useState(false); // Global loading
```

**Bây giờ:**
```typescript
const [loading, setLoading] = useState(false); // Keep for backward compatibility
const [loadingOperation, setLoadingOperation] = useState<string | null>(null); // Track specific operation
const [abortController, setAbortController] = useState<AbortController | null>(null); // For canceling
```

**Helper Functions:**
```typescript
// Check if specific operation is running
const isOperationLoading = (operation: string): boolean => {
  return loadingOperation === operation;
};

// Check if ANY operation is running
const isAnyOperationLoading = (): boolean => {
  return loadingOperation !== null;
};
```

### 2. **Targeted Button Disabling**

**Trước:**
```typescript
<Button 
  onClick={handleWordToPdf}
  disabled={loading} // Disabled khi BẤT KỲ operation nào chạy
>
  {loading ? <Loader2 /> : '📄'} 
  Chuyển sang PDF
</Button>
```

**Sau:**
```typescript
<Button 
  onClick={handleWordToPdf}
  disabled={isOperationLoading('word-to-pdf')} // CHỈ disabled khi word-to-pdf chạy
>
  {isOperationLoading('word-to-pdf') ? <Loader2 /> : '📄'} 
  Chuyển sang PDF
</Button>
```

### 3. **Cancel/Abort Functionality**

**AbortController Integration:**
```typescript
const handleWordToPdf = async () => {
  // Check if another operation is running
  if (isAnyOperationLoading()) {
    toast('⚠️ Một thao tác khác đang chạy!', { icon: '⚠️' });
    return;
  }

  // Create abort controller
  const controller = new AbortController();
  setAbortController(controller);
  setLoadingOperation('word-to-pdf'); // Track operation
  
  try {
    const response = await axios.post(url, formData, {
      signal: controller.signal, // Pass abort signal
      onUploadProgress: (progress) => {...}
    });
    
    // Success handling...
  } catch (error: any) {
    // Check if aborted
    if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
      toast('❌ Đã hủy chuyển đổi', { icon: 'ℹ️' });
      return;
    }
    
    // Other errors...
  } finally {
    setLoadingOperation(null); // Clear operation
    setAbortController(null); // Clear controller
  }
};
```

**Cancel Button in UI:**
```typescript
{/* Progress UI */}
<div className="flex items-center justify-center gap-4 py-4">
  <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
  {abortController && (
    <Button
      onClick={handleCancelOperation}
      variant="outline"
      className="text-red-600 hover:bg-red-50"
    >
      ❌ Hủy
    </Button>
  )}
</div>
```

**Cancel Handler:**
```typescript
const handleCancelOperation = () => {
  if (abortController) {
    abortController.abort(); // Abort axios request
    setAbortController(null);
    setLoadingOperation(null);
    setLoading(false);
    setUploadProgress(0);
    setProcessingProgress(0);
    toast('❌ Đã hủy thao tác!', { icon: 'ℹ️' });
  }
};
```

### 4. **Warning for Concurrent Operations**

**Batch Mode Buttons:**
```typescript
<Button
  onClick={() => {
    // Check before starting new operation
    if (isAnyOperationLoading()) {
      toast('⚠️ Một thao tác khác đang chạy!', { icon: '⚠️' });
      return;
    }
    setBatchMode(true);
    setBatchOperation('word-to-pdf');
  }}
  disabled={isOperationLoading('batch-word-to-pdf')}
>
  📚 Chuyển NHIỀU file Word → PDF
</Button>
```

## 📊 So Sánh Trước/Sau

### Scenario 1: User đang convert Word → PDF

**TRƯỚC:**
```
✅ Word → PDF    [⏳ Đang chạy...]  disabled=true
❌ Excel → PDF   [⏳ Loading...]    disabled=true  ← KHÔNG HỢP LÝ
❌ Image → PDF   [⏳ Loading...]    disabled=true  ← KHÔNG HỢP LÝ
❌ PDF Merge     [⏳ Loading...]    disabled=true  ← KHÔNG HỢP LÝ
❌ Batch Convert [⏳ Loading...]    disabled=true  ← KHÔNG HỢP LÝ
```

**SAU:**
```
✅ Word → PDF    [⏳ Đang chạy...] [❌ Hủy]  disabled=true
✅ Excel → PDF   [📊 Ready]                  disabled=false  ← Click = Warning
✅ Image → PDF   [🖼️ Ready]                  disabled=false  ← Click = Warning
✅ PDF Merge     [🔗 Ready]                  disabled=false  ← Click = Warning
✅ Batch Convert [📚 Ready]                  disabled=false  ← Click = Warning
```

### Scenario 2: User đang merge 5 Word files

**TRƯỚC:**
```
- Progress: 45%
- Không thể làm gì khác
- Không thể hủy
- Nếu lỗi phải đợi timeout
```

**SAU:**
```
- Progress: 45%
- Có nút [❌ Hủy] để abort
- Các nút khác vẫn hiển thị bình thường
- Click nút khác → Warning: "⚠️ Một thao tác khác đang chạy!"
- User có control đầy đủ
```

## 🎨 Behavior Details

### Operation Naming Convention

```typescript
// Single file operations
'word-to-pdf'
'pdf-to-word'
'excel-to-pdf'
'image-to-pdf'

// Batch operations
'batch-word-to-pdf'
'batch-pdf-to-word'
'batch-excel-to-pdf'
'batch-image-to-pdf'

// Merge operations
'merge-word-to-pdf'
'merge-pdfs'

// Bulk operations
'bulk-pdf-to-word'
'bulk-pdf-to-excel'
```

### Button States

```typescript
// State 1: Idle (operation not running)
disabled={false}
icon={'📄'} 
text={'Chuyển sang PDF'}

// State 2: This operation is running
disabled={true}
icon={<Loader2 className="animate-spin" />}
text={'Chuyển sang PDF'}

// State 3: Another operation is running
disabled={false} // Still enabled!
icon={'📄'} // Normal icon
text={'Chuyển sang PDF'}
onClick={() => toast('⚠️ Một thao tác khác đang chạy!')}
```

## 🔧 Technical Implementation

### Files Modified

1. **frontend/src/pages/ToolsPage.tsx**
   - Added `loadingOperation` state
   - Added `abortController` state
   - Created helper functions
   - Updated all operation handlers
   - Updated all button components
   - Added cancel button to progress UI

### Key Functions Updated

```typescript
✅ handleWordToPdf()        - Added abort + operation tracking
✅ handleMergeWordToPdf()   - Added abort + operation tracking
✅ isOperationLoading()     - NEW helper
✅ isAnyOperationLoading()  - NEW helper
✅ handleCancelOperation()  - NEW cancel handler
```

### Remaining Tasks

**To Update (Same Pattern):**
- [ ] handleBatchWordToPdf()
- [ ] handleBatchPdfToWord()
- [ ] handleBatchExcelToPdf()
- [ ] handleBatchImageToPdf()
- [ ] handleBatchCompressPdf()
- [ ] handleBulkPdfConvert()
- [ ] handlePdfToPowerpoint()
- [ ] handleExcelToPdf()
- [ ] handleImageToPdf()
- [ ] All other conversion handlers...

**Pattern to apply:**
```typescript
const handleXXX = async () => {
  // 1. Check concurrent operation
  if (isAnyOperationLoading()) {
    toast('⚠️ Một thao tác khác đang chạy!', { icon: '⚠️' });
    return;
  }

  // 2. Create abort controller
  const controller = new AbortController();
  setAbortController(controller);
  setLoadingOperation('operation-name');
  
  try {
    // 3. Add signal to axios
    await axios.post(url, data, { signal: controller.signal });
  } catch (error: any) {
    // 4. Handle abort
    if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
      toast('❌ Đã hủy', { icon: 'ℹ️' });
      return;
    }
  } finally {
    // 5. Clear operation
    setLoadingOperation(null);
    setAbortController(null);
  }
};
```

## 🎯 Benefits

### User Experience
1. ✅ **Clarity**: User biết chính xác operation nào đang chạy
2. ✅ **Control**: User có thể hủy operation nếu cần
3. ✅ **Flexibility**: User có thể thử click vào features khác (sẽ có warning)
4. ✅ **Feedback**: Rõ ràng về trạng thái của từng nút
5. ✅ **Predictable**: Logic nghiệp vụ hợp lý hơn

### Developer Experience
1. ✅ **Maintainable**: Dễ debug operation nào đang chạy
2. ✅ **Extensible**: Dễ thêm operations mới
3. ✅ **Consistent**: Pattern nhất quán cho tất cả operations
4. ✅ **Testable**: Dễ test từng operation riêng biệt

### Performance
1. ✅ **Resource Management**: Có thể abort request không cần thiết
2. ✅ **Memory**: Clear controllers sau khi xong
3. ✅ **Network**: Không waste bandwidth cho operation bị hủy

## 📝 Example Usage

### User Flow 1: Convert Word → PDF successfully
```
1. User clicks [📄 Chuyển sang PDF]
2. Button shows: [⏳ Chuyển sang PDF] + [❌ Hủy]
3. Other buttons: [📊 Ready] [🖼️ Ready] [🔗 Ready]
4. Progress: 45%... 78%... 100%
5. Download starts
6. Button returns to: [📄 Chuyển sang PDF]
```

### User Flow 2: Cancel Merge Operation
```
1. User clicks [🔗 Gộp 4 Word → 1 PDF]
2. Button shows: [⏳ Gộp 4 Word...] + [❌ Hủy]
3. User realizes wrong files
4. User clicks [❌ Hủy]
5. Request aborted immediately
6. Toast: "❌ Đã hủy thao tác!"
7. Button returns to: [🔗 Gộp NHIỀU Word → 1 PDF]
```

### User Flow 3: Try Concurrent Operations
```
1. User clicks [📄 Word → PDF] (operation starts)
2. User clicks [📊 Excel → PDF] (while word-to-pdf running)
3. Toast appears: "⚠️ Một thao tác khác đang chạy!"
4. Excel button doesn't start
5. User waits for Word conversion to complete
6. Then user clicks [📊 Excel → PDF] (now it works)
```

## 🚀 Next Steps

### Phase 1: Core Operations (✅ DONE)
- [x] handleWordToPdf
- [x] handleMergeWordToPdf
- [x] Cancel button UI
- [x] Helper functions
- [x] Button state management

### Phase 2: Batch Operations (⏳ TODO)
- [ ] Apply pattern to all batch handlers
- [ ] Update all batch buttons
- [ ] Test cancel functionality for batch

### Phase 3: All Operations (⏳ TODO)
- [ ] Apply pattern to remaining ~20 handlers
- [ ] Unified error handling
- [ ] Unified progress tracking

### Phase 4: Advanced Features (💡 FUTURE)
- [ ] Queue system (cho phép queue nhiều operations)
- [ ] Operation history (xem operations đã chạy)
- [ ] Resume functionality (tiếp tục operation bị gián đoạn)
- [ ] Parallel operations (cho phép 2-3 operations cùng lúc nếu hợp lý)

## 🎉 Conclusion

Cải tiến này giải quyết vấn đề **logic nghiệp vụ không hợp lý** của UI cũ, mang lại:

1. **Better UX**: User có control và feedback rõ ràng
2. **Better Logic**: Chỉ disable operation đang chạy, không block toàn bộ UI
3. **Better Performance**: Có thể abort operations không cần thiết
4. **Better Maintainability**: Code dễ hiểu và mở rộng

**Kết quả:**
- UI logic ✅
- UX tốt hơn ✅
- Performance tốt hơn ✅
- Code maintainable ✅
