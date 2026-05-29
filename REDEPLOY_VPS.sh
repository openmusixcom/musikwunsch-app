#!/bin/bash
# Complete VPS Redeployment Script
# Run this on the VPS as root

set -e

echo "🚀 Starting Musikwunsch VPS Redeployment..."
echo ""

# Configuration
REPO_URL="https://github.com/cwoll/DJapp.git"
DEPLOY_DIR="/var/www/musikwunsch-app-docker"
SSH_USER="root"
SSH_HOST="187.124.20.215"

# Step 1: Check if directory exists, if not create it
if [ ! -d "$DEPLOY_DIR" ]; then
    echo "📁 Creating deployment directory..."
    mkdir -p "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
    git init
    git remote add origin "$REPO_URL"
else
    cd "$DEPLOY_DIR"
fi

# Step 2: Fetch latest code
echo "📥 Fetching latest code from GitHub..."
git fetch origin main
git reset --hard origin/main

# Step 3: Check Docker installation
echo "🐳 Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    bash get-docker.sh
    rm get-docker.sh
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Installing..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Step 4: Stop old containers
echo "🛑 Stopping old containers..."
docker-compose down 2>/dev/null || true

# Step 5: Build new images
echo "🏗️  Building Docker images..."
docker-compose build --no-cache

# Step 6: Start containers
echo "🚀 Starting containers..."
docker-compose up -d

# Step 7: Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 15

# Step 8: Run migrations
echo "📊 Running database migrations..."
docker-compose exec -T musikwunsch-api npm run migrate

# Step 9: Load sample songs (optional)
echo "🎵 Loading sample songs..."
docker-compose exec -T musikwunsch-db psql -U postgres -d musikwunsch << 'ENDSQL'
INSERT INTO songs (title, artist, album, duration, genre) VALUES
('Hello', 'Adele', '25', 295, 'Pop'),
('Shape of You', 'Ed Sheeran', '÷', 233, 'Pop'),
('Blinding Lights', 'The Weeknd', 'After Hours', 200, 'Synthwave'),
('As It Was', 'Harry Styles', 'Harry''s House', 167, 'Pop'),
('Like a Rolling Stone', 'Bob Dylan', 'Bringing It All Back Home', 369, 'Rock'),
('Imagine', 'John Lennon', 'Imagine', 183, 'Rock'),
('Bohemian Rhapsody', 'Queen', 'A Night at the Opera', 354, 'Rock'),
('Stairway to Heaven', 'Led Zeppelin', 'Led Zeppelin IV', 482, 'Rock'),
('Smells Like Teen Spirit', 'Nirvana', 'Nevermind', 301, 'Grunge'),
('Purple Haze', 'Jimi Hendrix', 'Are You Experienced', 175, 'Rock')
ON CONFLICT DO NOTHING;
ENDSQL

# Step 10: Verify deployment
echo "✅ Verifying deployment..."
echo ""
echo "Container Status:"
docker-compose ps

echo ""
echo "Testing API Health..."
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo "✅ Backend API is responding"
else
    echo "⚠️  Backend API not responding yet, waiting..."
    sleep 5
fi

echo ""
echo "🎉 Deployment Complete!"
echo ""
echo "Access the application at:"
echo "  - Frontend: http://87.106.215.187.nip.io"
echo "  - Guest App: http://87.106.215.187.nip.io/guest"
echo "  - API: http://87.106.215.187.nip.io/api"
echo ""
echo "Test Login:"
echo "  curl -X POST http://87.106.215.187.nip.io/api/auth/login \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"email\":\"admin@test.local\",\"password\":\"testpass123\"}'"
echo ""
