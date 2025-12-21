# Start backend with UTF-8 encoding
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
Set-Location -Path "$PSScriptRoot\backend"
Write-Host "Starting backend with UTF-8 encoding..." -ForegroundColor Green
python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000
