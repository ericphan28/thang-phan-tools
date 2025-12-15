#!/bin/bash

# 🚀 Quick Deployment Script for Ubuntu VPS
# This script automates the deployment process

set -e  # Exit on error

echo "🚀 Starting Utility Server Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/utility-server"
DOMAIN="yourdomain.com"  # Change this!
EMAIL="your@email.com"   # Change this!

# Step 1: Update system
echo -e "${YELLOW}📦 Updating system...${NC}"
sudo apt update && sudo apt upgrade -y

# Step 2: Install Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}🐳 Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
else
    echo -e "${GREEN}✅ Docker already installed${NC}"
fi

# Step 3: Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Docker Compose...${NC}"
    sudo apt install docker-compose -y
else
    echo -e "${GREEN}✅ Docker Compose already installed${NC}"
fi

# Step 4: Create app directory
echo -e "${YELLOW}📁 Creating application directory...${NC}"
sudo mkdir -p $APP_DIR
cd $APP_DIR

# Step 5: Clone repository (if not exists)
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}📥 Cloning repository...${NC}"
    read -p "Enter GitHub repository URL: " REPO_URL
    git clone $REPO_URL .
else
    echo -e "${GREEN}✅ Repository already exists${NC}"
    echo -e "${YELLOW}📥 Pulling latest changes...${NC}"
    git pull
fi

# Step 6: Configure environment
echo -e "${YELLOW}⚙️  Configuring environment...${NC}"

# Backend .env
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}Creating backend .env...${NC}"
    cat > backend/.env << EOF
# Production Environment
APP_NAME="Utility Server API"
APP_VERSION="1.0.0"
ENVIRONMENT="production"
DEBUG=False

HOST="0.0.0.0"
PORT=8000

DATABASE_URL="postgresql://utility_user:$(openssl rand -hex 16)@postgres:5432/utility_db"

JWT_SECRET_KEY="$(openssl rand -hex 32)"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

CORS_ORIGINS=["https://$DOMAIN","https://www.$DOMAIN"]

USE_ADOBE_PDF_API=true
PDF_SERVICES_CLIENT_ID="d46f7e349fe44f7ca933c216eaa9bd48"
PDF_SERVICES_CLIENT_SECRET="p8e-Bg7-Ce-gj80zF62wXyhY-rqjbVmDHgzz"
ADOBE_ORG_ID="491221D76920D5EB0A495C5D@AdobeOrg"

GEMINI_API_KEY="AIzaSyC3X92AYepFgVhIidH4QR0umGXZ5XFP27A"
GEMINI_MODEL="gemini-2.5-flash"

OCR_PRIORITY="tesseract,adobe"
EOF
    echo -e "${GREEN}✅ Backend .env created${NC}"
else
    echo -e "${GREEN}✅ Backend .env already exists${NC}"
fi

# Frontend .env
if [ ! -f "frontend/.env" ]; then
    echo -e "${YELLOW}Creating frontend .env...${NC}"
    cat > frontend/.env << EOF
VITE_API_BASE_URL=https://$DOMAIN/api/v1
EOF
    echo -e "${GREEN}✅ Frontend .env created${NC}"
else
    echo -e "${GREEN}✅ Frontend .env already exists${NC}"
fi

# Step 7: Build and start services
echo -e "${YELLOW}🔨 Building and starting services...${NC}"
docker-compose up -d --build

# Step 8: Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Step 9: Check services status
echo -e "${YELLOW}📊 Checking services status...${NC}"
docker-compose ps

# Step 10: Test endpoints
echo -e "${YELLOW}🧪 Testing endpoints...${NC}"
if curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
fi

if curl -s http://localhost/ > /dev/null; then
    echo -e "${GREEN}✅ Frontend is running${NC}"
else
    echo -e "${RED}❌ Frontend check failed${NC}"
fi

# Step 11: Configure firewall
echo -e "${YELLOW}🔒 Configuring firewall...${NC}"
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
echo "y" | sudo ufw enable

# Step 12: Setup SSL (optional)
echo -e "${YELLOW}🔐 Setup SSL certificate?${NC}"
read -p "Do you want to setup SSL with Let's Encrypt? (y/n): " SETUP_SSL

if [ "$SETUP_SSL" = "y" ]; then
    echo -e "${YELLOW}Installing Certbot...${NC}"
    sudo apt install certbot python3-certbot-nginx -y
    
    echo -e "${YELLOW}Stopping containers...${NC}"
    docker-compose down
    
    echo -e "${YELLOW}Getting SSL certificate...${NC}"
    sudo certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos
    
    # Copy certificates
    sudo mkdir -p nginx/ssl
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/
    
    echo -e "${YELLOW}Restarting containers...${NC}"
    docker-compose up -d
    
    echo -e "${GREEN}✅ SSL certificate installed${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Frontend: ${YELLOW}http://$(curl -s ifconfig.me)${NC}"
echo -e "Backend API: ${YELLOW}http://$(curl -s ifconfig.me)/api/v1${NC}"
echo ""
echo -e "Useful commands:"
echo -e "  ${YELLOW}docker-compose ps${NC}          - Check services status"
echo -e "  ${YELLOW}docker-compose logs -f${NC}     - View logs"
echo -e "  ${YELLOW}docker-compose restart${NC}     - Restart services"
echo -e "  ${YELLOW}docker-compose down${NC}        - Stop services"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
