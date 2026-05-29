# 🛠️ Setup Guide - Phase 1

## Schritt 1: PostgreSQL lokal installieren & starten

### Windows
```bash
# Option A: PostgreSQL Download
# https://www.postgresql.org/download/windows/

# Option B: Docker
docker run --name musikwunsch-db -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15
```

### macOS
```bash
brew install postgresql
brew services start postgresql
```

### Linux
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

## Schritt 2: Datenbank erstellen

```bash
# Connect to PostgreSQL
psql -U postgres

# Inside psql:
CREATE DATABASE musikwunsch;
\q
```

## Schritt 3: Backend Setup & Migration

```bash
cd backend
npm install

# Stelle sicher, dass .env korrekt konfiguriert ist
cat .env

# Führe Migrations aus
npm run migrate

# Starte Backend
npm run dev
```

**Erwartete Output:**
```
🚀 Server running on http://localhost:3000
📝 API available at http://localhost:3000/api
```

## Schritt 4: Frontend Setup

```bash
cd ../frontend
npm install

# Starte Development Server
npm run dev
```

**Erwartete Output:**
```
  VITE v5.0.8  ready in 123 ms

  ➜  Local:   http://localhost:5173/
```

## Schritt 5: Test der Installation

### 5a. Health Check
```bash
curl http://localhost:3000/api/health
```

Erwartete Response:
```json
{
  "status": "ok",
  "timestamp": "2024-05-29T10:30:00Z",
  "message": "Backend is running"
}
```

### 5b. Registrierung testen
```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "role": "dj"
  }'
```

Erwartete Response:
```json
{
  "user": {
    "id": "uuid",
    "email": "test@example.com",
    "role": "dj"
  },
  "token": "jwt-token",
  "refreshToken": "refresh-token"
}
```

### 5c. Login testen
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

## Schritt 6: Projekt im Browser öffnen

1. Öffne `http://localhost:5173`
2. Klick auf "Register here"
3. Erstelle ein Testkonto:
   - Email: `yourname@test.local`
   - Password: `testpass123`
   - Role: `dj`
4. Nach Registration solltest du zum DJ-Dashboard weitergeleitet werden

## 🧪 Troubleshooting

### Backend startet nicht
```bash
# Check ob Port 3000 frei ist
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Check .env Datei
cat .env

# Check PostgreSQL Connection
psql -U postgres -d musikwunsch -c "SELECT NOW();"
```

### Migration schlägt fehl
```bash
# PostgreSQL ist nicht erreichbar?
psql -U postgres

# Oder in .env konfigurieren:
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=musikwunsch
```

### Frontend startet nicht
```bash
# Port 5173 ist belegt?
lsof -i :5173  # macOS/Linux
netstat -ano | findstr :5173  # Windows

# Dependencies Problem?
rm -rf node_modules package-lock.json
npm install
```

## 📊 Datenbank prüfen

```bash
# Connect to PostgreSQL
psql -U postgres -d musikwunsch

# List tables
\dt

# Check users table
SELECT * FROM users;

# Check events table
SELECT * FROM events;

# Exit
\q
```

## 🔄 Nächste Schritte

1. ✅ Phase 1 setup abgeschlossen
2. → Phase 2: Gäste-App implementieren
   - Event-Zugang (QR-Code)
   - Musiksuche
   - Wünsche & Voting

## 📝 Wichtige Dateien

- `backend/.env` - Backend-Konfiguration
- `backend/src/server.js` - Express Server Entry Point
- `backend/src/migrations/001_initial_schema.sql` - Database Schema
- `frontend/src/App.jsx` - React App Root

## 💡 Development Tips

### Logs prüfen
```bash
# Backend Logs in Terminal where `npm run dev` läuft
# Frontend Logs in Browser Console (F12)
```

### Database Query testen
```bash
psql -U postgres -d musikwunsch -c "SELECT COUNT(*) as user_count FROM users;"
```

### API mit Postman testen
```
1. Postman öffnen
2. POST http://localhost:3000/api/auth/login
3. Body (JSON):
   {
     "email": "test@example.com",
     "password": "password123"
   }
4. Send
```

## 🚀 Bereit für Phase 2?

Wenn alles funktioniert:
- [ ] Backend läuft auf http://localhost:3000
- [ ] Frontend läuft auf http://localhost:5173
- [ ] Datenbank ist verbunden
- [ ] Registration & Login funktionieren

→ Dann kann Phase 2 starten! 🎉
