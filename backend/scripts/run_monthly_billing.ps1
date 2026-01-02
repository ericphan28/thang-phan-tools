# Monthly billing cron job for Windows
# Run via Task Scheduler: Daily at 00:00 on day 1 of month

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path (Split-Path -Parent $scriptDir) ""

Set-Location $backendDir

Write-Host "[$(Get-Date)] Running monthly billing job..." -ForegroundColor Cyan
python -m app.jobs.monthly_billing
Write-Host "[$(Get-Date)] Monthly billing job completed" -ForegroundColor Green
