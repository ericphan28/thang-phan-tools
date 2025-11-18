# Simple Deployment Script
$VPS_IP = "165.99.59.47"
$VPS_USER = "root"
$VPS_PATH = "/opt/utility-server"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   DEPLOYING ALL 4 TOOLS TO VPS" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Deploy infrastructure
Write-Host "[1/4] Installing Docker + Management Tools..." -ForegroundColor Yellow

$setupScript = @'
#!/bin/bash
set -e

echo "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

echo "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

echo "Installing Cockpit..."
apt update
apt install -y cockpit cockpit-docker
systemctl enable --now cockpit.socket

echo "Installing Portainer..."
docker volume create portainer_data
docker rm -f portainer 2>/dev/null || true
docker run -d -p 9443:9443 --name portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest

echo "Installing Dozzle..."
docker rm -f dozzle 2>/dev/null || true
docker run -d --name dozzle -p 9999:8080 --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  amir20/dozzle:latest

echo "Configuring Firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 9090/tcp
ufw allow 9443/tcp
ufw allow 9999/tcp
ufw reload

echo "DONE!"
'@

$setupScript | ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} "cat > /tmp/setup.sh && bash /tmp/setup.sh"

Write-Host "[OK] Management tools installed!" -ForegroundColor Green
Write-Host ""

# Step 2: Upload project files
Write-Host "[2/4] Uploading project files..." -ForegroundColor Yellow

ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} "mkdir -p $VPS_PATH"

# Using tar to upload (faster than scp)
tar -czf "$env:TEMP\utility-server.tar.gz" -C "D:\thang\utility-server" --exclude=".git" --exclude="__pycache__" --exclude="*.pyc" --exclude="node_modules" .
scp -o StrictHostKeyChecking=no "$env:TEMP\utility-server.tar.gz" ${VPS_USER}@${VPS_IP}:${VPS_PATH}/
ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} "cd $VPS_PATH && tar -xzf utility-server.tar.gz && rm utility-server.tar.gz"
Remove-Item "$env:TEMP\utility-server.tar.gz"

Write-Host "[OK] Files uploaded!" -ForegroundColor Green
Write-Host ""

# Step 3: Configure and deploy
Write-Host "[3/4] Deploying Utility Server..." -ForegroundColor Yellow

$deployScript = @"
cd $VPS_PATH

# Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    # Generate random passwords
    DB_PASS=\$(openssl rand -hex 16)
    REDIS_PASS=\$(openssl rand -hex 16)
    SECRET=\$(openssl rand -hex 32)
    JWT_SECRET=\$(openssl rand -hex 32)
    
    sed -i "s/your_strong_password_here_123/\$DB_PASS/g" .env
    sed -i "s/your_redis_password_here_456/\$REDIS_PASS/g" .env
    sed -i "s/your-super-secret-key-change-this-to-random-string/\$SECRET/g" .env
    sed -i "s/another-secret-key-for-jwt-tokens/\$JWT_SECRET/g" .env
fi

# Deploy
docker-compose down 2>/dev/null || true
docker-compose up -d --build

# Wait for services
sleep 15

# Show status
docker-compose ps
"@

$deployScript | ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} "bash"

Write-Host "[OK] Utility Server deployed!" -ForegroundColor Green
Write-Host ""

# Step 4: Verify
Write-Host "[4/4] Verifying all services..." -ForegroundColor Yellow

$verifyScript = @"
echo '=== VERIFICATION ==='
echo ''
echo 'Docker Containers:'
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'portainer|dozzle|utility'
echo ''
echo 'Cockpit Status:'
systemctl is-active cockpit 2>/dev/null || echo 'Not active'
echo ''
echo 'Testing API:'
curl -s http://localhost/health || echo 'API not ready yet'
"@

$verifyScript | ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} "bash"

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "   DEPLOYMENT COMPLETED!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "ACCESS YOUR 4 TOOLS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Cockpit (VPS Management)" -ForegroundColor White
Write-Host "   URL: http://$VPS_IP`:9090" -ForegroundColor Yellow
Write-Host "   Login: root / @8Alm523jIqS" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Portainer (Docker Management)" -ForegroundColor White
Write-Host "   URL: https://$VPS_IP`:9443" -ForegroundColor Yellow
Write-Host "   Setup: Create admin account on first visit" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Dozzle (Logs Viewer)" -ForegroundColor White
Write-Host "   URL: http://$VPS_IP`:9999" -ForegroundColor Yellow
Write-Host "   No login required" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Utility Server (Your API)" -ForegroundColor White
Write-Host "   URL: http://$VPS_IP/docs" -ForegroundColor Yellow
Write-Host "   Health: http://$VPS_IP/health" -ForegroundColor Yellow
Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""

# Ask to open browser
$open = Read-Host "Open Cockpit in browser? (y/n)"
if ($open -eq "y") {
    Start-Process "http://$VPS_IP`:9090"
}
