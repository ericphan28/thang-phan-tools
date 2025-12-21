# Script to add user directly to database (when backend is running)
# This script uses the backend's internal API

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "🔐 THÊM TÀI KHOẢN VÀO DATABASE" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Thông tin tài khoản sẽ được thêm:" -ForegroundColor Yellow
Write-Host "   Email:    cym_sunset@yahoo.com" -ForegroundColor White
Write-Host "   Username: cym_sunset" -ForegroundColor White
Write-Host "   Password: Tnt@9961266" -ForegroundColor White
Write-Host "   Role:     Super Admin`n" -ForegroundColor White

# Check if backend is running
Write-Host "Kiểm tra backend server..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -ErrorAction Stop
    Write-Host "✅ Backend đang chạy!`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend chưa chạy! Vui lòng khởi động backend trước:" -ForegroundColor Red
    Write-Host "   cd backend" -ForegroundColor Yellow
    Write-Host "   `$env:PYTHONPATH='D:\Thang\thang-phan-tools\backend'" -ForegroundColor Yellow
    Write-Host "   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`n" -ForegroundColor Yellow
    
    $choice = Read-Host "Bạn có muốn khởi động backend ngay không? (y/n)"
    if ($choice -eq "y") {
        Write-Host "`nĐang khởi động backend..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd D:\Thang\thang-phan-tools\backend; `$env:PYTHONPATH='D:\Thang\thang-phan-tools\backend'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
        Write-Host "Đợi 10 giây để backend khởi động..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    } else {
        exit 1
    }
}

# Method 1: Try to login with admin and create user
Write-Host "Cách 1: Thử tạo user qua API..." -ForegroundColor Cyan

try {
    # Login as admin
    $loginData = @{
        username = "admin"
        password = "admin123"
    } | ConvertTo-Json
    
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -Body $loginData -ContentType "application/json"
    $token = $loginResponse.access_token
    
    Write-Host "✅ Đăng nhập admin thành công!" -ForegroundColor Green
    
    # Create user
    $userData = @{
        email = "cym_sunset@yahoo.com"
        username = "cym_sunset"
        password = "Tnt@9961266"
        full_name = "CYM Sunset"
        is_active = $true
        is_superuser = $true
    } | ConvertTo-Json
    
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    try {
        $newUser = Invoke-RestMethod -Uri "http://localhost:8000/api/users" -Method POST -Body $userData -Headers $headers
        Write-Host "✅ Tạo user thành công!" -ForegroundColor Green
        Write-Host "`nThông tin user mới:" -ForegroundColor Cyan
        Write-Host "   ID:       $($newUser.id)" -ForegroundColor White
        Write-Host "   Username: $($newUser.username)" -ForegroundColor White
        Write-Host "   Email:    $($newUser.email)" -ForegroundColor White
    } catch {
        if ($_.Exception.Message -like "*already registered*" -or $_.Exception.Message -like "*already exists*") {
            Write-Host "⚠️  User đã tồn tại! Đang cập nhật..." -ForegroundColor Yellow
            
            # Get user ID
            $users = Invoke-RestMethod -Uri "http://localhost:8000/api/users?search=cym_sunset" -Method GET -Headers $headers
            $existingUser = $users.items | Where-Object { $_.email -eq "cym_sunset@yahoo.com" }
            
            if ($existingUser) {
                # Update user to ensure is_superuser is true
                $updateData = @{
                    email = "cym_sunset@yahoo.com"
                    username = "cym_sunset"
                    full_name = "CYM Sunset"
                    is_active = $true
                    is_superuser = $true
                } | ConvertTo-Json
                
                $updatedUser = Invoke-RestMethod -Uri "http://localhost:8000/api/users/$($existingUser.id)" -Method PUT -Body $updateData -Headers $headers
                Write-Host "✅ Cập nhật user thành công!" -ForegroundColor Green
            }
        } else {
            throw
        }
    }
    
} catch {
    Write-Host "❌ Lỗi: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "Chi tiết: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

# Display final credentials
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "COMPLETED!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "`nLOGIN INFORMATION:" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Email:    cym_sunset@yahoo.com" -ForegroundColor White
Write-Host "   Username: cym_sunset" -ForegroundColor White  
Write-Host "   Password: Tnt@9961266" -ForegroundColor White
Write-Host "   Role:     Super Admin" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "`nACCESS SYSTEM:" -ForegroundColor Yellow
Write-Host "   Frontend Local:  http://localhost:5173" -ForegroundColor White
Write-Host "   Backend Local:   http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Production:      http://165.99.59.47" -ForegroundColor White
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Notes:" -ForegroundColor Yellow
Write-Host "   - Account has Super Admin privileges" -ForegroundColor White
Write-Host "   - Can login with email OR username" -ForegroundColor White
Write-Host "   - Password: Tnt@9961266" -ForegroundColor White
Write-Host ""
