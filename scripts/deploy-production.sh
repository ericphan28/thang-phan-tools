#!/bin/bash
set -e  # Exit on error

echo "🚀 Starting deployment..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/opt/utility-server"
COMPOSE_FILE="docker-compose.prod.yml"
SERVICES=("backend" "frontend")

cd $PROJECT_DIR

echo -e "${YELLOW}📦 Pulling latest images...${NC}"
docker-compose -f $COMPOSE_FILE pull

echo -e "${YELLOW}🔄 Restarting services...${NC}"
docker-compose -f $COMPOSE_FILE up -d --force-recreate

echo -e "${YELLOW}⏳ Waiting 15s for services to start...${NC}"
sleep 15

# Health checks
echo -e "${YELLOW}🏥 Running health checks...${NC}"

# Check backend
BACKEND_HEALTH=$(curl -s http://localhost:8000/health | grep -o '"status":"healthy"' || echo "fail")
if [ "$BACKEND_HEALTH" = '"status":"healthy"' ]; then
    echo -e "${GREEN}✅ Backend: HEALTHY${NC}"
else
    echo -e "${RED}❌ Backend: UNHEALTHY${NC}"
    docker logs utility-backend-prod --tail=50
    exit 1
fi

# Check frontend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:80)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Frontend: HEALTHY${NC}"
else
    echo -e "${RED}❌ Frontend: UNHEALTHY (HTTP $FRONTEND_STATUS)${NC}"
    exit 1
fi

# Cleanup old images
echo -e "${YELLOW}🧹 Cleaning up old images...${NC}"
docker image prune -f

# Show running containers
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "backend|frontend"

echo ""
echo -e "${GREEN}🎉 Production is live at https://tienich.giakiemso.com${NC}"
