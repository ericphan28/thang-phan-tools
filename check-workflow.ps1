# Check GitHub Actions Workflow Status

Write-Host ""
Write-Host "Checking GitHub Actions..." -ForegroundColor Cyan
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/ericphan28/thang-phan-tools/actions/runs?per_page=5"
    $runs = $response.workflow_runs | Select-Object -First 5

    Write-Host "Latest 5 workflow runs:" -ForegroundColor Yellow
    Write-Host ""

    foreach ($run in $runs) {
        $status = $run.status
        $conclusion = $run.conclusion
        
        if ($conclusion -eq "success") {
            $icon = "[SUCCESS]"
            $color = "Green"
        } elseif ($conclusion -eq "failure") {
            $icon = "[FAILED]"
            $color = "Red"
        } elseif ($status -eq "in_progress") {
            $icon = "[RUNNING]"
            $color = "Yellow"
        } else {
            $icon = "[PENDING]"
            $color = "Gray"
        }

        Write-Host "$icon Run #$($run.run_number)" -ForegroundColor White
        Write-Host "  Status: $status" -ForegroundColor $color
        if ($conclusion) {
            Write-Host "  Result: $conclusion" -ForegroundColor $color
        }
        Write-Host "  Time: $($run.created_at)"
        Write-Host "  Commit: $($run.head_commit.message)"
        Write-Host "  URL: $($run.html_url)"
        Write-Host ""
    }

    $runningWorkflows = $runs | Where-Object { $_.status -eq "in_progress" }
    if ($runningWorkflows) {
        Write-Host "WORKFLOWS RUNNING: $($runningWorkflows.Count)" -ForegroundColor Yellow
        Write-Host "Wait 5-10 minutes for build to complete" -ForegroundColor Gray
    } else {
        Write-Host "NO WORKFLOWS RUNNING" -ForegroundColor Green
        
        $latestRun = $runs[0]
        if ($latestRun.conclusion -eq "success") {
            Write-Host "Latest workflow: SUCCESS" -ForegroundColor Green
            Write-Host "Images pushed to GHCR" -ForegroundColor Gray
        } elseif ($latestRun.conclusion -eq "failure") {
            Write-Host "Latest workflow: FAILED" -ForegroundColor Red
            Write-Host "View logs: $($latestRun.html_url)" -ForegroundColor Gray
        }
    }

} catch {
    Write-Host "ERROR calling GitHub API: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Full details: https://github.com/ericphan28/thang-phan-tools/actions" -ForegroundColor Cyan
Write-Host ""
