#!/bin/bash

# ============================================
# FULL DEPLOYMENT SCRIPT
# Deploy Utility Server + Management Tools
# ============================================

set -e

echo "🚀 Starting Full Deployment..."
echo "This will install:"
echo "  1. Docker & Docker Compose"
echo "  2. Cockpit (VPS Management)"
echo "  3. Portainer (Docker Management)"
echo "  4. Dozzle (Logs Viewer)"
echo "  5. Utility Server (Your API)"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root: sudo bash full_deploy.sh"
    exit 1
fi

# ============================================
# STEP 1: System Update
# ============================================
echo "📦 Step 1/6: Updating system packages..."
apt update && apt upgrade -y

# ============================================
# STEP 2: Install Docker
# ============================================
if ! command -v docker &> /dev/null; then
    echo "🐳 Step 2/6: Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
    rm get-docker.sh
    echo "✅ Docker installed"
else
    echo "✅ Step 2/6: Docker already installed"
fi

# ============================================
# STEP 3: Install Docker Compose
# ============================================
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Step 3/6: Installing Docker Compose..."
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
else
    echo "✅ Step 3/6: Docker Compose already installed"
fi

# ============================================
# STEP 4: Install Cockpit (VPS Management)
# ============================================
echo "🖥️  Step 4/6: Installing Cockpit..."
apt install -y cockpit cockpit-docker cockpit-packagekit
systemctl enable --now cockpit.socket
echo "✅ Cockpit installed - Access at http://YOUR_IP:9090"

# ============================================
# STEP 5: Install Portainer & Dozzle
# ============================================
echo "🐳 Step 5/6: Installing Portainer & Dozzle..."

# Create Portainer volume
docker volume create portainer_data

# Install Portainer
docker run -d \
  -p 9443:9443 \
  -p 8000:8000 \
  --name portainer \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest

echo "✅ Portainer installed - Access at https://YOUR_IP:9443"

# Install Dozzle
docker run -d \
  --name dozzle \
  -p 9999:8080 \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  amir20/dozzle:latest

echo "✅ Dozzle installed - Access at http://YOUR_IP:9999"

# ============================================
# STEP 6: Configure Firewall
# ============================================
echo "🔥 Step 6/6: Configuring firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment "SSH"
ufw allow 80/tcp comment "HTTP"
ufw allow 443/tcp comment "HTTPS"
ufw allow 9090/tcp comment "Cockpit"
ufw allow 9443/tcp comment "Portainer"
ufw allow 9999/tcp comment "Dozzle"
ufw --force enable
echo "✅ Firewall configured"

# ============================================
# Get Server IP
# ============================================
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

# ============================================
# SUMMARY
# ============================================
echo ""
echo "✅ ========================================="
echo "✅ DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "✅ ========================================="
echo ""
echo "📊 System Information:"
echo "- Docker: $(docker --version)"
echo "- Docker Compose: $(docker-compose --version)"
echo "- Server IP: $SERVER_IP"
echo ""
echo "🌐 Management Tools:"
echo "┌─────────────────────────────────────────────────────────┐"
echo "│ 🖥️  Cockpit    http://$SERVER_IP:9090          │"
echo "│    Login: root / your-password                          │"
echo "│    Function: Full VPS Management                        │"
echo "├─────────────────────────────────────────────────────────┤"
echo "│ 🐳 Portainer   https://$SERVER_IP:9443         │"
echo "│    Setup: Create admin account on first visit          │"
echo "│    Function: Docker Management                          │"
echo "├─────────────────────────────────────────────────────────┤"
echo "│ 📋 Dozzle      http://$SERVER_IP:9999          │"
echo "│    No login required                                    │"
echo "│    Function: Real-time Docker Logs                      │"
echo "└─────────────────────────────────────────────────────────┘"
echo ""
echo "🚀 Next Steps:"
echo "1. Upload your project to /opt/utility-server"
echo "2. Configure .env file"
echo "3. Run: cd /opt/utility-server && docker-compose up -d"
echo ""
echo "📝 Utility Server will be available at:"
echo "   - API Docs: http://$SERVER_IP/docs"
echo "   - Health: http://$SERVER_IP/health"
echo ""
