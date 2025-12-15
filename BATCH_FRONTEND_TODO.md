# Add Batch Generation UI to Frontend

## Current Status
- ✅ Backend batch endpoint working: `/api/v1/documents/pdf/generate-batch`
- ✅ PowerShell testing successful
- ❌ Frontend only has single document UI

## Requirements for Frontend Batch UI

### 1. Add Toggle/Tab in AdobePdfPage.tsx

```typescript
const [batchMode, setBatchMode] = useState(false);
```

### 2. UI Changes When Batch Mode = true

**Form Fields:**
- Template file upload (same)
- JSON file upload (array expected)
- Output format dropdown (PDF/DOCX)
- **NEW:** Merge output checkbox
  - ☑️ "Merge into single PDF" (merge_output=true)
  - ☐ "Separate files (ZIP)" (merge_output=false)

### 3. API Call Modification

```typescript
if (batchMode) {
  // Call batch endpoint
  const response = await axios.post(
    `${API_BASE}/documents/pdf/generate-batch`,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: mergeOutput ? 'blob' : 'blob' // Both return blob
    }
  );
  
  // Handle response
  if (mergeOutput) {
    // Download single PDF
    downloadFile(response.data, 'batch_merged.pdf');
  } else {
    // Download ZIP
    downloadFile(response.data, 'batch_files.zip');
  }
} else {
  // Existing single document logic
}
```

### 4. FormData Construction

```typescript
const formData = new FormData();
formData.append('template_file', templateFile);
formData.append('json_data', jsonFileContent); // Read file content as string
formData.append('output_format', outputFormat);

if (batchMode) {
  formData.append('merge_output', mergeOutput.toString());
}
```

### 5. JSON File Reading

For batch mode, need to:
1. Read JSON file content
2. Validate it's an array
3. Show preview (number of records)

```typescript
const handleJsonFile = (file: File) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const content = e.target?.result as string;
      const parsed = JSON.parse(content);
      
      if (batchMode) {
        if (!Array.isArray(parsed)) {
          setError('Batch mode requires JSON array');
          return;
        }
        setRecordCount(parsed.length);
      } else {
        if (Array.isArray(parsed)) {
          setError('Single mode requires JSON object, not array');
          return;
        }
      }
      
      setJsonContent(content);
    } catch (err) {
      setError('Invalid JSON file');
    }
  };
  reader.readAsText(file);
};
```

### 6. UI Elements to Add

```tsx
{/* Mode Toggle */}
<div className="mode-toggle">
  <button 
    onClick={() => setBatchMode(false)}
    className={!batchMode ? 'active' : ''}
  >
    Single Document
  </button>
  <button 
    onClick={() => setBatchMode(true)}
    className={batchMode ? 'active' : ''}
  >
    Batch Generation
  </button>
</div>

{/* Batch Options (only show when batchMode=true) */}
{batchMode && (
  <div className="batch-options">
    <label>
      <input
        type="checkbox"
        checked={mergeOutput}
        onChange={(e) => setMergeOutput(e.target.checked)}
      />
      Merge into single PDF
    </label>
    
    {jsonContent && (
      <div className="batch-info">
        <p>📊 Records to generate: {recordCount}</p>
        <p>📄 Output: {mergeOutput ? 'Single merged PDF' : 'ZIP with separate files'}</p>
      </div>
    )}
  </div>
)}
```

### 7. Help Text

```tsx
<div className="help-text">
  {batchMode ? (
    <>
      <p>📦 <strong>Batch Mode:</strong></p>
      <ul>
        <li>Upload 1 template + 1 JSON array file</li>
        <li>JSON must contain array: <code>[{'{...}'}, {'{...}'}]</code></li>
        <li>Example: <code>thiep_khai_truong_batch.json</code></li>
        <li>Max 100 records per batch</li>
      </ul>
    </>
  ) : (
    <>
      <p>📄 <strong>Single Mode:</strong></p>
      <ul>
        <li>Upload 1 template + 1 JSON object file</li>
        <li>JSON must be single object: <code>{'{...}'}</code></li>
        <li>Example: <code>thiep_khai_truong_sample1.json</code></li>
      </ul>
    </>
  )}
</div>
```

## Implementation Steps

1. [ ] Add state variables (`batchMode`, `mergeOutput`, `recordCount`)
2. [ ] Add mode toggle buttons
3. [ ] Modify JSON file reader to validate array vs object
4. [ ] Add batch options UI (merge checkbox)
5. [ ] Modify API call logic (if batchMode...)
6. [ ] Update help text based on mode
7. [ ] Test with both modes
8. [ ] Add loading indicator for batch (may take longer)
9. [ ] Add progress tracking (optional, advanced)

## Files to Modify

- `frontend/src/pages/AdobePdfPage.tsx` - Main changes
- `frontend/src/components/BatchModeToggle.tsx` - New component (optional)

## Testing Checklist

### Single Mode
- [ ] Upload `thiep_khai_truong.docx` + `sample1.json` → Works
- [ ] Upload batch JSON → Shows error "requires object, not array"

### Batch Mode  
- [ ] Upload `thiep_khai_truong.docx` + `batch.json` + merge=true → Single PDF
- [ ] Upload `thiep_khai_truong.docx` + `batch.json` + merge=false → ZIP
- [ ] Upload single JSON → Shows error "requires array, not object"
- [ ] Shows correct record count
- [ ] Downloads with correct filename

## Expected User Experience

**Scenario 1: Wedding Invitations (50 guests)**
1. Toggle to "Batch Mode"
2. Upload `wedding_invitation.docx`
3. Upload `wedding_guests.json` (50 guests)
4. Check "Merge into single PDF"
5. Click Generate
6. Download `batch_50_merged.pdf` → Send to print shop ✅

**Scenario 2: Personalized Certificates (30 students)**
1. Toggle to "Batch Mode"
2. Upload `certificate_template.docx`
3. Upload `students.json` (30 students)
4. Uncheck merge (get separate files)
5. Click Generate
6. Download `batch_30_files.zip` → Extract → Email individual PDFs ✅

## Priority

🔥 **Medium Priority**
- Current workaround: Use PowerShell script (works perfectly)
- Frontend batch UI is "nice to have" for better UX
- Not blocking any functionality

## Estimated Effort

- Development: 2-3 hours
- Testing: 1 hour
- Total: 3-4 hours
