#!/bin/bash
# Script to check database on VPS Production

echo "🔍 CHECKING VPS PRODUCTION DATABASE"
echo "===================================="
echo ""

# Check PostgreSQL container
echo "1️⃣ PostgreSQL Container Status:"
docker ps | grep postgres || echo "❌ PostgreSQL container not running!"
echo ""

# Check PostgreSQL connection and tables
echo "2️⃣ PostgreSQL Database Info:"
docker exec utility-postgres-prod psql -U utility_user -d utility_db -c "\dt" 2>/dev/null || echo "❌ Cannot connect to PostgreSQL"
echo ""

# Count users in PostgreSQL
echo "3️⃣ Users in PostgreSQL:"
docker exec utility-postgres-prod psql -U utility_user -d utility_db -c "SELECT COUNT(*) as total_users FROM users;" 2>/dev/null || echo "❌ Table 'users' does not exist or cannot query"
echo ""

# List users
echo "4️⃣ User List:"
docker exec utility-postgres-prod psql -U utility_user -d utility_db -c "SELECT id, username, email, is_active FROM users LIMIT 5;" 2>/dev/null || echo "❌ Cannot query users"
echo ""

# Check backend connection
echo "5️⃣ Backend Database Connection:"
docker logs utility-backend-prod 2>&1 | grep -i "database\|connection\|sqlite\|postgresql" | tail -5
echo ""

# Check if backend is using SQLite instead
echo "6️⃣ Check if Backend Using SQLite (should be empty):"
docker exec utility-backend-prod ls -la /app/*.db 2>/dev/null || echo "✅ No SQLite files found (good!)"
echo ""

# Environment check
echo "7️⃣ Backend DATABASE_URL:"
docker exec utility-backend-prod env | grep DATABASE_URL || echo "⚠️ DATABASE_URL not set in environment!"
echo ""

echo "===================================="
echo "✅ Check complete!"
