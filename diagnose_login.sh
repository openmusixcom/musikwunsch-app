#!/bin/bash

echo "🔍 Diagnosing Login Issues..."
echo ""

# Check if containers are running
echo "1️⃣  Checking Docker containers..."
docker ps

echo ""
echo "2️⃣  Checking backend logs for errors..."
docker logs musikwunsch-api | tail -30

echo ""
echo "3️⃣  Checking database connection..."
docker exec musikwunsch-db psql -U musikwunsch -d musikwunsch -c "SELECT COUNT(*) as user_count FROM users;"

echo ""
echo "4️⃣  Listing all users in database..."
docker exec musikwunsch-db psql -U musikwunsch -d musikwunsch -c "SELECT id, email, role FROM users;"

echo ""
echo "5️⃣  Testing API health check..."
curl -s http://localhost:3000/api/health | jq . || echo "Health check failed"

echo ""
echo "6️⃣  Testing login endpoint..."
curl -s -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.local",
    "password": "testpass123"
  }' | jq . || echo "Login test failed"

echo ""
echo "✅ Diagnostics complete"
