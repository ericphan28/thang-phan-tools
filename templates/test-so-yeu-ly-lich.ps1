# Test document generation với mẫu Sơ yếu lý lịch nhà nước

$template = "d:\thang\utility-server\templates\so_yeu_ly_lich_nha_nuoc.docx"
$json1 = "d:\thang\utility-server\templates\so_yeu_ly_lich_mau_1_can_bo_tre.json"

$url = "http://localhost:8000/api/v1/documents/pdf/generate"

Write-Host "🧪 Test 1: Cán bộ trẻ - Nguyễn Văn An" -ForegroundColor Cyan
curl.exe -X POST $url `
  -F "template_file=@$template" `
  -F "json_data=@$json1" `
  -F "output_format=pdf" `
  -o "d:\thang\utility-server\templates\test_so_yeu_ly_lich_1.pdf"

if ($LASTEXITCODE -eq 0) {
    $size = (Get-Item "d:\thang\utility-server\templates\test_so_yeu_ly_lich_1.pdf").Length
    Write-Host "✅ Thành công! File size: $([math]::Round($size/1KB, 2)) KB" -ForegroundColor Green
} else {
    Write-Host "❌ Lỗi khi tạo file" -ForegroundColor Red
}
