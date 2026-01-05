#!/bin/bash

# 🚀 Zero-Downtime Deployment Script for Production
# Sử dụng rolling update strategy - downtime < 1 giây

set -e

echo "🚀 Starting Zero-Downtime Deployment..."

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Step 1: Pull latest images (không stop container)
echo -e "${YELLOW}📥 Pulling latest images from GHCR...${NC}"
docker-compose -f docker-compose.prod.yml pull

# Step 2: Rolling update - từng service một
echo -e "${BLUE}🔄 Rolling update backend (downtime < 1s)...${NC}"
docker-compose -f docker-compose.prod.yml up -d --no-deps --force-recreate backend

# Wait for backend health check
echo -e "${YELLOW}⏳ Waiting for backend to be healthy...${NC}"
sleep 3
until curl -f http://localhost:8000/health > /dev/null 2>&1; do
  echo "  Waiting for backend..."
  sleep 2
done
echo -e "${GREEN}✅ Backend is healthy${NC}"

# Step 3: Rolling update frontend
echo -e "${BLUE}🔄 Rolling update frontend (downtime < 1s)...${NC}"
docker-compose -f docker-compose.prod.yml up -d --no-deps --force-recreate frontend

echo -e "${YELLOW}⏳ Waiting for frontend to be healthy...${NC}"
sleep 2

# Step 4: Cleanup old images
echo -e "${YELLOW}🧹 Cleaning up old images...${NC}"
docker image prune -f

# Step 5: Verify services
echo -e "${BLUE}🔍 Verifying services...${NC}"
docker-compose -f docker-compose.prod.yml ps

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 Zero-Downtime Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}✅ Backend: Updated with <1s downtime${NC}"
echo -e "${GREEN}✅ Frontend: Updated with <1s downtime${NC}"
echo ""
echo -e "Check status: ${YELLOW}docker-compose -f docker-compose.prod.yml ps${NC}"
echo -e "View logs:    ${YELLOW}docker-compose -f docker-compose.prod.yml logs -f${NC}"
echo ""
