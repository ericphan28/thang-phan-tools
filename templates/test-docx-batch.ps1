# Test Batch DOCX Generation (Simple)
Write-Host "Testing Batch DOCX Generation..." -ForegroundColor Cyan

$templatesPath = "d:\thang\utility-server\templates"
Set-Location $templatesPath

# Read JSON
$jsonFile = Join-Path $templatesPath "thiep_khai_truong_batch.json"
$jsonBytes = [System.IO.File]::ReadAllBytes($jsonFile)
Write-Host "JSON loaded: $($jsonBytes.Length) bytes" -ForegroundColor Green

# Create temp file
$tempJsonFile = Join-Path $templatesPath "temp_batch.json"
[System.IO.File]::WriteAllBytes($tempJsonFile, $jsonBytes)

# Generate 5 DOCX files in ZIP
Write-Host "`nGenerating 5 DOCX files..." -ForegroundColor Yellow

$response = curl.exe -X POST "http://localhost:8000/api/v1/documents/pdf/generate-batch" `
    -F "template_file=@thiep_khai_truong.docx" `
    -F "json_data=<$tempJsonFile" `
    -F "output_format=docx" `
    -F "merge_output=false" `
    -o "test_batch_docx.zip" `
    -w "%{http_code}" `
    -s

Write-Host "HTTP Status: $response"

if (Test-Path "test_batch_docx.zip") {
    $zipSize = (Get-Item "test_batch_docx.zip").Length
    Write-Host "`nGenerated: test_batch_docx.zip ($zipSize bytes)" -ForegroundColor Green
    
    if ($zipSize -gt 1000) {
        Write-Host "Extracting..." -ForegroundColor Yellow
        
        $extractPath = "test_batch_docx_output"
        if (Test-Path $extractPath) { Remove-Item $extractPath -Recurse -Force }
        Expand-Archive -Path "test_batch_docx.zip" -DestinationPath $extractPath -Force
        
        Write-Host "`nExtracted DOCX files:" -ForegroundColor Cyan
        Get-ChildItem $extractPath -Filter "*.docx" | ForEach-Object {
            Write-Host "  $($_.Name) - $($_.Length) bytes"
        }
        
        Write-Host "`nSUCCESS! Opening folder..." -ForegroundColor Green
        Start-Process $extractPath
    }
} else {
    Write-Host "Failed to generate ZIP" -ForegroundColor Red
}

# Cleanup
Remove-Item $tempJsonFile -ErrorAction SilentlyContinue

Write-Host "`nDone!" -ForegroundColor Green
