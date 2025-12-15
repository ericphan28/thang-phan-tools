#!/bin/bash

################################################################################
# ONE-COMMAND PRODUCTION DEPLOYMENT
# Run this on your Ubuntu VPS: curl -sSL https://raw.githubusercontent.com/yourusername/utility-server/main/quick-deploy.sh | sudo bash
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 Utility Server Quick Deploy${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Configuration
PROJECT_DIR="/opt/utility-server"
SERVER_IP="165.99.59.47"

# Step 1: Navigate to project
echo -e "${YELLOW}📂 Step 1: Navigating to project...${NC}"
cd $PROJECT_DIR
echo -e "${GREEN}✓ Done${NC}"

# Step 2: Pull latest code
echo -e "\n${YELLOW}📥 Step 2: Pulling latest code...${NC}"
git pull origin main
echo -e "${GREEN}✓ Done${NC}"

# Step 3: Copy production compose file
echo -e "\n${YELLOW}📋 Step 3: Setting up production configuration...${NC}"
if [ -f "docker-compose.prod.yml" ]; then
    cp docker-compose.prod.yml docker-compose.yml
    echo -e "${GREEN}✓ Production config applied${NC}"
else
    echo -e "${YELLOW}⚠️  Using existing docker-compose.yml${NC}"
fi

# Step 4: Stop existing containers
echo -e "\n${YELLOW}🛑 Step 4: Stopping existing containers...${NC}"
docker-compose down
echo -e "${GREEN}✓ Done${NC}"

# Step 5: Build containers
echo -e "\n${YELLOW}🔨 Step 5: Building containers...${NC}"
docker-compose build --no-cache
echo -e "${GREEN}✓ Done${NC}"

# Step 6: Start containers
echo -e "\n${YELLOW}🚀 Step 6: Starting containers...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Done${NC}"

# Step 7: Wait for services
echo -e "\n${YELLOW}⏳ Step 7: Waiting for services to be ready...${NC}"
sleep 15

# Step 8: Health checks
echo -e "\n${YELLOW}🏥 Step 8: Running health checks...${NC}"

# Check backend
if curl -f http://localhost:8000/api/v1/health &> /dev/null; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Backend not responding yet (may need more time)${NC}"
fi

# Check frontend
if curl -f http://localhost/ &> /dev/null; then
    echo -e "${GREEN}✓ Frontend is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend not responding yet (may need more time)${NC}"
fi

# Final summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}🔗 Access Your Application:${NC}"
echo -e "Frontend:  ${GREEN}http://$SERVER_IP${NC}"
echo -e "API Docs:  ${GREEN}http://$SERVER_IP/api/v1/docs${NC}"
echo -e "Portainer: ${GREEN}http://$SERVER_IP:9000${NC}"
echo ""
echo -e "${YELLOW}📊 Check Status:${NC}"
echo -e "docker-compose ps"
echo ""
echo -e "${YELLOW}📝 View Logs:${NC}"
echo -e "docker-compose logs -f"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo -e "Make sure to add your ${YELLOW}GEMINI_API_KEY${NC} in backend/.env"
echo -e "Then restart: ${YELLOW}docker-compose restart backend${NC}"
echo ""
echo -e "${GREEN}🎉 Happy deploying!${NC}"
