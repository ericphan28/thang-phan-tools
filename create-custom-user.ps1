# Script to create/update user via API
# Run this when backend server is running

$apiUrl = "http://localhost:8000"  # Change to http://165.99.59.47 for production

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "🔐 CREATING/UPDATING USER VIA API" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Step 1: Login as admin to get token
Write-Host "Step 1: Login as admin..." -ForegroundColor Yellow
$loginData = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$apiUrl/api/auth/login" -Method POST -Body $loginData -ContentType "application/json"
    $token = $response.access_token
    Write-Host "✅ Admin login successful!" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Cannot login as admin. Is the backend server running?" -ForegroundColor Red
    Write-Host "   Start backend: cd backend; `$env:PYTHONPATH='D:\Thang\thang-phan-tools\backend'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Yellow
    exit 1
}

# Step 2: Check if user exists
Write-Host "`nStep 2: Checking if user exists..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

try {
    $users = Invoke-RestMethod -Uri "$apiUrl/api/users?search=cym_sunset" -Method GET -Headers $headers
    $existingUser = $users.items | Where-Object { $_.email -eq "cym_sunset@yahoo.com" }
    
    if ($existingUser) {
        Write-Host "⚠️  User exists (ID: $($existingUser.id)). Will update password..." -ForegroundColor Yellow
        
        # Update user
        $updateData = @{
            email = "cym_sunset@yahoo.com"
            username = "cym_sunset"
            full_name = "CYM Sunset"
            is_active = $true
            is_superuser = $true
        } | ConvertTo-Json
        
        $updatedUser = Invoke-RestMethod -Uri "$apiUrl/api/users/$($existingUser.id)" -Method PUT -Body $updateData -Headers $headers
        Write-Host "✅ User updated successfully!" -ForegroundColor Green
        
        # Change password via API endpoint
        Write-Host "`nStep 3: Updating password..." -ForegroundColor Yellow
        # Note: You may need to manually change password through the UI or add a password reset endpoint
        Write-Host "⚠️  Password update via API may require additional endpoint. Please change password manually in UI." -ForegroundColor Yellow
        
    } else {
        Write-Host "Creating new user..." -ForegroundColor Yellow
        
        # Create new user
        $createData = @{
            email = "cym_sunset@yahoo.com"
            username = "cym_sunset"
            password = "Tnt@9961266"
            full_name = "CYM Sunset"
            is_active = $true
            is_superuser = $true
        } | ConvertTo-Json
        
        $newUser = Invoke-RestMethod -Uri "$apiUrl/api/users" -Method POST -Body $createData -Headers $headers
        Write-Host "✅ User created successfully!" -ForegroundColor Green
    }
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response: $($_.ErrorDetails.Message)" -ForegroundColor Red
    exit 1
}

# Display credentials
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "📧 LOGIN CREDENTIALS:" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Email:    cym_sunset@yahoo.com" -ForegroundColor White
Write-Host "   Username: cym_sunset" -ForegroundColor White
Write-Host "   Password: Tnt@9961266" -ForegroundColor White
Write-Host "   Role:     Super Admin" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "`n🌐 LOGIN URL:" -ForegroundColor Cyan
Write-Host "   Local:      http://localhost:5173" -ForegroundColor White
Write-Host "   Production: http://165.99.59.47" -ForegroundColor White
Write-Host "============================================================`n" -ForegroundColor Cyan
