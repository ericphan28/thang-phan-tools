# ============================================
# Development Servers Manager - Simple Version
# Quan ly Backend (FastAPI) + Frontend (Vite)
# ============================================

function Write-Log {
    param([string]$Message, [string]$Color = "White", [string]$Tag = "INFO")
    $time = Get-Date -Format "HH:mm:ss"
    Write-Host "[$time][$Tag] $Message" -ForegroundColor $Color
}

function Stop-AllServers {
    Write-Log "Dang dung tat ca servers..." "Yellow" "STOP"
    
    # Dung Python
    Get-Process python -ErrorAction SilentlyContinue | Where-Object { 
        $_.Path -like "*utility-server*" 
    } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    # Dung Node
    Get-Process node -ErrorAction SilentlyContinue | Where-Object { 
        $_.CommandLine -like "*vite*" 
    } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Start-Sleep -Seconds 1
    Write-Log "Da don dep xong!" "Green" "STOP"
}

# ============================================
# MAIN
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   UTILITY SERVER - DEV MODE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Cleanup truoc
Stop-AllServers
Start-Sleep -Seconds 2

# Start Backend
Write-Log "Dang khoi dong Backend (Port 8000)..." "Cyan" "BACKEND"
$backendPath = Join-Path $PSScriptRoot "backend"
$backendJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location $path
    $env:PYTHONPATH = $path
    python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000 2>&1
} -ArgumentList $backendPath

Start-Sleep -Seconds 4

# Start Frontend
Write-Log "Dang khoi dong Frontend (Port 5173)..." "Magenta" "FRONTEND"
$frontendPath = Join-Path $PSScriptRoot "frontend"
$frontendJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location $path
    npm run dev 2>&1
} -ArgumentList $frontendPath

Start-Sleep -Seconds 5

# Hien thi thong tin
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SERVERS DANG CHAY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Backend:  http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "  Frontend: http://127.0.0.1:5173" -ForegroundColor Green
Write-Host "  API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Nhan Ctrl+C de dung servers" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Dang theo doi logs (Ctrl+C de thoat)..." "White" "MONITOR"
Write-Host ""

# Monitor logs with auto-restart
$backendRestarts = 0
$frontendRestarts = 0
$maxRestarts = 3

try {
    while ($true) {
        # Backend logs
        $backendOut = Receive-Job -Job $backendJob -ErrorAction SilentlyContinue
        if ($backendOut) {
            $backendOut | ForEach-Object {
                if ($_ -match "error|exception") {
                    Write-Log $_ "Red" "BACKEND"
                } elseif ($_ -match "WARNING") {
                    Write-Log $_ "Yellow" "BACKEND"
                } elseif ($_ -match "startup complete|running") {
                    Write-Log $_ "Green" "BACKEND"
                } else {
                    Write-Host "[BACKEND] $_" -ForegroundColor Cyan
                }
            }
        }
        
        # Frontend logs
        $frontendOut = Receive-Job -Job $frontendJob -ErrorAction SilentlyContinue
        if ($frontendOut) {
            $frontendOut | ForEach-Object {
                if ($_ -match "error|failed") {
                    Write-Log $_ "Red" "FRONTEND"
                } elseif ($_ -match "warning") {
                    Write-Log $_ "Yellow" "FRONTEND"
                } elseif ($_ -match "ready|Local|Server running") {
                    Write-Log $_ "Green" "FRONTEND"
                } else {
                    Write-Host "[FRONTEND] $_" -ForegroundColor Magenta
                }
            }
        }
        
        # Auto-restart backend if crashed
        if ($backendJob.State -ne "Running") {
            if ($backendRestarts -lt $maxRestarts) {
                $backendRestarts++
                Write-Log "Backend da dung! Tu dong restart lan $backendRestarts/$maxRestarts..." "Yellow" "AUTO-RESTART"
                Remove-Job -Job $backendJob -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2
                $backendJob = Start-Job -ScriptBlock {
                    param($path)
                    Set-Location $path
                    $env:PYTHONPATH = $path
                    python -m uvicorn app.main_simple:app --reload --host 0.0.0.0 --port 8000 2>&1
                } -ArgumentList $backendPath
                Write-Log "Backend da duoc khoi dong lai!" "Green" "AUTO-RESTART"
            } else {
                Write-Log "Backend da crash qua $maxRestarts lan. Dung lai!" "Red" "ERROR"
                break
            }
        }
        
        # Auto-restart frontend if crashed
        if ($frontendJob.State -ne "Running") {
            if ($frontendRestarts -lt $maxRestarts) {
                $frontendRestarts++
                Write-Log "Frontend da dung! Tu dong restart lan $frontendRestarts/$maxRestarts..." "Yellow" "AUTO-RESTART"
                Remove-Job -Job $frontendJob -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2
                $frontendJob = Start-Job -ScriptBlock {
                    param($path)
                    Set-Location $path
                    npm run dev 2>&1
                } -ArgumentList $frontendPath
                Write-Log "Frontend da duoc khoi dong lai!" "Green" "AUTO-RESTART"
            } else {
                Write-Log "Frontend da crash qua $maxRestarts lan. Dung lai!" "Red" "ERROR"
                break
            }
        }
        
        Start-Sleep -Milliseconds 500
    }
} finally {
    Write-Host ""
    Write-Log "Dang don dep va thoat..." "Yellow" "EXIT"
    Stop-Job -Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job -Job $backendJob, $frontendJob -Force -ErrorAction SilentlyContinue
    Stop-AllServers
    Write-Log "Da thoat sach se!" "Green" "EXIT"
}
