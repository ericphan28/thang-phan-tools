# Test Mau 2C with proper JSON string format

$template = "d:\thang\utility-server\templates\so_yeu_ly_lich_2c_template.docx"
$jsonFile = "d:\thang\utility-server\templates\mau_2c_sample_1_can_bo_tre.json"
$output = "d:\thang\utility-server\templates\test_2c_result.pdf"
$url = "http://localhost:8000/api/v1/documents/pdf/generate"

Write-Host "TEST MAU 2C" -ForegroundColor Cyan
Write-Host "Reading JSON file..." -ForegroundColor Yellow

# Read and minify JSON (remove whitespace for safer transmission)
$jsonObj = Get-Content $jsonFile -Raw | ConvertFrom-Json
$jsonString = $jsonObj | ConvertTo-Json -Compress -Depth 10

Write-Host "JSON size: $($jsonString.Length) characters" -ForegroundColor Gray

# Create multipart form data manually using Invoke-WebRequest
$form = @{
    template_file = Get-Item $template
    json_data = $jsonString
    output_format = 'pdf'
}

Write-Host "Calling API..." -ForegroundColor Yellow

try {
    Invoke-WebRequest -Uri $url -Method Post -Form $form -OutFile $output
    
    $file = Get-Item $output
    if ($file.Length -gt 10000) {
        Write-Host "SUCCESS! File size: $([math]::Round($file.Length/1KB, 2)) KB" -ForegroundColor Green
    } else {
        Write-Host "ERROR: File too small" -ForegroundColor Red
        Get-Content $output
    }
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
