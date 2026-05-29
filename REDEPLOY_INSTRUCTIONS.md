# Musikwunsch VPS Redeploy - Anleitung

Das Login-Problem wurde behoben. Hier ist wie man das Update auf die VPS deployt.

## Option 1: Bash-Skript direkt auf VPS ausführen (Empfohlen)

### Schritt 1: SSH auf VPS verbinden
```bash
ssh root@187.124.20.215
```
Passwort: `Extra01#1234`

### Schritt 2: Redeploy-Skript ausführen
```bash
# Download the script and execute it
curl -fsSL https://raw.githubusercontent.com/cwoll/DJapp/main/REDEPLOY_VPS.sh | bash
```

Oder wenn Sie das Skript lokal haben:
```bash
scp REDEPLOY_VPS.sh root@187.124.20.215:/tmp/
ssh root@187.124.20.215 'bash /tmp/REDEPLOY_VPS.sh'
```

---

## Option 2: Python-Skript von lokal ausführen

### Voraussetzung: sshpass installiert
```bash
# Windows (mit Git Bash oder WSL):
# sshpass ist in Git Bash enthalten

# macOS:
brew install sshpass

# Linux:
sudo apt-get install sshpass
```

### Ausführen:
```bash
python3 redeploy_vps.py
```

Das Skript:
- Installiert Docker wenn nötig
- Clont das GitHub Repo
- Baut alle Docker Images
- Startet die Containers
- Führt Migrations aus
- Lädt Sample Songs

---

## Option 3: Manuelle Schritte (wenn Skripte nicht funktionieren)

### SSH auf VPS verbinden
```bash
ssh root@187.124.20.215
```

### Manuell deployen:
```bash
# 1. In das Deployment-Verzeichnis gehen oder es erstellen
mkdir -p /var/www/musikwunsch-app-docker
cd /var/www/musikwunsch-app-docker

# 2. Git Repo initialisieren (nur beim ersten Mal)
git init
git remote add origin https://github.com/cwoll/DJapp.git

# 3. Latest Code pullen
git fetch origin main
git reset --hard origin/main

# 4. Docker Images bauen
docker-compose build --no-cache

# 5. Alte Container stoppen und neue starten
docker-compose down
docker-compose up -d

# 6. Warten dass Services bereit sind
sleep 15

# 7. Migrations ausführen
docker-compose exec -T musikwunsch-api npm run migrate

# 8. Status prüfen
docker-compose ps
```

---

## Nach dem Redeploy - Testen

### 1. API Health Check
```bash
curl http://87.106.215.187.nip.io/api/health
```

**Erwartet:**
```json
{
  "status": "ok",
  "timestamp": "2026-05-29T...",
  "message": "Backend is running"
}
```

### 2. Admin Login
```bash
curl -X POST http://87.106.215.187.nip.io/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.local",
    "password": "testpass123"
  }'
```

**Erwartet:**
```json
{
  "user": {
    "id": "...",
    "email": "admin@test.local",
    "role": "admin"
  },
  "token": "eyJ...",
  "refreshToken": "eyJ..."
}
```

### 3. DJ Login
```bash
curl -X POST http://87.106.215.187.nip.io/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dj@test.local",
    "password": "testpass123"
  }'
```

### 4. Frontend testen
Öffnen Sie: `http://87.106.215.187.nip.io`
- Sollte zur Login-Seite gehen
- Login mit admin@test.local / testpass123
- Sollte zum Admin-Dashboard gehen

### 5. Guest App testen
Öffnen Sie: `http://87.106.215.187.nip.io/guest`
- Sollte QR-Code Entry-Seite zeigen

---

## Was wurde behoben?

### Nginx Routing (301 Redirect)
- `/api` location hat jetzt höhere Priorität
- Korrekte Proxy-Header gesetzt
- Trailing slashes hinzugefügt

### Backend Konfiguration
- `.env` hat jetzt `DB_HOST=db` (für Docker)
- `NODE_ENV=production`
- `FRONTEND_URL` korrekt gesetzt

### Dependencies
- `qrcode` Paket entfernt (nicht benötigt)
- Alle anderen Abhängigkeiten aktuell

---

## Troubleshooting

### Skript sagt "docker-compose: command not found"
Das bedeutet Docker Compose ist nicht installiert. Verwenden Sie **Option 3** (Manuelle Schritte) - das Skript wird Docker Compose installieren.

### API antwortet nicht / 503 Service Unavailable
- Warten Sie 20-30 Sekunden nach dem Deployment
- Backend braucht Zeit zum Starten
- Prüfen Sie Logs: `docker logs musikwunsch-api`

### Login gibt immer noch 301 Redirect
- Überprüfen Sie dass git pull funktioniert hat: `cd /var/www/musikwunsch-app-docker && git log -1`
- Sollte commit `20da4c9` oder später zeigen
- Wenn nicht: `git reset --hard origin/main` ausführen

### Datenbankfehler
```bash
# Prüfe PostgreSQL Status
docker logs musikwunsch-db

# Prüfe Migrations
docker logs musikwunsch-api | grep -i migrate

# Re-run migrations
docker-compose exec -T musikwunsch-api npm run migrate
```

---

## Wichtige Commit-Hashes

- **e7db50a** - Phase 2 Guest App Implementierung
- **dbf91f7** - Phase 2 Deployment Automation
- **20da4c9** - Login & Deployment Issues Fixed ← **DIESER COMMIT MUSS DEPLOYT SEIN**

---

## Support

Falls Sie Probleme haben:

1. Prüfen Sie welcher Commit auf der VPS deployed ist:
   ```bash
   cd /var/www/musikwunsch-app-docker
   git log -1 --oneline
   ```

2. Prüfen Sie Container Status:
   ```bash
   docker-compose ps
   docker-compose logs
   ```

3. Versuchen Sie noch einmal mit **Option 3** (Manuelle Schritte)

---

## Nächste Schritte nach erfolgreichem Redeploy

1. ✅ Testen Sie das Login (siehe oben)
2. ✅ Testen Sie Phase 2 Guest App
3. ✅ Laden Sie Sample Songs (wird automatisch gemacht)
4. 📋 Siehe `PHASE2_TESTING.md` für vollständige Tests
5. 🚀 Phase 3 Development planen (DJ Dashboard)
