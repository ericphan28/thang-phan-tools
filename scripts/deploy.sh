#!/bin/bash

# ============================================
# Deploy Script for Utility Server
# Run this after uploading code to VPS
# ============================================

set -e

echo "🚀 Deploying Utility Server..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down || true

# Pull latest images
echo "📦 Pulling latest images..."
docker-compose pull || true

# Build images
echo "🔨 Building images..."
docker-compose build --no-cache

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
docker-compose ps

# Check logs
echo "📋 Recent logs:"
docker-compose logs --tail=20

echo ""
echo "✅ ========================================="
echo "✅ Deployment Complete!"
echo "✅ ========================================="
echo ""
echo "Services Status:"
docker-compose ps
echo ""
echo "Access your API at:"
echo "- API Docs: http://$(curl -s ifconfig.me)/docs"
echo "- Health Check: http://$(curl -s ifconfig.me)/health"
echo ""
echo "Useful Commands:"
echo "- View logs: docker-compose logs -f"
echo "- Restart: docker-compose restart"
echo "- Stop: docker-compose down"
echo "- Update: git pull && bash scripts/deploy.sh"
echo ""
