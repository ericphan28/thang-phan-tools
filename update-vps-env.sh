#!/bin/bash
# Script: Update .env trên VPS để comment GEMINI_API_KEY
# Sử dụng: ssh root@165.99.59.47 'bash -s' < update-vps-env.sh

set -e

echo "🔧 Updating .env on VPS to use database keys..."

cd /root/thang-phan-tools/backend

# Backup .env trước khi sửa
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Created backup: .env.backup.$(date +%Y%m%d_%H%M%S)"

# Comment GEMINI_API_KEY line
sed -i 's/^GEMINI_API_KEY=/# GEMINI_API_KEY - DEPRECATED: Chuyển sang quản lý qua Admin > AI Keys\n# Old backup: /' .env

echo "✅ Commented GEMINI_API_KEY in .env"
echo ""
echo "📋 New .env Gemini section:"
grep -A 5 "Google Gemini" .env || echo "Section not found"
echo ""
echo "🔄 Restart backend container to apply changes:"
echo "   cd /root/thang-phan-tools"
echo "   docker-compose -f docker-compose.prod.yml restart backend"
