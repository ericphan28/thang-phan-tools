@echo off
REM Quick Install Tesseract OCR for Windows
REM Run as Administrator

echo ====================================
echo Tesseract OCR Quick Installer
echo ====================================
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script requires Administrator privileges
    echo.
    echo Please:
    echo 1. Right-click this file
    echo 2. Select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

REM Check if Chocolatey is installed
where choco >nul 2>&1
if %errorLevel% neq 0 (
    echo Chocolatey is not installed.
    echo.
    echo Option 1: Install Chocolatey first
    echo    Visit: https://chocolatey.org/install
    echo.
    echo Option 2: Manual install Tesseract
    echo    1. Download: https://github.com/UB-Mannheim/tesseract/wiki
    echo    2. Run installer: tesseract-ocr-w64-setup-v5.3.3.exe
    echo    3. Download vie.traineddata from: https://github.com/tesseract-ocr/tessdata
    echo    4. Copy to: C:\Program Files\Tesseract-OCR\tessdata\
    echo.
    pause
    exit /b 1
)

echo Installing Tesseract OCR...
echo.
choco install tesseract -y

if %errorLevel% neq 0 (
    echo ERROR: Installation failed
    pause
    exit /b 1
)

echo.
echo ====================================
echo Installation Complete!
echo ====================================
echo.
echo Tesseract installed at: C:\Program Files\Tesseract-OCR\
echo.
echo Next steps:
echo 1. Download Vietnamese language data:
echo    https://github.com/tesseract-ocr/tessdata/blob/main/vie.traineddata
echo.
echo 2. Copy vie.traineddata to:
echo    C:\Program Files\Tesseract-OCR\tessdata\
echo.
echo 3. Restart backend server
echo.
echo 4. Try OCR again - should work now!
echo.

REM Test installation
echo Testing installation...
tesseract --version
echo.

pause
