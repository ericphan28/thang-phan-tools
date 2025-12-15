# Test với JSON as STRING (đúng format backend expect)

$template = "d:\thang\utility-server\templates\so_yeu_ly_lich_2c_template.docx"
$sample1 = "d:\thang\utility-server\templates\mau_2c_sample_1_can_bo_tre.json"

# Đọc JSON content as string
$jsonContent = Get-Content $sample1 -Raw

$url = "http://localhost:8000/api/v1/documents/pdf/generate"

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "TEST MẪU 2C - GỬI JSON AS STRING" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

Write-Host "`n🧪 Test 1: Cán bộ trẻ - Trần Văn An" -ForegroundColor Yellow

# Gửi json_data as form field (string), NOT as file
curl.exe -X POST $url `
  -F "template_file=@$template" `
  -F "json_data=$jsonContent" `
  -F "output_format=pdf" `
  -o "d:\thang\utility-server\templates\test_2c_result.pdf"

if ($LASTEXITCODE -eq 0) {
    $file = Get-Item "d:\thang\utility-server\templates\test_2c_result.pdf" -ErrorAction SilentlyContinue
    if ($file -and $file.Length -gt 10000) {
        Write-Host "✅ THÀNH CÔNG! File size: $([math]::Round($file.Length/1KB, 2)) KB" -ForegroundColor Green
        Write-Host "📄 File đã được tạo tại: $($file.FullName)" -ForegroundColor Cyan
    } else {
        Write-Host "❌ File quá nhỏ hoặc có lỗi" -ForegroundColor Red
        if ($file) {
            Write-Host "Nội dung file:" -ForegroundColor Yellow
            Get-Content "d:\thang\utility-server\templates\test_2c_result.pdf" | Select-Object -First 5
        }
    }
} else {
    Write-Host "❌ Lỗi khi gọi API (exit code: $LASTEXITCODE)" -ForegroundColor Red
}
