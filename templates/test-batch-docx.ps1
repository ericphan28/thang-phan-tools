# Test Batch DOCX Generation
Write-Host "Testing Batch DOCX Generation..." -ForegroundColor Cyan

# Set paths
$templatesFolder = "d:\thang\utility-server\templates"
Set-Location $templatesFolder

# Read JSON as bytes
$jsonFile = Join-Path $templatesFolder "thiep_khai_truong_batch.json"
$jsonBytes = [System.IO.File]::ReadAllBytes($jsonFile)
Write-Host "JSON loaded: $($jsonBytes.Length) bytes (5 guests)" -ForegroundColor Green

# Create temp JSON file
$tempJsonFile = Join-Path $templatesFolder "temp_batch.json"
[System.IO.File]::WriteAllBytes($tempJsonFile, $jsonBytes)

# Test: Generate 5 DOCX files → ZIP
Write-Host "`nGenerating 5 Word documents (DOCX) in ZIP..." -ForegroundColor Yellow

$response = curl.exe -X POST "http://localhost:8000/api/v1/documents/pdf/generate-batch" `
    -F "template_file=@thiep_khai_truong.docx" `
    -F "json_data=<$tempJsonFile" `
    -F "output_format=docx" `
    -F "merge_output=false" `
    -o "test_batch_docx.zip" `
    -w "%{http_code}" `
    -s

Write-Host "HTTP Status: $response" -ForegroundColor $(if ($response -eq '200') {'Green'} else {'Red'})

if (Test-Path "test_batch_docx.zip") {
    $zipSize = (Get-Item "test_batch_docx.zip").Length
    Write-Host "`n✅ ZIP Generated!" -ForegroundColor Green
    Write-Host "📦 File: test_batch_docx.zip" -ForegroundColor Cyan
    Write-Host "📏 Size: $zipSize bytes" -ForegroundColor Cyan
    
    if ($zipSize -gt 1000) {
        Write-Host "`nExtracting ZIP..." -ForegroundColor Yellow
        
        # Extract ZIP
        $extractPath = "test_batch_docx_output"
        if (Test-Path $extractPath) {
            Remove-Item $extractPath -Recurse -Force
        }
        Expand-Archive -Path "test_batch_docx.zip" -DestinationPath $extractPath -Force
        
        # List contents
        Write-Host "`nExtracted DOCX files:" -ForegroundColor Cyan
        Get-ChildItem $extractPath -Filter "*.docx" | ForEach-Object {
            Write-Host "  - $($_.Name) ($($_.Length) bytes)" -ForegroundColor White
        }
        
        Write-Host "`n✅ SUCCESS! You can open these Word files to verify" -ForegroundColor Green
        
        # Open folder
        Write-Host "`nOpening folder..." -ForegroundColor Yellow
        Start-Process $extractPath
    } else {
        Write-Host "⚠️ File too small, might be an error" -ForegroundColor Yellow
        Get-Content "test_batch_docx.zip"
    }
} else {
    Write-Host "`n❌ ZIP was not created!" -ForegroundColor Red
}

# Cleanup
Remove-Item $tempJsonFile -ErrorAction SilentlyContinue

Write-Host "`n📋 Summary:" -ForegroundColor Cyan
Write-Host "  - Template: thiep_khai_truong.docx" -ForegroundColor White
Write-Host "  - JSON: 5 guests" -ForegroundColor White
Write-Host "  - Format: DOCX (Word)" -ForegroundColor White
Write-Host "  - Output: ZIP with 5 separate DOCX files" -ForegroundColor White
Write-Host "`nNote: DOCX cannot be merged (only PDF supports merge)" -ForegroundColor Yellow

Write-Host "`n✅ Test complete!" -ForegroundColor Green
