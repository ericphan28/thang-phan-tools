#!/bin/bash
# Quick VPS diagnostic script

echo "=== VPS Backend Diagnostics ==="
echo ""

echo "[1] All Docker containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -n 20

echo ""
echo "[2] Backend container details:"
docker ps -a | grep -i backend

echo ""
echo "[3] Testing backend port 8000:"
timeout 3 curl -s http://localhost:8000/docs | head -n 5 || echo "Backend not responding!"

echo ""
echo "[4] Check backend logs:"
cd /root/thang-phan-tools
docker-compose -f docker-compose.prod.yml logs backend --tail=15 2>&1

echo ""
echo "[5] Restart backend if needed:"
echo "Run: docker-compose -f docker-compose.prod.yml restart backend"
