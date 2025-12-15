# TEST ALL SAMPLES - Generate 9 PDFs

Write-Host "🚀 GENERATING 9 SAMPLE PDFs..." -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000/api/v1/pdf/document-generation"
$templatesDir = "d:\thang\utility-server\templates"

# Create output directory
$outputDir = "$templatesDir\output"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
    Write-Host "✅ Created output directory" -ForegroundColor Green
}

# Test counter
$success = 0
$failed = 0

Write-Host "📋 TESTING THIỆP KHAI TRƯƠNG..." -ForegroundColor Yellow

# Khai Trương Sample 1
try {
    Write-Host "  Testing Sample 1 (Điện Máy)..." -NoNewline
    curl -X POST $baseUrl `
      -F "template=@$templatesDir\thiep_khai_truong.docx" `
      -F "data=@$templatesDir\thiep_khai_truong_sample1.json" `
      -F "output_format=PDF" `
      -o "$outputDir\khai_truong_dien_may.pdf" `
      --silent
    Write-Host " ✅" -ForegroundColor Green
    $success++
} catch {
    Write-Host " ❌" -ForegroundColor Red
    $failed++
}

# Khai Trương Sample 2
try {
    Write-Host "  Testing Sample 2 (Nhà Hàng)..." -NoNewline
    curl -X POST $baseUrl `
      -F "template=@$templatesDir\thiep_khai_truong.docx" `
      -F "data=@$templatesDir\thiep_khai_truong_sample2.json" `
      -F "output_format=PDF" `
      -o "$outputDir\khai_truong_nha_hang.pdf" `
      --silent
    Write-Host " ✅" -ForegroundColor Green
    $success++
} catch {
    Write-Host " ❌" -ForegroundColor Red
    $failed++
}

# Khai Trương Sample 3
try {
    Write-Host "  Testing Sample 3 (Anh Ngữ)..." -NoNewline
    curl -X POST $baseUrl `
      -F "template=@$templatesDir\thiep_khai_truong.docx" `
      -F "data=@$templatesDir\thiep_khai_truong_sample3.json" `
      -F "output_format=PDF" `
      -o "$outputDir\khai_truong_anh_ngu.pdf" `
      --silent
    Write-Host " ✅" -ForegroundColor Green
    $success++
} catch {
    Write-Host " ❌" -ForegroundColor Red
    $failed++
}

Write-Host ""
Write-Host "🎂 TESTING THIỆP SINH NHẬT..." -ForegroundColor Yellow

# Sinh Nhật Sample 1
try {
    Write-Host "  Testing Sample 1 (Kid 5)..." -NoNewline
    curl -X POST $baseUrl `
      -F "template=@$templatesDir\thiep_sinh_nhat.docx" `
      -F "data=@$templatesDir\thiep_sinh_nhat_sample1.json" `
      -F "output_format=PDF" `
      -o "$outputDir\birthday_kid_5.pdf" `
      --silent
    Write-Host " ✅" -ForegroundColor Green
    $success++
} catch {
    Write-Host " ❌" -ForegroundColor Red
    $failed++
}

# Sinh Nhật Sample 2
try {
    Write-Host "  Testing Sample 2 (Adult 30)..." -NoNewline
    curl -X POST $baseUrl `
      -F "template=@$templatesDir\thiep_sinh_nhat.docx" `
      -F "data=@$templatesDir\thiep_sinh_nhat_sample2.json" `
      -F "output_format=PDF" `
      -o "$outputDir\birthday_adult_30.pdf" `
      --silent
    Write-Host " ✅" -ForegroundColor Green
    $success++
} catch {
    Write-Host " ❌" -ForegroundColor Red
    $failed++
}

# Sinh Nhật Sample 3
try {
    Write-Host "  Testing Sample 3 (Senior 60)..." -NoNewline
    curl -X POST $baseUrl `
      -F "template=@$templatesDir\thiep_sinh_nhat.docx" `
      -F "data=@$templatesDir\thiep_sinh_nhat_sample3.json" `
      -F "output_format=PDF" `
      -o "$outputDir\birthday_senior_60.pdf" `
      --silent
    Write-Host " ✅" -ForegroundColor Green
    $success++
} catch {
    Write-Host " ❌" -ForegroundColor Red
    $failed++
}

Write-Host ""
Write-Host "📄 TESTING HỢP ĐỒNG LAO ĐỘNG..." -ForegroundColor Yellow

# Hợp Đồng Sample 1
try {
    Write-Host "  Testing Sample 1 (Dev Senior)..." -NoNewline
    curl -X POST $baseUrl `
      -F "template=@$templatesDir\hop_dong_lao_dong.docx" `
      -F "data=@$templatesDir\hop_dong_lao_dong_sample1.json" `
      -F "output_format=PDF" `
      -o "$outputDir\contract_dev_senior.pdf" `
      --silent
    Write-Host " ✅" -ForegroundColor Green
    $success++
} catch {
    Write-Host " ❌" -ForegroundColor Red
    $failed++
}

# Hợp Đồng Sample 2
try {
    Write-Host "  Testing Sample 2 (Marketing Manager)..." -NoNewline
    curl -X POST $baseUrl `
      -F "template=@$templatesDir\hop_dong_lao_dong.docx" `
      -F "data=@$templatesDir\hop_dong_lao_dong_sample2.json" `
      -F "output_format=PDF" `
      -o "$outputDir\contract_marketing_manager.pdf" `
      --silent
    Write-Host " ✅" -ForegroundColor Green
    $success++
} catch {
    Write-Host " ❌" -ForegroundColor Red
    $failed++
}

# Hợp Đồng Sample 3
try {
    Write-Host "  Testing Sample 3 (Project Director)..." -NoNewline
    curl -X POST $baseUrl `
      -F "template=@$templatesDir\hop_dong_lao_dong.docx" `
      -F "data=@$templatesDir\hop_dong_lao_dong_sample3.json" `
      -F "output_format=PDF" `
      -o "$outputDir\contract_project_director.pdf" `
      --silent
    Write-Host " ✅" -ForegroundColor Green
    $success++
} catch {
    Write-Host " ❌" -ForegroundColor Red
    $failed++
}

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📊 TEST RESULTS:" -ForegroundColor Cyan
Write-Host "  ✅ Success: $success/9" -ForegroundColor Green
Write-Host "  ❌ Failed: $failed/9" -ForegroundColor Red
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($success -eq 9) {
    Write-Host "🎉 ALL TESTS PASSED! Check output folder:" -ForegroundColor Green
    Write-Host "   $outputDir" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📂 Opening output folder..." -ForegroundColor Cyan
    Start-Process $outputDir
} else {
    Write-Host "⚠️  Some tests failed. Check server logs for details." -ForegroundColor Yellow
}
