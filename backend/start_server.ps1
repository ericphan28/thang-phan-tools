# Start Utility Server (Windows)
# Run this from: D:\thang\utility-server\backend

Write-Host "🚀 Starting Utility Server..." -ForegroundColor Green
Write-Host ""

# Set Python path
$env:PYTHONPATH = "D:\thang\utility-server\backend"

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
