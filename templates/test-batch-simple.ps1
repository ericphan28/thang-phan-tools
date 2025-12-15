# Simple Batch Test Script
Write-Host "Testing Batch Document Generation..." -ForegroundColor Cyan

# Set paths
$templatesFolder = "d:\thang\utility-server\templates"
Set-Location $templatesFolder

# Read JSON as bytes (no encoding issues)
$jsonFile = Join-Path $templatesFolder "thiep_khai_truong_batch.json"
$jsonBytes = [System.IO.File]::ReadAllBytes($jsonFile)
Write-Host "JSON loaded: $($jsonBytes.Length) bytes" -ForegroundColor Green

# Create temp JSON file (copy bytes directly)
$tempJsonFile = Join-Path $templatesFolder "temp_batch.json"
[System.IO.File]::WriteAllBytes($tempJsonFile, $jsonBytes)

# Test 1: Merge
Write-Host "`nTest 1: Merging 5 invitations into 1 PDF..." -ForegroundColor Yellow

$response = curl.exe -X POST "http://localhost:8000/api/v1/documents/pdf/generate-batch" `
    -F "template_file=@thiep_khai_truong.docx" `
    -F "json_data=<$tempJsonFile" `
    -F "output_format=pdf" `
    -F "merge_output=true" `
    -o "test_merged.pdf" `
    -w "%{http_code}" `
    -s

Write-Host "HTTP Status: $response"

if (Test-Path "test_merged.pdf") {
    $size = (Get-Item "test_merged.pdf").Length
    Write-Host "Generated: test_merged.pdf ($size bytes)" -ForegroundColor Green
    
    if ($size -lt 1000) {
        Write-Host "ERROR - File too small:" -ForegroundColor Red
        Get-Content "test_merged.pdf"
    } else {
        Write-Host "SUCCESS! Opening PDF..." -ForegroundColor Green
        Start-Process "test_merged.pdf"
    }
} else {
    Write-Host "Failed to generate PDF" -ForegroundColor Red
}

# Test 2: ZIP
Write-Host "`nTest 2: Creating ZIP with 5 separate PDFs..." -ForegroundColor Yellow

$response2 = curl.exe -X POST "http://localhost:8000/api/v1/documents/pdf/generate-batch" `
    -F "template_file=@thiep_khai_truong.docx" `
    -F "json_data=<$tempJsonFile" `
    -F "output_format=pdf" `
    -F "merge_output=false" `
    -o "test_separate.zip" `
    -w "%{http_code}" `
    -s

Write-Host "HTTP Status: $response2"

if (Test-Path "test_separate.zip") {
    $zipSize = (Get-Item "test_separate.zip").Length
    Write-Host "Generated: test_separate.zip ($zipSize bytes)" -ForegroundColor Green
    
    if ($zipSize -gt 1000) {
        Write-Host "Extracting ZIP..." -ForegroundColor Yellow
        $extractPath = "test_output"
        if (Test-Path $extractPath) { Remove-Item $extractPath -Recurse -Force }
        Expand-Archive -Path "test_separate.zip" -DestinationPath $extractPath -Force
        
        Write-Host "`nExtracted files:" -ForegroundColor Cyan
        Get-ChildItem $extractPath | ForEach-Object {
            Write-Host "  $($_.Name) - $($_.Length) bytes"
        }
        
        Write-Host "`nOpening folder..." -ForegroundColor Green
        Start-Process $extractPath
    }
} else {
    Write-Host "Failed to generate ZIP" -ForegroundColor Red
}

# Cleanup
Remove-Item $tempJsonFile -ErrorAction SilentlyContinue

Write-Host "`nDone!" -ForegroundColor Green
