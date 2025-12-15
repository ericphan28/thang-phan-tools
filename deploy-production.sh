#!/bin/bash
# ================================================================
# PRODUCTION DEPLOYMENT - ADOBE PDF SERVICES
# Server: 165.99.59.47
# ================================================================

set -e

echo "========================================"
echo "🚀 DEPLOYING ADOBE PDF INTEGRATION"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SERVER_PATH="/opt/utility-server"

echo -e "${YELLOW}📥 Step 1: Pulling latest code...${NC}"
cd $SERVER_PATH
git pull origin main

echo ""
echo -e "${YELLOW}📝 Step 2: Adding Adobe credentials...${NC}"

# Check if credentials already exist
if grep -q "PDF_SERVICES_CLIENT_ID" backend/.env 2>/dev/null; then
    echo -e "${GREEN}✅ Adobe credentials already configured${NC}"
else
    echo -e "${CYAN}Adding new credentials...${NC}"
    cat >> backend/.env << 'EOF'

# Adobe PDF Services API Configuration
# Added: 2025-01-22
USE_ADOBE_PDF_API=true
PDF_SERVICES_CLIENT_ID=your_client_id_here
PDF_SERVICES_CLIENT_SECRET=your_client_secret_here
ADOBE_ORG_ID=your_org_id_here
EOF
    echo -e "${GREEN}✅ Credentials added${NC}"
fi

echo ""
echo -e "${YELLOW}🔨 Step 3: Rebuilding backend container...${NC}"
docker-compose build backend

echo ""
echo -e "${YELLOW}♻️  Step 4: Restarting backend service...${NC}"
docker-compose up -d backend

echo ""
echo -e "${YELLOW}⏳ Step 5: Waiting for backend to start...${NC}"
sleep 10

echo ""
echo -e "${YELLOW}📋 Step 6: Checking logs...${NC}"
echo ""
docker logs utility_backend --tail=50 | grep -E "INFO|Adobe|ERROR" || docker logs utility_backend --tail=50

echo ""
echo "========================================"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo "========================================"
echo ""
echo -e "${CYAN}📊 Next steps:${NC}"
echo "  1. Test PDF to Word conversion"
echo "  2. Check logs: docker logs utility_backend -f"
echo "  3. Monitor Adobe usage: https://developer.adobe.com/console"
echo ""
echo -e "${GREEN}🎉 Adobe integration is now live!${NC}"
echo ""
