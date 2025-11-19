#!/bin/bash

# ============================================
# VPS Ubuntu Setup Script for Utility Server
# Run this on your VPS: bash setup_vps.sh
# ============================================

set -e

echo "🚀 Starting VPS Utility Server Setup..."
echo "This will install Docker, Docker Compose, and system dependencies"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root: sudo bash setup_vps.sh"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install basic tools
echo "🔧 Installing basic tools..."
apt install -y curl wget git vim htop tmux build-essential ufw

# Install LibreOffice for document conversion
echo "📄 Installing LibreOffice for Word→PDF conversion..."
apt install -y libreoffice libreoffice-writer libreoffice-core --no-install-recommends
echo "✅ LibreOffice installed"

# Install Docker
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
    rm get-docker.sh
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose already installed"
fi

# Setup firewall
echo "🔥 Configuring firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment "SSH"
ufw allow 80/tcp comment "HTTP"
ufw allow 443/tcp comment "HTTPS"
ufw --force enable
echo "✅ Firewall configured"

# Install Certbot for SSL
echo "🔒 Installing Certbot for SSL..."
apt install -y certbot
echo "✅ Certbot installed"

# Create app directory
echo "📁 Creating application directory..."
mkdir -p /opt/utility-server
mkdir -p /opt/utility-server/certbot/conf
mkdir -p /opt/utility-server/certbot/www
echo "✅ Directories created"

# Optimize system for production
echo "⚙️  Optimizing system settings..."

# Increase file descriptors
cat >> /etc/security/limits.conf <<EOF
* soft nofile 65535
* hard nofile 65535
EOF

# Optimize network
cat >> /etc/sysctl.conf <<EOF
# Network optimizations
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.ip_local_port_range = 1024 65535
EOF

sysctl -p

echo "✅ System optimized"

# Create swap if needed (for low memory VPS)
if [ $(free | grep Swap | awk '{print $2}') -eq 0 ]; then
    echo "💾 Creating 4GB swap file..."
    fallocate -l 4G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "✅ Swap created"
fi

echo ""
echo "✅ ========================================="
echo "✅ VPS Setup Complete!"
echo "✅ ========================================="
echo ""
echo "System Information:"
echo "- Docker: $(docker --version)"
echo "- Docker Compose: $(docker-compose --version)"
echo ""
echo "Next Steps:"
echo "1. Upload your project to /opt/utility-server"
echo "2. Copy and configure .env file"
echo "3. Run: cd /opt/utility-server && docker-compose up -d"
echo ""
echo "Optional - Setup SSL:"
echo "certbot certonly --webroot -w /opt/utility-server/certbot/www -d yourdomain.com"
echo ""
