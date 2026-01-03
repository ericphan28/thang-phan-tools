# Monitor GitHub Actions Workflow
param(
    [string]$RunId = "20663749630"
)

$headers = @{ Accept = "application/vnd.github+json" }
$baseUrl = "https://api.github.com/repos/ericphan28/thang-phan-tools/actions/runs"

Write-Host "`n🚀 Monitoring GitHub Actions Workflow #$RunId" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Gray

$checkCount = 0
while ($true) {
    $checkCount++
    
    try {
        $run = Invoke-RestMethod -Uri "$baseUrl/$RunId" -Headers $headers
        
        $duration = [math]::Round((New-TimeSpan -Start $run.created_at -End (Get-Date)).TotalMinutes, 1)
        $timestamp = Get-Date -Format "HH:mm:ss"
        
        Write-Host "[$timestamp] Check #$checkCount | " -NoNewline -ForegroundColor Gray
        
        if ($run.status -eq "completed") {
            Write-Host "COMPLETED | " -NoNewline -ForegroundColor Green
            
            if ($run.conclusion -eq "success") {
                Write-Host "✅ SUCCESS" -ForegroundColor Green
                
                Write-Host "`n════════════════════════════════════════" -ForegroundColor Green
                Write-Host "   🎉 DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
                Write-Host "════════════════════════════════════════" -ForegroundColor Green
                
                Write-Host "`n✅ Docker image pushed to:" -ForegroundColor Cyan
                Write-Host "   ghcr.io/ericphan28/thang-phan-tools-backend:latest" -ForegroundColor White
                
                Write-Host "`n📦 Next steps - Deploy to VPS:" -ForegroundColor Yellow
                Write-Host "   1. SSH vào VPS: ssh root@your-vps-ip" -ForegroundColor Gray
                Write-Host "   2. cd /root/thang-phan-tools" -ForegroundColor Gray
                Write-Host "   3. docker-compose -f docker-compose.prod.yml pull" -ForegroundColor Gray
                Write-Host "   4. docker-compose -f docker-compose.prod.yml up -d" -ForegroundColor Gray
                
                Write-Host "`n🔗 Workflow URL:" -ForegroundColor Cyan
                Write-Host "   $($run.html_url)" -ForegroundColor Blue
                
                Write-Host "`n⏱️  Total time: $duration minutes`n" -ForegroundColor Gray
                
                break
            }
            elseif ($run.conclusion -eq "failure") {
                Write-Host "❌ FAILED" -ForegroundColor Red
                
                Write-Host "`n════════════════════════════════════════" -ForegroundColor Red
                Write-Host "   ⚠️  BUILD FAILED!" -ForegroundColor Red
                Write-Host "════════════════════════════════════════" -ForegroundColor Red
                
                Write-Host "`n❌ Workflow failed after $duration minutes" -ForegroundColor Red
                Write-Host "`n🔍 Check logs at:" -ForegroundColor Yellow
                Write-Host "   $($run.html_url)" -ForegroundColor Blue
                
                Write-Host "`n💡 Common issues:" -ForegroundColor Cyan
                Write-Host "   - Docker build errors" -ForegroundColor Gray
                Write-Host "   - Missing dependencies" -ForegroundColor Gray
                Write-Host "   - GitHub Actions permissions" -ForegroundColor Gray
                Write-Host "   - GHCR authentication`n" -ForegroundColor Gray
                
                break
            }
            else {
                Write-Host "⚠️  $($run.conclusion.ToUpper())" -ForegroundColor Yellow
                break
            }
        }
        else {
            Write-Host "⏳ IN PROGRESS | $duration mins" -ForegroundColor Yellow
            
            # Get job details
            try {
                $jobs = Invoke-RestMethod -Uri "$baseUrl/$RunId/jobs" -Headers $headers
                if ($jobs.jobs.Count -gt 0) {
                    $currentJob = $jobs.jobs[0]
                    $completedSteps = ($currentJob.steps | Where-Object { $_.status -eq "completed" }).Count
                    $totalSteps = $currentJob.steps.Count
                    Write-Host " | Steps: $completedSteps/$totalSteps" -NoNewline -ForegroundColor Cyan
                }
            }
            catch {
                # Ignore job fetch errors
            }
            
            Write-Host ""
        }
        
        if ($run.status -ne "completed") {
            Start-Sleep -Seconds 15
        }
    }
    catch {
        Write-Host "[$timestamp] ⚠️  API Error: $($_.Exception.Message)" -ForegroundColor Red
        Start-Sleep -Seconds 20
    }
}

Write-Host "Monitoring stopped.`n" -ForegroundColor Gray
