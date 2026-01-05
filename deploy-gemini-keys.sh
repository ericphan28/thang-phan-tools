#!/bin/bash
# Deploy Gemini Keys Management to VPS
# Run on VPS: bash <(curl -s https://raw.githubusercontent.com/ericphan28/thang-phan-tools/main/deploy-gemini-keys.sh)

set -e

echo "🚀 Deploying Gemini Keys Management to VPS..."

cd /root/thang-phan-tools

echo "📥 Pulling latest code from GitHub..."
git pull origin main

echo "🛑 Stopping containers..."
docker-compose -f docker-compose.prod.yml down

echo "🏗️ Rebuilding backend..."
docker-compose -f docker-compose.prod.yml build backend

echo "🚀 Starting containers..."
docker-compose -f docker-compose.prod.yml up -d

echo "⏳ Waiting for backend to start..."
sleep 10

echo "🏥 Health check..."
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✅ Backend healthy" || echo "❌ Backend unhealthy"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Add API keys in database: http://165.99.59.47/admin/gemini-keys"
echo "2. Remove GEMINI_API_KEY from .env:"
echo "   cd /root/thang-phan-tools/backend"
echo "   nano .env  # Delete GEMINI_API_KEY line"
echo "   cd .."
echo "   docker-compose -f docker-compose.prod.yml restart backend"
echo ""
echo "📊 Monitor logs:"
echo "   docker-compose -f docker-compose.prod.yml logs -f backend"
