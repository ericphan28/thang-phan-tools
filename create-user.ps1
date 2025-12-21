# Add custom user to database
# Email: cym_sunset@yahoo.com
# Password: Tnt@9961266

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "ADD CUSTOM USER TO DATABASE" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "User Information:" -ForegroundColor Yellow
Write-Host "   Email:    cym_sunset@yahoo.com" -ForegroundColor White
Write-Host "   Username: cym_sunset" -ForegroundColor White
Write-Host "   Password: Tnt@9961266" -ForegroundColor White
Write-Host "   Role:     Super Admin`n" -ForegroundColor White

# Check if backend is running
Write-Host "Checking backend server..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -ErrorAction Stop
    Write-Host "Backend is running!`n" -ForegroundColor Green
} catch {
    Write-Host "Backend is not running! Please start it first:" -ForegroundColor Red
    Write-Host "   cd backend" -ForegroundColor Yellow
    Write-Host "   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`n" -ForegroundColor Yellow
    exit 1
}

# Login as admin
Write-Host "Step 1: Login as admin..." -ForegroundColor Cyan

try {
    $loginData = @{
        username = "admin"
        password = "admin123"
    } | ConvertTo-Json
    
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -Body $loginData -ContentType "application/json"
    $token = $loginResponse.access_token
    
    Write-Host "Admin login successful!" -ForegroundColor Green
    
    # Create user
    Write-Host "`nStep 2: Creating user..." -ForegroundColor Cyan
    
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
        Write-Host "User created successfully!" -ForegroundColor Green
        Write-Host "`nNew user info:" -ForegroundColor Cyan
        Write-Host "   ID:       $($newUser.id)" -ForegroundColor White
        Write-Host "   Username: $($newUser.username)" -ForegroundColor White
        Write-Host "   Email:    $($newUser.email)" -ForegroundColor White
    } catch {
        $errorMsg = $_.ErrorDetails.Message | ConvertFrom-Json
        if ($errorMsg.detail -like "*already registered*" -or $errorMsg.detail -like "*already exists*") {
            Write-Host "User already exists! Updating..." -ForegroundColor Yellow
            
            # Get existing user
            $users = Invoke-RestMethod -Uri "http://localhost:8000/api/users?search=cym_sunset" -Method GET -Headers $headers
            $existingUser = $users.items | Where-Object { $_.email -eq "cym_sunset@yahoo.com" }
            
            if ($existingUser) {
                # Update user
                $updateData = @{
                    email = "cym_sunset@yahoo.com"
                    username = "cym_sunset"
                    full_name = "CYM Sunset"
                    is_active = $true
                    is_superuser = $true
                } | ConvertTo-Json
                
                $updatedUser = Invoke-RestMethod -Uri "http://localhost:8000/api/users/$($existingUser.id)" -Method PUT -Body $updateData -Headers $headers
                Write-Host "User updated successfully!" -ForegroundColor Green
                Write-Host "Note: Password cannot be updated via API. Current password should still work." -ForegroundColor Yellow
            }
        } else {
            Write-Host "Error: $($errorMsg.detail)" -ForegroundColor Red
            throw
        }
    }
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Display credentials
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "COMPLETED!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "`nLOGIN CREDENTIALS:" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Email:    cym_sunset@yahoo.com" -ForegroundColor White
Write-Host "   Username: cym_sunset" -ForegroundColor White  
Write-Host "   Password: Tnt@9961266" -ForegroundColor White
Write-Host "   Role:     Super Admin (Full Access)" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "`nACCESS URLS:" -ForegroundColor Yellow
Write-Host "   Frontend Local:  http://localhost:5173" -ForegroundColor White
Write-Host "   Backend Local:   http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Production:      http://165.99.59.47" -ForegroundColor White
Write-Host "============================================================`n" -ForegroundColor Cyan
