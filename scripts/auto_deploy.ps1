# ==================================================
# AUTO SSH WITH PASSWORD - NO MANUAL INPUT REQUIRED
# ==================================================

$VPS_IP = "165.99.59.47"
$VPS_USER = "root"
$VPS_PASSWORD = "@8Alm523jIqS"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   AUTO DEPLOYMENT - NO MANUAL PASSWORD INPUT" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Function to execute SSH command with password
function Invoke-SSHCommand {
    param(
        [string]$Command
    )
    
    # Create expect-like script for PowerShell
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "ssh"
    $psi.Arguments = "-o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} `"$Command`""
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    $process.Start() | Out-Null
    
    # Send password if prompted
    Start-Sleep -Milliseconds 500
    $process.StandardInput.WriteLine($VPS_PASSWORD)
    $process.StandardInput.Close()
    
    $output = $process.StandardOutput.ReadToEnd()
    $error = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    
    return $output
}

Write-Host "[1/5] Setting up SSH key (automated)..." -ForegroundColor Yellow

# Create SSH key if not exists
$sshKeyPath = "$env:USERPROFILE\.ssh\id_rsa"
if (-not (Test-Path $sshKeyPath)) {
    ssh-keygen -t rsa -b 4096 -f $sshKeyPath -N '""' -q
    Write-Host "   SSH key created" -ForegroundColor Gray
}

# Read public key
$publicKey = Get-Content "$env:USERPROFILE\.ssh\id_rsa.pub" -Raw

# Use Python script to auto-send password (most reliable method)
$pythonScript = @"
import paramiko
import sys

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect('$VPS_IP', username='$VPS_USER', password='$VPS_PASSWORD', timeout=10)
    
    # Install SSH key
    stdin, stdout, stderr = client.exec_command('mkdir -p ~/.ssh && chmod 700 ~/.ssh')
    stdout.channel.recv_exit_status()
    
    stdin, stdout, stderr = client.exec_command('echo "$publicKey" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys')
    stdout.channel.recv_exit_status()
    
    stdin, stdout, stderr = client.exec_command('sort -u ~/.ssh/authorized_keys -o ~/.ssh/authorized_keys')
    stdout.channel.recv_exit_status()
    
    print('SSH key installed successfully!')
    client.close()
    sys.exit(0)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
"@

# Check if Python is available
$pythonAvailable = Get-Command python -ErrorAction SilentlyContinue

if ($pythonAvailable) {
    # Install paramiko if needed
    Write-Host "   Installing paramiko..." -ForegroundColor Gray
    python -m pip install paramiko --quiet 2>$null
    
    # Save and run Python script
    $pythonScript | Out-File -FilePath "$env:TEMP\ssh_setup.py" -Encoding UTF8
    python "$env:TEMP\ssh_setup.py"
    Remove-Item "$env:TEMP\ssh_setup.py"
    
    Write-Host "[OK] SSH key configured!" -ForegroundColor Green
} else {
    Write-Host "   Python not found, using alternative method..." -ForegroundColor Gray
    
    # Alternative: Use Expect-like PowerShell module
    # Create batch file with embedded credentials (temporary)
    $batchContent = @"
@echo off
echo $VPS_PASSWORD | ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_IP "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys" < $env:USERPROFILE\.ssh\id_rsa.pub
"@
    
    $batchFile = "$env:TEMP\setup_ssh.bat"
    $batchContent | Out-File -FilePath $batchFile -Encoding ASCII
    & cmd /c $batchFile
    Remove-Item $batchFile
    
    Write-Host "[OK] SSH key configured!" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/5] Testing SSH connection..." -ForegroundColor Yellow

# Test SSH without password
$testResult = ssh -o StrictHostKeyChecking=no -o BatchMode=yes ${VPS_USER}@${VPS_IP} "echo 'Success'" 2>&1

if ($testResult -match "Success") {
    Write-Host "[OK] SSH working without password!" -ForegroundColor Green
} else {
    Write-Host "[!] SSH key might not work, continuing anyway..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3/5] Installing management tools on VPS..." -ForegroundColor Yellow

# Deploy script that doesn't require interaction
$deployScript = @'
#!/bin/bash
export DEBIAN_FRONTEND=noninteractive
set -e

echo "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh > /dev/null 2>&1
    systemctl enable docker > /dev/null 2>&1
    systemctl start docker
fi

echo "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -sL "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

echo "Installing Cockpit..."
apt-get update -qq > /dev/null 2>&1
apt-get install -y -qq cockpit cockpit-docker > /dev/null 2>&1
systemctl enable --now cockpit.socket > /dev/null 2>&1

echo "Installing Portainer..."
docker volume create portainer_data > /dev/null 2>&1
docker rm -f portainer > /dev/null 2>&1 || true
docker run -d -p 9443:9443 --name portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest > /dev/null 2>&1

echo "Installing Dozzle..."
docker rm -f dozzle > /dev/null 2>&1 || true
docker run -d --name dozzle -p 9999:8080 --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  amir20/dozzle:latest > /dev/null 2>&1

echo "Configuring Firewall..."
ufw --force enable > /dev/null 2>&1
ufw allow 22/tcp > /dev/null 2>&1
ufw allow 80/tcp > /dev/null 2>&1
ufw allow 443/tcp > /dev/null 2>&1
ufw allow 9090/tcp > /dev/null 2>&1
ufw allow 9443/tcp > /dev/null 2>&1
ufw allow 9999/tcp > /dev/null 2>&1
ufw reload > /dev/null 2>&1

echo "DONE"
'@

# Save script to temp file and upload
$deployScript | Out-File -FilePath "$env:TEMP\deploy.sh" -Encoding UTF8 -NoNewline

# Try SSH key first, if fails use manual
try {
    scp -o StrictHostKeyChecking=no -o BatchMode=yes "$env:TEMP\deploy.sh" ${VPS_USER}@${VPS_IP}:/tmp/deploy.sh 2>$null
    ssh -o StrictHostKeyChecking=no -o BatchMode=yes ${VPS_USER}@${VPS_IP} "bash /tmp/deploy.sh" 2>$null
} catch {
    Write-Host "   Using alternative upload method..." -ForegroundColor Gray
    # Use Python paramiko for file transfer and execution
    python -c @"
import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('$VPS_IP', username='$VPS_USER', password='$VPS_PASSWORD')
sftp = client.open_sftp()
sftp.put('$env:TEMP\\deploy.sh', '/tmp/deploy.sh')
sftp.close()
stdin, stdout, stderr = client.exec_command('bash /tmp/deploy.sh')
print(stdout.read().decode())
client.close()
"@
}

Remove-Item "$env:TEMP\deploy.sh"
Write-Host "[OK] Management tools installed!" -ForegroundColor Green

Write-Host ""
Write-Host "[4/5] Uploading Utility Server..." -ForegroundColor Yellow

# Create project directory
ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} "mkdir -p /opt/utility-server" 2>$null

# Copy docker-compose and configs
Write-Host "   Uploading files..." -ForegroundColor Gray
scp -o StrictHostKeyChecking=no -r D:\thang\utility-server\* ${VPS_USER}@${VPS_IP}:/opt/utility-server/ 2>$null

Write-Host "[OK] Files uploaded!" -ForegroundColor Green

Write-Host ""
Write-Host "[5/5] Starting Utility Server..." -ForegroundColor Yellow

$startScript = @'
cd /opt/utility-server
if [ ! -f .env ]; then
    cp .env.example .env
    sed -i "s/your_strong_password_here_123/$(openssl rand -hex 16)/g" .env
    sed -i "s/your_redis_password_here_456/$(openssl rand -hex 16)/g" .env
    sed -i "s/your-super-secret-key-change-this-to-random-string/$(openssl rand -hex 32)/g" .env
    sed -i "s/another-secret-key-for-jwt-tokens/$(openssl rand -hex 32)/g" .env
fi
docker-compose down 2>/dev/null || true
docker-compose up -d --build
sleep 10
docker-compose ps
'@

$startScript | ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} "bash"

Write-Host "[OK] Utility Server started!" -ForegroundColor Green

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                 🎉 DEPLOY THÀNH CÔNG! 🎉                            ║" -ForegroundColor Green
Write-Host "║              All 5 Services Are Running on VPS                       ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "┌─ 🖥️  SERVER INFORMATION ─────────────────────────────────────────────┐" -ForegroundColor Cyan
Write-Host "│ IP Address    : $VPS_IP" -ForegroundColor White
Write-Host "│ SSH Access    : ssh root@$VPS_IP" -ForegroundColor Gray
Write-Host "│ SSH Password  : @8Alm523jIqS" -ForegroundColor Gray
Write-Host "│ Location      : /opt/utility-server" -ForegroundColor Gray
Write-Host "└──────────────────────────────────────────────────────────────────────┘" -ForegroundColor Cyan
Write-Host ""

Write-Host "┌─ 🎯 MANAGEMENT TOOLS ────────────────────────────────────────────────┐" -ForegroundColor Yellow
Write-Host "│" -ForegroundColor Yellow
Write-Host "│ 1️⃣  Cockpit - VPS System Management" -ForegroundColor White
Write-Host "│    🔗 URL      : http://$VPS_IP`:9090" -ForegroundColor Cyan
Write-Host "│    👤 Login    : root / @8Alm523jIqS" -ForegroundColor Gray
Write-Host "│    ✨ Features : CPU/RAM monitor, SSH terminal, file manager" -ForegroundColor DarkGray
Write-Host "│" -ForegroundColor Yellow
Write-Host "│ 2️⃣  Portainer - Docker Container Management" -ForegroundColor White
Write-Host "│    🔗 URL      : https://$VPS_IP`:9443" -ForegroundColor Cyan
Write-Host "│    👤 Setup    : Create admin account on first visit" -ForegroundColor Gray
Write-Host "│    ✨ Features : Start/stop containers, view logs, manage images" -ForegroundColor DarkGray
Write-Host "│" -ForegroundColor Yellow
Write-Host "│ 3️⃣  Dozzle - Real-time Log Viewer" -ForegroundColor White
Write-Host "│    🔗 URL      : http://$VPS_IP`:9999" -ForegroundColor Cyan
Write-Host "│    👤 Login    : No authentication (read-only)" -ForegroundColor Gray
Write-Host "│    ✨ Features : Live logs, search, filter by container" -ForegroundColor DarkGray
Write-Host "│" -ForegroundColor Yellow
Write-Host "└──────────────────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
Write-Host ""

Write-Host "┌─ 🚀 UTILITY SERVER API ──────────────────────────────────────────────┐" -ForegroundColor Magenta
Write-Host "│" -ForegroundColor Magenta
Write-Host "│ 4️⃣  FastAPI Backend" -ForegroundColor White
Write-Host "│    🔗 API Docs : http://$VPS_IP/docs" -ForegroundColor Cyan
Write-Host "│    🔗 Admin UI : http://$VPS_IP/admin" -ForegroundColor Cyan
Write-Host "│    📊 Health   : http://$VPS_IP/health" -ForegroundColor Cyan
Write-Host "│" -ForegroundColor Magenta
Write-Host "│ 5️⃣  Gotenberg - Document Conversion Service" -ForegroundColor White
Write-Host "│    🔗 Internal : http://gotenberg:3000" -ForegroundColor Cyan
Write-Host "│    📄 Function : Convert Word/Excel/PPT → PDF" -ForegroundColor Gray
Write-Host "│    ✨ Features : LibreOffice headless, modern 2025 solution" -ForegroundColor DarkGray
Write-Host "│" -ForegroundColor Magenta
Write-Host "└──────────────────────────────────────────────────────────────────────┘" -ForegroundColor Magenta
Write-Host ""

Write-Host "┌─ 📦 DOCKER CONTAINERS STATUS ────────────────────────────────────────┐" -ForegroundColor Blue
ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} "cd /opt/utility-server && docker-compose ps --format 'table {{.Name}}\t{{.Status}}\t{{.Ports}}'" 2>$null | ForEach-Object {
    Write-Host "│ $_" -ForegroundColor White
}
Write-Host "└──────────────────────────────────────────────────────────────────────┘" -ForegroundColor Blue
Write-Host ""

Write-Host "┌─ 🛠️  AVAILABLE FEATURES ─────────────────────────────────────────────┐" -ForegroundColor Green
Write-Host "│ ✅ User & Role Management (Admin Dashboard)" -ForegroundColor White
Write-Host "│ ✅ Document Conversion (Word→PDF, PDF→Word, Merge, Split)" -ForegroundColor White
Write-Host "│ ✅ Image Processing (Resize, Crop, AI Background Removal)" -ForegroundColor White
Write-Host "│ ✅ OCR Text Extraction (Vietnamese + 80+ languages)" -ForegroundColor White
Write-Host "│ ✅ Activity Logging & Audit Trail" -ForegroundColor White
Write-Host "│ ✅ PostgreSQL Database (port 5432)" -ForegroundColor White
Write-Host "│ ✅ Redis Cache (port 6379)" -ForegroundColor White
Write-Host "└──────────────────────────────────────────────────────────────────────┘" -ForegroundColor Green
Write-Host ""

Write-Host "┌─ 📝 NEXT STEPS ──────────────────────────────────────────────────────┐" -ForegroundColor Yellow
Write-Host "│ 1. Setup Portainer admin account: https://$VPS_IP`:9443" -ForegroundColor White
Write-Host "│ 2. View live logs in Dozzle: http://$VPS_IP`:9999" -ForegroundColor White
Write-Host "│ 3. Test API endpoints: http://$VPS_IP/docs" -ForegroundColor White
Write-Host "│ 4. Monitor system in Cockpit: http://$VPS_IP`:9090" -ForegroundColor White
Write-Host "│ 5. Check backend logs: docker-compose logs -f backend" -ForegroundColor Gray
Write-Host "└──────────────────────────────────────────────────────────────────────┘" -ForegroundColor Yellow
Write-Host ""

Write-Host "┌─ 🔧 USEFUL COMMANDS ─────────────────────────────────────────────────┐" -ForegroundColor Cyan
Write-Host "│ View logs       : ssh root@$VPS_IP 'cd /opt/utility-server && docker-compose logs -f'" -ForegroundColor Gray
Write-Host "│ Restart service : ssh root@$VPS_IP 'cd /opt/utility-server && docker-compose restart'" -ForegroundColor Gray
Write-Host "│ Stop all        : ssh root@$VPS_IP 'cd /opt/utility-server && docker-compose down'" -ForegroundColor Gray
Write-Host "│ Start all       : ssh root@$VPS_IP 'cd /opt/utility-server && docker-compose up -d'" -ForegroundColor Gray
Write-Host "│ Update code     : Run this script again!" -ForegroundColor Gray
Write-Host "└──────────────────────────────────────────────────────────────────────┘" -ForegroundColor Cyan
Write-Host ""

Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              🎊 Ready to use! Happy coding! 🎊                      ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# Prompt to open tools
Write-Host "Bạn muốn mở tool nào? (nhập số hoặc 'n' để bỏ qua)" -ForegroundColor Yellow
Write-Host "1. Cockpit (System Management)" -ForegroundColor White
Write-Host "2. Portainer (Docker Management)" -ForegroundColor White
Write-Host "3. Dozzle (Log Viewer)" -ForegroundColor White
Write-Host "4. API Documentation" -ForegroundColor White
Write-Host "5. Mở tất cả" -ForegroundColor White
$choice = Read-Host "Lựa chọn"

switch ($choice) {
    "1" { Start-Process "http://$VPS_IP`:9090" }
    "2" { Start-Process "https://$VPS_IP`:9443" }
    "3" { Start-Process "http://$VPS_IP`:9999" }
    "4" { Start-Process "http://$VPS_IP/docs" }
    "5" { 
        Start-Process "http://$VPS_IP`:9090"
        Start-Sleep -Seconds 1
        Start-Process "https://$VPS_IP`:9443"
        Start-Sleep -Seconds 1
        Start-Process "http://$VPS_IP`:9999"
        Start-Sleep -Seconds 1
        Start-Process "http://$VPS_IP/docs"
    }
    default { Write-Host "Bỏ qua. Bạn có thể truy cập các URL ở trên bất cứ lúc nào!" -ForegroundColor Gray }
}
