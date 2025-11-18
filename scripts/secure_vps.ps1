# ====================================
# SECURE VPS - FIX FAILED LOGIN ATTEMPTS
# ====================================

$VPS_IP = "165.99.59.47"
$VPS_USER = "root"

Write-Host "`n=== SECURING VPS ===" -ForegroundColor Cyan

Write-Host "`n[1/4] Installing Fail2Ban..." -ForegroundColor Yellow
ssh ${VPS_USER}@${VPS_IP} @"
apt-get update -qq
apt-get install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban
"@
Write-Host "   [OK] Fail2Ban installed and running" -ForegroundColor Green

Write-Host "`n[2/4] Configuring SSH security..." -ForegroundColor Yellow
ssh ${VPS_USER}@${VPS_IP} @"
# Backup original sshd_config
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Apply security settings
sed -i 's/#PermitRootLogin yes/PermitRootLogin yes/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/#MaxAuthTries 6/MaxAuthTries 3/' /etc/ssh/sshd_config

# Add if not exists
grep -q 'MaxStartups' /etc/ssh/sshd_config || echo 'MaxStartups 10:30:60' >> /etc/ssh/sshd_config

# Restart SSH
systemctl restart sshd
"@
Write-Host "   [OK] SSH hardened" -ForegroundColor Green

Write-Host "`n[3/4] Configuring UFW firewall..." -ForegroundColor Yellow
ssh ${VPS_USER}@${VPS_IP} @"
# Reset firewall to clean state
ufw --force reset

# Default policies
ufw default deny incoming
ufw default allow outgoing

# Allow essential services
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw allow 9090/tcp comment 'Cockpit'
ufw allow 9443/tcp comment 'Portainer'
ufw allow 9999/tcp comment 'Dozzle'

# Enable firewall
ufw --force enable
ufw status verbose
"@
Write-Host "   [OK] Firewall configured" -ForegroundColor Green

Write-Host "`n[4/4] Checking failed login history..." -ForegroundColor Yellow
$failedLogins = ssh ${VPS_USER}@${VPS_IP} "grep 'Failed password' /var/log/auth.log | tail -10"
Write-Host "   Last 10 failed login attempts:" -ForegroundColor Gray
Write-Host $failedLogins -ForegroundColor DarkGray

Write-Host "`n=== SECURITY STATUS ===" -ForegroundColor Cyan
ssh ${VPS_USER}@${VPS_IP} @"
echo ""
echo "Fail2Ban status:"
fail2ban-client status sshd
echo ""
echo "UFW status:"
ufw status numbered
"@

Write-Host "`n[OK] VPS secured!" -ForegroundColor Green
Write-Host "`nFail2Ban will now automatically ban IPs after 3 failed attempts." -ForegroundColor Yellow
Write-Host ""
