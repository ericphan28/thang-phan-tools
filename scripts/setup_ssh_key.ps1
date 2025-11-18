# =================================================
# SETUP SSH KEY - NO PASSWORD REQUIRED
# =================================================

$VPS_IP = "165.99.59.47"
$VPS_USER = "root"
$VPS_PASSWORD = "@8Alm523jIqS"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   SETUP SSH KEY AUTHENTICATION" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will configure SSH key so you never need to type password again!" -ForegroundColor Yellow
Write-Host ""

# Check if SSH key exists
$sshKeyPath = "$env:USERPROFILE\.ssh\id_rsa"
$sshPubKeyPath = "$env:USERPROFILE\.ssh\id_rsa.pub"

if (-not (Test-Path $sshKeyPath)) {
    Write-Host "[1/3] Generating SSH key pair..." -ForegroundColor Yellow
    
    # Create .ssh directory if not exists
    $sshDir = "$env:USERPROFILE\.ssh"
    if (-not (Test-Path $sshDir)) {
        New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
    }
    
    # Generate SSH key (no passphrase for convenience)
    ssh-keygen -t rsa -b 4096 -f $sshKeyPath -N '""' -C "windows-to-vps"
    
    Write-Host "[OK] SSH key generated!" -ForegroundColor Green
} else {
    Write-Host "[1/3] SSH key already exists" -ForegroundColor Green
}

# Read public key
$publicKey = Get-Content $sshPubKeyPath -Raw

Write-Host ""
Write-Host "[2/3] Copying public key to VPS..." -ForegroundColor Yellow

# Create script to add SSH key to authorized_keys
$setupKeyScript = @"
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo '$publicKey' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
# Remove duplicates
sort -u ~/.ssh/authorized_keys -o ~/.ssh/authorized_keys
echo 'SSH key installed successfully!'
"@

# Use sshpass or expect to handle password (if available)
# For Windows, we'll use a workaround with plink
Write-Host "Installing SSH key (you may need to enter password one last time)..." -ForegroundColor Gray

# Method 1: Try with direct SSH (will ask for password)
try {
    $setupKeyScript | ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} "bash"
    Write-Host "[OK] SSH key installed!" -ForegroundColor Green
} catch {
    Write-Host "[!] Direct SSH failed. Trying alternative method..." -ForegroundColor Yellow
    
    # Method 2: Create temp script file
    $tempScript = "$env:TEMP\setup_ssh_key.sh"
    $setupKeyScript | Out-File -FilePath $tempScript -Encoding ASCII
    
    # Upload and execute
    scp -o StrictHostKeyChecking=no $tempScript ${VPS_USER}@${VPS_IP}:/tmp/setup_ssh_key.sh
    ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} "bash /tmp/setup_ssh_key.sh && rm /tmp/setup_ssh_key.sh"
    
    Remove-Item $tempScript
    Write-Host "[OK] SSH key installed!" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/3] Testing SSH key authentication..." -ForegroundColor Yellow

# Test SSH connection without password
$testResult = ssh -o StrictHostKeyChecking=no -o BatchMode=yes ${VPS_USER}@${VPS_IP} "echo 'SSH key works!'" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] SSH key authentication working!" -ForegroundColor Green
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "   SUCCESS! NO MORE PASSWORDS NEEDED!" -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now SSH without password:" -ForegroundColor Cyan
    Write-Host "  ssh root@$VPS_IP" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "SCP without password:" -ForegroundColor Cyan
    Write-Host "  scp file.txt root@${VPS_IP}:/tmp/" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "[!] SSH key test failed. You may still need password." -ForegroundColor Yellow
    Write-Host "Error: $testResult" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
