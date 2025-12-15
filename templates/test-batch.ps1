# Test Batch Document Generation
# Run this to test the batch endpoint with proper JSON content

Write-Host "🚀 Testing Batch Document Generation..." -ForegroundColor Cyan
Write-Host ""

# Navigate to templates folder
Set-Location "d:\thang\utility-server\templates"

# Read JSON file content
Write-Host "📖 Reading JSON file..." -ForegroundColor Yellow
$jsonContent = Get-Content "thiep_khai_truong_batch.json" -Raw
Write-Host "✅ JSON loaded: $($jsonContent.Length) characters" -ForegroundColor Green
Write-Host ""

# Test 1: Merge into single PDF
Write-Host "🔄 Test 1: Generate 5 invitations → Merge into 1 PDF (5 pages)" -ForegroundColor Cyan
Write-Host "Endpoint: POST /api/v1/documents/pdf/generate-batch" -ForegroundColor Gray
Write-Host "merge_output=true" -ForegroundColor Gray
Write-Host ""

# Create a temporary file for JSON content
$tempJsonFile = "temp_batch_test.json"
$jsonContent | Out-File -FilePath $tempJsonFile -Encoding UTF8 -NoNewline

# Use curl with multipart form data
$response = & curl.exe -X POST "http://localhost:8000/api/v1/documents/pdf/generate-batch" `
    -F "template_file=@thiep_khai_truong.docx" `
    -F "json_data=<$tempJsonFile" `
    -F "output_format=pdf" `
    -F "merge_output=true" `
    -o "test_batch_merged_final.pdf" `
    -w "%{http_code}" `
    -s

# Clean up temp file
Remove-Item $tempJsonFile -ErrorAction SilentlyContinue

Write-Host "HTTP Status: $response" -ForegroundColor $(if ($response -eq '200') {'Green'} else {'Red'})
Write-Host ""

# Check result
if (Test-Path "test_batch_merged_final.pdf") {
    $fileSize = (Get-Item "test_batch_merged_final.pdf").Length
    Write-Host "✅ PDF Generated!" -ForegroundColor Green
    Write-Host "📄 File: test_batch_merged_final.pdf" -ForegroundColor Cyan
    Write-Host "📏 Size: $fileSize bytes" -ForegroundColor Cyan
    
    if ($fileSize -lt 1000) {
        Write-Host "⚠️  File is very small, might be an error. Reading content:" -ForegroundColor Yellow
        Get-Content "test_batch_merged_final.pdf"
    } else {
        Write-Host "🎉 SUCCESS! Open the PDF to verify 5 personalized invitations" -ForegroundColor Green
        
        # Try to open the PDF
        Write-Host ""
        $openPdf = Read-Host "Open PDF now? (Y/N)"
        if ($openPdf -eq 'Y' -or $openPdf -eq 'y') {
            Start-Process "test_batch_merged_final.pdf"
        }
    }
} else {
    Write-Host "❌ PDF was not created!" -ForegroundColor Red
    Write-Host "Check server logs for errors" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "-----------------------------------" -ForegroundColor Gray

# Test 2: ZIP with separate files
Write-Host ""
Write-Host "🔄 Test 2: Generate 5 invitations → ZIP with 5 separate PDFs" -ForegroundColor Cyan
Write-Host "merge_output=false" -ForegroundColor Gray
Write-Host ""

# Recreate temp JSON file
$jsonContent | Out-File -FilePath $tempJsonFile -Encoding UTF8 -NoNewline

$response2 = & curl.exe -X POST "http://localhost:8000/api/v1/documents/pdf/generate-batch" `
    -F "template_file=@thiep_khai_truong.docx" `
    -F "json_data=<$tempJsonFile" `
    -F "output_format=pdf" `
    -F "merge_output=false" `
    -o "test_batch_separate.zip" `
    -w "%{http_code}" `
    -s

# Clean up temp file
Remove-Item $tempJsonFile -ErrorAction SilentlyContinue

Write-Host "HTTP Status: $response2" -ForegroundColor $(if ($response2 -eq '200') {'Green'} else {'Red'})
Write-Host ""

if (Test-Path "test_batch_separate.zip") {
    $zipSize = (Get-Item "test_batch_separate.zip").Length
    Write-Host "✅ ZIP Generated!" -ForegroundColor Green
    Write-Host "📦 File: test_batch_separate.zip" -ForegroundColor Cyan
    Write-Host "📏 Size: $zipSize bytes" -ForegroundColor Cyan
    
    if ($zipSize -lt 1000) {
        Write-Host "⚠️  File is very small, might be an error" -ForegroundColor Yellow
    } else {
        Write-Host "🎉 SUCCESS! Extracting ZIP..." -ForegroundColor Green
        
        # Extract ZIP
        $extractPath = "test_batch_output"
        if (Test-Path $extractPath) {
            Remove-Item $extractPath -Recurse -Force
        }
        Expand-Archive -Path "test_batch_separate.zip" -DestinationPath $extractPath -Force
        
        # List contents
        Write-Host ""
        Write-Host "📂 Extracted files:" -ForegroundColor Cyan
        Get-ChildItem $extractPath | ForEach-Object {
            Write-Host "  - $($_.Name) ($($_.Length) bytes)" -ForegroundColor White
        }
        
        # Try to open folder
        Write-Host ""
        $openFolder = Read-Host "Open folder? (Y/N)"
        if ($openFolder -eq 'Y' -or $openFolder -eq 'y') {
            Start-Process $extractPath
        }
    }
} else {
    Write-Host "❌ ZIP was not created!" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ Batch testing complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  - Template: thiep_khai_truong.docx" -ForegroundColor White
Write-Host "  - JSON: thiep_khai_truong_batch.json (5 guests)" -ForegroundColor White
Write-Host "  - Output 1: test_batch_merged_final.pdf (merged)" -ForegroundColor White
Write-Host "  - Output 2: test_batch_separate.zip (5 separate files)" -ForegroundColor White
