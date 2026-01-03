# Live Monitor GitHub Workflow
param([string]$RunId = "20663984063")

$url = "https://api.github.com/repos/ericphan28/thang-phan-tools/actions/runs/$RunId"

Write-Host "`nMonitoring workflow $RunId..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop`n"

$count = 0
while ($true) {
    $count++
    $run = Invoke-RestMethod $url
    
    $mins = [math]::Round((New-TimeSpan -Start $run.created_at -End (Get-Date)).TotalMinutes, 1)
    $time = Get-Date -Format "HH:mm:ss"
    
    Write-Host "[$time] Check #$count | Status: $($run.status) | Duration: $mins mins"
    
    if ($run.status -eq "completed") {
        Write-Host "`n========================================" -ForegroundColor $(if($run.conclusion -eq 'success'){'Green'}else{'Red'})
        Write-Host "WORKFLOW COMPLETED: $($run.conclusion.ToUpper())" -ForegroundColor $(if($run.conclusion -eq 'success'){'Green'}else{'Red'})
        Write-Host "========================================" -ForegroundColor $(if($run.conclusion -eq 'success'){'Green'}else{'Red'})
        
        if ($run.conclusion -eq "success") {
            Write-Host "`nDocker image pushed successfully!" -ForegroundColor Green
            Write-Host "Image: ghcr.io/ericphan28/thang-phan-tools-backend:latest" -ForegroundColor Cyan
            Write-Host "`nNext: Deploy to VPS" -ForegroundColor Yellow
            Write-Host "  docker-compose -f docker-compose.prod.yml pull" -ForegroundColor Gray
            Write-Host "  docker-compose -f docker-compose.prod.yml up -d`n" -ForegroundColor Gray
        } else {
            Write-Host "`nCheck logs at: $($run.html_url)`n" -ForegroundColor Yellow
        }
        
        break
    }
    
    Start-Sleep 15
}
