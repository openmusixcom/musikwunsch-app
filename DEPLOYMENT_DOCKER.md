# Musikwunsch App - Docker Deployment Guide

## Deployment Status ✅

The Musikwunsch application is successfully deployed on Hostinger using Docker Compose.

### Access Points
- **Frontend:** http://187.124.20.215:8080
- **API Health:** http://187.124.20.215:8080/api/health
- **SSH:** ssh root@187.124.20.215 (PW: Extra01#1234)

### Deployment Details
- **Server:** Hostinger VPS (187.124.20.215)
- **Project Directory:** `/var/www/musikwunsch-app-docker`
- **Architecture:** Docker Compose (3 containers)

## Docker Containers

### 1. PostgreSQL Database (`musikwunsch-db`)
- **Image:** postgres:16-alpine
- **Port:** 5432 (internal only, exposed through Docker network)
- **Database:** musikwunsch
- **User:** postgres / postgres
- **Status:** Healthy with health checks

### 2. Node.js Backend API (`musikwunsch-api`)
- **Image:** Custom built from Dockerfile.backend
- **Port:** 3000 (internal only, accessed through Nginx)
- **Runtime:** Node.js 18-alpine
- **Features:**
  - Express.js REST API
  - JWT authentication with refresh tokens
  - Socket.io for real-time features
  - Environment: production
  - Auto-restart: enabled

### 3. Nginx Frontend (`musikwunsch-web`)
- **Image:** Custom built from Dockerfile.frontend
- **Port:** 8080 (mapped from container port 80)
- **Runtime:** Nginx alpine
- **Features:**
  - React/Vite SPA serving
  - API proxy to backend at `/api/*`
  - WebSocket support at `/socket.io`
  - SPA fallback routing (any path -> index.html)

## File Structure

```
/var/www/musikwunsch-app-docker/
├── docker-compose.yml          # Orchestration configuration
├── Dockerfile.backend          # Backend image definition
├── Dockerfile.frontend         # Frontend image definition  
├── nginx.conf                  # Nginx reverse proxy config
├── backend/                    # Backend source code
│   ├── src/
│   ├── package.json
│   └── node_modules/
├── frontend/                   # Frontend source code
│   ├── src/
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
└── docker.tar.gz              # Project archive
```

## Useful Commands

### View Logs
```bash
docker logs musikwunsch-api      # Backend logs
docker logs musikwunsch-web      # Frontend logs
docker logs musikwunsch-db       # Database logs
```

### Stop All Containers
```bash
cd /var/www/musikwunsch-app-docker
docker compose down
```

### Restart Containers
```bash
cd /var/www/musikwunsch-app-docker
docker compose restart
```

### View Container Status
```bash
cd /var/www/musikwunsch-app-docker
docker compose ps
```

### Access Backend Shell
```bash
docker exec -it musikwunsch-api /bin/sh
```

### Access Database
```bash
docker exec -it musikwunsch-db psql -U postgres -d musikwunsch
```

### Rebuild Images
```bash
cd /var/www/musikwunsch-app-docker
docker compose build --no-cache
docker compose up -d
```

## Environment Variables

Backend environment variables (set in docker-compose.yml):
- `NODE_ENV`: production
- `PORT`: 3000
- `DB_HOST`: db (Docker DNS name)
- `DB_PORT`: 5432
- `DB_USER`: postgres
- `DB_PASSWORD`: postgres
- `DB_NAME`: musikwunsch
- `JWT_SECRET`: your-secret-key-change-in-production
- `JWT_EXPIRY`: 24h
- `REFRESH_TOKEN_EXPIRY`: 7d
- `FRONTEND_URL`: http://87.106.215.187.nip.io

**⚠️ Important:** Change `JWT_SECRET` in production!

## Configuration Changes from Standard Setup

### Port Mappings
- Database (5432): Internal only via Docker network
- Backend (3000): Internal only via Docker network
- Frontend (8080): Exposed to host as 8080:80

**Why?** The Hostinger server runs other Docker projects using Traefik. We avoid port conflicts by:
- Not exposing backend to host (accessed through Nginx)
- Not exposing database to host (accessed through Docker network)
- Using port 8080 instead of 80 (Traefik uses 80)

### Docker Networking
All containers connect through the `musikwunsch-app-docker_default` network:
- Backend can access database at hostname `db`
- Frontend can access backend at hostname `backend`
- All use internal DNS resolution

## Deployment Automation

### Deploy Script: `deploy_docker.py`

Located in project root. Usage:
```bash
cd C:\Users\cwoll\Doku\Claude\DJapp
python deploy_docker.py
```

The script:
1. Creates tar.gz of project files
2. Connects to Hostinger via SFTP
3. Uploads files to `/var/www/musikwunsch-app-docker`
4. Extracts files on server
5. Stops old containers
6. Builds Docker images
7. Starts new containers
8. Tests health endpoints

## Health Checks

All containers have health checks:

### Database Health
```bash
docker exec musikwunsch-db pg_isready -U postgres
```

### Backend Health
```bash
curl http://localhost:8080/api/health
# Response: {"status":"ok","timestamp":"...","message":"Backend is running"}
```

### Frontend Health
```bash
curl http://localhost:8080/
# Response: HTML index with status 200
```

## Data Persistence

PostgreSQL data is stored in a named volume: `postgres_data`
- Location: `/var/lib/docker/volumes/musikwunsch-app-docker_postgres_data/_data`
- Persists across container restarts
- Not removed when containers are stopped

To backup:
```bash
docker run --rm -v musikwunsch-app-docker_postgres_data:/dbdata \
  -v $(pwd):/backup postgres:16-alpine \
  pg_dump -U postgres -d musikwunsch > /backup/musikwunsch_backup.sql
```

## Troubleshooting

### Containers not starting
```bash
# Check logs
docker logs musikwunsch-api
docker logs musikwunsch-web

# Verify port availability
netstat -tuln | grep 8080

# Force restart
docker compose down
docker compose up -d
```

### Database connection errors
```bash
# Test connection from backend
docker exec musikwunsch-api psql -h db -U postgres -d musikwunsch -c "SELECT 1"
```

### Nginx not proxying to backend
```bash
# Check backend is accessible from Nginx container
docker exec musikwunsch-web curl -v http://backend:3000/api/health
```

### Port already in use
The Hostinger server runs Traefik and other services. If you get "port X already in use":
1. Check what's using it: `netstat -tuln | grep :PORT`
2. Update port mapping in docker-compose.yml
3. Restart containers

## Next Steps

1. **Access the application:** Open http://187.124.20.215:8080 in browser
2. **Register admin account:** Use the registration form
3. **Test the API:** Hit /api/health endpoint
4. **Implement Phase 2 features:** Guest App with QR-code access
5. **Scale up:** Implement authentication, DJ dashboard, admin panel

## Security Notes

- Change `JWT_SECRET` to a strong random value
- Use HTTPS in production (configure reverse proxy or Let's Encrypt)
- Don't commit sensitive values to Git
- Database runs internally, not exposed to external network
- API runs internally, accessed through Nginx proxy only
