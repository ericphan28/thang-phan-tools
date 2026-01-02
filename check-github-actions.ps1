# ==================================================
# CHECK GITHUB ACTIONS WORKFLOW STATUS
# ==================================================

Write-Host "`n🔍 KIỂM TRA GITHUB ACTIONS..." -ForegroundColor Cyan
Write-Host ""

try {
    # Get latest workflow runs
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/ericphan28/thang-phan-tools/actions/runs?per_page=5"
    $runs = $response.workflow_runs | Select-Object -First 5

    Write-Host "📊 5 WORKFLOW RUNS GẦN NHẤT:`n" -ForegroundColor Yellow

    foreach ($run in $runs) {
        $status = $run.status
        $conclusion = $run.conclusion
        
        # Icon
        $icon = switch ($conclusion) {
            "success" { "✅" }
            "failure" { "❌" }
            default {
                if ($status -eq "in_progress") { "🔄" }
                elseif ($status -eq "queued") { "⏳" }
                else { "⏸️" }
            }
        }
        
        # Color
        $color = switch ($conclusion) {
            "success" { "Green" }
            "failure" { "Red" }
            default { "Yellow" }
        }

        Write-Host "$icon Run #$($run.run_number)" -ForegroundColor White
        Write-Host "   Status:  $status" -ForegroundColor $color
        if ($conclusion) {
            Write-Host "   Result:  $conclusion" -ForegroundColor $color
        }
        Write-Host "   Created: $($run.created_at)"
        Write-Host "   Commit:  $($run.head_commit.message)"
        Write-Host "   URL:     $($run.html_url)"
        Write-Host ""
    }

    # Check if any workflow is running
    $runningWorkflows = $runs | Where-Object { $_.status -eq "in_progress" }
    if ($runningWorkflows) {
        Write-Host "🔄 CÓ $($runningWorkflows.Count) WORKFLOW ĐANG CHẠY!" -ForegroundColor Yellow
        Write-Host "   Đợi khoảng 5-10 phút để build xong`n" -ForegroundColor Gray
    } else {
        Write-Host "✅ KHÔNG CÓ WORKFLOW NÀO ĐANG CHẠY" -ForegroundColor Green
        
        $latestRun = $runs[0]
        if ($latestRun.conclusion -eq "success") {
            Write-Host "✅ Workflow gần nhất THÀNH CÔNG" -ForegroundColor Green
            Write-Host "   → Images đã được push lên GHCR`n" -ForegroundColor Gray
        } elseif ($latestRun.conclusion -eq "failure") {
            Write-Host "❌ Workflow gần nhất BỊ LỖI" -ForegroundColor Red
            Write-Host "   → Xem logs tại: $($latestRun.html_url)`n" -ForegroundColor Gray
        }
    }

} catch {
    Write-Host "❌ Lỗi khi gọi GitHub API: $_" -ForegroundColor Red
}

Write-Host "📍 Chi tiết đầy đủ:" -ForegroundColor Cyan
Write-Host "   https://github.com/ericphan28/thang-phan-tools/actions`n" -ForegroundColor White

Write-Host "TIP: If workflow fails, check:" -ForegroundColor Yellow
Write-Host "   1. View logs of failed job (click red job)" -ForegroundColor Gray
Write-Host "   2. Check file .github/workflows/backend-image-ghcr.yml" -ForegroundColor Gray
Write-Host "   3. Check Docker build errors" -ForegroundColor Gray
Write-Host ""
