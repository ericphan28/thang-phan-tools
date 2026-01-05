# Update .env trên VPS - XÓA GEMINI_API_KEY hoàn toàn
# Chuyển sang dùng database keys ONLY

Write-Host "🚀 Cleaning VPS .env - removing GEMINI_API_KEY..." -ForegroundColor Cyan

# SSH vào VPS và chạy commands
$commands = @"
cd /root/thang-phan-tools/backend

# Backup .env
cp .env .env.backup.\$(date +%Y%m%d_%H%M%S)
echo '✅ Created backup'

# XÓA dòng GEMINI_API_KEY (không comment, xóa hẳn)
sed -i '/^GEMINI_API_KEY=/d' .env
sed -i '/^# GEMINI_API_KEY/d' .env
sed -i '/^# Old backup:/d' .env

# Update comment cho section
sed -i 's/^# Google Gemini AI$/# Google Gemini AI - Keys managed in database (Admin > AI Keys)/' .env

echo ''
echo '📋 New Gemini section in .env:'
grep -A 5 'Google Gemini' .env

echo ''
echo '✅ Done! GEMINI_API_KEY removed completely'
echo '⚠️  Make sure to add keys in database: http://165.99.59.47/admin/gemini-keys'
echo ''
echo '🔄 Now restart backend:'
echo '   docker-compose -f docker-compose.prod.yml restart backend'
"@

Write-Host "`nExecuting on VPS..." -ForegroundColor Yellow
ssh root@165.99.59.47 $commands

Write-Host "`n✅ VPS .env cleaned!" -ForegroundColor Green
Write-Host "`n⚠️  CRITICAL NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Add keys in database: http://165.99.59.47/admin/gemini-keys" -ForegroundColor White
Write-Host "2. Restart backend:" -ForegroundColor White
Write-Host "   ssh root@165.99.59.47" -ForegroundColor White
Write-Host "   cd /root/thang-phan-tools" -ForegroundColor White
Write-Host "   docker-compose -f docker-compose.prod.yml restart backend" -ForegroundColor White
