# Test with JSON as STRING (correct format for backend)

$template = "d:\thang\utility-server\templates\so_yeu_ly_lich_2c_template.docx"
$sample1 = "d:\thang\utility-server\templates\mau_2c_sample_1_can_bo_tre.json"

# Read JSON content as string
$jsonContent = Get-Content $sample1 -Raw

$url = "http://localhost:8000/api/v1/documents/pdf/generate"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "TEST MAU 2C - SEND JSON AS STRING" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

Write-Host "`nTest 1: Can bo tre - Tran Van An" -ForegroundColor Yellow

# Send json_data as form field (string), NOT as file
curl.exe -X POST $url -F "template_file=@$template" -F "json_data=$jsonContent" -F "output_format=pdf" -o "d:\thang\utility-server\templates\test_2c_result.pdf"

if ($LASTEXITCODE -eq 0) {
    $file = Get-Item "d:\thang\utility-server\templates\test_2c_result.pdf" -ErrorAction SilentlyContinue
    if ($file -and $file.Length -gt 10000) {
        Write-Host "SUCCESS! File size: $([math]::Round($file.Length/1KB, 2)) KB" -ForegroundColor Green
        Write-Host "File created at: $($file.FullName)" -ForegroundColor Cyan
    } else {
        Write-Host "File too small or error" -ForegroundColor Red
        if ($file) {
            Write-Host "File content:" -ForegroundColor Yellow
            Get-Content "d:\thang\utility-server\templates\test_2c_result.pdf" | Select-Object -First 5
        }
    }
} else {
    Write-Host "Error calling API (exit code: $LASTEXITCODE)" -ForegroundColor Red
}
