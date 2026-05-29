# Login-Fehler Behebung

## Problem
Das Login gibt einen **301 Moved Permanently** Fehler zurück statt der Login-Antwort.

## Ursachen (behoben in commit 20da4c9)

1. **Nginx-Routing-Konflikt**: Die `/` location hat `try_files` mit höherer Priorität als `/api` location
2. **Backend DB-Verbindung**: Die .env hatte `DB_HOST=localhost` statt `DB_HOST=db` für Docker
3. **Unused Dependency**: qrcode Paket war noch in package.json enthalten

## Behobene Änderungen

### 1. nginx.conf - Verbessert Routing
```
- Moved /api location before / location
- Added trailing slashes for correct routing
- Added X-Forwarded-* headers for proxy transparency
- Exact match for /api/health endpoint
```

### 2. backend/.env - Docker-konfiguriert
```
DB_HOST=db          (vorher: localhost)
FRONTEND_URL=http://87.106.215.187.nip.io
NODE_ENV=production
```

### 3. Dockerfile.backend - Optional .env
```
COPY backend/.env* ./    (statt COPY backend/.env ./)
```

### 4. backend/package.json - Entfernt unused dependency
```
Removed: "qrcode": "^1.5.3"
```

## Deployment-Schritte

### Option 1: Auf VPS (SSH)
```bash
ssh root@187.124.20.215
cd /var/www/musikwunsch-app-docker

# Neuesten Code pullen
git pull origin main

# Docker-Images neu bauen
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Warten, bis Container bereit sind
sleep 10

# Migrations ausführen
docker exec musikwunsch-api npm run migrate

# Status prüfen
docker-compose ps
```

### Option 2: Remote-Deployment (von lokal)
```bash
# Letzten Code zu GitHub pushen (bereits gemacht: commit 20da4c9)
git push origin main

# SSH und Remote-Commands ausführen
ssh root@187.124.20.215 << 'EOF'
cd /var/www/musikwunsch-app-docker
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
sleep 10
docker exec musikwunsch-api npm run migrate
docker-compose ps
EOF
```

## Nach dem Update Testen

### 1. Health Check
```bash
curl http://87.106.215.187.nip.io/api/health
```

Erwartet: HTTP 200 mit Timestamp

### 2. Login Test (Admin)
```bash
curl -X POST http://87.106.215.187.nip.io/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.local",
    "password": "testpass123"
  }'
```

Erwartet: HTTP 200 mit User-Daten und Token

### 3. Login Test (DJ)
```bash
curl -X POST http://87.106.215.187.nip.io/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dj@test.local",
    "password": "testpass123"
  }'
```

Erwartet: HTTP 200 mit User-Daten und Token

### 4. Frontend Test
Öffne: `http://87.106.215.187.nip.io/login`
- Login mit `admin@test.local` / `testpass123`
- Should redirect to admin dashboard

## Troubleshooting

### Noch immer 301 Redirect?
```bash
# Prüfe Backend-Container Status
docker logs musikwunsch-api

# Prüfe Nginx-Konfiguration
docker exec musikwunsch-web nginx -t

# Prüfe Proxy-Verbindung (innerhalb Container)
docker exec musikwunsch-web curl http://backend:3000/api/health
```

### Backend konnte nicht starten?
```bash
# Prüfe Logs
docker logs musikwunsch-api

# Prüfe npm start Command
docker exec musikwunsch-api npm start
```

### Datenbankverbindung fehlgeschlagen?
```bash
# Prüfe PostgreSQL Status
docker logs musikwunsch-db

# Test DB connection
docker exec musikwunsch-db psql -U postgres -d musikwunsch -c "SELECT 1;"

# Check environment variables im Backend
docker exec musikwunsch-api env | grep DB_
```

## Commit-Details

**Commit**: `20da4c9`
**Datum**: 2026-05-29
**Dateien geändert**: 5
- `backend/package.json` - Removed qrcode dependency
- `backend/.env` - Updated Docker values
- `Dockerfile.backend` - Optional .env copy
- `nginx.conf` - Fixed routing priority
- `diagnose_login.sh` - Diagnostic script added

## Nächste Schritte

Nach erfolgreicher Behebung des Login-Problems:
1. ✅ Testen Sie die Phase 2 Guest App (`/guest` route)
2. ✅ Führen Sie die Phase 2 Tests durch (siehe PHASE2_TESTING.md)
3. ✅ Laden Sie Sample-Songs in die Datenbank
4. Planen Sie Phase 3: DJ Dashboard
