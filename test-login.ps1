Write-Host "Testing Backend Login..." -ForegroundColor Cyan

$body = @{
    username = 'admin'
    password = 'admin123'
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/auth/login' `
        -Method Post `
        -Body $body `
        -ContentType 'application/json'
    
    Write-Host "`n✅ LOGIN SUCCESS!" -ForegroundColor Green
    Write-Host "`nUser Info:" -ForegroundColor Yellow
    Write-Host "  Username: $($response.user.username)"
    Write-Host "  Email: $($response.user.email)"
    Write-Host "  Roles: $($response.user.roles -join ', ')"
    Write-Host "`nToken:" -ForegroundColor Yellow
    Write-Host "  Access Token: $($response.token.access_token.Substring(0,50))..."
    Write-Host "  Token Type: $($response.token.token_type)"
    
} catch {
    Write-Host "`n❌ LOGIN FAILED!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody" -ForegroundColor Red
    }
}
