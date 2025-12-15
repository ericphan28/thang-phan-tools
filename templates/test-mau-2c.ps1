# Test document generation với Mẫu 2C đầy đủ

$template = "d:\thang\utility-server\templates\so_yeu_ly_lich_2c_template.docx"
$sample1 = "d:\thang\utility-server\templates\mau_2c_sample_1_can_bo_tre.json"
$sample2 = "d:\thang\utility-server\templates\mau_2c_sample_2_trung_nien.json"
$sample3 = "d:\thang\utility-server\templates\mau_2c_sample_3_giam_doc_so.json"

$url = "http://localhost:8000/api/v1/documents/pdf/generate"

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "TEST MẪU 2C-TCTW-98 - SƠ YẾU LÝ LỊCH CÁN BỘ" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

Write-Host "`n🧪 Test 1: Cán bộ trẻ - Trần Văn An (Chuyên viên)" -ForegroundColor Yellow
curl.exe -X POST $url `
  -F "template_file=@$template" `
  -F "json_data=@$sample1" `
  -F "output_format=pdf" `
  -o "d:\thang\utility-server\templates\test_2c_can_bo_tre.pdf"

if ($LASTEXITCODE -eq 0) {
    $size = (Get-Item "d:\thang\utility-server\templates\test_2c_can_bo_tre.pdf").Length
    if ($size -gt 10000) {
        Write-Host "✅ Thành công! File size: $([math]::Round($size/1KB, 2)) KB" -ForegroundColor Green
    } else {
        Write-Host "❌ File quá nhỏ ($size bytes), có thể bị lỗi" -ForegroundColor Red
        Get-Content "d:\thang\utility-server\templates\test_2c_can_bo_tre.pdf"
    }
}

Write-Host "`n🧪 Test 2: Cán bộ trung niên - Nguyễn Thị Bích Hằng (Phó Trưởng phòng)" -ForegroundColor Yellow
curl.exe -X POST $url `
  -F "template_file=@$template" `
  -F "json_data=@$sample2" `
  -F "output_format=pdf" `
  -o "d:\thang\utility-server\templates\test_2c_trung_nien.pdf"

if ($LASTEXITCODE -eq 0) {
    $size = (Get-Item "d:\thang\utility-server\templates\test_2c_trung_nien.pdf").Length
    if ($size -gt 10000) {
        Write-Host "✅ Thành công! File size: $([math]::Round($size/1KB, 2)) KB" -ForegroundColor Green
    } else {
        Write-Host "❌ File quá nhỏ, có thể bị lỗi" -ForegroundColor Red
    }
}

Write-Host "`n🧪 Test 3: Cán bộ cao cấp - Võ Minh Châu (Giám đốc Sở)" -ForegroundColor Yellow
curl.exe -X POST $url `
  -F "template_file=@$template" `
  -F "json_data=@$sample3" `
  -F "output_format=pdf" `
  -o "d:\thang\utility-server\templates\test_2c_giam_doc_so.pdf"

if ($LASTEXITCODE -eq 0) {
    $size = (Get-Item "d:\thang\utility-server\templates\test_2c_giam_doc_so.pdf").Length
    if ($size -gt 10000) {
        Write-Host "✅ Thành công! File size: $([math]::Round($size/1KB, 2)) KB" -ForegroundColor Green
    } else {
        Write-Host "❌ File quá nhỏ, có thể bị lỗi" -ForegroundColor Red
    }
}

Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "📊 TỔNG KẾT" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Get-ChildItem "d:\thang\utility-server\templates\test_2c_*.pdf" | ForEach-Object {
    Write-Host "$($_.Name): $([math]::Round($_.Length/1KB, 2)) KB" -ForegroundColor White
}
